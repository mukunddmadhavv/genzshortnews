"""Prepare this episode with one continuous voice take and approved image layout."""
import json
import subprocess
from pathlib import Path

EP = Path(__file__).resolve().parent
REF = "../../references/ez1YRJeIJyw/"
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
        beat(None, "frames/000.jpg", "Introduce Sunil Pal and Salman Khan", [0, 194, 1080, 1004], 0),
        beat("दरअसल", "frames/034.jpg", "Salman's prior on-show response to trolling", [150, 194, 930, 1004], 34),
        beat("इस पर", "images/bhl-sunil.jpg", "Attribute Pal's audience argument"),
        beat("उन्होंने कहा", "frames/010.jpg", "Pal speaking; paraphrased quote attributed in narration", [135, 194, 945, 1004], 10),
        beat("फिर उन्होंने", "frames/024.jpg", "Pal making the film earnings comparison", [150, 194, 930, 1004], 24),
        beat("ध्यान रहे", "images/news18-salman.jpg", "Qualification: box-office comparison is Pal's claim"),
        beat("बात यहीं", "images/bhl-sunil.jpg", "Pal's criticism of Bigg Boss; publisher watermark retained"),
        beat("यानी सलमान", "frames/034.jpg", "Recall Salman discussing personal attacks, not replying to Pal", [150, 194, 930, 1004], 34),
        beat("जबकि सुनील", "images/outlook-sunil-salman.webp", "Contrast positions and retain relevant imagery through the CTA"),
    ]
    (EP / "image-plan.json").write_text(json.dumps({
        "alignment": "narration-final.alignment.json", "narration": "narration-final.wav",
        "output": "news-panel.mp4", "beats": beats
    }, ensure_ascii=False, indent=2))
    (EP / "sfx-cues.json").write_text(json.dumps([
        {"file": "../../library/sfx/user-whoosh.mp3", "start_seconds": max(0, beats[i]["start"] - 0.3), "gain_db": -11}
        for i in (1, 2, 4, 6)
    ], indent=2))
    (EP / "audio-production.json").write_text(json.dumps({
        "model": "eleven_v3", "voice": "Configured ELEVENLABS_VOICE_ID",
        "language": "hi", "tts_speed": 1.12, "atempo": SPEED,
        "outro_text": "Follow GENZ SHORT NEWS for more!",
        "outro": "Same generation and processing as body; alignment covers complete take",
        "sfx": "Unmodified user-whoosh.mp3 at four narration-aligned cuts"
    }, indent=2))
    print("Prepared continuous narration, nine image beats, and four whoosh cues.")


if __name__ == "__main__":
    main()
