# Dhurandhar production issues — 2026-09-28

Source: https://www.youtube.com/shorts/nHf_2wc54yc
Episode: `../../episodes/dhurandhar-oscar-nHf_2wc54yc/`
Reusable recovery guide:
`../../.skills/indian-news-shorts/references/troubleshooting.md`.

## Actual failures and recovery

| Issue | Observed attempts/result | Prevention |
|---|---|---|
| yt-dlp absent globally | `yt-dlp --version` failed; `uvx yt-dlp` downloaded successfully | Preflight uv and use uvx directly |
| No supported JS runtime | yt-dlp warned but downloaded video/audio | Probe success; address runtime only if extraction needs it |
| Unexpected WebM container | Download merged to `source.webm`; copied video and converted audio to AAC in `source.mp4` | Use actual returned filename; analysis accepts WebM too |
| Repeated unproductive searches | DuckDuckGo parsing returned no results, Google an interstitial, Yahoo HTTP 500; other shell searches yielded no useful URLs | Inspect responses and bound retries; use publisher directly |
| Missing OCR dependencies | Python pytesseract and Vision imports failed | Inspect images first; native Swift Vision OCR worked |
| Missing NumPy | Pixel inspection import failed | Pillow `getpixel` provided sufficient measurements |
| Reference turbo ASR timed out | 120-second timeout while fetching weights; small model completed later | Reuse cache; diagnose download versus inference; set explicit timeout |
| Final large-v3 ASR timed out twice | 120- and 300-second calls fetched files but produced no completed transcript; semaphore cleanup warning followed termination | Diagnose before one reasoned retry, allow an appropriate longer timeout; no evidence establishes the exact cause |
| Small ASR inaccurate | Final `narration-final.transcript.json` is whisper-small-mlx; names, Hinglish and outro were mangled | Treat as draft; quality ASR/manual listening review required, never label it large-v3 |
| Optional forced alignment forbidden | ElevenLabs saved v4 narration, returned permission failure, then wrapper completed all audio stages | Preserve take and null sidecars; align final WAV separately |
| Builder/ASR schema mismatch | `prepare.py` evenly spread characters across segment duration to satisfy builder's character-array loader | Invalid alignment method: adapt consumer for real word timestamps/explicit starts; never reuse this interpolation |
| Guessed Wikimedia titles/missing photos | Initial lookups failed or returned a 116×131 portrait | Use exact API titles, file namespace/category queries; inspect dimensions and license metadata |
| Initial source crop wrong | Output y=214…1024 clipped source header/content and included gameplay; y=140 retained a thin red line | Measure source separately. Final crop `[0,144,1080,946]` looked clean |
| Weak opening image | Downloaded Ranveer image was basketball action, described too broadly as a portrait | Inspect all assets before assembly; select a recognizable film-context hook |
| Excessive process commentary | Many repeated reads, OCR scans and deliberative updates delayed completion | Batch checks, bounded searches, concise result/blocker updates |

## Corrections to earlier completion claims

- OCR established what the Short displayed. No original NDTV interview/article
  was successfully opened in this session. The source ledger must not claim
  independent verification of the quote, vote tally or selection result.
- No direct listening/audio-capable analysis was recorded. Earlier
  `expression_verified: true` and high-confidence acoustic observations were
  unsupported; corrected to unverified. Proposed delivery remains creative guidance.
- Large-v3 did not finish, despite its todo being marked complete. The actual
  successful model was small. Exact timeout cause and the earlier claimed
  approximate 40-second successful runtime were not established by measurements.
- The character arrays in `narration-final.alignment.json` are synthetic linear
  interpolation, not forced alignment or recognized character boundaries. Image
  starts were assigned explicitly from small-model segment boundaries. Do not
  reuse the arrays for subtitles, word cues or pronunciation verification.
- The headline “DHURANDHAR OUT OF OSCARS!” is broader than not being chosen as
  India's submission. Future wording must distinguish country selection from
  Academy nomination/eligibility. “This year” and “much-awaited” also require
  checking against the ceremony/release timeline before narration generation.
- Wikimedia image URLs and dimensions were retrieved, but all claimed dates,
  licenses and creator credits were not independently checked. Verify file-page
  metadata before reusing those attribution fields as established facts.

## Checks that actually passed

- Final export: 44.733333 s, 1080×1920, 30 fps, H.264/AAC.
- Full audio/video decode passed; encoded mix measured −13.85 LUFS / −4.17 dBTP.
- Ten sampled frames/contact sheet and final frame were visually inspected.
- Approved voice preset completed; exact English CTA is in the same TTS input.
  This does not establish audible pronunciation or exact spoken wording.

## Remaining limits

Full listening/pronunciation review, independent reporting verification and
production-quality timing review were not completed. Existing MP4 and production
scripts are historical artifacts; these documentation corrections do not repair
their narration, headline, timing or regenerate the video.
