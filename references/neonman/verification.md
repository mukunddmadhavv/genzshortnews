# Verification status

Completed 2026-09-27:

- Downloaded and probed the reference: 1080×1920, 60 fps, 45.116667 s video.
- Extracted/reviewed 46 integer-second samples, plus full-size selected frames.
- Extracted mono audio and generated local large-v3-turbo ASR with word timings.
- Measured editorial cut candidates and full-mix loudness.
- Compiled all Python scripts successfully.
- Ran ElevenLabs helper CLI help successfully; live account calls await credentials.
- Rendered two synthetic 2-second compositor smoke tests, with and without a timed
  SFX cue and with a nonzero gameplay offset.
- Confirmed output H.264, 1080×1920, square pixels, yuv420p, 30 fps, AAC 48 kHz,
  duration 2.000 s; decoded SFX test without errors and inspected its output frame.

Synthetic outputs are in `output/verification/`; they are not production videos.
No direct listening review or account-authenticated ElevenLabs audition was
performed. Exact vocal modulation and reference SFX remain unverified. The
gameplay library has folders but awaits usable source recordings.
