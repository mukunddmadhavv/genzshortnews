# Sunil Pal criticises Salman Khan — GENZ SHORT NEWS

## Finished video

`final-genz-short-news.mp4` — **47.175 seconds**, 1080×1920, 30 fps, H.264/yuv420p, stereo AAC.

- Original Hindi-led Hinglish narration with context for Salman's anti-trolling statement and clearly attributed Pal comments.
- Nine narration-aligned image beats using reviewed source frames and three publisher images.
- Approved red headline, image-only black contain-fit panel, continuous muted Rocket League gameplay, and blue **GENZ SHORT NEWS** footer.
- Fresh Eleven v3 narration, configured voice, Hindi, TTS speed 1.12, fixed pitch-preserving 1.218× retiming with consistent EQ/compression.
- Exact closing line **“Follow GENZ SHORT NEWS for more!”** generated in the same take and processed identically to the body.
- Four transitions use the unchanged user-supplied whoosh at −11 dB cue gain.

## Verification

- Complete video/audio decode passed.
- Encoded loudness: **−14.14 LUFS**, true peak **−4.18 dBTP**.
- Final narration Scribe transcription matches the intended story, names, attribution and corrected closing line.
- Reviewed all nine visual beats at phone size and the full-resolution closing frame. Source composites/watermark remain intact; imagery matches narration; branding is correctly spelled.
- No direct acoustic listening pass was performed. ASR checks wording, not subjective voice quality or pronunciation nuances.
- Gameplay reuses the prior episode's reference-derived demo clip from offset 8 seconds; the local gameplay library is still empty.

## Reproducibility

- `narration-hinglish.txt`, original MP3 and alignment: complete fresh take.
- `prepare.py`: processing, retimed alignment, image plan and SFX cues.
- `image-plan.json`, `image-beats.json`: crops, reference timestamps, purposes and resolved timings.
- `final-genz-short-news.manifest.json`: complete compositor command and media probe.
- `verify.py`, `verification.json`, `contact-sheet.jpg`, `final-frame.jpg`: output checks.
- `../../references/ez1YRJeIJyw/sources.md` and `image-sources.json`: source and asset provenance.

Run from project root using `python3 episodes/sunil-pal-ez1YRJeIJyw/prepare.py`, `uv run --with pillow scripts/build_image_panel.py episodes/sunil-pal-ez1YRJeIJyw/image-plan.json`, then the render command recorded in the manifest. Existing media outputs are protected; choose new paths for revised takes/renders. Run `uv run --with pillow episodes/sunil-pal-ez1YRJeIJyw/verify.py` for verification.
