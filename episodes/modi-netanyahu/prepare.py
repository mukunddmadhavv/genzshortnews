"""Prepare the Modi-Netanyahu episode from narration alignment and source images."""
import json
from pathlib import Path

EP = Path(__file__).resolve().parent
SPEED = 1.218


def main():
    align_file = EP / "narration-final.alignment.json"
    data = json.loads(align_file.read_text())
    alignment = data.get("normalized_alignment") or data["alignment"]
    text = "".join(alignment["characters"])

    def beat(phrase, rel_file, purpose):
        pos = text.casefold().find(phrase.casefold()) if phrase else 0
        if pos < 0:
            raise ValueError(f"Missing aligned phrase: {phrase}")
        start = alignment["character_start_times_seconds"][pos] if phrase else 0.0
        return {"start": start, "file": rel_file, "purpose": purpose}

    beats = [
        beat(None, "images/beat-01-greeting.jpg", "PM Modi and Netanyahu personal chemistry introduction"),
        beat("साल 2017", "images/beat-02-2017-visit.jpg", "Historic 2017 first visit to Israel by an Indian PM"),
        beat("बीच पर", "images/beat-03-beach-walk.jpg", "Iconic barefoot walk at Olga Beach"),
        beat("2018", "images/beat-04-ahmedabad-2018.jpg", "Netanyahu visiting Ahmedabad and Sabarmati Ashram in 2018"),
        beat("पीएम मोदी ने इज़राइल", "images/beat-05-knesset-speech.jpg", "PM Modi addressing the Knesset"),
        beat("डिफेंस टेक्नोलॉजी", "images/beat-06-agreements-mou.jpg", "Defense agreements and bilateral MoUs exchange"),
        beat("ब्रदर एंड ग्रेट फ्रेंड", "images/beat-07-tete-a-tete.jpg", "Warm tete-a-tete meeting / close personal bond"),
        beat("वैसे आपको इंडिया", "images/beat-08-partnership-cta.jpg", "Strategic partnership question and same-voice CTA"),
    ]

    (EP / "image-plan.json").write_text(json.dumps({
        "alignment": "narration-final.alignment.json",
        "narration": "narration-final.wav",
        "output": "news-panel.mp4",
        "beats": beats
    }, ensure_ascii=False, indent=2))

    # SFX whoosh cues at major story shifts: cuts 1 (2017), 3 (2018 visit), 4 (Knesset), 6 (friendship)
    whoosh_cuts = (1, 3, 4, 6)
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
        "sfx": "Four user-whoosh cues at key transition cuts, below speech"
    }, indent=2))

    print(f"Prepared {len(beats)} image beats and {len(cues)} whoosh cues.")


if __name__ == "__main__":
    main()
