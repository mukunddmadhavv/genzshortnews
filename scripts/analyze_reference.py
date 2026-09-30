"""Extract exact integer-second samples and labeled contact sheets with FFmpeg."""
import argparse
import json
import math
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw


def run(args):
    return subprocess.run(args, check=True, capture_output=True, text=True).stdout


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("video", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    frames = args.out / "frames"
    sheets = args.out / "contact-sheets"
    frames.mkdir(exist_ok=True)
    sheets.mkdir(exist_ok=True)
    probe = json.loads(run(["ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", str(args.video)]))
    (args.out / "probe.json").write_text(json.dumps(probe, indent=2))
    video = next(s for s in probe["streams"] if s["codec_type"] == "video")
    duration = float(video.get("duration", probe["format"]["duration"]))
    entries = []
    for second in range(math.ceil(duration)):
        frame = frames / f"{second:03d}.jpg"
        run(["ffmpeg", "-v", "error", "-y", "-ss", str(second), "-i", str(args.video), "-frames:v", "1", "-q:v", "2", str(frame)])
        entries.append({"second": second, "file": str(frame.relative_to(args.out))})
    (args.out / "frames.json").write_text(json.dumps(entries, indent=2))
    for start in range(0, len(entries), 12):
        sheet = Image.new("RGB", (1080, 3 * 508), "#222222")
        draw = ImageDraw.Draw(sheet)
        for idx, entry in enumerate(entries[start:start + 12]):
            image = Image.open(args.out / entry["file"])
            image.thumbnail((270, 480))
            x, y = (idx % 4) * 270, (idx // 4) * 508
            sheet.paste(image, (x, y + 28))
            draw.text((x + 8, y + 6), f"t = {entry['second']:02d}s", fill="white")
        sheet.save(sheets / f"{start:03d}-{min(start+11, len(entries)-1):03d}.jpg", quality=92)
    run(["ffmpeg", "-v", "error", "-y", "-i", str(args.video), "-vn", "-ar", "16000", "-ac", "1", str(args.out / "audio.wav")])
    print(json.dumps({"duration": duration, "width": video["width"], "height": video["height"], "fps": video["avg_frame_rate"], "samples": len(entries)}, indent=2))


if __name__ == "__main__":
    main()
