# MrBeast at the Taj Mahal — GENZ SHORT NEWS

Finished video: **`final-genz-short-news.mp4`**, 46.181 seconds, 1080×1920, 30 fps, H.264 and stereo AAC.

## Production

- Original Hinglish explanation of the Taj Mahal visit, fan interactions, reported filming permission and sketchbook gift, ending with the visible “Mr Bean” reel-caption joke.
- Approved configured Eleven v3 voice, Hindi, speed 1.12, fixed 1.218× pitch-preserving processing. Excited opening and a brief laugh direction; the same take includes “Follow GENZ SHORT NEWS for more!”.
- Eight timed image beats, two additional publisher images, black contain-fit upper panel, continuous muted gameplay, red headline and blue corrected footer.
- Three user-selected whoosh cues at −11 dB, with final mix targeting −14 LUFS.
- Gameplay reuses the prior reference-derived demo clip from 8 seconds; the local gameplay library has no recordings.

## Checks

- Complete video/audio decode passed.
- Encoded loudness **−14.14 LUFS**, true peak **−4.32 dBTP**.
- Final Scribe transcript matches the wording, names and correct closing line. It detected a non-speech laughing event at the joke; direction tags were not transcribed as spoken words.
- Reviewed contact sheet covering all eight visual beats plus closing frame: relevant imagery, readable source caption, retained fan handles, correct branding, gameplay throughout.
- Reference transcription used full Whisper large-v3 and Scribe cross-check. Scribe recovered the code-switched names more clearly.
- Direct listening/audio-capable emotion analysis was unavailable. The reference's emotion remains unverified; expressive choices are creative directions, not claims about the original narrator. ASR laughter detection is not a subjective naturalness review.

## Reproduce and revise

`prepare.py` processes narration and builds phrase-aligned image/SFX plans. Use `scripts/build_image_panel.py` to render the plan, then the compositor command in `final-genz-short-news.manifest.json`. Existing media outputs are protected: use new paths for revised takes.

`verify.py` runs the established export checker from the Sunil Pal episode with this episode's paths. Checks and review images are in `verification.json`, `contact-sheet.jpg` and `final-frame.jpg`.

Sources, image provenance and expression notes: `../../references/vpFaBSrCEsc/`.
