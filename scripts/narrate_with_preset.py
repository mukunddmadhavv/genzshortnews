"""Generate a complete narration using a named UI-ready voice preset."""
import argparse
import json
import subprocess
import sys
from pathlib import Path

from dotenv import dotenv_values, set_key

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "library/voices/presets.json"


def main():
    registry = json.loads(REGISTRY.read_text())
    presets = {p["id"]: p for p in registry["presets"]}
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preset", choices=presets, default=registry["default_preset"])
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--set-default", action="store_true")
    parser.add_argument("--text", type=Path)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--raw-audio", type=Path, help="Reuse an existing raw TTS take and adjacent alignment without an API call")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.list:
        print(json.dumps(registry, ensure_ascii=False, indent=2))
        return
    profile = presets[args.preset]
    if args.set_default:
        settings = {
            "NARRATION_PRESET": args.preset,
            "ELEVENLABS_VOICE_ID": profile["voice_id"],
            "ELEVENLABS_MODEL_ID": profile["model"],
            "ELEVENLABS_LANGUAGE_CODE": profile["language"],
            "ELEVENLABS_SPEED": str(profile["tts_speed"]),
            "ELEVENLABS_STABILITY": str(profile["stability"]),
            "ELEVENLABS_SIMILARITY": str(profile["similarity_boost"]),
            "ELEVENLABS_STYLE": str(profile["style"]),
            "ELEVENLABS_SPEAKER_BOOST": str(profile["use_speaker_boost"]).lower(),
        }
        if args.dry_run:
            print(json.dumps(settings, indent=2))
            return
        for name, value in settings.items():
            set_key(str(ROOT / ".env"), name, value)
        registry["default_preset"] = args.preset
        REGISTRY.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n")
        saved = dotenv_values(ROOT / ".env")
        assert all(saved[k] == v for k, v in settings.items())
        print(f"Default saved and verified: {profile['label']}")
        return
    if not args.out or not (args.text or args.raw_audio):
        parser.error("Provide --out and either --text or --raw-audio.")
    text = args.text.resolve() if args.text else None
    out = args.out.resolve()
    if (text and not text.is_file()) or out.suffix.lower() != ".wav":
        parser.error("Provide an existing script and a .wav output.")
    raw = args.raw_audio.resolve() if args.raw_audio else out.with_name(out.stem + "-raw.mp3")
    if args.raw_audio and (not raw.is_file() or not raw.with_suffix(".alignment.json").is_file()):
        parser.error("Raw audio and adjacent alignment are required.")
    if args.raw_audio and not args.dry_run:
        alignment = json.loads(raw.with_suffix(".alignment.json").read_text())
        if not (alignment.get("alignment") or alignment.get("normalized_alignment")):
            print("Raw take has no timestamps: processing audio only; align the final WAV before timing visuals.")
    polished = out.with_name(out.stem + "-polished.wav") if profile["tighten_pauses"] else out
    profile_path = out.with_suffix(".profile.json")
    outputs = {profile_path, out, polished}
    if not args.raw_audio:
        outputs.update((raw, raw.with_suffix(".alignment.json"), raw.with_suffix(".generation.json")))
    for audio in (polished, out):
        outputs.add(audio.with_suffix(".alignment.json"))
    outputs.update((polished.with_suffix(".production.json"), out.with_suffix(".pauses.json")))
    commands = [
        [sys.executable, str(ROOT / "scripts/elevenlabs_audio.py"), "tts",
         "--voice", profile["voice_id"], "--model", profile["model"],
         "--language", profile["language"], "--speed", str(profile["tts_speed"]),
         "--stability", str(profile["stability"]), "--similarity", str(profile["similarity_boost"]),
         "--style", str(profile["style"]),
         "--speaker-boost" if profile["use_speaker_boost"] else "--no-speaker-boost",
         "--text", str(text), "--out", str(raw)],
        [sys.executable, str(ROOT / "scripts/polish_narration.py"),
         "--audio", str(raw), "--profile", str(profile_path), "--out", str(polished)],
    ]
    if args.raw_audio:
        commands = commands[1:]
    stage_profiles = {}
    if profile["tighten_pauses"]:
        stages = profile.get("post_tightening_stages", [])
        tight = out.with_name(out.stem + "-tight.wav") if stages else out
        outputs.update((tight, tight.with_suffix(".alignment.json"), tight.with_suffix(".pauses.json")))
        commands.append([sys.executable, str(ROOT / "scripts/tighten_narration_pauses.py"),
                         "--audio", str(polished), "--out", str(tight),
                         "--minimum-gap", str(profile["pause_settings"]["minimum_gap_seconds"]),
                         "--keep-gap", str(2 * profile["pause_settings"]["keep_each_edge_seconds"])])
        previous = tight
        for index, stage in enumerate(stages):
            target = out if index == len(stages)-1 else out.with_name(out.stem + "-" + stage["id"] + ".wav")
            outputs.update((target, target.with_suffix(".alignment.json")))
            if stage["type"] == "polish":
                stage_path = out.with_name(out.stem + "-" + stage["id"] + ".profile.json")
                stage_profiles[stage_path] = {**stage, "voice_id": profile["voice_id"]}
                outputs.update((stage_path, target.with_suffix(".production.json")))
                commands.append([sys.executable, str(ROOT / "scripts/polish_narration.py"),
                                 "--audio", str(previous), "--profile", str(stage_path), "--out", str(target)])
            elif stage["type"] == "tighten":
                outputs.add(target.with_suffix(".pauses.json"))
                commands.append([sys.executable, str(ROOT / "scripts/tighten_narration_pauses.py"),
                                 "--audio", str(previous), "--out", str(target),
                                 "--minimum-gap", str(stage["minimum_gap_seconds"]),
                                 "--keep-gap", str(stage["retained_gap_seconds"])])
            else:
                parser.error("Unknown processing stage type.")
            previous = target
    if any(p.exists() for p in outputs):
        parser.error("Output files already exist; use a new output name.")
    if args.dry_run:
        print(json.dumps({"preset": profile, "commands": commands}, indent=2))
        return
    out.parent.mkdir(parents=True, exist_ok=True)
    profile_path.write_text(json.dumps(profile, ensure_ascii=False, indent=2))
    for path, stage_profile in stage_profiles.items():
        path.write_text(json.dumps(stage_profile, indent=2))
    for command in commands:
        subprocess.run(command, check=True, cwd=ROOT)
    print(f"Saved {profile['label']}: {out}")


if __name__ == "__main__":
    main()
