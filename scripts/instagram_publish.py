"""Instagram Reels publishing helper using Instagram Graph API and Supabase video hosting."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import urllib.parse
import urllib.request
import urllib.error

DEFAULT_APP_ID = "1736345594332140"
DEFAULT_APP_SECRET = "59ae7b5b3662810ec883abb048e6aa94"
GRAPH_BASE = "https://graph.instagram.com"


DEFAULT_BUCKET = "genz-video"


def emit(**data):
    print(json.dumps(data), flush=True)


def load_env():
    # Attempt loading .env or .env.dashboard if present
    for name in [".env", ".env.dashboard"]:
        path = Path(name)
        if path.exists():
            for line in path.read_text().splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip().strip("'\"")
                    if k and not os.environ.get(k):
                        os.environ[k] = v


def remux_faststart(video_path: Path, output_path: Path) -> Path:
    """Remux mp4 with +faststart so moov atom is at start to prevent container stall."""
    cmd = ["ffmpeg", "-y", "-i", str(video_path), "-c", "copy", "-movflags", "+faststart", str(output_path)]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"FFmpeg faststart remux failed: {res.stderr[-300:]}")
    return output_path


def upload_to_supabase(video_path: Path, supabase_url: str, service_key: str, bucket: str = DEFAULT_BUCKET) -> str:
    """Upload MP4 video to Supabase Storage and return public URL."""
    supabase_url = supabase_url.rstrip("/")
    filename = f"{video_path.stem}-{int(time.time())}.mp4"
    upload_url = f"{supabase_url}/storage/v1/object/{bucket}/{filename}"

    with video_path.open("rb") as f:
        data = f.read()

    req = urllib.request.Request(
        upload_url,
        data=data,
        headers={
            "apikey": service_key,
            "Authorization": f"Bearer {service_key}",
            "Content-Type": "video/mp4",
            "x-upsert": "true",
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            pass
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Supabase video upload failed ({e.code}): {body}")

    public_url = f"{supabase_url}/storage/v1/object/public/{bucket}/{filename}"
    return public_url


def create_reel_container(video_url: str, caption: str, access_token: str) -> str:
    """Create Instagram Reel media container."""
    url = f"{GRAPH_BASE}/me/media"
    payload = urllib.parse.urlencode({
        "media_type": "REELS",
        "video_url": video_url,
        "caption": caption,
        "access_token": access_token
    }).encode("utf-8")

    req = urllib.request.Request(url, data=payload, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            res = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Instagram reel container creation failed ({e.code}): {body}")

    container_id = res.get("id")
    if not container_id:
        raise RuntimeError(f"Invalid response from container creation: {res}")
    return container_id


def wait_for_container(container_id: str, access_token: str, max_wait_sec: int = 600, poll_interval: int = 5) -> None:
    """Poll container status until FINISHED, ERROR, or timeout."""
    deadline = time.time() + max_wait_sec
    fields = "status_code"
    url = f"{GRAPH_BASE}/{container_id}?fields={fields}&access_token={urllib.parse.quote(access_token)}"

    while time.time() < deadline:
        time.sleep(poll_interval)
        try:
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=30) as resp:
                res = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Failed to check container status ({e.code}): {body}")

        status = res.get("status_code")
        emit(type="progress", status=status, container_id=container_id)
        if status == "FINISHED":
            return
        if status in ("ERROR", "EXPIRED"):
            raise RuntimeError(f"Instagram video container failed: {res}")

    raise TimeoutError("Instagram video container processing timed out")


def publish_reel_container(container_id: str, access_token: str) -> str:
    """Publish the processed Reel container."""
    url = f"{GRAPH_BASE}/me/media_publish"
    payload = urllib.parse.urlencode({
        "creation_id": container_id,
        "access_token": access_token
    }).encode("utf-8")

    req = urllib.request.Request(url, data=payload, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            res = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Instagram reel publish failed ({e.code}): {body}")

    media_id = res.get("id")
    if not media_id:
        raise RuntimeError(f"Invalid publish response: {res}")
    return media_id


def check_account(access_token: str):
    """Verify Instagram access token and get account info."""
    url = f"{GRAPH_BASE}/me?fields=id,username&access_token={urllib.parse.quote(access_token)}"
    req = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            res = json.loads(resp.read().decode("utf-8"))
        emit(type="checked", valid=True, username=res.get("username"), id=res.get("id"))
        return res
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        emit(type="checked", valid=False, error=body)
        raise RuntimeError(f"Token validation failed: {body}")


def main():
    load_env()
    parser = argparse.ArgumentParser(description="Publish video to Instagram Reels via Graph API")
    parser.add_argument("--spec", help="Path to JSON spec with file and caption")
    parser.add_argument("--video", help="Direct path to MP4 video")
    parser.add_argument("--caption", help="Reel caption")
    parser.add_argument("--token", help="Instagram API token override")
    parser.add_argument("--bucket", default=os.environ.get("SUPABASE_BUCKET", DEFAULT_BUCKET), help="Supabase storage bucket name")
    parser.add_argument("--check", action="store_true", help="Check account and token validity")
    args = parser.parse_args()

    token = args.token or os.environ.get("INSTAGRAM_API_TOKEN") or os.environ.get("INSTAGRAM_ACCESS_TOKEN")

    if args.check:
        if not token:
            emit(type="error", message="INSTAGRAM_API_TOKEN is not configured.")
            sys.exit(1)
        try:
            check_account(token)
            sys.exit(0)
        except Exception as e:
            sys.exit(1)

    # Determine video and caption from args or spec
    video_file = args.video
    caption = args.caption or ""

    if args.spec:
        spec_path = Path(args.spec)
        if not spec_path.exists():
            emit(type="error", message=f"Spec file not found: {args.spec}")
            sys.exit(1)
        spec = json.loads(spec_path.read_text())
        video_file = spec.get("file") or video_file
        caption = spec.get("instagram_caption") or spec.get("caption") or caption

    if not video_file or not Path(video_file).exists():
        emit(type="error", message=f"Video file missing: {video_file}")
        sys.exit(1)

    if not token:
        emit(type="error", message="INSTAGRAM_API_TOKEN is not set.")
        sys.exit(1)

    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if not supabase_url or not supabase_key:
        emit(type="error", message="SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are required for public video hosting.")
        sys.exit(1)

    with tempfile.TemporaryDirectory() as tmpdir:
        fast_video = Path(tmpdir) / "faststart.mp4"
        emit(type="status", message="Remuxing video with faststart flag...")
        remux_faststart(Path(video_file), fast_video)

        emit(type="status", message=f"Uploading video to storage bucket '{args.bucket}' for public accessibility...")
        public_url = upload_to_supabase(fast_video, supabase_url, supabase_key, bucket=args.bucket)
        emit(type="uploaded", url=public_url)

        emit(type="status", message="Creating Instagram Reel container...")
        container_id = create_reel_container(public_url, caption, token)
        emit(type="container_created", container_id=container_id)

        emit(type="status", message="Waiting for Instagram to process video container...")
        wait_for_container(container_id, token)

        emit(type="status", message="Publishing Instagram Reel...")
        media_id = publish_reel_container(container_id, token)

        emit(type="published", platform="instagram", instagramMediaId=media_id, mediaId=media_id, caption=caption)


if __name__ == "__main__":
    main()
