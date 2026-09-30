# Production workflow and ideation

Start with `troubleshooting.md` for dependency/download preflight, bounded web
search, ASR timeout recovery, alignment schema handling and truthful completion.

**Current audio default:** Hindi-led conversational Hinglish narration with
natural English terms, plus locally synthesized DSP sound effects. Earlier
English-only or ElevenLabs-SFX suggestions below are superseded. Read
`narration-and-elevenlabs.md` and `dsp-sfx.md` before audio generation.

**Current timestamp default:** local Whisper large-v3 on the **final processed
Mukund Tight v4 WAV**, after pause shortening and tempo changes. Save word-timed
JSON and compare it to the script before placing images/SFX. No ElevenLabs
alignment permission is required. See the command and review procedure below.

**Approved visual contract:** read `approved-format.md` first. Use the image-only
format from `preview-v2-images.mp4`. Any earlier references below to cards,
comparisons, captions or CTA graphics are superseded: communicate those ideas
through narration and related reference images/screenshots instead.

## 1. Find a topic worth explaining

Use the channel for format inspiration and possible leads, then research the
underlying event. Gather primary statements/posts, actual release notes, official
announcements or original reporting. Record publication and checked-at dates.
Do not treat a screenshot inside a YouTube Short as independent corroboration.

Good topic families: Indian creator developments, gaming changes, viral internet
debates, entertainment, consumer tech and AI, global events with a clear youth
or India connection. Develop one angle per Short:

- **What changed?** One before/after fact.
- **Why India cares:** Price, access, platform reach, creator income or audience impact.
- **Claim vs evidence:** A reported allegation, the response, and what is unknown.
- **One missing detail:** Context absent from viral reposts.
- **What happens next?** A stated deadline or next step, attributed to a source.

New ideation means original explanation and useful context, not invented facts.

## 2. Episode package

Every episode must include ready-to-post caption/title, description and hashtags.
Read `youtube-publishing.md` during generation, not only when uploading. Always
include #shorts and #genzshortnews plus 3–6 relevant topic tags; write the copy
from the final script and verified sources and update it for story-changing edits.
Persist this copy before marking generation complete. Show caption/title, full
description and hashtags openly in the dashboard; publication only consumes the
saved copy and must not generate it on click.

Create `episodes/<date>-<slug>/` with:

```text
episode.json          # source claims, chosen gameplay, planned beats
sources.md            # URLs, dates, supporting excerpts
narration-hinglish.txt # Devanagari Hinglish plus exact English brand ending
narration-final-raw.mp3
narration-final.wav   # fully processed Mukund Tight v4 narration
narration-final.transcript.large-v3.json # raw local Whisper word timestamps
visuals/              # relevant source images and screenshots
news-panel.mp4        # editorial timeline, no audio required
sfx-cues.json         # optional array of placed effect files/times/gains
render-manifest.json  # measured duration and final asset choices
final.mp4
publishing-copy.json   # caption/title, complete description, required + relevant hashtags
dashboard-result.json  # final video, same publishing fields, summary and actual checks
```

`templates/episode.json` is a planning template. `render_short.py` receives
explicit CLI inputs and does not auto-research or render this planning JSON.
The web dashboard queues skill-driven generation and stores resumable OpenCode
session IDs. Its Post to YouTube button uses the generated publishing package;
explicitly enabled automatic-upload sessions publish after a successful render.
See `youtube-publishing.md` for the handoff and comment-setting limitations.

## 3. Script-to-visual mapping

| Rough 45 s plan | Job | Asset |
|---|---|---|
| 0–3 | Hook/new development | Recognizable subject + short headline |
| 3–9 | People/platform and what happened | Portrait, logo, relevant clip |
| 9–18 | Evidence/source | Legible source excerpt, attribution |
| 18–28 | Explain why it matters | Relevant photo or readable source excerpt |
| 28–38 | Twist/response/qualification | Contrasting source/statement |
| 38–45 | Takeaway/next step | Relevant image retained through spoken brand CTA |

These are planning estimates. Generate narration first, then retime the final
visuals to real spoken phrases. Do not force every story into exactly 45 seconds.
Avoid a new visual cut during an important half-read statement just to hit a timer.

After completing all audio processing, run:

```sh
uv run --with mlx-whisper scripts/transcribe_reference.py episodes/STORY/narration-final.wav --out episodes/STORY/narration-final.transcript.large-v3.json --model mlx-community/whisper-large-v3-mlx
```

The helper uses `word_timestamps=True`. Read `segments[].words[]` for word text
and start/end seconds. Check the transcript against the original script, especially
names, fast Hinglish and the full English outro. Listen to spot-check boundaries.
Keep raw ASR output and any corrections separately. Derive image/SFX cues from
checked phrase times; do not force-align the script by inventing character times.
Whisper timestamps are estimates, not guaranteed frame-accurate boundaries.
Run it again if audio changes. This is a separate step after the preset wrapper;
null `.alignment.json` sidecars are not the production timing source.

## 4. Gameplay library, without indexing

```text
library/gameplay/subway-surfers/
library/gameplay/rocket-league/
library/gameplay/driving/
library/gameplay/other/
library/sfx/
```

Use self-recorded gameplay or footage you have permission to reuse. Store optional
source/license notes beside files. Keep the reference Short outside this library;
it contains the creator's branding and editorial composite.

File names can simply be descriptive: `subway-run-01.mp4`, `car-track-02.mp4`.
No asset index is required. Scan folders when selecting a clip. Prefer recordings
2–10 minutes long with no intro, loading screens, menus, facecam or embedded music.
Start with ~3–5 usable recordings across game types when assets are supplied.

Pick a continuous section at least as long as the narration. Select one file and
offset per episode and save them. Reuse different sections later. If a short clip
must loop, inspect the loop seam. Cropping should keep the player/car/track visible;
Subway Surfers and landscape car games need different crop decisions.

The supplied renderer requires sufficient gameplay duration and rejects too-short
inputs rather than silently freezing or looping. Add long recordings to avoid this.

## 5. Layout for new output

Baseline uses measured reference proportions: headline 214 px, editorial 810 px,
gameplay 730 px, footer 166 px. Preserve the approved red header and blue branded footer. Keep
critical text horizontally within approximately x=70…900; preview against actual
Shorts UI because device/title overlays vary. A lower 166 px footer can be covered
by platform UI, so do not place essential information there.

Use contain-fit for documents to preserve words and aspect ratio. Use fill/crop
for gameplay. Preserve attribution within source screenshots. Do not add editorial
cards or phrase captions unless explicitly requested; never obscure a quote.

## 6. Quality check

- Source dates and claims correct; uncertainty and responses represented.
- Hinglish pronunciation checked by listening, especially names and English outro.
- Correct 1080×1920 square-pixel output, H.264/yuv420p, AAC 48 kHz, fast-start MP4.
- No black gaps, accidental silent ending, stretched faces/documents or frozen game.
- Headline and source excerpts legible in a 270×480 preview and clear of Shorts controls.
- Gameplay audio muted; narration dominant; SFX intentional and not startling.
- Final audio target around −14 LUFS with true peak ≤−1.5 dBTP. Measure the encoded
  result, not just intermediate WAV; re-normalize if the final measurement fails.
- Watch/listen to the complete finished Short before upload.
- Record unavailable listening or factual checks as incomplete. ASR, OCR, full
  decode and sampled screenshots are distinct checks, not substitutes for them.
- Validate `publishing-copy.json` and `dashboard-result.json`: caption/title,
  complete description with sources, #shorts, #genzshortnews and relevant tags.
  The user should only need to click Post to YouTube, not write metadata.
