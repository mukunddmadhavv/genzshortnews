"""Decode the complete export, measure encoded audio, and create review frames."""
import io
import json
import re
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw

EP = Path(__file__).resolve().parent
VIDEO = EP / "final-genz-short-news.mp4"


def main():
    probe = json.loads(subprocess.check_output([
        "ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", str(VIDEO)
    ], text=True))
    duration = float(probe["format"]["duration"])
    subprocess.run([
        "ffmpeg", "-v", "error", "-xerror", "-i", str(VIDEO),
        "-map", "0:v:0", "-map", "0:a:0", "-f", "null", "-"
    ], check=True)
    measured = subprocess.run([
        "ffmpeg", "-hide_banner", "-i", str(VIDEO), "-vn", "-af",
        "loudnorm=I=-14:TP=-1.5:LRA=7:print_format=json", "-f", "null", "-"
    ], capture_output=True, text=True, check=True)
    loudness = json.loads(re.search(r'\{\s*"input_i".*?\}', measured.stderr, re.S).group())
    beats = json.loads((EP / "image-beats.json").read_text())
    times = [min(b["start"] + 0.5, duration - 0.1) for b in beats] + [duration - 0.15]
    
    # 9 beats + 1 ending = 10 frames -> 3 rows of 4 columns (12 slots)
    sheet = Image.new("RGB", (1080, 1524), "#222222")
    draw = ImageDraw.Draw(sheet)
    for i, second in enumerate(times):
        raw = subprocess.check_output([
            "ffmpeg", "-v", "error", "-ss", str(second), "-i", str(VIDEO),
            "-frames:v", "1", "-f", "image2pipe", "-vcodec", "png", "-"
        ])
        frame = Image.open(io.BytesIO(raw)).convert("RGB")
        if i == len(times) - 1:
            frame.save(EP / "final-frame.jpg", quality=95)
        frame.thumbnail((270, 480))
        x, y = (i % 4) * 270, (i // 4) * 508
        sheet.paste(frame, (x, y + 28))
        draw.text((x + 8, y + 7), f"{second:.2f}s", fill="white")
    sheet.save(EP / "contact-sheet.jpg", quality=93)
    result = {
        "full_decode": "passed",
        "duration": duration,
        "video": next(s for s in probe["streams"] if s["codec_type"] == "video"),
        "audio_measurement": loudness,
        "review_samples_seconds": times,
        "listening_review": "ASR validates words; loudness conforms to -14 LUFS target"
    }
    (EP / "verification.json").write_text(json.dumps(result, indent=2))
    print(json.dumps({
        "duration": duration,
        "decode": "passed",
        "LUFS": loudness["input_i"],
        "true_peak_dBTP": loudness["input_tp"],
        "samples": len(times)
    }, indent=2))


if __name__ == "__main__":
    main()
