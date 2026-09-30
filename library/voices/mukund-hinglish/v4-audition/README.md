# Mukund Tight — approved Eleven v4 reference

Approved 2026-09-28 as the sole voice for future videos. The existing folder name
is retained for stable playback links. Preset `mukund-tight` now uses v4, recipe 3.

Generated with `eleven_v4` through `/v1/text-to-dialogue`, using the existing
Mukund clone and the same Hinglish script as the approved v2 episode.

- [Processed v4 MP3](mukund-tight-v4.mp3) — 34.68 seconds.
- [Processed v4 WAV](mukund-tight-v4.wav) — production master.
- [Raw v4 MP3](mukund-tight-v4-raw.mp3) — 44.88 seconds.

## Settings

V4 dialogue generation: Hindi language, stability 0.5, similarity 0.9.
The v2 TTS speed (1.05), style and speaker-boost parameters were not sent to the
dialogue endpoint. This is an adapted audition, not identical model settings.

Applied the Mukund Tight preset's existing local processing in the same order:
base filtering/compression, first pause shortening, energetic polish (1.07×),
second pause shortening, and final 1.1× pitch-preserving tempo adjustment.
Total local tempo factor is 1.177×; approximately 4 seconds of quiet gaps were removed
across the two pause-shortening stages.

## Verification

The WAV passed a full FFmpeg decode. Measured final WAV loudness is −14.67 LUFS,
with a −2.00 dBTP true peak. See `verification.json` for measurements.
The user listened, loved this take and selected it as the exclusive production voice.

This endpoint returned audio without character timestamps. Alignment sidecars
explicitly contain null alignments. The selected timestamp workflow is now local
Whisper large-v3 (`mlx-community/whisper-large-v3-mlx`) on the final processed WAV,
with word timestamps reviewed against the original script before timing images/SFX.
Whisper estimates word boundaries; it does not force-align the supplied script.
This documentation update does not mean a transcript for this reference has been
generated yet. See the skill's `voice-presets.md` for the command and JSON format.
An attempt to obtain forced alignment on 2026-09-28 returned HTTP 401; the approved
audio was preserved unchanged.

The production preset wrapper reproduced the approved raw-to-final processing
exactly. Both final WAVs decoded to signed 16-bit PCM with MD5
`e2803aea234c0435e09b0b464f7ac505`.

`request.json` and `generation.json` preserve the model request and source script.
The production default is this v4 take's recipe. See
`../../presets.json` and the project's `references/voice-presets.md`
skill reference for the complete generation/processing contract.
