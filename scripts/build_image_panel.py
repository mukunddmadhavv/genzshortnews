"""Render an image-only news panel from a per-episode, narration-aligned plan."""
import argparse
import json
import math
import subprocess
from pathlib import Path

from PIL import Image, ImageOps


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", type=Path)
    args = parser.parse_args()
    root = args.plan.resolve().parent
    plan = json.loads(args.plan.read_text())
    align_path = (root / plan["alignment"]) if "alignment" in plan else None
    data = json.loads(align_path.read_text()) if align_path and align_path.is_file() else {}
    alignment = data.get("normalized_alignment") or data.get("alignment")
    text = "".join(alignment["characters"]) if alignment and "characters" in alignment else ""
    duration = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(root / plan["narration"])], text=True))
    beats = plan["beats"]
    panels = []
    search_pos = 0
    for beat in beats:
        if "phrase" in beat and text:
            position = text.casefold().find(beat["phrase"].casefold(), search_pos)
            if position < 0:
                position = text.casefold().find(beat["phrase"].casefold())
            if position < 0:
                raise ValueError(f"Missing aligned phrase: {beat['phrase']}")
            search_pos = position + len(beat["phrase"])
            beat["start"] = alignment["character_start_times_seconds"][position]
        elif "start" not in beat:
            raise ValueError(f"Beat must provide either 'phrase' or 'start': {beat}")

        with Image.open(root / beat["file"]) as original:
            image = ImageOps.exif_transpose(original).convert("RGB")
            if "crop" in beat:
                left, top, right, bottom = beat["crop"]
                if not (0 <= left < right <= image.width and 0 <= top < bottom <= image.height):
                    raise ValueError(f"Crop outside source: {beat['file']}")
                image = image.crop(beat["crop"])
            image = ImageOps.contain(image, (1080, 810), Image.Resampling.LANCZOS)
            panel = Image.new("RGB", (1080, 810), "black")
            panel.paste(image, ((1080-image.width)//2, (810-image.height)//2))
            panels.append(panel.tobytes())
    starts = [b["start"] for b in beats]
    if starts[0] != 0 or any(a >= b for a, b in zip(starts, starts[1:])) or starts[-1] >= duration:
        raise ValueError("Beats must start at zero, increase strictly, and fit narration")
    output = root / plan["output"]
    if output.exists():
        raise FileExistsError(output)
    proc = subprocess.Popen(["ffmpeg", "-v", "error", "-n", "-f", "rawvideo", "-pixel_format", "rgb24", "-video_size", "1080x810", "-framerate", "30", "-i", "pipe:0", "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", str(output)], stdin=subprocess.PIPE)
    try:
        for n in range(math.ceil(duration*30)):
            index = max(i for i, start in enumerate(starts) if start <= n/30)
            proc.stdin.write(panels[index])
    finally:
        proc.stdin.close()
    if proc.wait():
        raise RuntimeError("Image panel render failed")
    (root / plan.get("beats_output", "image-beats.json")).write_text(json.dumps(beats, ensure_ascii=False, indent=2))
    print(f"Rendered {len(beats)} image beats over {duration:.2f}s: {output}")


if __name__ == "__main__":
    main()
