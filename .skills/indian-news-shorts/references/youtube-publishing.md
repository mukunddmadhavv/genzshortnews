# YouTube publishing package — required for every Short

## Automatic generation

Generate publishing copy during video production, without asking the user to
write it. Read the final script and verified source records. Reconcile the copy
with the finished video after edits. This requirement applies to topic-based,
YouTube-reference and resumed/edit sessions.

- **Destination:** @genzshotnews; display name GENZ SHORT NEWS.
- **Caption/title:** a concise, engaging Hinglish hook that accurately describes
  the story. Maximum 92 characters before the uploader adds ` #shorts`, keeping
  the YouTube title within 100 characters. No unsupported claims or misleading
  clickbait. Natural Roman Hinglish or Devanagari may be used for publishing copy;
  the narration's Devanagari requirement remains separate.
- **Description:** write a useful original summary of the actual video, preserving
  attribution, uncertainty and distinctions between separate events. Include
  relevant verified source URLs from the episode records and the brand CTA
  `Follow GENZ SHORT NEWS for more!`. Leave room for hashtags within YouTube's
  5,000-character limit. Never invent source URLs.
- **Hashtags:** always use exactly spelled `#shorts` and `#genzshortnews`, plus
  3–6 relevant tags about the people, event, subject or platform actually covered.
  Use no spaces within tags, no duplicates, and no unrelated trending tags.
  Put the tags on a final description line, separated by spaces rather than commas.

These are YouTube metadata fields, not burned-in subtitles or caption boxes.
Maintain the image-only visual contract in `approved-format.md`.

## Required files

Save `publishing-copy.json` beside the final render in the current episode/revision
directory. Use the actual story's copy, not placeholders:

```json
{
  "title": "Accurate, engaging Hinglish title",
  "caption": "Accurate, engaging Hinglish title",
  "description": "Story summary with attribution and verified source links.\n\nFollow GENZ SHORT NEWS for more!\n\n#shorts #genzshortnews #RelevantTopic #RelevantPerson #RelevantEvent",
  "hashtags": ["#shorts", "#genzshortnews", "#RelevantTopic", "#RelevantPerson", "#RelevantEvent"]
}
```

Also save `dashboard-result.json` with the same `title`, `caption`, `description`
and `hashtags` fields, plus:

- `video`: `final.mp4` for dashboard generation jobs.
- `summary`: a short account of what was produced or changed.
- `checks`: `decode` and `dimensions` booleans, true only after actual checks.

Keep both files consistent. Never mark a failed video complete just because its
publishing copy is ready. Keep copy and renders for older revisions unchanged.

## One-click publication

Caption/title, full description and hashtags must be visible in the dashboard
before publication. Generate and save them as part of the video job, before
marking the revision Ready. The publish job must not invoke an AI model or write
new copy: it only uploads the saved fields. Missing copy blocks publication.
For older/imported videos, run a separate copy-preparation job first and display
the result for review; do not hide that work inside the upload action.

The dashboard's **Post to YouTube** button queues publication with the generated
title and description, defaults to requested **public** visibility, and marks
these general-audience news videos **not made for kids**. The operator can change
publishing options when appropriate. A generation agent must not independently
upload the video: the dashboard's channel-verified uploader owns that action.
An explicitly enabled automatic-upload session uses the same prepared copy and
the visibility selected for that session.

The uploader verifies @genzshotnews before upload, records YouTube's returned
visibility and video URL, and resumes interrupted uploads using checkpoints.
Unaudited API projects may have public requests restricted to private by YouTube;
report the actual result rather than claiming public publication.

## Comments

The user wants comments enabled. YouTube's video-upload API does not expose a
comment-enable parameter. Configure comments in **YouTube Studio → Settings →
Upload defaults → Advanced settings → Comments** and check the resulting video.
Do not invent a `commentsEnabled` API field or claim the API enabled comments.
“Not made for kids” avoids that specific automatic restriction but does not
override other YouTube comment restrictions.

## Completion checklist

- Caption/title matches the finished story and fits the length limit.
- Description is complete, original, attributed and within 5,000 characters.
- Required hashtags and 3–6 relevant additional tags are present.
- Both JSON files contain identical publishing fields and parse successfully.
- The saved package is ready for the dashboard button without manual writing.
