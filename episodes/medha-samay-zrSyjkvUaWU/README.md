# Medha & Samay: viral clip

## Voice replacement — 2026-09-28

The user replaced all earlier Mukund audio takes with the approved Eleven v4
Mukund Tight preset (recipe 3). Current voice reference:
`../../library/voices/mukund-hinglish/v4-audition/mukund-tight-v4.wav`.
The superseded standalone Mukund MP3/WAV takes were removed by request.
The finished videos and timing/manifests below remain historical episode records;
they are not current voice references, and their old audio inputs may no longer
exist. Future narration uses only `mukund-tight` with `eleven_v4`.

## Latest revision — fewer breaks, another 10% faster

**`final-mukund-fast10.mp4`** — 40.73 seconds. Audio:
`narration-mukund-fast10.wav`. Starts from the energetic revision, shortens
eight remaining quiet gaps (≥120 ms at -28 dB) to 60 ms, removes approximately
0.78 seconds, then applies one additional 1.10× pitch-preserving tempo pass.
Both cut and tempo changes are reflected in the final character alignment,
eight image beats and four whoosh cues. Full decode passed; encoded mix
measured -14.00 LUFS, -4.02 dBTP. ASR confirms the script/outro is retained.
Contact sheet reviewed. Exact processing: `mukund-fast10-profile.json` and
`narration-mukund-energetic-depaused.pauses.json`.

## Latest revision — louder and faster Mukund

**`final-mukund-energetic.mp4`** — 45.58 seconds. Uses the approved Mukund
Tight take with one 1.07× pitch-preserving tempo pass and firmer compression.
Narration: `narration-mukund-energetic.wav`; recipe:
`mukund-tight-energetic-profile.json`. Eight image beats and four whooshes retimed.
Full decode passed; encoded mix measured **-14.02 LUFS**, **-3.87 dBTP**
(previous Tight video -15.17 LUFS). Five-second contact sheet inspected.
This is an episode revision; perceived confidence/energy awaits user listening.

## Current version — Mukund Tight

**`final-mukund-tight.mp4`** — 48.77 seconds, 1080×1920, 30 fps.
Uses the exact approved `narration-mukund-tight.wav` take, mixed with whooshes.
Eight image cuts and four whooshes retimed from its pause-adjusted alignment.
Minecraft continues from the same 28-second offset. Current timing files:
`image-plan-mukund-tight.json`, `image-beats-mukund-tight.json`, and
`sfx-cues-mukund-tight.json`. Layout reviewed in `contact-sheet-mukund-tight.jpg`.
Full decode passed; encoded audio measured -15.17 LUFS, -4.24 dBTP.

## Previous version

Final: `final-genz-short-news.mp4` — 45.87 seconds, 1080×1920, 30 fps.

Uses the user's selected Identity 2 clone (Multilingual v2, speed 1.03,
stability 0.4, similarity 0.9, style 0.15, speaker boost). No additional tempo
acceleration. Full narration and branded outro generated together.

Eight image beats, two additional publisher images, continuous Minecraft
parkour from library offset 28 seconds, four user-provided whoosh cues.

Sources and reference review: `../../references/zrSyjkvUaWU/sources.md`.
Audio measurements and review limitations: `verification.json`.
Production profile: `narration-final.production.json`.
