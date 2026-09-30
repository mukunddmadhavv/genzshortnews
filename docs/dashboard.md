# GENZ Production Studio

## Start

```sh
npm install
npm run build
npm run db:migrate
npm start
```

Open http://localhost:6969. Run `npm run access` locally to display the studio
password. Authentication protects generation, media and upload endpoints.
The password and signing key live in `.secrets/dashboard-access.json` (0600).

The current machine uses PostgreSQL 17 on loopback port 55432, database
`genz_studio`. To restart it:

```sh
/opt/homebrew/opt/postgresql@17/bin/pg_ctl \
  -D /opt/homebrew/var/postgresql@17 \
  -l /tmp/genz-postgres.log -o '-p 55432 -h 127.0.0.1' start
```

Alternatively use `compose.yaml` with Docker and set `POSTGRES_PASSWORD`. Put the
matching `DATABASE_URL` in `.env.dashboard`. See `.env.dashboard.example` for
all settings. Existing ElevenLabs settings remain in `.env`.

## Workflow

For automatic NeonManShorts discovery and public publishing, see
[channel automation](source-watch.md). The **Channels** page at `/channel` shows
fetched counts, source history, health and controls for adding or pausing channels.

1. **New session:** supply a topic or YouTube video/Short URL. Select automatic
   upload if wanted, otherwise the video stops at Ready for review.
2. The PostgreSQL queue runs one resource-heavy job at a time. An OpenCode CLI
   process reads the current `indian-news-shorts` skill and executes its actual
   research, ASR, script, image sourcing, narration, alignment, gameplay and FFmpeg
   pipeline. It uses your configured OpenCode provider/model and ElevenLabs account.
3. The CLI emits its session ID; the worker saves it immediately in PostgreSQL.
   Progress stages and tool/text events appear in the session activity feed.
4. Each generation writes `data/sessions/<session UUID>/<job UUID>/`. The worker
   requires `dashboard-result.json` and a real `final.mp4`, verifies 1080×1920 plus
   audio, performs a full FFmpeg decode, and indexes the revision's artifacts.
5. **Resume:** send editing instructions. The worker invokes OpenCode with the
   saved `--session` ID and a new revision directory. Previous renders remain.
6. **Post to YouTube:** click once on a revision. The dashboard uses its generated
   caption/title, description and relevant hashtags, always including `#shorts`
   and `#genzshortnews`. Copy is produced and displayed during generation, before
   a revision becomes Ready. New imports queue a separate copy-preparation job.
   Older imports without copy show Prepare copy; publication stays disabled until
   that finishes. The publishing job never invokes the generation model.
   The default is a public upload marked not made for kids. **Edit publishing
   options** remains available for optional title, description or visibility edits.
   The uploader refreshes OAuth credentials and verifies the actual authenticated
   channel handle is `@genzshotnews` before uploading. Actual returned visibility
   is stored because YouTube may enforce private uploads on unaudited projects.
   The upload API has no comment-enable field. In YouTube Studio, configure
   **Settings → Upload defaults → Advanced settings → Comments** to enable
   comments, and verify the setting on API-uploaded videos. Marking a video not
   made for kids avoids that specific automatic comment restriction; YouTube can
   still restrict comments independently.
7. Upload checkpoints in `.secrets/uploads/` preserve YouTube's resumable session
   URL. Retry reconciles uploaded bytes/completion; it does not blindly insert a
   second video. An expired upload session requires checking YouTube Studio before
   starting again.

**Media library** imports existing `episodes/*/final*.mp4` into new sessions.
Repeated imports (including concurrent clicks) return the existing session. The
library shows **Open session** for imported files. Older untouched duplicate
imports are hidden from the session list, with their files and records retained;
sessions with edits, jobs or publishing history are preserved visibly.
The original episode and its sources remain available to the editing agent.
For imported videos, select **Find original session** and link the OpenCode
conversation that actually created the video before editing. The dashboard never
silently starts a replacement conversation for an unlinked imported video.
Every revision uses the same `--session` ID; a new output directory is only file
versioning. An unexpected session-ID change fails instead of replacing the link.

## Recovery

- Jobs and history persist in PostgreSQL. Closing the browser does not stop work.
- Pause stops the process group. A subsequent Resume continues the saved session.
- A server restart marks in-flight work interrupted/paused. Resume generation or
  retry its publication explicitly. Queued jobs resume automatically.
- Only one worker can acquire the PostgreSQL advisory lock.
- Generation has a 90-minute timeout. Missing provider authorization, downloads,
  permissions or render output become visible failures, not fake completed videos.
- New CLI runs use `--auto` to execute the requested pipeline unattended. Run this
  private studio only for trusted operators: the generation agent can execute local
  tools using your existing OpenCode credentials. The prompt forbids credential
  disclosure, changing dashboard files and publishing outside the uploader.
- Activity stores tool names/status, not raw tool arguments or outputs. Agent text
  is length-limited and redacted for common token patterns; never ask it to print secrets.

## Cloudflare Tunnel

Set `DASHBOARD_ORIGIN=https://u.trypitch.co` in `.env.dashboard`, rebuild if you
changed frontend code, restart the server, and route that hostname to
`http://localhost:6969`. The origin enables secure cookies and same-origin checks.
The hostname currently serves another application; change its route deliberately.
The YouTube refresh token works from either local or hosted backend, with no new
OAuth consent needed merely for moving the dashboard hostname.

## Storage and backup

PostgreSQL stores sessions, jobs, events, media metadata and publications. Actual
video/image/audio/document bytes are local files, not PostgreSQL blobs. Back up
the `genz_studio` database, `data/`, `episodes/`, `.secrets/` and the OpenCode local
session store together. Credentials are never returned by the dashboard API.

## Tests

```sh
npm test
.venv/bin/python -m unittest discover -s scripts -p 'test_youtube*.py'
```

The integration test creates and drops an isolated PostgreSQL test database,
uses a deterministic engine fixture and an actual short MP4, and checks auth,
session creation/resume, byte-range video playback, duplicate upload protection,
publication bookkeeping and cancellation. It does not upload a real video or
spend ElevenLabs credits. Real generation uses the existing external providers and
may still encounter source availability or provider errors reported in Activity.
