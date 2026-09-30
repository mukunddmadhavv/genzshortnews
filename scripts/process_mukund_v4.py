"""Apply Mukund Tight's local processing to the v4 audition, without another API call."""
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "library/voices/mukund-hinglish/v4-audition"


def main():
    registry = json.loads((ROOT / "library/voices/presets.json").read_text())
    preset = next(p for p in registry["presets"] if p["id"] == "mukund-tight")
    raw = OUT / "mukund-tight-v4-raw.mp3"
    raw.with_suffix(".alignment.json").write_text(json.dumps({
        "alignment": None, "normalized_alignment": None,
        "note": "Text-to-dialogue returned audio only; no character timestamps are available.",
    }, indent=2) + "\n")
    profile = {
        "voice_id": preset["voice_id"], "model": "eleven_v4",
        "stability": 0.5, "similarity": 0.9,
        "atempo": preset["atempo"], "audio_filter": preset["audio_filter"],
        "note": "Mukund Tight local processing. V2 TTS speed/style/speaker boost were not sent to the dialogue endpoint.",
    }

    def polish(source, name, settings):
        target = OUT / (name + ".wav")
        if target.exists():
            return target
        path = OUT / (name + ".profile.json")
        path.write_text(json.dumps(settings, indent=2) + "\n")
        subprocess.run([sys.executable, str(ROOT / "scripts/polish_narration.py"),
                        "--audio", str(source), "--profile", str(path), "--out", str(target)], check=True)
        return target

    def tighten(source, name, minimum, keep):
        target = OUT / (name + ".wav")
        if target.exists():
            return target
        subprocess.run([sys.executable, str(ROOT / "scripts/tighten_narration_pauses.py"),
                        "--audio", str(source), "--out", str(target),
                        "--minimum-gap", str(minimum), "--keep-gap", str(keep)], check=True)
        return target

    previous = polish(raw, "v4-polished", profile)
    pauses = preset["pause_settings"]
    previous = tighten(previous, "v4-tight", pauses["minimum_gap_seconds"], 2 * pauses["keep_each_edge_seconds"])
    for stage in preset["post_tightening_stages"]:
        name = "mukund-tight-v4" if stage["id"] == "fast10" else "v4-" + stage["id"]
        if stage["type"] == "polish":
            previous = polish(previous, name, {**stage, "model": "eleven_v4", "voice_id": preset["voice_id"]})
        else:
            previous = tighten(previous, name, stage["minimum_gap_seconds"], stage["retained_gap_seconds"])
    if not (OUT / "mukund-tight-v4.mp3").exists():
        subprocess.run(["ffmpeg", "-v", "error", "-n", "-i", str(previous),
                        "-c:a", "libmp3lame", "-b:a", "192k", str(OUT / "mukund-tight-v4.mp3")], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-xerror", "-i", str(previous), "-f", "null", "-"], check=True)
    result = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(previous),
                             "-af", "loudnorm=I=-14:TP=-1.5:LRA=7:print_format=json", "-f", "null", "-"],
                            capture_output=True, text=True, check=True)
    loudness, _ = json.JSONDecoder().raw_decode(result.stderr[result.stderr.rfind("{"):])
    probe = json.loads(subprocess.check_output(["ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", str(previous)], text=True))
    (OUT / "verification.json").write_text(json.dumps({"full_decode_passed": True, "probe": probe, "loudness": loudness,
        "visual_or_listening_identity_review": "Not performed; user comparison required."}, indent=2) + "\n")
    print(json.dumps({"duration": probe["format"]["duration"], "loudness": loudness}, indent=2))


if __name__ == "__main__":
    main()
