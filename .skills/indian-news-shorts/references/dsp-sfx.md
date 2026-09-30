# DSP sound effects — default audio workflow

## User-selected whoosh takes priority

Use `/Users/mukundmadhav/pitch/assets/sfx/whoosh.mp3`, stored byte-for-byte at
`library/sfx/user-whoosh.mp3`. This 0.650-second stereo MP3 is the required whoosh
source for new episodes, replacing generated whooshes. `user-whoosh.source.json`
records origin and SHA-256. Do not synthesize a substitute when this file exists.
Start cue gain around −11 dB and position its sweep around relevant image cuts.
Keep the branded closing words unobscured. DSP still handles EQ, gain, fades,
mixing and any additional locally generated effects.

## Updated energy preference

The user requests more engaging whooshes and a faster, confident, louder voice.
Use audible but controlled sweeps and occasional short impacts at key transitions,
not only soft clicks. Start with 4–6 purposeful cues in a 75-second video.
Latest example: `scripts/prepare_punchy_revision.py` generates a 0.48-second
filtered-noise sweep and a 0.62-second whoosh with a descending sine impact.
Peak-normalize source effects to −3 dBFS, then apply cue gain around −8…−11 dB.
Align the whoosh apex or impact onset to the visual change. These values are
starting points; judge speech masking and harshness in the final mix.

Final target is now approximately **−14 LUFS**, true peak ≤−1.5 dBTP; this
supersedes the earlier −16 LUFS default below. Use gentle compression and presence
EQ for a forward voice. Faster pacing and compression cannot alone guarantee a
confident performance; choose an assertive conversational take when generating.

The user explicitly requests DSP (digital signal processing) to generate SFX.
Future agents should synthesize effects locally and keep them as reusable WAVs.
Narration still uses ElevenLabs. Do not call an SFX-generation API by default.

## Run

```sh
python3 scripts/generate_dsp_sfx.py
```

Outputs in `library/sfx/dsp/`:
- `soft-click.wav`: descending sine oscillator plus a little seeded noise,
  exponential decay, short attack and fade; 0.16 s, peak −9 dBFS.
- `soft-whoosh.wav`: seeded white noise, swept low-pass and high-pass subtraction,
  sine-squared envelope; 0.38 s, peak −12 dBFS.
- `generation.json`: repeatable parameters and provenance.

48 kHz, 16-bit mono WAV; fixed RNG seed. Endpoint envelopes prevent hard clicks.
Scale each effect peak before PCM encoding; do not hard-clip a loud waveform.
Inspect waveform/peaks and audition a new effect when listening is available.

## Placement

Choose 2–4 meaningful transitions: new source, response, important qualification.
Use quiet clicks for source changes and a restrained whoosh for a major section.
Derive times from the final Hinglish alignment; regenerate cue timestamps whenever
the narration changes. Keep gameplay silent and speech dominant. The existing
FFmpeg compositor accepts these WAV files through `--sfx-cues`.

Start cue gains around −12 to −18 dB relative to these already peak-normalized
files, then measure the complete encoded mix. Target around −16 LUFS integrated,
true peak ≤−1.5 dBTP. Effects are editorial punctuation, not evidence audio.
