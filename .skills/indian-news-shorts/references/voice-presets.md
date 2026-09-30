# Mukund Tight — approved Eleven v4 recipe

## Selection contract

Approved 2026-09-28: the user loved the v4 take and requested it as the only
future narration voice. This supersedes all earlier Identity 2, Multilingual v2,
fast10 v2 and Original Narrator selections.

Source of truth: `library/voices/presets.json`.

| Label | Preset ID | Voice ID | Model | Recipe |
|---|---|---|---|---|
| Mukund Tight | `mukund-tight` | `F2bjsMJJPYo3S15YpV24` | `eleven_v4` | 3 |

Keep the same preset ID/UI name. Only this preset is selectable. Save its full
profile with each episode. Never silently fall back to another voice/model.
Reuse the existing clone; do not upload generated audio to create a new clone.

## Original recording and approved reference

- Original: `library/voices/mukund-hinglish/source.m4a`.
- 89.152 seconds, mono AAC, 48 kHz, Hinglish Apple Voice Memos recording.
- Decoded source PCM MD5: `7122b5c59797999e6a6be87630e68126`.
- Clone metadata: `library/voices/mukund-hinglish/voice.json`.
- Approved folder: `library/voices/mukund-hinglish/v4-audition/`.
  The folder retains its audition name so existing playback links keep working;
  its processed v4 take is now the production reference.
- Approved WAV: `mukund-tight-v4.wav`, **34.681333 seconds**.
- Convenient preview: `mukund-tight-v4.mp3`.
- Raw generation: `mukund-tight-v4-raw.mp3`, **44.88 seconds**.
- Script: `episodes/medha-samay-zrSyjkvUaWU/narration-hinglish.txt`.
- API request/source: `request.json`, `generation.json`.
- Measurements: `verification.json`; final WAV **−14.67 LUFS / −2.00 dBTP**.
- User approval is the identity/delivery review; the technical check was a full
  FFmpeg decode. New model generations are not guaranteed to be bit-identical.

## 1. Generate with v4

`POST /v1/text-to-dialogue?output_format=mp3_44100_128`

```json
{
  "inputs": [{"text": "SCRIPT INCLUDING BRAND ENDING", "voice_id": "F2bjsMJJPYo3S15YpV24"}],
  "model_id": "eleven_v4",
  "language_code": "hi",
  "settings": {"stability": 0.5, "similarity": 0.9}
}
```

Keep requests within 2,000 characters for reliable dialogue generation. No seed
was used. Write Hindi-led Hinglish in Devanagari, including names and loanwords.
No bracketed audio tags in the approved recipe. The only Latin-script spoken
text is the exact ending: **Follow GENZ SHORT NEWS for more!**

V4 dialogue does not use the v2 TTS speed/style/speaker-boost controls. The preset
stores neutral compatibility values (1.0 / 0 / false); they are omitted from the
API payload. Local tempo processing below provides the approved speed.

## 2. Base polish

```text
atempo=1.0,highpass=f=55,acompressor=threshold=0.125:ratio=1.8:attack=15:release=120:makeup=1,loudnorm=I=-16:TP=-2:LRA=7
```

Save mono 48 kHz 24-bit PCM WAV. No acceleration in this step. Conversion from
MP3 to WAV does not restore compression detail. No pitch shift or presence EQ.

## 3. First pause trim

Detect `silencedetect=noise=-28dB:d=0.3`. Preserve 80 ms at each end of a quiet
gap, retaining 160 ms total; remove its middle. Apply 3 ms segment-edge fades.
Use `scripts/tighten_narration_pauses.py --minimum-gap 0.3 --keep-gap 0.16`.
The approved take shortened 12 gaps, removing approximately 3.11 seconds.

## 4. Energetic polish

```text
atempo=1.07,acompressor=threshold=0.125:ratio=2.2:attack=12:release=100:makeup=1.25,loudnorm=I=-14:TP=-2:LRA=5
```

## 5. Second pause trim, then final tempo

Trim gaps ≥0.12 seconds at −28 dB to 0.06 seconds, preserving 30 ms on each end
with 3 ms fades. The approved take shortened 11 gaps, removing about 0.88 seconds.
Then apply exactly `atempo=1.1,anull`, saving mono 48 kHz 24-bit WAV.

