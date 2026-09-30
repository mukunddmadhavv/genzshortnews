# User-approved format — image-only news panel

The user explicitly approved `episodes/preview-01/preview-v2-images.mp4` and
asked to use this format for future videos. Treat this as the default production
contract. It overrides earlier creative suggestions elsewhere in this pack.

## Layout: 1080×1920, 9:16

| Area | Position and size | Appearance |
|---|---|---|
| Headline bar | x=0, y=0, w=1080, h=214 | Red, short white uppercase bold italic headline with black outline |
| News imagery | x=0, y=214, w=1080, h=810 | Related images and reference screenshots on black |
| Gameplay | x=0, y=1024, w=1080, h=730 | Continuous muted gameplay, fill/crop to panel |
| Channel footer | x=0, y=1754, w=1080, h=166 | Blue #1260dc, white uppercase bold italic GENZ SHORT NEWS with black outline; second line FOLLOW FOR MORE |

The confirmed channel name is **GENZ SHORT NEWS**. Default 30 fps; retain the same
panel geometry across stories. The blue/white footer supersedes v2's red footer.
Every video closes with the spoken line “Follow GENZ SHORT NEWS for more!” in a
confident delivery **using the same narrator voice as the rest of that video**,
while relevant imagery and the branded footer remain. Generate the line in the
same narration take by default; preserve tone, accent, pace and processing through
the ending. A cached outro from a previous episode is not the default. Follow
`narration-and-elevenlabs.md` for separate-take matching and continuity checks.

## Upper panel rules

- Show actual topic-related images: people, show/event photos, logos, original
  posts, article screenshots and document excerpts that support the narration.
- Use one visual at a time with direct cuts on meaningful narration changes.
  Aim for 6–10 beats when appropriate; align them to generated speech timestamps.
- Crop away irrelevant source padding/UI, then contain-fit without stretching.
  Center portrait images with black side padding. Center wide article excerpts
  with black padding above/below. Preserve source text and enough context.
- No dark-blue backgrounds, dashboard-like cards, designed explainer slides,
  added bullet lists, caption boxes or burned-in phrase subtitles in this panel.
- Text already inside a reference screenshot is welcome. The persistent headline
  and channel footer are part of the approved design.
- The narration supplies explanation and original context; imagery supports it.
  Do not insert a text-heavy summary slide or end card to fill missing imagery.
- Keep the final relevant image on screen during a spoken follow/subscribe line.
  The approved revision has no separate CTA card over the imagery.

## Gameplay and audio

- Gameplay runs independently of news-image cuts. Default audio is muted.
- Hindi-led conversational Hinglish ElevenLabs narration is primary. Use the
  supplied `library/sfx/user-whoosh.mp3` for whooshes, with DSP for processing or
  other effects. This supersedes the preview's English audio and synthetic whoosh.
- Preview v2's George voice is historical. The current approved narrator is
  Mukund Tight on Eleven v4; follow `narration-and-elevenlabs.md`.
- The preview cropped gameplay from the supplied reference and looped at 35 s.
  For production, use the local gameplay library and a long continuous section.

## Implementation reference

- `scripts/build_image_panel.py`: reusable builder for new episodes from an
  image plan and narration alignment; prefer this over story-specific builders.
- `references/image-sourcing.md`: additional-image validation and source records.
- `scripts/build_image_preview.py`: approved image-only panel implementation.
- `episodes/preview-01/image-beats.json`: example narration-aligned image choices.
- `scripts/render_short.py`: panel compositor, headline/footer, narration and SFX.
- `episodes/preview-01/contact-sheet-v2.jpg`: quick visual comparison reference.
- `scripts/build_preview.py` and `preview.mp4`: earlier card-based experiment;
  do not use their design as the default for new episodes.

The preview builder is specific to its source story. For a new story select new
related assets and phrase timings; retain this layout and presentation style.

## Final visual check

Compare a contact sheet with the approved v2 reference, applying current branding: red headline/blue footer,
image-only black news panel, continuous gameplay. Confirm every image matches
the spoken subject, source text remains readable, and no old cards/captions have
been introduced. Inspect the complete export for gaps and crop errors.
