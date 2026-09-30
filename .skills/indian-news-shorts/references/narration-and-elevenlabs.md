# Hinglish narration and ElevenLabs

## Only approved voice — Mukund Tight on Eleven v4

The user approved `library/voices/mukund-hinglish/v4-audition/mukund-tight-v4.wav`
on 2026-09-28 and requested this cloned voice exclusively for future videos.
Use preset `mukund-tight`, recipe 3, model `eleven_v4`, existing clone
`F2bjsMJJPYo3S15YpV24`. Do not select the previous narrator, Multilingual v2,
Identity 2 or v3. Do not create another clone for new episodes.

**Full exact recipe and reference evidence: [voice-presets.md](voice-presets.md).**
Registry: `library/voices/presets.json`. Wrapper: `scripts/narrate_with_preset.py`.

Generate via `/v1/text-to-dialogue`: language `hi`, stability 0.5, similarity 0.9,
one text/voice pair, output `mp3_44100_128`. Do not send TTS speed/style/speaker
boost. Keep each request within 2,000 characters. Apply the fixed local sequence:
base high-pass/compression/normalization → pause trim → 1.07× energetic polish →
second pause trim → 1.10× tempo. The approved reference is 34.681333 seconds,
measured −14.67 LUFS / −2.00 dBTP. No extra speed increase each episode.

## Script and expressive delivery

- Hindi-led conversational Hinglish with Hindi sentence structure, short clauses,
  clear attribution and decisive endings. Use natural loanwords rather than pure
  Hindi or all-English narration.
- Entire body in **Devanagari**, including names/titles/English loanwords:
  पीएम नरेंद्र मोदी, पार्लियामेंट, ट्वीट्स, रिपोर्ट्स. The only Latin-script
  spoken line is the exact closing brand line below.
- The approved v4 script uses no bracketed audio tags. Prefer wording, punctuation,
  emphasis and natural intonation. Do not insert direction prose into the script.
- Context-appropriate surprise, warmth, brief laughter or controlled sarcasm are
  welcome; do not force emotions into every story or sensationalize allegations.
- Keep clear names, factual qualifications and natural breaths even at brisk pace.
- A listening review checks identity and expression; ASR alone cannot do that.

## Required same-voice ending

End every episode exactly **“Follow GENZ SHORT NEWS for more!”** in the same voice
as the body. Include it in the same generation, with confident emphasis and
natural tone/accent/pace. Do not double it with another generic follow request.

If a separate ending is necessary, use the same v4 model, voice, settings and
processing, and listen across the join. A matching voice ID alone does not
guarantee audible continuity. Do not append cached outros from older episodes.
Keep related imagery and the branded footer visible to the end.

## Timestamp and API workflow

Credentials live in `.env` and must never be logged. The v4 audition successfully
used this account; listing models returned `missing_permissions` for `models_read`.
That listing failure does not mean speech generation is unavailable.

```sh
uv run --with httpx --with python-dotenv scripts/narrate_with_preset.py --preset mukund-tight --text episodes/STORY/narration-hinglish.txt --out episodes/STORY/narration-final.wav
```

**Use local Whisper large-v3 for production timestamps.** Complete v4 generation
and all Mukund Tight processing, then transcribe the final WAV with the full
`mlx-community/whisper-large-v3-mlx` model. Do not use the raw audio or substitute
small/turbo as an unreviewed production substitute. The existing helper enables
Hindi and word timestamps. For timeouts, use the bounded recovery procedure in
`troubleshooting.md`: an explicit long timeout, diagnosis before retry, and a
clearly labeled draft fallback followed by quality ASR or manual listening review.

```sh
uv run --with mlx-whisper scripts/transcribe_reference.py episodes/STORY/narration-final.wav --out episodes/STORY/narration-final.transcript.large-v3.json --model mlx-community/whisper-large-v3-mlx
```

Use `segments[].words[]` (`word`, `start`, `end`) as timing evidence for image
beats/SFX. Preserve the raw JSON and compare transcription against the script.
Listen around Hinglish names, fast speech, long gaps and the English brand ending;
record corrections without overwriting the raw evidence. If word timings are
missing, review/reprocess rather than invent equal durations.

Whisper estimates boundaries for its transcription; this is **not forced
alignment to the supplied script**. It can misrecognize words or drift at word
boundaries. Reviewed phrase timings are suitable for our image-only cuts and SFX.
Do not use ASR as proof of voice identity/emotion. Regenerate timing after any
further change to the final audio; reuse it only when the audio is unchanged.

Whisper output differs from the existing character-based `.alignment.json`
format. Consume its word records explicitly when authoring cues; code requiring
character arrays needs an adapter, not a renamed JSON or fabricated character times.
In particular, the current image-panel builder loads character alignment even
with explicit beat starts. Adapt that consumer for word-only/explicit-start plans;
never distribute segment duration evenly across characters to make it run.

ElevenLabs alignment access is optional. The current TTS helper still attempts
forced alignment after saving audio; on `missing_permissions` it writes null/status
sidecars and continues audio-only processing. Local Whisper is a separate step
after the wrapper, not yet automatically invoked. Null sidecars, including those
beside the approved audition, are not usable timing evidence. Do not regenerate
speech just to get timestamps.

## Reference transcription and expression review

Before scripting from a new reference, perform two distinct passes:

1. **Words/timing:** prefer Whisper large-v3 or Scribe v2. Check names,
   code-switching, quotations and difficult passages against audio and source
   context. Save raw output and corrections. Reuse good transcripts.
2. **Audible expression:** listen or use an available audio-capable analysis model.
   Note laughter, breaths, emphasis, pauses, pace and intonation; interpret anger
   or sarcasm in context with uncertainty. Whisper is not an emotion/prosody
   detector. Text sentiment and loudness do not establish expression.

Use original-quality audio for expression review; mono 16 kHz is enough for ASR.
Separate narration from quoted speakers and editorial SFX. Save timestamped
observations, methods and confidence in `references/<video-id>/expression-notes.json`.
Mark expression unverified when no listening review was possible. Translate useful
delivery patterns into an original performance with the approved Mukund v4 voice.

```sh
uv run --with mlx-whisper scripts/transcribe_reference.py references/VIDEO_ID/audio.wav --out references/VIDEO_ID/transcript.large-v3.json --model mlx-community/whisper-large-v3-mlx
uv run --with httpx --with python-dotenv scripts/elevenlabs_audio.py transcribe --audio episodes/STORY/narration-final.wav --language hin --out episodes/STORY/narration-check.json
```

The existing Neonman transcript is in `references/neonman/transcript.turbo.json`.
Its broad progression is hook → source → quote → context → uncertainty. Its
long final segment does not establish a single breath, edit map or vocal identity.
Refer to `reference-analysis.md` and `second-by-second.md` for the evidence.

## SFX and final mix

Use local DSP by default and the supplied `library/sfx/user-whoosh.mp3` for whoosh
transitions. See `dsp-sfx.md`. Effects support meaningful cuts and stay below
speech. Never imply generated SFX are authentic event audio. Measure encoded
mix loudness and true peak; default target roughly −14 LUFS, ≤−1.5 dBTP.

## Official references

- https://elevenlabs.io/docs/overview/models
- https://elevenlabs.io/docs/api-reference/text-to-dialogue/convert
- https://elevenlabs.io/docs/api-reference/forced-alignment/create
- https://elevenlabs.io/docs/api-reference/speech-to-text/convert