Total local tempo factor: **1.07 × 1.10 = 1.177**. Keep this exact order, once per
raw take. Do not add the old 1.05 TTS speed or an extra 1.218 tempo multiplier.
Detect gaps afresh for new audio; never reuse reference cut positions. Check
quiet words/breaths, since threshold detection alone cannot prove silence.

## Timestamp workflow — local Whisper large-v3

The selected default is **Whisper large-v3**, model
`mlx-community/whisper-large-v3-mlx`, running locally on Apple Silicon through
`scripts/transcribe_reference.py`. Explicitly pass this model: the helper's
historical default is small. Do not substitute large-v3-turbo for this workflow.
The helper already uses `language="hi"` and `word_timestamps=True`.
Always execute ASR with an extended command timeout (`timeout: 600000` / 10 minutes)
to avoid premature process termination during model loading or Metal kernel compilation.
If large-v3 stalls or network/Metal compilation times out, `scripts/transcribe_reference.py`
falls back to `mlx-community/whisper-small-mlx` (cached locally, completes in 3-5 seconds)
to prevent pipeline blocking, and uses `os._exit(0)` to prevent the macOS multiprocessing shutdown hang.


1. Generate v4 narration and finish every Mukund Tight audio-processing stage.
2. Transcribe the **final processed WAV**, not the raw take. Save the original
   result as `narration-final.transcript.large-v3.json`.
3. Read `segments[].words[]`: each word supplies `word`, `start` and `end` in
   seconds relative to that final audio. Retain segment context and probabilities
   when available. This JSON is not our character-based `.alignment.json` schema.
4. Compare the transcript with the script. Check Hinglish names, fast phrases,
   silence hallucinations, omissions and the complete English brand ending.
   Spot-check phrase/word boundaries by listening; record corrections separately.
5. Derive image beats and SFX cues from these checked word/phrase times. Existing
   code expecting character arrays needs an explicit adapter; never relabel raw
   Whisper JSON or invent equally spaced character timestamps.

Whisper transcribes what it detects and estimates word boundaries; it does not
force-align our original script. It is the default timing source for image cuts
and SFX after review, not a claim of frame-accurate phonetic alignment. If final
audio is edited, regenerate its timestamps. Reuse transcripts only for unchanged
audio; keep the source audio path/model with timing records.

No ElevenLabs alignment permission is needed. Current implementation detail:
the TTS helper still attempts `/v1/forced-alignment` after saving speech. The
account rejected that endpoint with HTTP 401; `missing_permissions` produces
explicit null/status alignment and lets audio processing continue. The Whisper
command is a separate required step, not yet automatic in the preset wrapper.
Never regenerate paid speech just to obtain timestamps. The approved audition's
null sidecars are retained as provenance and are not timing evidence.

## Commands

```sh
uv run --with httpx --with python-dotenv scripts/narrate_with_preset.py --list
uv run --with httpx --with python-dotenv scripts/narrate_with_preset.py --preset mukund-tight --set-default
uv run --with httpx --with python-dotenv scripts/narrate_with_preset.py --preset mukund-tight --text episodes/STORY/narration-hinglish.txt --out episodes/STORY/narration-final.wav
uv run --with mlx-whisper scripts/transcribe_reference.py episodes/STORY/narration-final.wav --out episodes/STORY/narration-final.transcript.large-v3.json --model mlx-community/whisper-large-v3-mlx
uv run --with httpx --with python-dotenv scripts/narrate_with_preset.py --preset mukund-tight --raw-audio episodes/STORY/narration-final-raw.mp3 --out episodes/STORY/narration-recovered.wav
```

The `--raw-audio` example is for recovering/reusing an existing take; after it,
run Whisper on `narration-recovered.wav` instead of `narration-final.wav`.

`--dry-run` inspects the pipeline without API requests. The low-level TTS helper
does not apply local processing; use the preset wrapper for episode narration.
Keep voice dominant when mixing SFX; measure the encoded mix around −14 LUFS
with true peak ≤−1.5 dBTP. Narration loudnorm targets are not guaranteed measurements.
