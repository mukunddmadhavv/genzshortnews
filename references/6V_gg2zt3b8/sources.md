# Mau / Flying Beast — source and image research

Checked 2026-09-27. Topic: the death of Labrador Mau, allegations made by
Pushpendra Choudhary, and Gaurav Taneja's response. Claims about neglect and
causation are disputed; a relevant photograph does not prove either account.

## Source reference

https://www.youtube.com/shorts/6V_gg2zt3b8

Downloaded to `reference.mp4`: 163.933333 s, 1080×1920, 60 fps. Extracted 164
integer-second frames. Selected contact sheets and full-size source frames were
reviewed to identify the story and choose visuals; this is not a claim that all
9,836 source frames were individually inspected.

Transcriptions:
- `transcript.json`: local Whisper turbo; long segments lose substantial detail.
- `transcript.scribe.json`: ElevenLabs Scribe v2; preferred working transcription.
  Proper names and assertions were checked against visible posts and reporting.

Reference narrative: early family/farmhouse context → Choudhary's allegations and
Instagram stories → response clip from Taneja → his challenge to critics. Upper
panel begins around y=200 and gameplay around y=1010, unlike the first reference's
y=214/1024 split. Source crops therefore use this video's actual boundaries.

## Opened publisher reports

### Hindustan Times — allegations, September 24

https://www.hindustantimes.com/trending/flying-beast-gaurav-taneja-s-dog-mau-dies-ex-employee-accuses-him-of-neglect-he-was-suffering-a-lot-101790241507712.html

By Sanya Jain; updated September 24, 2026, 15:10:24 IST.
Supports attribution of food/care allegations to Choudhary and earlier farmhouse
move. The statement that Taneja had not yet responded is superseded by later
reporting; it is not repeated in the new script.

Embedded primary-post lead:
https://www.instagram.com/reel/Ddi8SDVi8ei/
The original Instagram post itself was not independently downloaded/reviewed.

### Hindustan Times — response, September 25

https://www.hindustantimes.com/trending/gaurav-taneja-breaks-silence-on-pet-dog-maus-death-denies-neglect-allegations-mau-received-full-treatment-101790341544158.html

By Bhavya Sukheja; updated September 25, 2026, 18:46:40 IST.
Reports Taneja's denial, five-hospital statement, claim that records exist, and
challenge to allegations. These remain statements attributed to Taneja, not
medical records reviewed by this project.

Embedded response-post lead:
https://www.instagram.com/reel/DdtPP_bA2bL/
The original Instagram post itself was not independently downloaded/reviewed.

### The Indian Express — response and boycott context, September 26

https://indianexpress.com/article/trending/trending-in-india/gaurav-taneja-flying-beast-mau-labrador-death-controversy-beastlife-10893997/

Trends Desk; updated September 26, 2026, 14:01 IST.
Supports business-boycott context and qualification that public information does
not establish the cause of Mau's death or show that Taneja caused it. Contains
both the allegations and response, and a subject-specific lead collage.

## Additional downloaded images

`image-sources.json` stores page URLs, direct asset URLs, publication/check dates,
pixel sizes, relevance notes, rights status and SHA-256 hashes.

1. `images/ie-mau-collage.jpg` — 1024×576, Indian Express lead image showing Taneja
   with Mau as a puppy and a still from his response. Visually inspected. Used in
   response/attribution beats.
2. `images/ht-mau-photo.png` — 400×225, Hindustan Times lead collage showing Taneja
   and adult Mau. Visually inspected. Adds a distinct adult-dog image. Lower
   resolution retained honestly; not described as HD or sharpened with invented detail.

The HT response article's lead image was not selected: its filename points to
an older arrest/bail image and it would add generic portrait context rather than
useful evidence about this event. Source-video response stills were more relevant.

These publisher-hosted images have confirmed subject relevance; an open reuse
license has not been established. Do not label them public-domain or royalty-free.

## Discovery notes

Google returned a JavaScript interstitial, Bing gave irrelevant results, and the
HT search endpoint returned 410. DuckDuckGo HTML with exact subject names yielded
the actual article URLs. Article bodies were opened and checked before downloading
their images. Search snippets alone were not used as proof.

## Episode

`episodes/mau-6V_gg2zt3b8/`: original English script, Eleven v3 narration,
14 timestamped image beats, two added publisher images, continuous reference
gameplay from source seconds 5–80, and three low-level SFX cues. Full source and
crop details are in `image-plan.json` / `image-beats.json`.
