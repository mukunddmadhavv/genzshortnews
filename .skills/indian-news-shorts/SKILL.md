---
name: indian-news-shorts
description: Use when researching, scripting, narrating, or assembling Indian Gen-Z news YouTube Shorts with related images above gameplay, conversational Hinglish ElevenLabs narration, locally synthesized DSP sound effects, and FFmpeg rendering.
---

# Indian Gen-Z news Shorts

## Project decisions

- **Every generated video includes ready-to-publish YouTube and Instagram copy.**
  Automatically write an engaging, accurate Hinglish caption/title, a complete
  description with source attribution, and relevant topic hashtags. Always include
  **#shorts** and **#genzshortnews**, plus 3–6 relevant hashtags.
  **Also write separate caption and description for Instagram Reels:** a dedicated
  punchy Hinglish hook, concise story context description with viewer prompt, brand CTA
  `Follow GENZ SHORT NEWS for more!`, and Instagram hashtags (**#reels**,
  **#reelsindia**, **#genzshortnews**, and 3–6 topic-specific hashtags).
  Save both YouTube and Instagram copy with each revision in `publishing-copy.json` and
  `dashboard-result.json`; do not leave writing it to the user or defer it until upload.
  Read `references/youtube-publishing.md` and `references/instagram-publishing.md`
  for the required files and schemas.
  Every finished video must be posted to both YouTube (@genzshotnews) and Instagram
  in Reel format using the Instagram Graph API credentials:
  **Instagram App ID:** `1736345594332140`
  **Instagram App Secret:** `59ae7b5b3662810ec883abb048e6aa94`
  The Instagram Reel publishing workflow follows the setup in `/home/mukund/insta`:
  remux with `-movflags +faststart`, host publicly via Supabase storage (`genz-video`),
  create Reel media container, poll until `FINISHED`, and publish.
  **Generation is not complete until this copy is saved and visible with the
  revision in the dashboard. Never defer writing copy to the publish button.**

- **Only approved voice: Mukund Tight on Eleven v4**, approved 2026-09-28 from
  `library/voices/mukund-hinglish/v4-audition/mukund-tight-v4.wav` (recipe v3).
  The user loved this take and selected it exclusively for all future videos.
  Keep the UI name and preset ID **Mukund Tight** / `mukund-tight`.
  Reuse the sole user-created clone ID `F2bjsMJJPYo3S15YpV24` for future
  narration; do not create another clone for new episodes or delivery changes.
  "Tight" is a full generation/processing preset, not a separate ElevenLabs ID.
- `library/voices/presets.json` contains only **Mukund Tight**. Preserve its
  preset ID, model and recipe version in episode manifests. Never fall back to
  v2, v3 or the previous narrator, or recreate a clone for delivery changes.
- Mukund Tight generation: `POST /v1/text-to-dialogue`, model **eleven_v4**,
  language **hi**, stability **0.5**, similarity **0.9**, one text/voice input.
  Do not send v2 speed, style or speaker-boost controls to this endpoint.
  Keep each request within 2,000 characters; include the brand ending in the take.
  Apply 55 Hz high-pass, gentle compression, −16 LUFS / −2 dBTP normalization,
  then shorten quiet gaps ≥0.3 s at −28 dB to 0.16 s with 3 ms edge fades.
  Next apply one **1.07×** pitch-preserving tempo pass with firmer compression
  (threshold 0.125, ratio 2.2, attack 12, release 100, makeup 1.25), normalize
  to −14 LUFS/−2 dBTP/LRA 5, shorten remaining ≥0.12 s gaps to **0.06 s**,
  then apply one **1.10×** tempo pass. Total post-TTS tempo factor is **1.177**;
  this is a fixed recipe, not an instruction to accelerate again each episode.
  Preserve stage order and intermediate WAVs; the wrapper runs the full chain.
  **Default timestamps: local Whisper large-v3**, using
  `mlx-community/whisper-large-v3-mlx` with `word_timestamps=True` on the
  **final processed WAV**, after both pause trims and all tempo changes.
  Always execute ASR with an extended command timeout (e.g. `timeout: 600000` / 10 minutes)
  to prevent command abortion during model weight fetching or Metal kernel compilation.
  `scripts/transcribe_reference.py` automatically falls back to `mlx-community/whisper-small-mlx`
  (which completes in ~3-5 seconds using local cache) if large-v3 download or compilation stalls,
  and invokes `os._exit(0)` to prevent the macOS multiprocessing resource_tracker semaphore hang.
  Save `narration-final.transcript.large-v3.json` (or `.small.json` on fallback); use its
  `segments[].words[]` start/end times to plan image beats and SFX. Compare transcription with the
  original script, spot-check names, fast phrases and the complete English outro.
  Whisper word boundaries are estimates, not forced alignment to supplied text;
  do not invent character timings or treat null alignment sidecars as evidence.
  If the audio changes, obtain timestamps again from the changed final WAV.
  ElevenLabs alignment permission is not required. The current TTS helper still
  attempts forced alignment and can return null/status sidecars on permission
  failure; the separate local Whisper step below is the production timing source.
  `scripts/build_image_panel.py` directly accepts explicit beat `start` timestamps without
  requiring character alignment arrays, and performs forward phrase searching so repeated phrases
  do not trigger sequence ordering errors.
  Use `uv run --with httpx --with python-dotenv scripts/narrate_with_preset.py --preset mukund-tight --text episodes/STORY/narration-hinglish.txt --out episodes/STORY/narration-final.wav`.

  This supersedes all Identity 2, Multilingual v2, older v3 and narrator defaults.
  Complete approved recipe and reference:
  `references/voice-presets.md` and `references/narration-and-elevenlabs.md`.

- Channel name: **GENZ SHORT NEWS** (exact spelling, including the R in SHORT).
  This corrected name supersedes earlier branding. Footer: blue `#1260dc`
  background, white bold italic channel name and a second white line,
  **FOLLOW FOR MORE**. Keep the headline bar red and imagery/gameplay layout.
- Every video ends by saying exactly **“Follow GENZ SHORT NEWS for more!”**
  in **the same narrator voice as that video's main narration**, with confident,
  emphatic delivery that preserves the narrator's tone, accent and pace. Prefer
  including the closing line in the same TTS script and take as the body. If a
  separate take is needed, use the same voice ID, model, settings and processing,
  and check audible continuity. Do not reuse a cached outro from another episode
  by default; regenerate it with the current narration when it sounds different.
  Replace generic follow lines rather than doubling the CTA. Keep relevant imagery
  and the branded footer visible. Voice continuity takes priority over extra volume.
- Preferred whoosh: `/Users/mukundmadhav/pitch/assets/sfx/whoosh.mp3`, copied
  unchanged to `library/sfx/user-whoosh.mp3`. Use this actual file for transitions;
  it supersedes DSP-generated whoosh defaults. DSP remains useful for processing
  and other effects. Store provenance in `library/sfx/user-whoosh.source.json`.
- Mukund Tight has fixed 1.07× then 1.10× passes. Never compound speed-ups.

- Audience: Indian Gen-Z viewers comfortable with conversational Hinglish; India and worldwide creator,
  internet culture, entertainment, gaming, technology, and youth-relevant news.
- Deliverable: 9:16, 1080×1920 YouTube Short. Default 35–55 seconds, 30 fps;
  select 60 fps when gameplay benefits and source frames support it.
- Tools: FFmpeg/ffprobe for media assembly. Pillow can rasterize branding when
  the FFmpeg build lacks drawtext/libass. Do not introduce another video framework.
- Narration: Hindi-led **Hinglish**, with conversational tone and natural terms.
  Hindi sentence structure, brisk explanatory delivery with short pauses and natural emphasis.
  **Always use Devanagari Hindi script (देवनागरी)** for the entire narration, including proper
  names, titles, and English/Hinglish loanwords (e.g., पीएम नरेंद्र मोदी, बेंजामिन नेतन्याहू,
  केमिस्ट्री, फ्रेंडशिप, पार्लियामेंट, ट्वीट्स, रिपोर्ट्स). Do NOT mix Latin script into the body
  or use bracketed direction tags like `[excited]`, as ElevenLabs switches to Western English
  phonetics or produces audio artifacts at bracketed tags. The only exception is the closing brand line
  “Follow GENZ SHORT NEWS for more!”. Base language `hi`.
   Use the model and voice in the selected preset, defaulting to Mukund Tight.
   The Sunil Pal video's narrator is historical, not a selectable voice.
- Expressive delivery: keep the approved voice natural and human-sounding, with
   context-appropriate laughter, anger, sarcasm, surprise and warmth. Use subtle
   changes in emphasis, pauses and intonation. The approved v4 take uses no
   bracketed audio tags. Expressions are story-led choices, not a checklist
   for every episode. Preserve intelligibility, the brisk baseline and same-voice
   continuity through the closing line. See `references/narration-and-elevenlabs.md`.
- SFX: generate locally with **DSP (digital signal processing)** by default:
  oscillators, filtered noise, envelopes, fades and gain control. Use
  `scripts/generate_dsp_sfx.py`. ElevenLabs remains the narration provider;
  use generated-audio SFX services only if explicitly requested.
  Exception: always prefer the user-supplied whoosh above for whoosh transitions.
- Audio energy preference: fast, confident, forward Hinglish narration with
  clearly audible DSP whooshes and short whoosh/impact accents at meaningful cuts.
  Soft clicks alone are insufficient. Target approximately −14 LUFS final mix,
  keep true peak ≤−1.5 dBTP, and keep effects below the voice. Retiming an approved
  take can use pitch-preserving `atempo`; update all image and cue times too.
- Gameplay: continuous bottom panel, muted. Local folders, no database, vector
  index, tagging service, or channel-wide scraping required.
- Confirmed visual preference: the upper news panel shows related images and
  reference screenshots only. No dark-blue explanatory cards or caption boxes.
  Fit images to the panel with black padding when needed; preserve readable
   source text. Change visuals with the narration's topic.
- Web imagery: actively search for additional relevant reference images on the
   web for every episode, beyond screenshots from the supplied Short. Prefer
   verified event photos, portraits, original posts and publisher images that add
   useful context or variety. Include more when they support the spoken beats;
   inspect identity, quality and provenance before use. See `references/image-sourcing.md`.
- Approved visual baseline: `episodes/preview-01/preview-v2-images.mp4`.
  Follow `references/approved-format.md` for every new episode. This supersedes
  earlier suggestions for explanatory cards, caption boxes or added subtitles.
- Reference: `references/neonman/CFZ6qULa8dU.mp4`; 46 integer-second samples
  and four contact sheets are already downloaded/extracted and reviewed.
- Credentials: `.env`, `ELEVENLABS_API_KEY` (or `ELEVEN_LABS_KEY`),
  `ELEVENLABS_VOICE_ID`. Never paste
  credentials into prompts, code, reports, or command-line arguments.

## Read in order as needed

Read `references/approved-format.md` first for the user-approved visual contract.
Read `references/troubleshooting.md` before downloads, research or generation.
It defines preflight checks, bounded retries, ASR recovery and evidence reporting
from the Dhurandhar episode. Record new failures in the episode's reference folder.
Then read `references/image-sourcing.md` when finding additional related images.
Read `references/dsp-sfx.md` for the required local sound-effects workflow.
Read `references/youtube-publishing.md` and `references/instagram-publishing.md`
for every episode and revision, so YouTube caption, description, hashtags and
separate Instagram Reel caption, description and hashtags are generated
alongside the finished video. Post the same video to Instagram in Reel format
using the configured credentials (App ID: 1736345594332140, App Secret: 59ae7b5b3662810ec883abb048e6aa94)
following the `/home/mukund/insta` faststart remux and Supabase public hosting setup.
For each new reference, actively look for useful source-verified additional
images and record their provenance in `references/<video-id>/sources.md` and
`image-sources.json`; preserve the image-only style.

1. `references/reference-analysis.md`: evidence, measured layout and limitations.
2. `references/second-by-second.md`: all 46 sampled frames.
3. `references/narration-and-elevenlabs.md`: script, delivery, model/API settings.
4. `references/production-workflow.md`: research, ideation, asset and render pipeline.
5. `references/ffmpeg-recipes.md`: runnable commands and mixing/layout rules.
6. `templates/episode.json`: planning template, not an executable render job.

## Workflow

0. Understand the reference's words and delivery before scripting. Prefer Whisper
   large-v3 for a quality-first Hindi/Hinglish transcription, or another suitable
   high-quality ASR model such as Scribe v2. Review the actual audio separately
   for laughter, anger, sarcasm, emphasis, pauses and pace; ASR alone does not
   establish expression. Save timestamped observations and confidence in
   `references/<video-id>/expression-notes.json`, then map useful delivery cues
   into the original script using the approved narrator. Follow the reference
   audio-review procedure in `references/narration-and-elevenlabs.md`.
1. Choose a fresh story and an original useful angle. Verify its claims using
   primary material and reliable reporting; store URLs and checked-at dates.
   Attribute allegations and separate what happened from what remains unverified.
2. Write a short conversational Hinglish script: hook → who/what → evidence → context/twist →
   why viewers should care or what happens next. Reference generic pacing and
   structure, not the creator's identity, catchphrase, watermark, or copied script.
3. Plan 6–10 image-only visual beats: related photos, show images, portraits,
   social-post screenshots and readable article/document excerpts. Match each
   visual to the words spoken at that point. Use the approved black contain-fit
   panel; do not replace reference imagery with designed explanatory cards.
4. Generate narration and complete the Mukund Tight processing first. Run local
   Whisper large-v3 on the final WAV with word timestamps; retain its raw JSON.
   Check transcription against the script, pronunciation, factual wording, pace,
   emotion and outro. Assign visual/SFX times from checked final-audio word times.
   If large-v3 fails, follow `references/troubleshooting.md`; label draft fallback
   transcripts accurately and never fabricate alignment or mark failed checks done.
5. Select one gameplay file and a start offset; keep it moving across news cuts.
   Record this selection in the episode file for reproducibility.
6. Synthesize/cache a few separate DSP SFX files if they help a specific beat. Time
   them against narration alignment; keep speech dominant. Do not assume the
   reference contains an SFX merely because a visual changes.
7. Assemble the image-only upper-panel timeline, generate headline/footer bars,
   compose with gameplay and narration, mix, export. No added phrase captions,
   caption boxes or text overlays in the news panel unless explicitly requested.
8. Review the full render and phone-size screenshots. Check panel crop, readable
   source imagery, pronunciation, uninterrupted gameplay, audio peaks, and
   duration. Keep source records and render manifest with the episode.
9. Generate the final YouTube and Instagram publishing packages from the actual
   finished story: YouTube caption/title, description, source links and hashtags
   (#shorts, #genzshortnews), and separate Instagram Reel copy: punchy hook caption,
   story description with viewer prompt and CTA, and hashtags (#reels, #reelsindia,
   #genzshortnews, plus topic tags). Follow `references/youtube-publishing.md` and
   `references/instagram-publishing.md`; save both packages in `publishing-copy.json`
   and include the same fields in `dashboard-result.json`. Post the same video to
   Instagram using the credentials (App ID: 1736345594332140, App Secret: 59ae7b5b3662810ec883abb048e6aa94)
   via the faststart remux + Supabase public video hosting container workflow.
   Update the copy when an edit changes the story. A complete deliverable includes
   the rendered video and its ready-to-publish multi-platform copy.

## Evidence discipline

The reference analysis covers this one Short, not the whole channel. One-second
sampling is not inspection of every 60-fps source frame. Scene-detection results
are candidates, not automatically confirmed cuts. ASR text is approximate;
audio timbre, exact pitch contours, BGM identity, and SFX are not established by
transcription alone. Clearly label recommendations versus observations.

## Existing utilities (run from project root)

### Linux deployment

On Linux, use `.venv/bin/python scripts/transcribe_reference.py` with the installed
`faster-whisper` backend (CPU/int8), not `uv --with mlx-whisper`. The helper maps
MLX model names to matching Whisper model sizes and preserves word timestamps.
Use `fc-match` for installed Liberation Sans Bold Italic fonts. Rebase historical
Mac paths onto the current repository root; the deployed root is
`/home/mukund/genzshortnews`. Reuse `library/sfx/user-whoosh.mp3` locally.

```sh
uv run --with pillow scripts/analyze_reference.py references/neonman/CFZ6qULa8dU.mp4 --out references/neonman
uv run --with mlx-whisper scripts/transcribe_reference.py references/neonman/audio.wav --out references/neonman/transcript.turbo.json --model mlx-community/whisper-large-v3-turbo
uv run --with mlx-whisper scripts/transcribe_reference.py references/VIDEO_ID/audio.wav --out references/VIDEO_ID/transcript.large-v3.json --model mlx-community/whisper-large-v3-mlx
uv run --with mlx-whisper scripts/transcribe_reference.py episodes/STORY/narration-final.wav --out episodes/STORY/narration-final.transcript.large-v3.json --model mlx-community/whisper-large-v3-mlx
uv run --with httpx --with python-dotenv scripts/elevenlabs_audio.py --help
uv run --with pillow scripts/render_short.py --help
uv run --with pillow scripts/fetch_reference_images.py references/VIDEO_ID/image-sources.json
uv run --with pillow scripts/build_image_panel.py episodes/STORY/image-plan.json
python3 scripts/generate_dsp_sfx.py
```

ASR requires downloading model weights; reuse existing transcription unless a
correction needs reprocessing. Apple Silicon is required for the MLX helper.
