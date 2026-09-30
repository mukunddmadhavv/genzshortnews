"""Create faster speech, retimed image plan, and punchier locally synthesized SFX."""
import json
import math
import random
import subprocess
from pathlib import Path

from generate_dsp_sfx import RATE, save


def main():
    ep = Path("episodes/mau-6V_gg2zt3b8")
    folder = Path("library/sfx/dsp")
    speed = 1.16
    # Preserve the approved take's wording and pitch; increase pace and vocal density.
    subprocess.run([
        "ffmpeg", "-v", "error", "-n", "-i", str(ep / "narration-hinglish.mp3"),
        "-af", f"atempo={speed},highpass=f=75,equalizer=f=2600:t=q:w=0.8:g=1.5,acompressor=threshold=0.1:ratio=2.5:attack=8:release=90:makeup=1.4,loudnorm=I=-14:TP=-2:LRA=5",
        "-ar", "48000", "-c:a", "pcm_s16le", str(ep / "narration-punchy.wav"),
    ], check=True)
    data = json.loads((ep / "narration-hinglish.alignment.json").read_text())
    for key in ("alignment", "normalized_alignment"):
        if data.get(key):
            for field in ("character_start_times_seconds", "character_end_times_seconds"):
                data[key][field] = [t/speed for t in data[key][field]]
    (ep / "narration-punchy.alignment.json").write_text(json.dumps(data, ensure_ascii=False, indent=2))
    plan = json.loads((ep / "image-plan-hinglish.json").read_text())
    plan.update(alignment="narration-punchy.alignment.json", narration="narration-punchy.wav", output="news-panel-punchy.mp4", beats_output="image-beats-punchy.json")
    (ep / "image-plan-punchy.json").write_text(json.dumps(plan, ensure_ascii=False, indent=2))

    rng = random.Random(711)
    for name, duration, impact in [("sweep-whoosh.wav", 0.48, False), ("whoosh-impact.wav", 0.62, True)]:
        samples = []
        low = bass = phase = 0.0
        for i in range(round(duration*RATE)):
            t = i/RATE
            u = min(t/0.4, 1)
            cutoff = 700 + 6000*u*u
            low += (1-math.exp(-2*math.pi*cutoff/RATE))*(rng.uniform(-1,1)-low)
            bass += (1-math.exp(-2*math.pi*400/RATE))*(low-bass)
            envelope = math.sin(math.pi*min(t/0.48,1))**2
            sample = (low-bass)*envelope
            if impact and t >= 0.32:
                v = t-0.32
                phase += 2*math.pi*(75+110*math.exp(-25*v))/RATE
                sample += 0.7*math.sin(phase)*min(1,v/0.004)*math.exp(-18*v)
            sample *= min(1,t/0.008)*min(1,(duration-t)/0.025)
            samples.append(sample)
        save(folder/name, samples, -3)
    # Align impact onset / whoosh apex with scene change, rather than starting late.
    transitions = [(11.4, "sweep-whoosh.wav", -10), (26.453, "sweep-whoosh.wav", -9),
                   (39.68, "whoosh-impact.wav", -8), (59.947, "sweep-whoosh.wav", -11),
                   (65.13, "whoosh-impact.wav", -9), (80.0, "sweep-whoosh.wav", -11)]
    # First transition uses the actual Hinglish image beat, not the old English time.
    beats = json.loads((ep / "image-beats-hinglish.json").read_text())
    transitions[0] = (beats[2]["start"], "sweep-whoosh.wav", -10)
    cues = [{"file": f"../../library/sfx/dsp/{name}", "start_seconds": max(0,t/speed-(0.32 if "impact" in name else 0.24)), "gain_db": gain} for t,name,gain in transitions]
    (ep / "sfx-cues-punchy.json").write_text(json.dumps(cues, indent=2))
    (ep / "audio-revision.json").write_text(json.dumps({"speed_multiplier": speed, "source": "narration-hinglish.mp3", "processing": "pitch-preserving atempo, high-pass, presence EQ, compression", "target_lufs": -14, "dsp_seed": 711, "sfx": "filtered noise sweeps plus descending sine impact; peak -3 dBFS before cue gain", "alignment": "original times divided by 1.16; approximate DSP time mapping"}, indent=2))
    print("Prepared faster narration, retimed plan, and six DSP whoosh/impact cues.")


if __name__ == "__main__":
    main()
