# Instagram Reel publishing package — required for every Short

## Automatic generation & cross-platform publishing

Every finished video produced for **GENZ SHORT NEWS** must be prepared and published to **both** YouTube Shorts and **Instagram Reels**.

Do not ask the user to write Instagram copy or defer it until publish time. Generate both the YouTube and Instagram publishing copy as part of the video production job.

- **Destination:** Instagram account for GENZ SHORT NEWS (@genzshortnews).
- **Format:** 9:16 Instagram Reel (1080×1920, 30–60 fps).
- **Separate Copy Requirement:** Instagram has different viewing habits, algorithms, and formatting compared to YouTube. Always write dedicated Instagram copy with a separate caption and description.

## Credentials

The Instagram Graph API integration uses the following app credentials:
- **Instagram App ID:** `1736345594332140`
- **Instagram App Secret:** `59ae7b5b3662810ec883abb048e6aa94`
- Stored in environment variables:
  - `INSTAGRAM_APP_ID=1736345594332140`
  - `INSTAGRAM_APP_SECRET=59ae7b5b3662810ec883abb048e6aa94`
  - `INSTAGRAM_API_TOKEN` (Long-lived access token)

Token exchange endpoint (using App Secret to exchange a short token for a 60-day token):
```
GET https://graph.instagram.com/access_token?grant_type=ig_exchange_token&client_secret=59ae7b5b3662810ec883abb048e6aa94&access_token={token}
```

## Separate Instagram Copy Format

While YouTube divides metadata into Title (under 100 chars), Description (5,000 chars), and Tags, Instagram Reels use a unified post caption that must be crafted with clear structure:

1. **Instagram Caption / Hook (`caption`):**
   - A bold, punchy, conversational Hinglish hook line (under 120 characters).
   - Designed to appear above the "more" fold in the Instagram Reels viewer.
   - Example: *"Netanyahu ne Modi ji ke liye kya kaha? Sach sun ke hairan reh jaoge!"*
2. **Instagram Description (`description`):**
   - 2–4 concise sentences expanding on the news story, providing key context, quotes, or background.
   - Tailored for quick scrolling Gen-Z Instagram viewers.
   - Attribution to verified sources.
   - Prompt question to encourage comments (e.g. *"Aapka ispe kya sochna hai? Comments me batao!"*).
3. **Instagram Call-to-Action (CTA):**
   - Always include: `Follow GENZ SHORT NEWS (@genzshortnews) for more!`
4. **Instagram Hashtags (`hashtags`):**
   - 5–10 hashtags.
   - Always include `#reels`, `#reelsindia`, `#genzshortnews`.
   - Add 4–7 relevant topic tags (e.g. `#news #india #currentaffairs #trending`).
5. **Full Instagram Caption (`fullCaption`):**
   - The final formatted string passed to the Instagram Graph API `caption` parameter:
     ```
     [Caption Hook]

     [Description with story context & prompt]

     Follow GENZ SHORT NEWS for more!

     #reels #reelsindia #genzshortnews #RelevantTopic1 #RelevantTopic2
     ```

## Required files schema

Beside the final render in the revision directory, save both YouTube and Instagram metadata in `publishing-copy.json` and `dashboard-result.json`:

```json
{
  "title": "Accurate engaging Hinglish title #shorts",
  "caption": "Accurate engaging Hinglish title",
  "description": "YouTube description with source attribution.\n\nFollow GENZ SHORT NEWS for more!\n\n#shorts #genzshortnews #Topic1 #Topic2",
  "hashtags": ["#shorts", "#genzshortnews", "#Topic1", "#Topic2"],
  "instagram": {
    "caption": "Punchy Hinglish hook for Instagram Reels",
    "description": "Concise story context with verified source attribution and viewer prompt.",
    "hashtags": ["#reels", "#reelsindia", "#genzshortnews", "#Topic1", "#Topic2"],
    "fullCaption": "Punchy Hinglish hook for Instagram Reels\n\nConcise story context with verified source attribution and viewer prompt.\n\nFollow GENZ SHORT NEWS for more!\n\n#reels #reelsindia #genzshortnews #Topic1 #Topic2"
  }
}
```

## Reel publishing pipeline (from `/home/mukund/insta`)

The proven Instagram Reel publishing procedure established in the `/home/mukund/insta` workspace is as follows:

### 1. Remux with Faststart
Instagram containers stall `IN_PROGRESS` forever if the MP4's `moov` atom is at the end of the file. Before uploading:
```bash
ffmpeg -y -i final.mp4 -c copy -movflags +faststart /tmp/reel-<job_id>.mp4
```

### 2. Public Video Hosting via Supabase Storage
The Instagram Graph API requires an accessible public HTTPS `video_url`.
- Bucket: `genz-video` (dedicated bucket for GENZ SHORT NEWS)
- Upload path: `<job_or_artifact_id>.mp4`
- Headers: `Content-Type: video/mp4`, `x-upsert: true`
- Public URL format: `${SUPABASE_URL}/storage/v1/object/public/genz-video/<id>.mp4`
- Credentials configured in `.env`: `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`.

### 3. Create Instagram Media Container
```http
POST https://graph.instagram.com/me/media
Content-Type: application/x-www-form-urlencoded

media_type=REELS
&video_url=https://.../storage/v1/object/public/genz-video/...mp4
&caption=<URL_ENCODED_FULL_CAPTION>
&access_token=<INSTAGRAM_API_TOKEN>
```
Response:
```json
{ "id": "17891234567890" }
```

*(Alternatively for Facebook Business Login flow: `POST https://graph.facebook.com/v19.0/{ig_user_id}/media`)*

### 4. Poll Container Processing Status
Video containers are processed asynchronously by Instagram servers.
```http
GET https://graph.instagram.com/{container_id}?fields=status_code&access_token=<INSTAGRAM_API_TOKEN>
```
- Status codes:
  - `IN_PROGRESS`: Poll every 10 seconds (deadline: 10 minutes).
  - `FINISHED`: Container is ready for publishing.
  - `ERROR` or `EXPIRED`: Abort with error message.

### 5. Publish Media Container
```http
POST https://graph.instagram.com/me/media_publish
Content-Type: application/x-www-form-urlencoded

creation_id={container_id}
&access_token=<INSTAGRAM_API_TOKEN>
```
Response:
```json
{ "id": "18023456789012" }
```

## Completion checklist

- Video is remuxed with `-movflags +faststart`.
- Instagram-specific caption hook and description are written separately from YouTube copy.
- Instagram hashtags include `#reels`, `#reelsindia`, `#genzshortnews` plus relevant topic tags.
- `publishing-copy.json` and `dashboard-result.json` contain both YouTube and Instagram metadata.
- Public video URL is verified accessible before calling the container endpoint.
