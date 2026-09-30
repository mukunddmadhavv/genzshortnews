"""Build preview-01 editorial cards and aligned captions, then render with FFmpeg."""
import json
import math
import re
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[1]
EP = ROOT / "episodes/preview-01"
FONT = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
REGULAR = "/System/Library/Fonts/Supplemental/Arial.ttf"


def font(size, bold=True):
    return ImageFont.truetype(FONT if bold else REGULAR, size)


def wrap(draw, text, f, width):
    lines = []
    line = ""
    for word in text.split():
        candidate = f"{line} {word}".strip()
        if line and draw.textlength(candidate, font=f) > width:
            lines.append(line)
            line = word
        else:
            line = candidate
    if line:
        lines.append(line)
    return lines


def textblock(draw, text, xy, width, size, fill, bold=True):
    x, y = xy
    for line in wrap(draw, text, font(size, bold), width):
        draw.text((x, y), line, font=font(size, bold), fill=fill)
        y += size + 12
    return y


def main():
    data = json.loads((EP / "narration.alignment.json").read_text())
    align = data.get("normalized_alignment") or data["alignment"]
    text = "".join(align["characters"])
    starts = align["character_start_times_seconds"]
    ends = align["character_end_times_seconds"]
    duration = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(EP / "narration.mp3")], text=True))
    tags = [(m.start(), m.end()) for m in re.finditer(r"\[[^]]*\]", text)]
    words = []
    for m in re.finditer(r"\S+", text):
        if any(a <= m.start() < b for a, b in tags):
            continue
        words.append({"text": m.group(), "start": starts[m.start()], "end": ends[m.end()-1]})
    captions = []
    for i in range(0, len(words), 4):
        chunk = words[i:i+4]
        captions.append({"text": " ".join(w["text"] for w in chunk), "start": chunk[0]["start"], "end": chunk[-1]["end"]})
    (EP / "captions.json").write_text(json.dumps(captions, indent=2))

    def when(phrase):
        pos = text.lower().find(phrase.lower())
        if pos < 0:
            raise ValueError(f"Missing aligned phrase: {phrase}")
        return starts[pos]

    beats = [
        (0, "THE HEADLINE", "A COMPLAINT.\nBUT WHAT'S\nCONFIRMED?", "India's Got Latent", "000"),
        (when("The reference report"), "01 / WHAT WAS REPORTED", "A VIEWER\nFILES A\nCOMPLAINT", "Mukesh Chhabra + Netflix India", "017"),
        (when("The viewer reportedly"), "02 / THE OBJECTION", "A REMARK.\nA REACTION.\nA PLATFORM.", "The report describes a viewer's objection.", "008"),
        (when("But a complaint"), "03 / THE DISTINCTION", "ALLEGATION\nIS NOT\nA VERDICT.", "A complaint does not establish wrongdoing.", None),
        (when("And here's the key part"), "04 / THE IMPORTANT DETAIL", "THE SOURCE\nSTILL NEEDS\nCHECKING.", "The report itself includes this caveat.", "038"),
        (when("the speaker's identity"), "05 / THREE THINGS TO CHECK", "WHO SAID IT?\nWHAT CONTEXT?\nWHICH SOURCE?", "Identity / full context / original recording", None),
        (when("So before"), "THE TAKEAWAY", "CHECK THE\nFULL SOURCE.", "A viral clip is only part of the story.", "017"),
        (when("Follow for"), "GEN Z NEWS / FORMAT PREVIEW", "CONTEXT\nBEHIND THE\nHEADLINES.", "Follow for clear, concise explainers.", None),
    ]
    (EP / "beats.json").write_text(json.dumps([{"start": b[0], "label": b[1], "headline": b[2]} for b in beats], indent=2))
    cards = []
    for idx, (_, label, headline, sub, source_frame) in enumerate(beats):
        im = Image.new("RGB", (1080, 810), "#10131c")
        d = ImageDraw.Draw(im)
        d.rectangle((0, 0, 12, 810), fill="#f3dd4b")
        d.text((55, 25), label, font=font(25), fill="#f3dd4b")
        d.line((55, 70, 995, 70), fill="#3c414e", width=2)
        if source_frame:
            source = Image.open(ROOT / f"references/neonman/frames/{source_frame}.jpg").crop((0, 214, 1080, 1024))
            if source_frame == "000":
                source = source.crop((250, 0, 830, 810))
            visual = ImageOps.contain(source, (440, 425))
            im.paste(visual, (555 + (440-visual.width)//2, 110+(425-visual.height)//2))
            d.rounded_rectangle((545, 100, 1005, 545), radius=12, outline="#3c414e", width=2)
        size = 57 if source_frame else 72
        y = 125
        for line in headline.splitlines():
            d.text((55, y), line, font=font(size), fill="white")
            y += size + 17
        textblock(d, sub, (55, 460 if source_frame else 440), 465 if source_frame else 920, 28, "#b9c4d5", False)
        d.text((55, 575), "Based on the supplied Neon Man Shorts report / demo", font=font(20, False), fill="#8390a5")
        d.rounded_rectangle((48, 622, 1008, 790), radius=18, fill="#222b3b")
        im.save(EP / f"card-{idx:02d}.png")
        cards.append(im)
    fps = 30
    count = math.ceil(duration*fps)
    cmd = ["ffmpeg", "-v", "error", "-n", "-f", "rawvideo", "-pixel_format", "rgb24", "-video_size", "1080x810", "-framerate", str(fps), "-i", "pipe:0", "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", str(EP / "news-panel.mp4")]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    cached = None
    payload = None
    try:
        for n in range(count):
            t = n/fps
            beat = max(i for i, b in enumerate(beats) if b[0] <= t)
            cap = next((i for i, c in enumerate(captions) if c["start"] <= t < c["end"] + 0.08), -1)
            key = (beat, cap)
            if key != cached:
                image = cards[beat].copy()
                d = ImageDraw.Draw(image)
                if cap >= 0:
                    lines = wrap(d, captions[cap]["text"], font(42), 875)
                    y = 705 - len(lines)*27
                    for line in lines:
                        d.text((525, y), line, font=font(42), anchor="mt", fill="#f3dd4b")
                        y += 54
                payload = image.tobytes()
                cached = key
            proc.stdin.write(payload)
    finally:
        proc.stdin.close()
    if proc.wait():
        raise RuntimeError("News-panel render failed")
    # Use a clean part of the reference, before its late subscription graphics.
    subprocess.run(["ffmpeg", "-v", "error", "-n", "-i", str(ROOT / "references/neonman/CFZ6qULa8dU.mp4"), "-t", "35", "-vf", "crop=1080:730:0:1024,fps=30", "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", str(EP / "gameplay-section.mp4")], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-n", "-stream_loop", "-1", "-i", str(EP / "gameplay-section.mp4"), "-t", str(duration+0.1), "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", str(EP / "gameplay.mp4")], check=True)
    cues = [{"file": "pop.mp3", "start_seconds": beats[i][0], "gain_db": -17} for i in (1, 3, 4, 7)]
    (EP / "sfx-cues.json").write_text(json.dumps(cues, indent=2))
    print(f"Built {len(beats)} news cards, {len(captions)} timed captions, {duration:.2f}s gameplay.")


if __name__ == "__main__":
    main()
