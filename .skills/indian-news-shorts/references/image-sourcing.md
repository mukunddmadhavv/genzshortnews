# Related-image sourcing for image-only news Shorts

User preference: use related images/reference screenshots only in the upper
panel, and add more valid images when available. Follow `approved-format.md`.

The user explicitly requests more web-sourced reference imagery. For every new
episode, search beyond the supplied Short for relevant event photos, portraits,
official/social posts and publisher images. Include useful verified additions
when available, prioritizing variety that follows the narration over repeating
the same reference frame. There is no fixed image quota: avoid unrelated filler
or rapid changes solely to increase the count. Record unavailable or unsuitable
results when relying on source frames instead.

## Search and validate

1. Identify the actual people, event, dates and claims from the supplied reference.
   Check ASR against visible names; use stronger transcription if a pass loses
   words or merges large sections. ASR cannot verify factual allegations.
2. Search exact subject names plus the event. Prefer primary posts, official
   material, then established publishers that identify the pictured subject.
3. Open the source page, check date/caption/body and look for later developments.
   An older article saying “no response” may be superseded by a later response.
4. Select the actual relevant photo, screenshot or article crop. Match it visually
   to the person/event before using it. Do not use random dogs, unrelated hospitals,
   generic celebrities or AI-generated scenes as apparent evidence of a real event.
5. Prefer a usable original-size image linked by the page. If only a low-resolution
   asset is available, record that limitation; don't invent a higher-resolution URL
   or assume upscaling creates new detail.
6. Keep primary allegations, replies and context visually distinct through accurate
   timing and narration. A portrait is context, not corroboration of wrongdoing.
7. If a source is inaccessible, record the limitation and use verified relevant
   reference frames rather than fabricating an image or citation.

If a search engine returns an interstitial or irrelevant results, try another
accessible engine. In the Mau episode, DuckDuckGo HTML returned useful article
links after Google/Bing failed. A search snippet is discovery, not verification.
Limit retries: inspect a failed response, try one alternate, then visit the named
publisher/official source. See `troubleshooting.md` for native macOS OCR and
Wikimedia file/category lookup. OCR of a reference screenshot does not independently
verify its quote. Save unavailable sources and unresolved claims explicitly.

## Per-reference record, without a gameplay index

Create `references/<video-id>/sources.md` and `image-sources.json`. For each added
image record: local filename, publisher/creator, page URL, direct image URL,
publication date when known, checked-at date, pictured subject, intended use,
dimensions and rights/license status. Confirmed relevance is not an open license.
Record original footage timestamp/crop for images extracted from the reference.

This is an episode's source ledger; the gameplay library remains plain folders.

```sh
uv run --with pillow scripts/fetch_reference_images.py references/VIDEO_ID/image-sources.json
uv run --with pillow scripts/build_image_panel.py episodes/STORY/image-plan.json
```

The downloader validates image bytes and stores dimensions/hashes. It does not
establish identity or source credibility; visually inspect the downloaded image.

## Image timing and composition

- Build from final narration alignment: each beat has a start phrase or time,
  image file, optional crop and purpose. Use `build_image_panel.py` for new stories.
- Keep the exact approved image-only panel: black contain-fit, direct cuts,
  related imagery; no explanatory cards or added caption boxes.
- Preserve relevant text, attribution, handles and context inside screenshots.
  Do not crop an allegation so it looks like an established fact.
- Measure each source video's panel boundaries; do not blindly reuse crops from
   another reference. Remove only the surrounding composite's headline/gameplay.
- Crop coordinates are `[left, top, right, bottom]`, not x/y/w/h. Source `nHf_2wc54yc`
  needed `[0, 144, 1080, 946]`; the output panel's y=214…1024 was the wrong source
  crop. Inspect borders and full source text before rendering; see `troubleshooting.md`.
- Choose enough images to cover key beats without meaningless visual churn.
  Longer 60–90 s explainers can use more than the typical 6–10 beats when needed
  to represent context and responses accurately.
- For a voiced closing line, retain a relevant image rather than inserting a CTA
  slide. Check the complete output and a phone-size contact sheet.

## Worked reference

`references/6V_gg2zt3b8/sources.md` and `image-sources.json`: Mau/Flying Beast,
additional Hindustan Times and Indian Express images, allegations and response.
`episodes/mau-6V_gg2zt3b8/image-plan.json`: reusable plan shape with 14 image beats.
