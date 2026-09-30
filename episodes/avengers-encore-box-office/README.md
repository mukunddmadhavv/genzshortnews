# Avengers: Endgame Encore Box Office — GENZ SHORT NEWS

Finished video: **`final-genz-short-news.mp4`**, 53.911 seconds, 1080×1920 (9:16 vertical), 30 fps, H.264 video and stereo AAC audio.

## Story & Facts

- **Subject**: Box office comparison of *Avengers: Endgame* (2019) vs the September 2026 re-release extended edition *Avengers Endgame: Encore* in India and Worldwide.
- **Worldwide Comparison**:
  - *Endgame* (2019): Historic $1.223 Billion global opening weekend; lifetime worldwide gross reached $2.799 Billion.
  - *Encore* (Sept 2026): Added $86 Million worldwide in its opening weekend ($26 Million domestic + $60 Million overseas across 30+ markets), becoming the first re-release to top the US box office since 2011.
  - *Total Milestone*: Pushes *Endgame*'s total box office to **$2.89 Billion**, just ~$33 Million away from *Avatar*'s all-time crown ($2.923 Billion).
- **India Comparison**:
  - *Endgame* (2019): Collected **₹440 Crore gross** (₹373 Cr nett), holding the undisputed record as the highest-grossing Hollywood movie in Indian cinema history.
  - *Encore* (Sept 2026): Massive rush across Indian IMAX and premium screens to watch the new footage bridging into *Avengers: Doomsday* (December 2026), featuring Robert Downey Jr. as Doctor Doom and Loki visiting Steve Rogers.

## Production Details

- **Channel Branding**: Red headline bar (`AVENGERS ENCORE BOX OFFICE!`), blue footer bar (`GENZ SHORT NEWS / FOLLOW FOR MORE`).
- **Narration**: High-energy, conversational Hinglish written purely in Devanagari Hindi (देवनागरी) without bracketed tags for seamless vocal consistency.
- **Outro**: Spoken in the exact same narrator voice: **“Follow GENZ SHORT NEWS for more!”**.
- **Voice & Processing**: ElevenLabs `eleven_v3` voice model, base language `hi`, TTS speed 1.12, 1.30× pitch-preserving tempo adjustment (`atempo`), highpass filter (75 Hz), presence EQ (2.6 kHz), dynamics compression, and loudness normalization targeting −14 LUFS.
- **Visuals**: Eight narration-aligned image beats on a black contain-fit upper panel (1080×810), continuous driving gameplay (1080×730), red headline bar, and blue footer.
- **Audio & SFX**: Five user-selected whoosh cues (`library/sfx/user-whoosh.mp3`) at −11 dB cue gain on key thematic shifts, final mix targeting −14 LUFS.
- **Gameplay**: Continuous bottom panel using Rocket League driving gameplay from `episodes/mau-6V_gg2zt3b8/gameplay-hinglish.mp4` starting at offset 5.0s.

## Verification

- **Full Stream Decode**: Passed with zero errors (`ffmpeg -v error -xerror`).
- **Loudness**: **−14.13 LUFS**, true peak **−4.33 dBTP** (compliant with YouTube Shorts standards).
- **Visual Quality**: 9 sample checkpoints inspected via `contact-sheet.jpg` and `final-frame.jpg`. Proper aspect-ratio contain-fit, clear text, continuous gameplay, and branding.
- **Image Provenance**: Documented with SHA-256 hashes in `image-sources.json`.

## Files & Artifacts

- `narration-hinglish.txt`: Script in Devanagari Hindi + English CTA
- `narration-hinglish.mp3`: Raw ElevenLabs TTS generation
- `narration-hinglish.alignment.json`: Raw character-level alignment
- `narration-final.wav`: Processed narration track (53.91s)
- `narration-final.alignment.json`: Time-scaled alignment
- `image-plan.json`: Visual beat cues and timings
- `image-beats.json`: Rendered visual timeline
- `image-sources.json`: Image sources, dimensions, and SHA-256 hashes
- `sfx-cues.json`: Narration-aligned whoosh SFX timestamps
- `audio-production.json`: Audio engineering specifications
- `news-panel.mp4`: Upper news panel video (1080×810)
- `final-genz-short-news.brand.png`: Header and footer overlay
- `final-genz-short-news.manifest.json`: Full render manifest and stream metadata
- `final-genz-short-news.mp4`: Finished deliverable video (1080×1920)
- `contact-sheet.jpg`: 9-frame review contact sheet
- `final-frame.jpg`: High-resolution final frame export
- `verification.json`: Automated test and verification report
