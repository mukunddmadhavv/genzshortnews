"""Prepare this episode's approved pacing, reused brand outro and image timeline."""
import json
import subprocess
from pathlib import Path

EP = Path(__file__).resolve().parent
REF = "../../references/-HxnEOFxrhM/"
SPEED = 1.218


def run(*args):
    subprocess.run(["ffmpeg", "-v", "error", "-n", *map(str, args)], check=True)


def duration(path):
    return float(subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=nw=1:nk=1", str(path)
    ], text=True))


def main():
    run("-i", EP / "narration-hinglish.mp3", "-af",
        f"atempo={SPEED},highpass=f=75,equalizer=f=2600:t=q:w=0.8:g=1.5,"
        "acompressor=threshold=0.1:ratio=2.5:attack=8:release=90:makeup=1.4,"
        "loudnorm=I=-14:TP=-1.5:LRA=5", "-ar", "48000", "-ac", "1", EP / "body.wav")
    body_duration = duration(EP / "body.wav")
    outro = EP.parent / "mau-6V_gg2zt3b8/brand-outro.wav"
    run("-i", EP / "body.wav", "-i", outro, "-filter_complex",
        "[0:a][1:a]concat=n=2:v=0:a=1[a]", "-map", "[a]", "-ar", "48000",
        EP / "narration-final.wav")
    data = json.loads((EP / "narration-hinglish.alignment.json").read_text())
    for name in ("alignment", "normalized_alignment"):
        if data.get(name):
            for key in ("character_start_times_seconds", "character_end_times_seconds"):
                data[name][key] = [t / SPEED for t in data[name][key]]
    # Alignment covers the new body; outro is a separately checked cached take.
    (EP / "narration-final.alignment.json").write_text(json.dumps(data, ensure_ascii=False, indent=2))
    alignment = data.get("normalized_alignment") or data["alignment"]
    text = "".join(alignment["characters"])

    def beat(phrase, filename, crop=None):
        if phrase is None:
            start = 0
        else:
            position = text.casefold().find(phrase.casefold())
            if position < 0:
                raise ValueError(f"Missing narration phrase: {phrase}")
            start = alignment["character_start_times_seconds"][position]
        return {"start": start, "file": REF + filename, **({"crop": crop} if crop else {})}

    crop = [0, 214, 1080, 1008]
    beats = [
        beat(None, "frames/024.jpg", crop),
        beat("लेकिन इस", "images/ht-sharif-srinivas.png"),
        beat("पहला", "frames/006.jpg", crop),
        beat("उन्होंने दावा", "frames/010.jpg", crop),
        beat("इसी दौरान", "frames/024.jpg", crop),
        beat("ये उनका", "frames/000.jpg", [135, 214, 945, 1008]),
        beat("दूसरा moment", "images/it-jaishankar-briefing.jpg"),
        beat("वहाँ एक", "frames/038.jpg", crop),
        beat("एस जयशंकर", "frames/042.jpg", crop),
        beat("यानी एक", "images/it-jaishankar-briefing.jpg"),
    ]
    plan = {"alignment": "narration-final.alignment.json", "narration": "narration-final.wav",
            "output": "news-panel.mp4", "beats": beats}
    (EP / "image-plan.json").write_text(json.dumps(plan, ensure_ascii=False, indent=2))
    cues = [{"file": "../../library/sfx/user-whoosh.mp3",
             "start_seconds": max(0, beats[i]["start"] - 0.3), "gain_db": -11}
            for i in (2, 4, 6, 8)]
    (EP / "sfx-cues.json").write_text(json.dumps(cues, indent=2))
    (EP / "audio-production.json").write_text(json.dumps({
        "body_tts": "eleven_v3, configured voice, hi, speed 1.12",
        "body_atempo": SPEED, "body_duration": body_duration,
        "outro_file": str(outro), "outro_text": "Follow GENZ SHOT NEWS for more!",
        "duration": duration(EP / "narration-final.wav"),
        "alignment_scope": "Body only; outro starts at body_duration"
    }, indent=2))
    print(f"Prepared {duration(EP / 'narration-final.wav'):.2f}s with {len(beats)} visual beats")


if __name__ == "__main__":
    main()
