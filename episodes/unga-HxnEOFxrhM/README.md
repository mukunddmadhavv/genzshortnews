# UN viral moments — GENZ SHOT NEWS

## Finished video
`final-genz-shot-news.mp4` — **48.30 seconds**, 1080×1920, 30 fps, H.264/yuv420p, stereo AAC 48 kHz.

Original Hindi-led Hinglish narration explains the two separate events in the supplied Short: R Srinivas reacting during Shehbaz Sharif's UN speech, and S Jaishankar responding to a reporter at a separate press briefing. Claims and the quoted reply are attributed. Related imagery remains visible through the exact branded closing line.

- 10 narration-aligned image beats, including two additional publisher images.
- Approved red headline, image-only news panel on black, continuous muted Rocket League gameplay, blue GENZ SHOT NEWS footer.
- Eleven v3 narration with the configured voice, base language hi, speed 1.12; fixed 1.218× pitch-preserving body retiming per the approved pace baseline.
- Reused approved emphatic brand outro and four user-supplied whoosh cues.
- Gameplay: previous episode's reference-derived demo clip from 8 seconds; provenance in source ledger.

## Checks
- Full MP4 video/audio decode passed: 1,449 frames.
- Encoded audio measured **−14.15 LUFS**, **−4.35 dBTP**, 1.60 LU loudness range.
- Scribe transcription of the final narration matches the intended story, quoted response and “Follow GenZ Shot News for more.”
- Reviewed phone-size contact sheet and full-resolution closing frame: no gaps, unrelated imagery or extra caption cards; branding remains visible.
- No direct listening review was performed; pronunciation and subjective delivery were checked via ASR rather than acoustic audition.

## Files
- `narration-hinglish.txt`: original script (body); `narration-final.wav`: body plus approved CTA.
- `prepare.py`: reproducible body processing, alignment retiming and image/SFX planning.
- `image-plan.json`, `image-beats.json`: editable plan and resolved timings.
- `audio-production.json`, `final-genz-shot-news.manifest.json`: processing metadata and compositor command.
- `contact-sheet.jpg`, `final-frame.jpg`, `narration-check.json`: review artifacts.
- `../../references/-HxnEOFxrhM/sources.md`, `image-sources.json`: claim and image provenance.

Rebuild using `prepare.py`, `scripts/build_image_panel.py`, and the compositor command recorded in the manifest. Existing outputs are intentionally protected; use new filenames for revisions.
