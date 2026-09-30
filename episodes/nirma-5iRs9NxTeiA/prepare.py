"""Process the continuous narration and resolve this episode's image/SFX cues."""
import json
import subprocess
from pathlib import Path

EP = Path(__file__).resolve().parent
REF = "../../references/5iRs9NxTeiA/"
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

    def beat(phrase, file, purpose, crop=None, source_second=None):
        position = text.find(phrase) if phrase else 0
        if position < 0:
            raise ValueError(f"Missing phrase: {phrase}")
        item = {"start": alignment["character_start_times_seconds"][position] if phrase else 0,
                "file": REF + file, "purpose": purpose}
        if crop:
            item["crop"] = crop
        if source_second is not None:
            item["source_second"] = source_second
        return item

    beats = [
        beat(None, "frames/000.jpg", "Hook: actual confrontation", [60, 208, 1020, 1014], 0),
        beat("अहमदाबाद", "images/edex-probe.avif", "Identify university and incident"),
        beat("वीडियो में", "images/india-today-event.png", "Published screenshots show interaction"),
        beat("इसके बाद", "frames/039.jpg", "ABVP protest, original social handle retained", [0, 208, 1080, 1014], 39),
        beat("अब अपडेट", "images/edex-probe.avif", "University response and mutual apologies"),
        beat("साथ ही", "images/india-today-event.png", "Inquiry context; no result asserted"),
        beat("प्रोफेसर ने द प्रिंट", "images/theprint-event.png", "Attribute professor's account; central original image", [178, 0, 526, 392]),
        beat("उसी इवेंट", "frames/120.jpg", "Rajat Sood clarification, original handle retained", [313, 208, 763, 1014], 120),
        beat("तो सवाल", "frames/000.jpg", "Open question and same-voice brand ending", [60, 208, 1020, 1014], 0),
    ]
    (EP / "image-plan.json").write_text(json.dumps({
        "alignment": "narration-final.alignment.json", "narration": "narration-final.wav",
        "output": "news-panel.mp4", "beats": beats
    }, ensure_ascii=False, indent=2))
    (EP / "sfx-cues.json").write_text(json.dumps([
        {"file": "../../library/sfx/user-whoosh.mp3", "start_seconds": max(0, beats[i]["start"] - 0.3), "gain_db": -11}
        for i in (1, 3, 4, 7)
    ], indent=2))
    (EP / "episode.json").write_text(json.dumps({
        "subject": "Nirma University professor-student confrontation, apologies and inquiry",
        "source": "https://www.youtube.com/shorts/5iRs9NxTeiA",
        "checked_at": "2026-09-28", "model": "eleven_v3", "voice": "Configured approved ELEVENLABS_VOICE_ID",
        "language": "hi", "tts_speed": 1.12, "pitch_preserving_atempo": SPEED,
        "outro": "Follow GENZ SHORT NEWS for more!", "outro_generation": "Same take and processing as body",
        "gameplay": "../mau-6V_gg2zt3b8/gameplay-hinglish.mp4", "gameplay_start": 18,
        "gameplay_provenance": "Reused reference-derived Rocket League demo from approved prior episodes; local gameplay library remains empty",
        "format": "1080x1920, 30fps, image-only upper panel, red headline, blue footer",
        "sources": "../../references/5iRs9NxTeiA/sources.md",
        "direct_listening": "Unavailable; final wording checked separately with Scribe"
    }, ensure_ascii=False, indent=2))
    print("Prepared nine aligned image beats and four user-whoosh cues.")


if __name__ == "__main__":
    main()
