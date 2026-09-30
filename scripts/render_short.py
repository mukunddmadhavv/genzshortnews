"""Compose a news-panel video, continuous muted gameplay, branding and narration."""
import argparse
import json
import math
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def probe(path):
    result = subprocess.run(["ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", str(path)], capture_output=True, text=True, check=True)
    return json.loads(result.stdout)


def media_duration(path, kind):
    data = probe(path)
    stream = next((s for s in data["streams"] if s["codec_type"] == kind), None)
    if stream is None:
        raise ValueError(f"{path} has no {kind} stream")
    duration = float(stream.get("duration", data["format"]["duration"]))
    if not math.isfinite(duration) or duration <= 0:
        raise ValueError(f"Invalid duration: {path}")
    return duration


def brand_image(path, headline, channel, font_path):
    image = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 1079, 213), fill="#e91b27")
    draw.rectangle((0, 1754, 1079, 1919), fill="#1260dc")
    for text, center_y, max_size in [(headline.upper(), 107, 58), (channel.upper(), 1810, 58), ("FOLLOW FOR MORE", 1873, 36)]:
        if not text.strip():
            raise ValueError("Headline and channel must not be empty")
        for size in range(max_size, 23, -1):
            font = ImageFont.truetype(str(font_path), size)
            if draw.textbbox((0, 0), text, font=font, stroke_width=2)[2] <= 900:
                break
        else:
            raise ValueError("Headline/channel is too long; shorten it for mobile readability")
        draw.text((520, center_y), text, font=font, fill="white", stroke_width=2, stroke_fill="black", anchor="mm")
    image.save(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for flag in ["news", "gameplay", "narration", "font", "out"]:
        parser.add_argument(f"--{flag}", type=Path, required=True)
    parser.add_argument("--headline", required=True)
    parser.add_argument("--channel", required=True)
    parser.add_argument("--gameplay-start", type=float, default=0)
    parser.add_argument("--fps", type=int, choices=[30, 60], default=30)
    parser.add_argument("--loudness", type=float, default=-14, help="Final integrated loudness target in LUFS")
    parser.add_argument("--sfx-cues", type=Path, help="JSON array: file, start_seconds, gain_db; files relative to cue JSON")
    args = parser.parse_args()
    if not -24 <= args.loudness <= -12:
        parser.error("Loudness must be between -24 and -12 LUFS.")
    if args.out.exists():
        parser.error("Output exists; choose a new path.")
    if args.out.suffix.lower() != ".mp4":
        parser.error("Output must be an .mp4 file.")
    duration = media_duration(args.narration, "audio")
    if not math.isfinite(args.gameplay_start) or args.gameplay_start < 0:
        parser.error("Gameplay start must be finite and nonnegative.")
    for label, path, offset in [("News", args.news, 0), ("Gameplay", args.gameplay, args.gameplay_start)]:
        if media_duration(path, "video") - offset < duration - 1 / args.fps:
            parser.error(f"{label} video must cover the entire narration duration ({duration:.3f}s).")
    cues = json.loads(args.sfx_cues.read_text()) if args.sfx_cues else []
    for cue in cues:
        cue["file"] = str((args.sfx_cues.parent / cue["file"]).resolve())
        start = float(cue["start_seconds"])
        gain = float(cue.get("gain_db", -16))
        if not math.isfinite(start) or not 0 <= start < duration or not math.isfinite(gain):
            parser.error("Invalid SFX start or gain.")
        media_duration(cue["file"], "audio")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    brand = args.out.with_suffix(".brand.png")
    brand_image(brand, args.headline, args.channel, args.font)
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-nostdin", "-n", "-i", str(args.news), "-ss", str(args.gameplay_start), "-i", str(args.gameplay), "-i", str(args.narration), "-loop", "1", "-framerate", str(args.fps), "-i", str(brand)]
    for cue in cues:
        cmd += ["-i", cue["file"]]
    f = args.fps
    filters = [
        f"[0:v]setpts=PTS-STARTPTS,fps={f},scale=1080:810:force_original_aspect_ratio=decrease:force_divisible_by=2,pad=1080:810:(ow-iw)/2:(oh-ih)/2,setsar=1[news]",
        f"[1:v]setpts=PTS-STARTPTS,fps={f},scale=1080:730:force_original_aspect_ratio=increase:force_divisible_by=2,crop=1080:730,setsar=1[game]",
        "[news][game]vstack=inputs=2,pad=1080:1920:0:214:black[base]",
        "[base][3:v]overlay=0:0:shortest=1,format=yuv420p[v]",
        f"[2:a]asetpts=PTS-STARTPTS,aresample=48000,apad,atrim=duration={duration}[voice]",
    ]
    labels = "[voice]"
    for i, cue in enumerate(cues):
        start = float(cue["start_seconds"])
        gain = float(cue.get("gain_db", -16))
        filters.append(f"[{i+4}:a]asetpts=PTS-STARTPTS,aresample=48000,atrim=duration={duration-start},volume={gain}dB,adelay={round(start*1000)}:all=1[sfx{i}]")
        labels += f"[sfx{i}]"
    filters.append(f"{labels}amix=inputs={len(cues)+1}:duration=first:normalize=0,loudnorm=I={args.loudness}:TP=-1.5:LRA=7,aresample=48000[a]")
    cmd += ["-filter_complex", ";".join(filters), "-map", "[v]", "-map", "[a]", "-t", str(duration), "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", "-movflags", "+faststart", str(args.out)]
    subprocess.run(cmd, check=True)
    manifest = {"duration_seconds": duration, "fps": f, "news": str(args.news.resolve()), "gameplay": str(args.gameplay.resolve()), "gameplay_start": args.gameplay_start, "narration": str(args.narration.resolve()), "sfx": cues, "headline": args.headline, "channel": args.channel, "command": cmd, "probe": probe(args.out)}
    args.out.with_suffix(".manifest.json").write_text(json.dumps(manifest, indent=2))
    print(f"Saved {args.out} ({duration:.3f}s); inspect output and measure encoded loudness before publishing.")


if __name__ == "__main__":
    main()
