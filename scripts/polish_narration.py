"""Apply a saved narration delivery profile and retime its character alignment."""
import argparse
import json
import subprocess
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audio", type=Path, required=True)
    parser.add_argument("--profile", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    alignment_out = args.out.with_suffix(".alignment.json")
    manifest_out = args.out.with_suffix(".production.json")
    if args.out.suffix.lower() != ".wav":
        parser.error("Use a .wav output for the production master.")
    if any(path.exists() for path in (args.out, alignment_out, manifest_out)):
        parser.error("Output already exists; choose a new filename.")
    profile = json.loads(args.profile.read_text())
    speed = float(profile["atempo"])
    if not 0.5 <= speed <= 2:
        parser.error("Profile atempo must be between 0.5 and 2.")
    alignment = json.loads(args.audio.with_suffix(".alignment.json").read_text())
    for name in ("alignment", "normalized_alignment"):
        if alignment.get(name):
            for key in ("character_start_times_seconds", "character_end_times_seconds"):
                alignment[name][key] = [time / speed for time in alignment[name][key]]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    filters = f"atempo={speed},{profile['audio_filter']}"
    subprocess.run([
        "ffmpeg", "-hide_banner", "-v", "error", "-n", "-i", str(args.audio),
        "-af", filters, "-ar", "48000", "-ac", "1", "-c:a", "pcm_s24le", str(args.out)
    ], check=True)
    alignment_out.write_text(json.dumps(alignment, ensure_ascii=False, indent=2))
    manifest_out.write_text(json.dumps({
        "source": str(args.audio), "profile": profile, "filter": filters,
        "alignment": str(alignment_out),
        "note": "Apply once to the raw TTS take. Pitch is preserved; alignment times are divided by atempo."
    }, ensure_ascii=False, indent=2))
    print(f"Saved {args.out} and retimed alignment")


if __name__ == "__main__":
    main()
