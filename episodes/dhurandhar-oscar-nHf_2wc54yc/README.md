# Dhurandhar Oscar Entry Rejection — GENZ SHORT NEWS

## Finished Video

`final-genz-short-news.mp4` — **44.733 seconds**, 1080×1920, 30 fps, H.264/yuv420p, stereo AAC.

- Original Hindi-led Hinglish narration covering the rejection of Aditya Dhar's multi-starrer *Dhurandhar* (starring Ranveer Singh) as India's official entry for the Academy Awards in favor of Marathi film *Gondhal*.
- Direct attribution to Oscar selection jury member Vivek Vaswani quoting his interview with NDTV explaining the jury's perspective on Indian culture representation, the 4/14 vote tally, and the final 3 contenders (*Gondhal*, *Angh*, *Main Vaapas Aaunga*).
- Nine narration-aligned visual beats using verified high-res Wikimedia portraits of Ranveer Singh, director Aditya Dhar, and jury member Vivek Vaswani, paired with clean, readable reference excerpts of the official poster, the Marathi film entry announcement, Inshorts coverage, and NDTV report excerpt.
- Approved layout contract: red headline bar (`DHURANDHAR OUT OF OSCARS!`), image-only contain-fit upper panel with black padding, continuous muted Minecraft parkour gameplay, and blue `#1260dc` **GENZ SHORT NEWS** footer with `FOLLOW FOR MORE`.
- Narrated using the approved `mukund-tight` preset on ElevenLabs `eleven_v4` in Hindi (`hi`), processed with fixed highpass, compression, pause-shortening, and tempo polish.
- Exact closing line **“Follow GENZ SHORT NEWS for more!”** generated in the same continuous take and processed identically to the body.
- Four transitions use the unchanged user-supplied whoosh (`library/sfx/user-whoosh.mp3`) at −11 dB cue gain.

## Verification

**Correction:** Independent reporting verification and direct listening were not
completed. NDTV attribution came from the supplied Short's Inshorts screenshots,
not an opened interview. Large-v3 timed out twice; the successful transcript is
Whisper small, with noticeable errors in names and the English outro. See
`../../references/nHf_2wc54yc/production-issues.md` for all failures and prevention.

- Complete video/audio decode: **passed**.
- Encoded loudness: **−13.85 LUFS**, true peak **−4.17 dBTP** (target: −14 LUFS, TP ≤ −1.5 dBTP).
- Reviewed contact sheet (`contact-sheet.jpg`) across all 9 visual beats and full-resolution closing frame (`final-frame.jpg`).
- Continuous gameplay starts from offset 10.0 seconds in `library/gameplay/minecraft/minecraft-parkour.mp4`.

## Reproducibility

- `narration-hinglish.txt`: complete narration script in Devanagari Hindi with exact Latin outro.
- `narration-final.transcript.json`: raw Whisper-small word/segment estimates;
  production-quality timing and listening review remain incomplete.
- `prepare.py`: image/SFX planning and metadata generation. Its character-alignment
  interpolation is invalid timing evidence and must not be copied into future work.
- `narration-final.alignment.json`: synthetic evenly spaced character arrays, not
  recognized character timing or forced alignment. Image starts were explicit.
- `image-plan.json`, `image-beats.json`: resolved timestamps, source files, and crops.
- `final-genz-short-news.manifest.json`: FFmpeg command, layout metadata, and stream probe.
- `verify.py`, `verification.json`, `contact-sheet.jpg`, `final-frame.jpg`: output verification and quality checks.
- `../../references/nHf_2wc54yc/sources.md` and `image-sources.json`: source reporting and asset provenance.
