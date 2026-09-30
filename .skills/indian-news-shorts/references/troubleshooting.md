# Production preflight and failure recovery

Read before starting every episode. Lessons recorded from `nHf_2wc54yc` on
2026-09-28. External services can still fail; use these recovery paths rather
than repeating failed calls or claiming an incomplete check passed.

## 1. Preflight once, then reuse assets

- Check `uv`, `ffmpeg`, `ffprobe`, the selected gameplay, narration preset, font,
  and `library/sfx/user-whoosh.mp3` before production. Never print `.env` values.
- Use `uvx yt-dlp --version` and `uvx yt-dlp` when yt-dlp is not globally installed.
  Do not install globally merely to resolve `command not found`.
- Use dependency-scoped commands: `uv run --with pillow` for image tools and
  `uv run --with mlx-whisper` for ASR. Do not assume plain Python has packages
  installed because another uv environment does. Pillow pixel inspection does
  not require NumPy.
- Check existing source metadata, media, transcripts, narration and renders first.
  Reuse successful outputs. Do not regenerate a paid voice take to fix timestamps.
- Follow available tool/file-edit instructions; save scripts with the file-edit
  tool rather than long ad-hoc shell code. If graph tools required by AGENTS.md
  are unavailable, use the available exploration tools; do not claim graph use.
- Save all diagnostics in the episode/reference directory or the harness-approved
  temporary directory. Verify parent directories before commands create files.

## 2. Download and container handling

```sh
uvx yt-dlp --write-info-json -f "bv*+ba/b" -o "references/VIDEO_ID/source.%(ext)s" "https://www.youtube.com/shorts/VIDEO_ID"
```

- A missing JavaScript-runtime warning is distinct from download failure. Probe
  the result; configure a supported runtime if extraction/formats actually fail.
- The result can be WebM despite an MP4 video stream. Use the real returned path,
  inspect with ffprobe, and pass it to `analyze_reference.py` (it accepts video
  paths, not just MP4). Do not assume `source.mp4` exists or rename an extension.
- Remux/transcode only when a consumer requires it; preserve source metadata.
  In this episode the AV1 stream was copied and audio converted to AAC for MP4.

## 3. Bounded search and factual evidence

- Use the web-fetch tool first. If a search engine gives an interstitial, error,
  or empty parsed results, inspect the response once; an empty regex match is
  not evidence that no reporting exists.
- Try one alternate engine, then the named publisher or official source directly.
  Avoid cycling through essentially identical blocked searches.
- Inspect frame/contact-sheet images directly. For text extraction on macOS,
  Swift with `Vision` and `VNRecognizeTextRequest` worked without Python OCR
  packages. Check `swift --version` first. Python `Vision` needs separate bindings;
  pytesseract needs both its package and the Tesseract binary. Neither was present.
- OCR recovers visible text only. A screenshot quoting NDTV is a secondary
  reference, not an opened NDTV interview. Record the source URL, frame/time,
  quotation and verification level. Never invent publisher URLs or verification.
- Dates in downloaded metadata resolve the reference's timeline, not the truth
  of its claims. Check selection year versus ceremony year explicitly.
- Attribute unresolved claims to the supplied reference; omit unsupported budget,
  popularity or eligibility claims. Country submission selection is not the
  Academy's nomination decision or a blanket exclusion from all Oscar categories.

## 4. Whisper timeouts and optional ElevenLabs alignment

- Keep large-v3 as the production default on the **final processed WAV**. Always pass an
  explicit extended timeout to the execution tool (e.g. `timeout: 600000` / 10 minutes)
  rather than repeatedly starting the model with the default 120-second shell timeout.
- Distinguish weight downloads, inference and timeout termination from logs.
  `Fetching 4 files: 100%` does not mean transcription completed. Check for valid
  output JSON with nonempty segments and word timestamps.
- **Process shutdown hang on macOS**: MLX with multiprocessing can trigger `multiprocessing/resource_tracker.py`
  semaphore cleanup warnings and hang at Python exit. `scripts/transcribe_reference.py` calls
  `os._exit(0)` upon writing output to prevent this shutdown hang.
- **Fast fallback to prevent pipeline stalls**: If large-v3 download or initial Metal kernel compilation
  stalls or exceeds available time, use `mlx-community/whisper-small-mlx` (cached locally, finishes in 3–5 seconds)
  which provides word-level timestamps (`segments[].words[]`) suitable for scheduling beats.
  `scripts/transcribe_reference.py` includes automatic `--fallback-model mlx-community/whisper-small-mlx`.
- `missing_permissions` for ElevenLabs forced alignment is a known optional
  capability limitation. Preserve the successful v4 take, finish the preset's
  processing and obtain local timestamps. Do not switch narrator or regenerate.
- Preserve null/status alignment sidecars. Never fill them with uniformly spaced
  characters derived from segment duration. Consume ASR word records or reviewed
  explicit beat start times. Record any manual corrections separately.
- **Resilient image panel builder**: `scripts/build_image_panel.py` directly accepts
  explicit beat `start` times without requiring character arrays in the alignment sidecar.
  When matching `phrase`, it searches forward from the previous match so repeated words
  or phrases never match an earlier occurrence and violate strictly increasing starts.


## 5. Image discovery, crops and composition

- Prefer exact file titles/URLs returned by publisher or Wikimedia APIs over
  guessed names. Commons search defaults can return article pages; request file
  namespace `srnamespace=6`, or use `categorymembers` for a named person.
- Request `imageinfo` with URL, size and license metadata. Reject tiny thumbnails;
  the first Vivek Vaswani result was only 116×131. A category lookup found 585×881.
- Inspect each downloaded image before timing it. Resolution alone does not make
  a good portrait: this episode's Ranveer image shows basketball action. Prefer
  a recognizable face or film still for a film-news hook. Confirm actual license,
  creator, date and context; do not infer them just from the hosting domain.
- Output layout is not a source crop preset. Measure source boundaries, inspect
  representative frames and crop before contain-fitting into 1080×810.
- Crops use `[left, top, right, bottom]` (exclusive right/bottom), not x/y/w/h.
  This source used `[0, 144, 1080, 946]`; do not reuse it blindly for another video.
- Initial use of output y=214…1024 cut source content and included gameplay.
  A y=140 crop retained a thin red edge. Use row/pixel inspection plus visual
  review to remove border bleed while preserving attribution and complete text.
- Confirm gameplay remaining duration covers final speech, font path exists,
  and headline fits before rendering. Use the approved red header/blue footer.

## 6. Honest completion and concise updates

- Keep narration and rendering work moving after a bounded failed investigation.
  Batch independent reads/checks; avoid repeatedly inspecting identical frames.
- Send updates for a result, decision or blocker, not internal deliberation or
  every routine command. Maintain accurate todo states.
- Record full decode, encoded LUFS/true peak and sampled visual review separately
  from full playback/listening, pronunciation, voice identity and fact checks.
  ASR plus loudness measurement is not a listening review.
- Check the English ending by listening; Hindi ASR may transliterate it and cannot
  alone prove exact English wording. Mark unavailable listening review unverified.
- Keep an episode `production-issues.md` listing symptoms, attempts, actual
  recovery, unresolved limits and prevention. Update generated reports as well
  as summaries when earlier claims overstated verification.
