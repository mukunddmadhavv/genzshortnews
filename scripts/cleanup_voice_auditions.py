"""Remove superseded local Mukund audio takes after approval of the v4 preset.

Print the exact removal list by default; --apply performs the requested cleanup.
Keep the original recording, clone metadata, v4 recipe assets and finished videos.
"""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VOICE = ROOT / "library/voices/mukund-hinglish"
EPISODE = ROOT / "episodes/medha-samay-zrSyjkvUaWU"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    required = [VOICE / "source.m4a", VOICE / "voice.json",
                VOICE / "v4-audition/mukund-tight-v4.wav",
                VOICE / "v4-audition/mukund-tight-v4-raw.mp3"]
    if not all(p.is_file() for p in required):
        raise SystemExit("Original recording, clone metadata and approved v4 audio must exist.")
    preset = json.loads((ROOT / "library/voices/presets.json").read_text())
    if len(preset["presets"]) != 1 or preset["presets"][0]["model"] != "eleven_v4":
        raise SystemExit("Activate the approved v4-only registry first.")
    names = ["identity-review.json", "identity-v2-profile.json", "identity-v2-raw.alignment.json",
             "identity-v2-raw.mp3", "identity-v2.alignment.json", "identity-v2.production.json",
             "identity-v2.wav", "preview-identity.txt"]
    candidates = [VOICE / name for name in names]
    # Audited episode audio takes; retain historical manifests/alignments and final video exports.
    candidates.extend(EPISODE / name for name in [
        "narration-hinglish.mp3", "narration-final.wav", "narration-mukund-confident-raw.mp3",
        "narration-mukund-confident.wav", "narration-mukund-tight.wav",
        "narration-mukund-energetic.wav", "narration-mukund-energetic-depaused.wav",
        "narration-mukund-fast10.wav",
    ])
    existing = [p for p in candidates if p.is_file()]
    records = [{"path": str(p.relative_to(ROOT)), "bytes": p.stat().st_size} for p in existing]
    for record in records:
        print(record["path"])
    if args.apply and records:
        for path in existing:
            path.unlink()
        (VOICE / "cleanup-v4.json").write_text(json.dumps({
            "reason": "User selected v4 exclusively and requested remaining Mukund takes deleted.",
            "date": "2026-09-28", "removed": records,
            "preserved": "Original recording, clone metadata, v4 assets, historical episode manifests and finished videos",
        }, indent=2) + "\n")
    print(f"{'Removed' if args.apply else 'Would remove'} {len(records)} superseded files.")


if __name__ == "__main__":
    main()
