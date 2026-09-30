"""Prepare the GENZ SHOT NEWS brand revision from the approved punchy take."""
import hashlib
import json
import shutil
import subprocess
from pathlib import Path


def run(args):
    subprocess.run(["ffmpeg", "-v", "error", "-n", *args], check=True)


def duration(path):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(path)], text=True))


def main():
    ep = Path("episodes/mau-6V_gg2zt3b8")
    source = Path("/Users/mukundmadhav/pitch/assets/sfx/whoosh.mp3")
    target = Path("library/sfx/user-whoosh.mp3")
    if not target.exists():
        shutil.copyfile(source, target)
    elif target.read_bytes() != source.read_bytes():
        raise ValueError("Stored user whoosh differs from supplied file")
    target.with_suffix(".source.json").write_text(json.dumps({"source": str(source), "sha256": hashlib.sha256(target.read_bytes()).hexdigest(), "preference": "User-selected whoosh; use instead of synthesized whooshes", "duration": duration(target)}, indent=2))
    old_beats = json.loads((ep / "image-beats-punchy.json").read_text())
    # Replace the old generic CTA, rather than appending a second follow request.
    old_outro_start = old_beats[-1]["start"]
    speed = 1.05
    run(["-i", str(ep / "narration-punchy.wav"), "-af", f"atrim=end={old_outro_start},asetpts=PTS-STARTPTS,atempo={speed},afade=t=out:st={old_outro_start/speed-0.015}:d=0.015", "-ar", "48000", "-ac", "1", str(ep / "brand-body.wav")])
    run(["-i", str(ep / "outro-brand.mp3"), "-af", "highpass=f=75,equalizer=f=2600:t=q:w=0.8:g=1.5,acompressor=threshold=0.1:ratio=2.5:attack=8:release=90:makeup=1.4,loudnorm=I=-12:TP=-1.5:LRA=5", "-ar", "48000", "-ac", "1", str(ep / "brand-outro.wav")])
    body_length = duration(ep / "brand-body.wav")
    run(["-i", str(ep / "brand-body.wav"), "-i", str(ep / "brand-outro.wav"), "-filter_complex", "[0:a][1:a]concat=n=2:v=0:a=1[a]", "-map", "[a]", "-ar", "48000", str(ep / "narration-branded.wav")])
    beats = []
    for beat in old_beats[:-1]:
        beats.append({"start": beat["start"]/speed, "file": beat["file"], **({"crop": beat["crop"]} if "crop" in beat else {})})
    last = old_beats[-1]
    beats.append({"start": body_length, "file": last["file"], "crop": last["crop"]})
    plan = {"alignment": "narration-punchy.alignment.json", "narration": "narration-branded.wav", "output": "news-panel-branded.mp4", "beats_output": "image-beats-branded.json", "beats": beats}
    (ep / "image-plan-branded.json").write_text(json.dumps(plan, indent=2))
    cues = [{"file": "../../library/sfx/user-whoosh.mp3", "start_seconds": max(0,beats[i]["start"]-0.3), "gain_db": -11} for i in (2,4,6,9,10,12)]
    (ep / "sfx-cues-branded.json").write_text(json.dumps(cues, indent=2))
    (ep / "brand-revision.json").write_text(json.dumps({"speed_change": "1.05x applied to the already 1.16x Hinglish body", "body_duration": body_length, "outro_duration": duration(ep / "brand-outro.wav"), "outro": "Follow GENZ SHOT NEWS for more!", "footer": {"background": "#1260dc", "text": "white", "channel": "GENZ SHOT NEWS", "cta": "FOLLOW FOR MORE"}, "whoosh": str(source)}, indent=2))
    print(f"Prepared branded narration: {duration(ep / 'narration-branded.wav'):.2f}s")


if __name__ == "__main__":
    main()
