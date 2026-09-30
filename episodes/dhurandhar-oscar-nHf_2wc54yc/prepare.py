"""Prepare Dhurandhar Oscar episode with continuous narration and approved image layout."""
import json
import subprocess
from pathlib import Path

EP = Path(__file__).resolve().parent
REF = "../../references/nHf_2wc54yc/"


def main():
    transcript_path = EP / "narration-final.transcript.json"
    transcript = json.loads(transcript_path.read_text())

    # Build character-level alignment from Whisper transcription
    chars = []
    char_starts = []
    char_ends = []
    for seg in transcript["segments"]:
        text = seg["text"]
        start = seg["start"]
        end = seg["end"]
        n = len(text)
        if n == 0:
            continue
        dt = (end - start) / n
        for i, c in enumerate(text):
            chars.append(c)
            char_starts.append(start + i * dt)
            char_ends.append(start + (i + 1) * dt)

    alignment_data = {
        "alignment": {
            "characters": chars,
            "character_start_times_seconds": char_starts,
            "character_end_times_seconds": char_ends
        },
        "quality_check": {
            "source": "mlx-community/whisper-small-mlx",
            "segments_count": len(transcript["segments"]),
            "characters_count": len(chars)
        }
    }
    (EP / "narration-final.alignment.json").write_text(json.dumps(alignment_data, ensure_ascii=False, indent=2))

    beats = [
        {
            "start": 0.0,
            "file": REF + "images/ranveer-singh.jpg",
            "purpose": "Hook: High-res portrait of lead actor Ranveer Singh"
        },
        {
            "start": 4.28,
            "file": REF + "frames/001.jpg",
            "crop": [0, 144, 1080, 946],
            "purpose": "Official movie poster of Aditya Dhar's Dhurandhar"
        },
        {
            "start": 8.00,
            "file": REF + "frames/004.jpg",
            "crop": [0, 144, 1080, 946],
            "purpose": "Indian Tech & Infra tweet announcing Marathi film Gondhal as India's official entry for Oscars"
        },
        {
            "start": 15.02,
            "file": REF + "images/aditya-dhar.jpg",
            "purpose": "Director spotlight: High-res portrait of director Aditya Dhar"
        },
        {
            "start": 19.48,
            "file": REF + "images/vivek-vaswani.jpg",
            "purpose": "Jury attribution: High-res portrait of Oscar jury member Vivek Vaswani"
        },
        {
            "start": 24.48,
            "file": REF + "frames/009.jpg",
            "crop": [0, 144, 1080, 946],
            "purpose": "Inshorts card: Jury member reveals why Dhurandhar wasn't selected as India's Oscar entry"
        },
        {
            "start": 29.58,
            "file": REF + "frames/012.jpg",
            "crop": [0, 144, 1080, 946],
            "purpose": "Legible excerpt of NDTV report quoting Vivek Vaswani (4 of 14 votes, shortlist of Gondhal, Angh, Main Vaapas Aaunga)"
        },
        {
            "start": 38.06,
            "file": REF + "frames/004.jpg",
            "crop": [0, 144, 1080, 946],
            "purpose": "Winning entry: Marathi film Gondhal triumph"
        },
        {
            "start": 39.76,
            "file": REF + "frames/001.jpg",
            "crop": [0, 144, 1080, 946],
            "purpose": "Closing question and branded CTA with Dhurandhar poster backdrop"
        }
    ]

    image_plan = {
        "alignment": "narration-final.alignment.json",
        "narration": "narration-final.wav",
        "output": "news-panel.mp4",
        "beats": beats
    }
    (EP / "image-plan.json").write_text(json.dumps(image_plan, ensure_ascii=False, indent=2))
    (EP / "image-beats.json").write_text(json.dumps(beats, ensure_ascii=False, indent=2))

    # SFX whoosh cues at beats 1, 3, 5, 6
    sfx_cues = [
        {"file": "../../library/sfx/user-whoosh.mp3", "start_seconds": max(0, beats[i]["start"] - 0.3), "gain_db": -11}
        for i in (1, 3, 5, 6)
    ]
    (EP / "sfx-cues.json").write_text(json.dumps(sfx_cues, indent=2))

    audio_production = {
        "model": "eleven_v4",
        "preset": "mukund-tight",
        "voice_id": "F2bjsMJJPYo3S15YpV24",
        "language": "hi",
        "tts_speed": 1.0,
        "pause_shortening": "enabled (threshold -28 dB, min gap 0.3s)",
        "post_tightening_stages": ["energetic (1.07x)", "depaused", "fast10 (1.10x)"],
        "post_tts_tempo_product": 1.177,
        "outro_text": "Follow GENZ SHORT NEWS for more!",
        "outro": "Same generation and processing as body in one continuous take",
        "sfx": "Unmodified user-whoosh.mp3 at four narration-aligned cuts"
    }
    (EP / "audio-production.json").write_text(json.dumps(audio_production, indent=2))

    print(f"Prepared alignment, {len(beats)} image beats, and 4 whoosh cues.")


if __name__ == "__main__":
    main()
