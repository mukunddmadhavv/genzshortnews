"""Prepare this episode with one continuous voice take and approved image layout."""
import json
import subprocess
from pathlib import Path

EP = Path(__file__).resolve().parent
REF = "../../references/DAO_JgYbRL8/"
SPEED = 1.218


def main():
    # Audio was already rendered with ffmpeg at SPEED into narration-final.wav,
    # but ensure it exists and matches
    if not (EP / "narration-final.wav").exists():
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
        item = {
            "start": alignment["character_start_times_seconds"][position] if phrase else 0,
            "file": REF + filename,
            "purpose": purpose
        }
        if crop:
            item["crop"] = crop
        if source_second is not None:
            item["source_second"] = source_second
        return item

    beats = [
        beat(None, "images/thehindu-bhopal-scanner.jpg", "Hook: ANI photo of shopkeeper covering QR code scanner with black cloth in Bhopal"),
        beat("सबसे पहले", "frames/007.jpg", "Reporting headline: MP traders, retailers observe 'No UPI Day', seek rollback of MDR charges", [0, 140, 1080, 1004], 7),
        beat("उनका नारा", "images/fpj-no-upi-day.jpg", "Protest banner: shopkeeper displaying 'NO UPI DAY' poster in MP market"),
        beat("इसकी वजह", "images/indiatoday-mdr-gst.png", "Explainer infographic: 0.4% MDR charge on UPI transactions above Rs 2,000"),
        beat("हालांकि ये", "frames/018.jpg", "Livemint source: What consumers should keep in mind / UPI for people", [0, 140, 1080, 1004], 18),
        beat("लेकिन बड़े", "images/thehindu-bhopal-scanner.jpg", "Trader perspective: shops and soundboxes covered in protest against extra transaction costs"),
        beat("और अब एमपी", "frames/024.jpg", "Maharashtra escalation: 20,000 traders switching to cash only on Gandhi Jayanti", [0, 140, 1080, 1004], 24),
        beat("तो अगर आप", "frames/029.jpg", "Practical consumer takeaway: all payments in cash during protest", [0, 140, 1080, 1004], 29),
        beat("Follow GENZ", "images/livemint-maharashtra.jpg", "Closing call to action: retain relevant protest visuals through branded CTA")
    ]

    (EP / "image-plan.json").write_text(json.dumps({
        "alignment": "narration-final.alignment.json",
        "narration": "narration-final.wav",
        "output": "news-panel.mp4",
        "beats": beats
    }, ensure_ascii=False, indent=2))

    (EP / "sfx-cues.json").write_text(json.dumps([
        {"file": "../../library/sfx/user-whoosh.mp3", "start_seconds": max(0, beats[i]["start"] - 0.3), "gain_db": -11}
        for i in (1, 3, 6, 7)
    ], indent=2))

    (EP / "audio-production.json").write_text(json.dumps({
        "model": "eleven_v3",
        "voice": "Configured ELEVENLABS_VOICE_ID",
        "language": "hi",
        "tts_speed": 1.12,
        "atempo": SPEED,
        "outro_text": "Follow GENZ SHORT NEWS for more!",
        "outro": "Same generation and processing as body; alignment covers complete take",
        "sfx": "Unmodified user-whoosh.mp3 at four narration-aligned cuts"
    }, indent=2))

    print(f"Prepared continuous narration, {len(beats)} image beats, and 4 whoosh cues.")


if __name__ == "__main__":
    main()
