"""Replace preview cards with related reference visuals only, on a black panel."""
import json
import math
import subprocess
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
EP = ROOT / "episodes/preview-01"


def main():
    alignment = json.loads((EP / "narration.alignment.json").read_text())
    alignment = alignment.get("normalized_alignment") or alignment["alignment"]
    text = "".join(alignment["characters"])

    def when(phrase):
        position = text.lower().find(phrase.lower())
        if position < 0:
            raise ValueError(phrase)
        return alignment["character_start_times_seconds"][position]

    # Crop coordinates are relative to the reference's 1080x810 news panel.
    # Tight crops remove source padding, while contain-fit keeps source text intact.
    beats = [
        (0, "000", (260, 0, 820, 810)),
        (when("The reference report"), "005", (275, 0, 805, 810)),
        (when("Mukesh Chhabra"), "017", (0, 45, 1080, 755)),
        (when("The viewer reportedly"), "020", (0, 220, 1080, 610)),
        (when("questioned the platform"), "028", (0, 155, 1080, 650)),
        (when("But a complaint"), "017", (0, 45, 1080, 755)),
        (when("And here's the key part"), "038", (0, 285, 1080, 520)),
        (when("the speaker's identity"), "041", (0, 250, 1080, 550)),
        (when("So before"), "008", (0, 85, 1080, 725)),
        (when("Follow for"), "017", (0, 45, 1080, 755)),
    ]
    duration = float(subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=nw=1:nk=1", str(EP / "narration.mp3"),
    ], text=True))
    panels = []
    for _, frame, crop in beats:
        source = Image.open(ROOT / f"references/neonman/frames/{frame}.jpg")
        source = source.crop((0, 214, 1080, 1024)).crop(crop)
        source = ImageOps.contain(source, (1080, 810), Image.Resampling.LANCZOS)
        panel = Image.new("RGB", (1080, 810), "black")
        panel.paste(source, ((1080-source.width)//2, (810-source.height)//2))
        panels.append(panel.tobytes())
    output = EP / "news-panel-images.mp4"
    proc = subprocess.Popen([
        "ffmpeg", "-v", "error", "-n", "-f", "rawvideo", "-pixel_format", "rgb24",
        "-video_size", "1080x810", "-framerate", "30", "-i", "pipe:0", "-an",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", str(output),
    ], stdin=subprocess.PIPE)
    try:
        for n in range(math.ceil(duration*30)):
            index = max(i for i, beat in enumerate(beats) if beat[0] <= n/30)
            proc.stdin.write(panels[index])
    finally:
        proc.stdin.close()
    if proc.wait():
        raise RuntimeError("Image panel render failed")
    (EP / "image-beats.json").write_text(json.dumps([
        {"start": start, "reference_frame": frame, "crop": crop}
        for start, frame, crop in beats
    ], indent=2))
    print(f"Saved {output}")


if __name__ == "__main__":
    main()
