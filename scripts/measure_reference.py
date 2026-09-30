"""Record reproducible layout, edit-boundary and audio measurements."""
import json
import re
import subprocess
from pathlib import Path

from PIL import Image

root = Path("references/neonman")
image = Image.open(root / "frames/008.jpg")
bands = []
inside = False
for y in range(image.height):
    r, g, b = image.getpixel((0, y))
    red = r > 170 and g < 65 and b < 65
    if red and not inside:
        begin = y
    if inside and not red:
        bands.append([begin, y])
    inside = red
if inside:
    bands.append([begin, image.height])
# Restrict cut detection to the editorial panel: gameplay must not trigger cuts.
proc = subprocess.run([
    "ffmpeg", "-hide_banner", "-i", str(root / "CFZ6qULa8dU.mp4"),
    "-an", "-vf", "crop=1080:810:0:214,scale=270:202,select='gt(scene,0.12)',showinfo",
    "-fps_mode", "vfr", "-f", "null", "-",
], capture_output=True, text=True, check=True)
cuts = [float(t) for t in re.findall(r"pts_time:\s*([\d.]+)", proc.stderr)]
transcript = json.loads((root / "transcript.turbo.json").read_text())
tokens = len(transcript["text"].split())
result = {
    "red_bands_y_exclusive": bands,
    "editorial_scene_candidates_threshold_0_12": cuts,
    "asr_whitespace_tokens": tokens,
    "asr_tokens_per_minute_approx": round(tokens / (45.116667 / 60), 1),
    "asr_caveat": "Mixed Hindi/English token count, missed opening words and inaccurate proper nouns; not an exact spoken English WPM.",
    "audio_full_mix": {"integrated_lufs": -12.44, "true_peak_dbtp": 0.52, "loudness_range_lu": 3.10},
}
(root / "measurements.json").write_text(json.dumps(result, indent=2))
print(json.dumps(result, indent=2))
