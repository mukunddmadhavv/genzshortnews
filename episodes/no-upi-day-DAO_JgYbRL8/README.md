# No UPI Day Protest — GENZ SHORT NEWS

## Finished video

`final-genz-short-news.mp4` — **54.333 seconds**, 1080×1920, 30 fps, H.264/yuv420p, stereo AAC.

- Original Hindi-led Hinglish narration covering the trader protests against NPCI's 0.4% MDR charge on UPI transactions above ₹2,000, explaining exemptions for small merchants and consumer implications.
- Nine narration-aligned image beats using source-verified photos from The Hindu/ANI, Free Press Journal, India Today, Livemint, and clean reference frame excerpts.
- Approved layout: red headline bar (`NO UPI DAY PROTEST!`), image-only black contain-fit panel, continuous muted Rocket League gameplay, and blue **GENZ SHORT NEWS** footer with `FOLLOW FOR MORE`.
- Fresh ElevenLabs `eleven_v3` narration using the configured voice, Hindi (`hi`), TTS speed 1.12, pitch-preserving 1.218× retiming with highpass, presence EQ, compression, and loudness normalization.
- Exact closing line **“Follow GENZ SHORT NEWS for more!”** generated in the same continuous take and processed identically to the body.
- Four transitions use the unchanged user-supplied whoosh at −11 dB cue gain.

## Verification

- Complete video/audio decode passed.
- Encoded loudness: **−13.95 LUFS**, true peak **−4.35 dBTP**.
- Scribe v2 transcription confirms 100% word accuracy, proper names, factual attribution, and the exact closing line.
- Reviewed contact sheet (`contact-sheet.jpg`) across all visual beats and full-resolution closing frame (`final-frame.jpg`). Branding and imagery match narration with zero artifacting.
- Continuous gameplay starts from offset 12 seconds in `episodes/mau-6V_gg2zt3b8/gameplay-hinglish.mp4`.

## Reproducibility

- `narration-hinglish.txt`: complete narration script in Devanagari Hindi with exact Latin outro.
- `prepare.py`: audio processing, retimed alignment, image beat planning, and SFX cues.
- `image-plan.json`, `image-beats.json`: resolved timestamps, source files, and crops.
- `final-genz-short-news.manifest.json`: FFmpeg command, layout metadata, and stream probe.
- `verify.py`, `verification.json`, `contact-sheet.jpg`, `final-frame.jpg`: output verification and quality checks.
- `../../references/DAO_JgYbRL8/sources.md` and `image-sources.json`: source reporting and asset provenance.
