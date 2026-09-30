"""Channel-checked, resumable YouTube upload used only by the dashboard worker."""
import argparse
import json
import os
from pathlib import Path
import sys
import tempfile
import time

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import AuthorizedSession, Request

EXPECTED_HANDLE = "@genzshotnews"


def write_private(path, data):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd, name = tempfile.mkstemp(dir=path.parent)
    try:
        with os.fdopen(fd, "w") as stream:
            json.dump(data, stream)
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def emit(**data):
    print(json.dumps(data), flush=True)


def connect(token_file):
    credentials = Credentials.from_authorized_user_file(str(token_file))
    credentials.refresh(Request())
    session = AuthorizedSession(credentials)
    response = session.get("https://www.googleapis.com/youtube/v3/channels",
                           params={"part": "snippet", "mine": "true"}, timeout=30)
    response.raise_for_status()
    channels = response.json().get("items", [])
    if len(channels) != 1 or channels[0]["snippet"].get("customUrl", "").lower() != EXPECTED_HANDLE:
        raise ValueError("Credentials do not belong to @genzshotnews.")
    channel = channels[0]
    return session, {"id": channel["id"], "title": channel["snippet"]["title"], "handle": EXPECTED_HANDLE}


def upload(session, channel, spec, checkpoint_path):
    video = Path(spec["file"])
    size = video.stat().st_size
    checkpoint = json.loads(checkpoint_path.read_text()) if checkpoint_path.exists() else {}
    if checkpoint.get("youtube_id"):
        return checkpoint
    if not checkpoint.get("uri"):
        metadata = {"snippet": {"title": spec["title"], "description": spec["description"], "categoryId": "25"},
                    "status": {"privacyStatus": spec["privacy"], "selfDeclaredMadeForKids": spec["madeForKids"]}}
        response = session.post("https://www.googleapis.com/upload/youtube/v3/videos",
                                params={"uploadType": "resumable", "part": "snippet,status"}, json=metadata,
                                headers={"X-Upload-Content-Type": "video/mp4", "X-Upload-Content-Length": str(size)}, timeout=60)
        response.raise_for_status()
        checkpoint = {"uri": response.headers["Location"], "size": size, "file": str(video)}
        write_private(checkpoint_path, checkpoint)
    if checkpoint["size"] != size or checkpoint["file"] != str(video):
        raise ValueError("Upload file changed; refusing to resume with different media.")

    uri = checkpoint["uri"]
    def finish(response):
        result = response.json()
        checkpoint.update(youtube_id=result["id"], channel_id=channel["id"],
                          privacy=result.get("status", {}).get("privacyStatus", spec["privacy"]))
        write_private(checkpoint_path, checkpoint)
        return checkpoint

    # Ask YouTube which bytes it already has, including after worker restarts.
    response = session.put(uri, headers={"Content-Length": "0", "Content-Range": f"bytes */{size}"}, timeout=60)
    if response.status_code in (200, 201):
        return finish(response)
    if response.status_code in (404, 410):
        raise ValueError("Resumable upload expired. Check YouTube Studio before starting another upload.")
    if response.status_code != 308:
        response.raise_for_status()
        raise ValueError("Unexpected resumable upload response.")
    offset = int(response.headers.get("Range", "bytes=0--1").split("-")[-1]) + 1 if "Range" in response.headers else 0
    with video.open("rb") as stream:
        while offset < size:
            stream.seek(offset)
            data = stream.read(8 * 1024 * 1024)
            end = offset + len(data) - 1
            response = session.put(uri, data=data, headers={"Content-Type": "video/mp4",
                                   "Content-Range": f"bytes {offset}-{end}/{size}"}, timeout=180)
            if response.status_code in (200, 201):
                return finish(response)
            if response.status_code != 308:
                response.raise_for_status()
                raise ValueError("Unexpected upload response.")
            next_offset = int(response.headers["Range"].split("-")[-1]) + 1
            if next_offset <= offset:
                raise ValueError("Upload did not advance; retry to resume.")
            offset = next_offset
            emit(type="progress", percent=round(100 * offset / size))
    raise ValueError("Upload completion was not confirmed. Retry to reconcile with YouTube.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--token-file", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--spec", type=Path)
    parser.add_argument("--checkpoint", type=Path)
    args = parser.parse_args()
    try:
        session, channel = connect(args.token_file)
        if args.check:
            emit(type="channel", **channel)
            return
        if not args.spec or not args.checkpoint:
            parser.error("Upload requires --spec and --checkpoint")
        result = upload(session, channel, json.loads(args.spec.read_text()), args.checkpoint)
        emit(type="published", youtubeId=result["youtube_id"], channelId=result["channel_id"], privacy=result["privacy"])
    except Exception as error:
        # Never expose tokens, resumable-session URLs or raw provider responses.
        emit(type="error", message=str(error) if isinstance(error, ValueError) else f"YouTube operation failed ({type(error).__name__}). Check API enablement, quota and OAuth authorization.")
        sys.exit(1)


if __name__ == "__main__":
    main()
