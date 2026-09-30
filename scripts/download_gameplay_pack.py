"""Download the selected background-gameplay excerpts and keep source credits.

Run from the project root: uv run --with pillow scripts/download_gameplay_pack.py
"""

import concurrent.futures
import io
import json
from pathlib import Path
import subprocess

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1] / "library" / "gameplay"
CLIPS = [
    ("minecraft", "minecraft-parkour", "XBIaqOm0RKQ", "Minecraft parkour", 30),
    ("valorant", "valorant-gameplay", "gRO6CYbko9A", "Valorant", 30),
    ("subway-surfers", "subway-surfers-classic", "i0M4ARe9v0Y", "Subway Surfers", 30),
    ("driving", "gta5-mega-ramp", "ZtLrNBdXT7M", "GTA 5 mega ramp", 30),
    ("rocket-league", "rocket-league-gameplay", "x-5javV7KYM", "Rocket League", 30),
    ("trackmania", "trackmania-racing", "xFuqSVMA2ec", "Trackmania", 30),
    ("driving", "forza-horizon-5", "i-bBdHhD7xo", "Forza Horizon 5", 30),
    ("fall-guys", "fall-guys-gameplay", "nTLVxH9Bnqw", "Fall Guys", 30),
    ("geometry-dash", "geometry-dash-gameplay", "XLeRUGHIhzU", "Geometry Dash", 30),
    ("roblox", "roblox-parkour", "aIx8qw56cQg", "Roblox parkour", 30),
    ("fortnite", "fortnite-gameplay", "8TkVhpUCL08", "Fortnite", 30),
    ("counter-strike", "cs2-gameplay", "E3Grf9xDOtk", "Counter-Strike 2", 30),
    ("steep", "steep-snowboarding", "EnGiQrWBrko", "Steep snowboarding", 30),
    ("descenders", "descenders-biking", "-eHl8gGXI0Q", "Descenders biking", 30),
    ("driving", "beamng-drive", "u5g2H4_zUMs", "BeamNG.drive", 30),
]


def download(clip):
    folder, slug, video_id, label, start = clip
    base = ROOT / folder / slug
    base.parent.mkdir(parents=True, exist_ok=True)
    video = base.with_suffix(".mp4")
    url = f"https://www.youtube.com/watch?v={video_id}"
    if not video.exists():
        result = subprocess.run([
            "uvx", "yt-dlp", "--no-playlist", "--no-progress",
            "-f", "bestvideo[vcodec^=avc1][height<=1080][ext=mp4]/bestvideo[height<=1080][ext=mp4]",
            "--download-sections", f"*{start}-{start + 120}",
            "--write-info-json", "--write-description",
            "--external-downloader-args", "ffmpeg:-loglevel error -nostats",
            "-o", str(base) + ".%(ext)s", url,
        ], capture_output=True, text=True, timeout=600)
        if result.returncode:
            raise RuntimeError(f"Download failed for {label}: {result.stderr[-2000:]}")
    metadata = json.loads(base.with_suffix(".info.json").read_text())
    probe = subprocess.run([
        "ffprobe", "-v", "error", "-show_format", "-show_streams",
        "-of", "json", str(video),
    ], capture_output=True, text=True, check=True)
    details = json.loads(probe.stdout)
    stream = next(s for s in details["streams"] if s["codec_type"] == "video")
    duration = float(details["format"]["duration"])
    if not 119 <= duration <= 125:
        raise RuntimeError(f"Unexpected duration for {label}: {duration}")
    decode = subprocess.run([
        "ffmpeg", "-v", "error", "-xerror", "-i", str(video),
        "-map", "0:v:0", "-f", "null", "-",
    ], capture_output=True, text=True, timeout=240)
    if decode.returncode:
        raise RuntimeError(f"Decode failed for {label}: {decode.stderr[-1000:]}")
    creator = metadata.get("channel") or metadata.get("uploader")
    channel_url = metadata.get("channel_url") or metadata.get("uploader_url")
    credit = f"Gameplay by {creator}: {channel_url}. Source: {url}."
    if video_id == "XBIaqOm0RKQ":
        credit += " Licensed under CC BY 4.0: https://creativecommons.org/licenses/by/4.0/. Excerpted for background use."
    record = {
        "game": label, "file": str(video.relative_to(ROOT)),
        "source_url": url, "source_title": metadata["title"],
        "creator": creator, "channel_url": channel_url,
        "source_description": metadata.get("description", ""),
        "youtube_license_field": metadata.get("license"),
        "reuse_basis": "Uploader's reuse statement in the saved source description; not independently certified.",
        "credit": credit, "retrieved_on": "2026-09-28",
        "requested_source_start_seconds": start,
        "requested_source_end_seconds": start + 120,
        "cut_note": "Stream-copy excerpt; boundaries may differ slightly at keyframes.",
        "duration_seconds": duration, "width": stream["width"],
        "height": stream["height"], "fps": stream["avg_frame_rate"],
        "audio_streams": sum(s["codec_type"] == "audio" for s in details["streams"]),
        "size_bytes": video.stat().st_size, "full_decode_passed": True,
    }
    base.with_suffix(".source.json").write_text(json.dumps(record, indent=2) + "\n")
    print(f"Verified: {label} | {stream['width']}x{stream['height']} | {duration:.1f}s", flush=True)
    return record


