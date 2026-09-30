"""Shorten detected quiet gaps while preserving speech speed and retiming alignment."""
import argparse
import json
import re
import subprocess
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audio", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--minimum-gap", type=float, default=0.3)
    parser.add_argument("--keep-gap", type=float, default=0.16)
    args = parser.parse_args()
    if not 0.006 < args.keep_gap < args.minimum_gap:
        parser.error("Require 0.006 < keep-gap < minimum-gap.")
    outputs = [args.out, args.out.with_suffix(".alignment.json"), args.out.with_suffix(".pauses.json")]
    if args.out.suffix != ".wav" or any(p.exists() for p in outputs):
        parser.error("Choose a new .wav output path.")
    alignment = json.loads(args.audio.with_suffix(".alignment.json").read_text())
    duration = float(subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(args.audio)
    ], text=True))
    result = subprocess.run([
        "ffmpeg", "-hide_banner", "-i", str(args.audio), "-af",
        f"silencedetect=noise=-28dB:d={args.minimum_gap}", "-f", "null", "-"
    ], capture_output=True, text=True, check=True)
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", result.stderr)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", result.stderr)]
    if len(ends) < len(starts):
        ends.append(duration)
    # Preserve an equal amount of quiet audio on each side of the cut.
    edge = args.keep_gap / 2
    cuts = [(start + edge, end - edge) for start, end in zip(starts, ends) if end - start >= args.minimum_gap]
    if not cuts:
        # A naturally tight take still needs a valid final file and alignment.
        import shutil
        shutil.copyfile(args.audio, args.out)
        outputs[1].write_text(json.dumps(alignment, ensure_ascii=False, indent=2))
        outputs[2].write_text(json.dumps({"source": str(args.audio), "cuts": [], "removed_seconds": 0, "speech_speed_changed": False}, indent=2))
        print("No long quiet gaps; preserved the take and alignment unchanged.")
        return
    segments = []
    previous = 0
    for start, end in cuts:
        segments.append((previous, start))
        previous = end
    segments.append((previous, duration))
    filters = []
    for i, (start, end) in enumerate(segments):
        filters.append(
            f"[0:a]atrim=start={start}:end={end},asetpts=PTS-STARTPTS,"
            f"afade=t=in:d=0.003,afade=t=out:st={max(0, end-start-0.003)}:d=0.003[s{i}]"
        )
    filters.append("".join(f"[s{i}]" for i in range(len(segments))) + f"concat=n={len(segments)}:v=0:a=1[out]")
    subprocess.run([
        "ffmpeg", "-v", "error", "-n", "-i", str(args.audio), "-filter_complex", ";".join(filters),
        "-map", "[out]", "-c:a", "pcm_s24le", "-ar", "48000", str(args.out)
    ], check=True)

    def remap(time):
        return time - sum(max(0, min(time, end) - start) for start, end in cuts)

    for name in ("alignment", "normalized_alignment"):
        if alignment.get(name):
            for key in ("character_start_times_seconds", "character_end_times_seconds"):
                alignment[name][key] = [remap(t) for t in alignment[name][key]]
    outputs[1].write_text(json.dumps(alignment, ensure_ascii=False, indent=2))
    saved = sum(end-start for start, end in cuts)
    outputs[2].write_text(json.dumps({
        "source": str(args.audio), "cuts": cuts, "removed_seconds": saved,
        "retained_gap_seconds": args.keep_gap, "minimum_gap_seconds": args.minimum_gap, "threshold_db": -28,
        "speech_speed_changed": False, "edge_fade_seconds": 0.003
    }, indent=2))
    print(f"Shortened {len(cuts)} pauses; removed {saved:.2f}s; expected duration {duration-saved:.2f}s.")


if __name__ == "__main__":
    main()
