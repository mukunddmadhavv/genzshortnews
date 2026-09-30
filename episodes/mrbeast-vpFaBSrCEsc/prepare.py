"""Prepare the MrBeast episode from its complete expressive narration take."""
import json
import subprocess
from pathlib import Path

EP = Path(__file__).resolve().parent
REF = "../../references/vpFaBSrCEsc/"
SPEED = 1.218


def main():
    subprocess.run([
        "ffmpeg", "-v", "error", "-n", "-i", str(EP / "narration-hinglish.mp3"),
        "-af", f"atempo={SPEED},highpass=f=75,equalizer=f=2600:t=q:w=0.8:g=1.5,"
        "acompressor=threshold=0.1:ratio=2.5:attack=8:release=90:makeup=1.4,"
        "loudnorm=I=-14:TP=-1.5:LRA=5", "-ar", "48000", "-ac", "1",
        str(EP / "narration-final.wav")
    ], check=True)
    data = json.loads((EP / "narration-hinglish.alignment.json").read_text())
    for name in ("alignment", "normalized_alignment"):
        if data.get(name):
            for key in ("character_start_times_seconds", "character_end_times_seconds"):
                data[name][key] = [t / SPEED for t in data[name][key]]
    (EP / "narration-final.alignment.json").write_text(json.dumps(data, ensure_ascii=False, indent=2))
    alignment = data.get("normalized_alignment") or data["alignment"]
    text = "".join(alignment["characters"])

    def beat(phrase, filename, purpose, crop=None, source_second=None):
        position = text.casefold().find(phrase.casefold()) if phrase else 0
        if position < 0:
            raise ValueError(f"Missing aligned phrase: {phrase}")
        item = {"start": alignment["character_start_times_seconds"][position] if phrase else 0,
                "file": REF + filename, "purpose": purpose}
        if crop:
            item["crop"] = crop
        if source_second is not None:
            item["source_second"] = source_second
        return item

    beats = [
        beat(None, "images/indulge-visit.webp", "MrBeast waving at Taj Mahal: immediate event context"),
        beat("पहले ये देखो", "frames/006.jpg", "Fan-recorded Taj Mahal scene; preserve agrawitharshiya credit", [246, 214, 834, 1024], 6),
        beat("fans आसपास", "frames/017.jpg", "Crowd around MrBeast; preserve footage credit", [312, 214, 772, 1024], 17),
        beat("उनकी wife", "images/indulge-visit.webp", "Thea with MrBeast at the monument"),
        beat("India Today", "frames/008.jpg", "Filming location context for attributed permission report", [246, 214, 834, 1024], 8),
        beat("और एक छोटे", "images/india-today-visit.jpg", "Publisher composite shows handmade portrait and young fan"),
        beat("लेकिन अब", "frames/022.jpg", "Actual Mr Bean caption, keep complete caption and handle", [288, 214, 792, 1024], 22),
        beat("वैसे तुम्हें", "images/indulge-visit.webp", "Return to greeting image for viewer question and same-voice CTA"),
    ]
    (EP / "image-plan.json").write_text(json.dumps({
        "alignment": "narration-final.alignment.json", "narration": "narration-final.wav",
        "output": "news-panel.mp4", "beats": beats
    }, ensure_ascii=False, indent=2))
    (EP / "sfx-cues.json").write_text(json.dumps([
        {"file": "../../library/sfx/user-whoosh.mp3", "start_seconds": max(0, beats[i]["start"] - 0.3), "gain_db": -11}
        for i in (1, 5, 6)
    ], indent=2))
    (EP / "audio-production.json").write_text(json.dumps({
        "model": "eleven_v3", "voice": "Configured approved ELEVENLABS_VOICE_ID",
        "language": "hi", "tts_speed": 1.12, "atempo": SPEED,
        "directions": ["excited opening", "brief laugh at caption joke", "warm fan interaction"],
        "expression_evidence": "Creative recommendations; reference acoustic emotion unverified",
        "outro_text": "Follow GENZ SHORT NEWS for more!",
        "outro": "Same complete generation and processing as body",
        "sfx": "Three unchanged user-whoosh cues, below speech"
    }, indent=2))
    print("Prepared eight image beats and three whoosh cues.")


if __name__ == "__main__":
    main()
