# Modi & Netanyahu: Historic Friendship — GENZ SHORT NEWS

Finished video: **`final-genz-short-news.mp4`**, 53.336 seconds, 1080×1920, 30 fps, H.264 and stereo AAC.

## Production

- **Script & Delivery**: Script written completely in Devanagari Hindi (देवनागरी) without bracketed direction tags to ensure uniform vocal timbre, accent, and pitch across the entire video. Includes the mandatory channel outro: **“Follow GENZ SHORT NEWS for more!”**.
- **Narration**: Eleven v3 voice, base language `hi`, TTS speed 1.12, 1.218× pitch-preserving tempo adjustment, presence EQ, compression, and loudness normalization.
- **Visuals**: Eight narration-aligned image beats using official high-resolution photographs from the Press Information Bureau and Wikimedia Commons on a black contain-fit upper panel (1080×810), continuous muted gameplay (1080×730), red headline bar (`MODI AND NETANYAHU STORY!`), and blue footer (`GENZ SHORT NEWS / FOLLOW FOR MORE`).
- **Audio & SFX**: Four user-selected whoosh cues (`library/sfx/user-whoosh.mp3`) at −11 dB cue gain on key thematic shifts, final mix targeting −14 LUFS.
- **Gameplay**: Continuous bottom panel using Rocket League driving gameplay from `episodes/mau-6V_gg2zt3b8/gameplay-hinglish.mp4` starting at offset 8.0s.

## Verification

- Complete video and audio stream decode passed without errors.
- Encoded loudness **−14.19 LUFS**, true peak **−4.38 dBTP** (compliant with YouTube Shorts standards).
- 8 visual beats reviewed via `contact-sheet.jpg` and `final-frame.jpg`: clear topic alignment, correct aspect ratio padding, readable text, continuous gameplay, and proper branding.
- Image provenance recorded in `image-sources.json`.

## Files & Reproducibility

- `narration-hinglish.txt`, `narration-hinglish.mp3`, `narration-final.alignment.json`
- `prepare.py`: audio processing, alignment scaling, image beat plan, SFX cues
- `image-plan.json`, `image-beats.json`: visual timing and layout
- `news-panel.mp4`: upper 1080×810 video track
- `final-genz-short-news.manifest.json`: FFmpeg render manifest and probe data
- `verify.py`, `verification.json`, `contact-sheet.jpg`, `final-frame.jpg`: verification outputs
