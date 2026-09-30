"""Synthesize deterministic editorial SFX locally with oscillators and filtered noise."""
import array
import json
import math
import random
import sys
import wave
from pathlib import Path

RATE = 48000


def save(path, samples, peak_db):
    peak = max(abs(x) for x in samples)
    gain = 10 ** (peak_db / 20) / max(peak, 1e-12)
    pcm = array.array("h", (round(max(-1, min(1, x * gain)) * 32767) for x in samples))
    if sys.byteorder != "little":
        pcm.byteswap()
    with wave.open(str(path), "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(RATE)
        output.writeframes(pcm.tobytes())


def main():
    folder = Path("library/sfx/dsp")
    folder.mkdir(parents=True, exist_ok=True)
    rng = random.Random(320)
    click = []
    phase = 0
    duration = 0.16
    for i in range(round(duration * RATE)):
        t = i / RATE
        phase += 2 * math.pi * (900 - 520 * t / duration) / RATE
        envelope = min(1, t / 0.004) * math.exp(-42 * t) * min(1, (duration-t)/0.015)
        click.append(envelope * (math.sin(phase) + 0.08 * rng.uniform(-1, 1)))
    save(folder / "soft-click.wav", click, -9)

    whoosh = []
    low = 0
    high_low = 0
    duration = 0.38
    for i in range(round(duration * RATE)):
        t = i / RATE
        u = t / duration
        noise = rng.uniform(-1, 1)
        cutoff = 700 + 3000 * math.sin(math.pi * u) ** 2
        alpha = 1 - math.exp(-2 * math.pi * cutoff / RATE)
        low += alpha * (noise-low)
        high_low += (1 - math.exp(-2 * math.pi * 350 / RATE)) * (low-high_low)
        whoosh.append((low-high_low) * math.sin(math.pi*u) ** 2)
    save(folder / "soft-whoosh.wav", whoosh, -12)
    (folder / "generation.json").write_text(json.dumps({
        "method": "local DSP", "sample_rate": RATE, "seed": 320,
        "soft-click.wav": {"duration": 0.16, "peak_dbfs": -9, "method": "descending sine oscillator, noise transient, exponential decay, endpoint fades"},
        "soft-whoosh.wav": {"duration": 0.38, "peak_dbfs": -12, "method": "white noise, swept one-pole low-pass, high-pass subtraction, sine-squared envelope"},
    }, indent=2))
    print(f"Generated two DSP effects in {folder}")


if __name__ == "__main__":
    main()