def previews(records):
    for second in (5, 55, 105):
        sheet = Image.new("RGB", (1200, 1250), "#151515")
        draw = ImageDraw.Draw(sheet)
        for index, record in enumerate(records):
            result = subprocess.run([
                "ffmpeg", "-v", "error", "-ss", str(second),
                "-i", str(ROOT / record["file"]), "-frames:v", "1",
                "-vf", "scale=392:220:force_original_aspect_ratio=decrease,pad=392:220:(ow-iw)/2:(oh-ih)/2",
                "-f", "image2pipe", "-vcodec", "mjpeg", "-",
            ], capture_output=True, check=True)
            frame = Image.open(io.BytesIO(result.stdout))
            x, y = (index % 3) * 400 + 4, (index // 3) * 250 + 4
            sheet.paste(frame, (x, y))
            draw.text((x + 4, y + 226), f"{index + 1}. {record['game']} ({second}s)", fill="white")
        sheet.save(ROOT / f"preview-{second:03d}s.jpg", quality=90)


def main():
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        records = list(pool.map(download, CLIPS))
    previews(records)
    lines = [
        "# Gameplay collection — 15 clips", "",
        "Downloaded 2026-09-28. Approximately two minutes each, video-only (muted), up to 1080p.",
        "Each file passed a complete FFmpeg decode. Preview sheets sample 5, 55 and 105 seconds;",
        "these samples are not a full visual review. Choose a continuous active segment for each Short.",
        "", "Sources explicitly offer reuse in their descriptions. Follow the saved creator terms",
        "and paste the relevant credit below into your Short's description.",
        "The `.description` and `.source.json` files beside each video preserve the terms and source.",
        "", "| Game | Local MP4 | Duration | Resolution | Source |",
        "|---|---|---:|---|---|",
    ]
    for record in records:
        lines.append(f"| {record['game']} | [{record['file']}]({record['file']}) | {record['duration_seconds']:.1f}s | {record['width']}×{record['height']} | [YouTube]({record['source_url']}) |")
    lines += ["", "## Copy-paste credits", ""]
    for record in records:
        lines += [f"### {record['game']}", "", record["credit"], ""]
    lines += ["## Preview sheets", "", "- [5-second samples](preview-005s.jpg)", "- [55-second samples](preview-055s.jpg)", "- [105-second samples](preview-105s.jpg)", ""]
    (ROOT / "COLLECTION.md").write_text("\n".join(lines))
    print(f"DONE: {len(records)} clips; {sum(r['size_bytes'] for r in records) / 1e9:.2f} GB", flush=True)


if __name__ == "__main__":
    main()
