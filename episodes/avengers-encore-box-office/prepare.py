"""Prepare the Avengers Encore episode from narration alignment and source images."""
import json
import subprocess
from pathlib import Path

EP = Path(__file__).resolve().parent
SPEED = 1.30


def main():
    wav_out = EP / "narration-final.wav"
    if not wav_out.exists():
        subprocess.run([
            "ffmpeg", "-v", "error", "-y", "-i", str(EP / "narration-hinglish.mp3"),
            "-af", f"atempo={SPEED},highpass=f=75,equalizer=f=2600:t=q:w=0.8:g=1.5,"
            "acompressor=threshold=0.1:ratio=2.5:attack=8:release=90:makeup=1.4,"
            "loudnorm=I=-14:TP=-1.5:LRA=5", "-ar", "48000", "-ac", "1",
            str(wav_out)
        ], check=True)

    data = json.loads((EP / "narration-hinglish.alignment.json").read_text())
    for name in ("alignment", "normalized_alignment"):
        if data.get(name):
            for key in ("character_start_times_seconds", "character_end_times_seconds"):
                data[name][key] = [t / SPEED for t in data[name][key]]
    (EP / "narration-final.alignment.json").write_text(json.dumps(data, ensure_ascii=False, indent=2))

    alignment = data.get("normalized_alignment") or data["alignment"]
    text = "".join(alignment["characters"])

    def beat(phrase, rel_file, purpose):
        pos = text.casefold().find(phrase.casefold()) if phrase else 0
        if pos < 0:
            raise ValueError(f"Missing aligned phrase: {phrase}")
        start = alignment["character_start_times_seconds"][pos] if phrase else 0.0
        return {"start": start, "file": rel_file, "purpose": purpose}

    beats = [
        beat(None, "images/beat-01-endgame-poster.jpg", "Avengers Endgame Encore re-release intro"),
        beat("साल 2019", "images/beat-02-russo-brothers.jpg", "Russo Brothers and 2019 historic $1.2B Endgame opening"),
        beat("अब सितंबर 2026", "images/beat-03-imax-theater.jpg", "September 2026 Encore $86M opening weekend / IMAX record"),
        beat("जिसके बाद", "images/beat-04-james-cameron.jpg", "James Cameron Avatar ($2.92B) box office chase at $2.89B"),
        beat("वहीं इंडिया", "images/beat-05-cinema-crowd.jpg", "Indian box office ₹440 Cr gross record for Hollywood films"),
        beat("और अब एनकोर", "images/beat-06-robert-downey-jr.jpg", "Robert Downey Jr. returning as Victor von Doom / Doctor Doom"),
        beat("टीज़र्स देखने", "images/beat-07-doomsday-teaser.jpg", "Avengers: Doomsday teaser connection in Encore scenes"),
        beat("क्या एंडगेम", "images/beat-08-chris-evans.jpg", "Chris Evans (Steve Rogers) and engagement question + same-voice CTA"),
    ]

    (EP / "image-plan.json").write_text(json.dumps({
        "alignment": "narration-final.alignment.json",
        "narration": "narration-final.wav",
        "output": "news-panel.mp4",
        "beats": beats
    }, ensure_ascii=False, indent=2))

    # SFX whoosh cues at major thematic shifts: cuts 1 (2019), 2 (2026 Encore), 3 (Avatar chase), 4 (India record), 5 (Doctor Doom)
    whoosh_cuts = (1, 2, 3, 4, 5)
    cues = [
        {
            "file": "../../library/sfx/user-whoosh.mp3",
            "start_seconds": max(0.0, beats[i]["start"] - 0.25),
            "gain_db": -11.0
        }
        for i in whoosh_cuts
    ]
    (EP / "sfx-cues.json").write_text(json.dumps(cues, indent=2))

    (EP / "audio-production.json").write_text(json.dumps({
        "model": "eleven_v3",
        "voice": "Configured ELEVENLABS_VOICE_ID",
        "language": "hi",
        "script": "Devanagari Hindi always (no bracketed tags)",
        "tts_speed": 1.12,
        "atempo": SPEED,
        "outro_text": "Follow GENZ SHORT NEWS for more!",
        "outro": "Same complete generation and processing as body",
        "sfx": "Five user-whoosh cues at key transition cuts, below speech"
    }, indent=2))

    print(f"Prepared {len(beats)} image beats and {len(cues)} whoosh cues.")


if __name__ == "__main__":
    main()
