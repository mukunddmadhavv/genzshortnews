# Reference analysis — CFZ6qULa8dU

Analyzed 2026-09-27. Source: https://www.youtube.com/shorts/CFZ6qULa8dU
Channel supplied by user: https://www.youtube.com/@NeonManShorts

## Evidence collected

- Download: `references/neonman/CFZ6qULa8dU.mp4` and yt-dlp metadata.
- Video: **45.116667 s**, **1080×1920**, **60 fps**, AV1, square pixels.
- Audio: Opus, stereo, 48 kHz. Container audio language says English, but ASR
  clearly indicates **Hindi/Hinglish**; container tags are not language evidence.
- 46 full-resolution JPEGs at t=0,1,…,45 seconds. Four labeled contact sheets.
- FFmpeg editorial-panel scene-detection candidates in `measurements.json`.
- Local Whisper small result failed substantially; retained as `transcript.raw.json`.
  Prefer `transcript.turbo.json` from Whisper large-v3-turbo. This result still
  drops opening words and misspells names. No human-verified transcript exists yet.
- YouTube subtitles could not be downloaded (HTTP 429).

## Layout, measured in source pixels

Coordinates are approximate at compressed color boundaries; heights sum to 1920.

| Layer | Rectangle (x,y,w,h) | Fraction of height | Treatment |
|---|---|---:|---|
| Headline | 0,0,1080,214 | 11.15% | Solid bright red, white uppercase bold italic text, black outline/shadow, shocked-face emoji |
| News panel | 0,214,1080,810 | 42.19% | Black background; contain-fit images, talking head, social post, article crops, show panel |
| Gameplay | 0,1024,1080,730 | 38.02% | Continuous Rocket League gameplay; orange car, ball, neon arena |
| Footer | 0,1754,1080,166 | 8.65% | Solid red, centered white uppercase italic channel name, black edge/shadow |

Headline reads “COMPLAINT! INDIA'S GOT LATENT NEW CONTROVERSY!” with a surprised
emoji. Footer reads “NEON MAN SHORTS”. Both stay throughout the sampled frames.
The reference's exact font family is unverified; only the visual attributes above
are established. For a new channel use its own name, headline and design choices.

The upper and lower media panels together are **52.6% news / 47.4% gameplay**.
Calling the full video “top half news, bottom half game” misses ~20% occupied by
branding bars. On mobile, the long headline is relatively small.

## Elements and timing

| Approximate interval | Editorial visual | Purpose |
|---|---|---|
| 0–1.58 | Purple India's Got Latent logo, black side pillars | Instant subject recognition |
| 1.58–4.55 | Creator talking into microphone with headphones | Presenter/context |
| 4.55–7.93 | Portrait-format social post collage | Introduce complaint and parties |
| 7.93–11.95 | Article heading and paragraph describing viewing circumstances | Source-shaped evidence |
| 11.95–16.47 | Narrow paragraph quoting alleged remark | Focus on allegation |
| 16.47–19.70 | Three-person show-panel visual, central person holding microphone | Identify source context |
| 19.70–26.90 | Article excerpt on complainant's characterization | Explain objection |
| 26.90–34.83 | “Complainant questions Netflix India's role” excerpt | Broaden the story |
| 34.83–40.75 | Cropped paragraph acknowledging need to verify statement/identity | Introduce qualification |
| 40.75–45.12 | Continuation mentioning context, timestamp and original recording | End on verification caveat |

Times combine one-second visual review with automatic candidate cuts; subframe
precision is not manually verified. Candidates at 3.85/3.88 and 19.70/19.72 can
be motion/adjacent transition frames, not separate narrative scenes. Ten main
editorial states imply ~4.5 seconds per state, ranging from ~1.6 to ~7.9 seconds.
Most of the runtime from ~8 s onward uses held text excerpts, interrupted once
by the show panel. No sampled phrase-by-phrase or karaoke captions were found.

Late CTA overlays appear over the gameplay: subscribe at 38 s, subscribed/bell
state at 39–40 s, “DON'T FORGET TO LIKE” at 41–42 s, gone at 43 s. The gameplay
continues behind these overlays and independently of the editorial sequence.

No elaborate transitions, countdown, progress bar, pervasive emojis, highlighted
keywords, or frequent meme cutaways are visible in the sampled frames. Do not
invent them as channel conventions. A visual panel with people is not evidence
that its original audio was mixed in.

## What the story says (reference summary, not independently verified news)

The Short describes a complaint concerning an India's Got Latent clip and names
Mukesh Chhabra and Netflix India. It attributes an account to IANS, explains
that a viewer objected to a remark, discusses questions about the platform's
role, and ends with the complaint's acknowledgement that authenticity, identity,
full context, timestamps and the original recording need verification.

The full-resolution article crop at 8 s visibly names **Mukesh Chhabra**, which
corrects the ASR's name spelling. It displays September 22, 2026. The publisher
URL is not visible in the crop; do not manufacture a citation from this screenshot.

## Narration and audio: supported findings

- ASR indicates Hindi sentence structure with English phrases such as “complaint”,
  “according to”, “highly inappropriate”, “platform”, and “complete context”.
- The recovered text moves rapidly from topic → complaint → source → alleged
  remark → objection → platform responsibility → caveat; “but” introduces the
  final qualification. This supports a conversational explanatory script design.
- ~140 whitespace-separated ASR tokens / 45.12 s = ~186 tokens/min. Mixed-script
  tokenization, missing words and inaccurate segments make this a rough density
  estimate, **not exact WPM** and not a target to copy mechanically in English.
- Full-mix loudness: **−12.44 LUFS integrated**, **+0.52 dBTP**, **3.10 LU LRA**.
  This is a loud, low-dynamic-range mix. These are measurements of all audio,
  not an isolated narrator. A positive reconstructed true peak does not by itself
  prove audible clipping. Aim for more headroom in new exports.
- Voice pitch range, accent subtleties, emotional inflection and exact SFX/BGM
  timing have **not been verified by direct listening**. ASR cannot establish them.
  The proposed English performance guide is a production recommendation, not a
  claim of a forensic vocal match.

## Recommended improvements for this project

Historical suggestions below predate user approval of the image-only v2 preview.
`approved-format.md` supersedes suggestions for key-fact cards, added captions
and CTA graphics. Retain relevant source images/screenshots as the visual style.

1. Preserve the understandable split-screen structure and continuous gameplay.
2. Replace long article paragraphs with a short key-fact card plus a readable
   attributed excerpt when needed. Show source/date without tiny text.
3. Give the story an original angle: “what this changes for viewers”, “what is
   confirmed vs alleged”, a two-event timeline, or an India-specific consequence.
4. Optional English phrase captions (3–6 words) can improve muted viewing;
   position them near the panel boundary without covering evidence.
5. Use a brief original CTA after the main payoff. Keep it away from the Shorts
   right-side buttons and bottom title/caption area; inspect in a mobile preview.
6. Default to restrained editorial SFX and −16 LUFS / ≤−1.5 dBTP final audio.
