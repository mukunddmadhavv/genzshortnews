# Source channels → OpenCode → public YouTube Shorts

Source: https://www.youtube.com/@NeonManShorts/shorts
Channel ID: `UCg48OIfYWyNrUAIM2CLeWLg`

Open **[/channel](https://u.trypitch.co/channel)** or choose **Channels** in the navigation.
The page shows all-time fetched Shorts, last-24-hour counts, in-production and published
totals, per-channel counts and health, and the latest 100 source/session/output links.
Counts represent unique Shorts accepted into the pipeline since activation, not the
channel's total upload count. Publication counts include uploads with any actual visibility.

Add channels using a YouTube `/@handle` URL, `/channel/UC…` URL, plain @handle, or
UC channel ID. The server resolves and verifies the channel feed before enabling it.
Every channel has its own webhook token, signing secret, subscription lease, activation
time and duplicate ledger. Adding an existing channel preserves its existing state.
All sources use the same current skill, fresh OpenCode session and public-upload flow.

Enable or pause each channel on this page. The first enable
stores an activation timestamp: earlier uploads never generate jobs. Re-enabling
preserves that timestamp and catches up on unseen entries still in YouTube's feed.

## How it runs

- The existing `genz-studio` service owns the watcher; no separate OpenCode daemon
  or process on your Mac is required.
- WebSub subscription verifies through `GET /webhooks/youtube/<private token>`.
  Signed POST notifications wake a fresh fetch of the canonical channel feed.
  Notification bodies never become agent prompts or generation jobs.
- The feed is also checked every **300 seconds (5 minutes)**, including after service restart.
  Failed requests retry automatically. Subscription leases renew automatically.
- Only canonical `/shorts/<video ID>` entries are admitted. Titles containing
  `#shorts` or short duration alone are not treated as evidence.
- A PostgreSQL transaction locks the channel watcher and records each source video
  ID with its session. Repeated notifications, title edits and overlapping polls
  reuse the ledger instead of starting another session.
- Each new session contains the source URL, `auto_publish=true`, `privacy=public`,
  and no previous OpenCode session ID. The existing worker starts `opencode run
  --auto` in this workspace, follows the current `indian-news-shorts` skill and
  records the actual new OpenCode session ID.
- Existing rendering checks and saved publishing copy precede the existing
  channel-verified uploader. YouTube's **actual returned visibility** appears in
  publication history; a requested public upload can still be restricted by YouTube.

## Operations

The authenticated endpoints are `GET /api/source-watch` for status and recent
source/session/output links, and `POST /api/source-watch` with `{"enabled":true}`
or `{"enabled":false}`. Status never returns the webhook token or HMAC secret.

Multi-channel APIs: `GET /api/channels` returns the dashboard, `POST /api/channels`
with `{"url":"@ChannelHandle"}` adds a verified channel, and `PATCH /api/channels/:id`
with `{"enabled":false}` pauses it (use `true` to resume). The older `/api/source-watch`
endpoints remain compatible with the original NeonManShorts control.

On the server, `node scripts/source_watch.mjs status` shows status;
replace `status` with `enable`, `pause`, or `check-youtube` as needed.

The live deployment uses `DASHBOARD_ORIGIN=https://u.trypitch.co`, whose existing
tunnel already reaches the studio. Both `/webhooks/youtube/*` methods must reach
the server without an interactive tunnel login. No YouTube API key is needed for
discovery; publishing uses the existing OAuth credentials.

Pausing stops discovery, not existing jobs. Cancel queued/running jobs on their
session pages if needed. Generation/provider failures remain visible in Activity;
resume that session rather than creating another. Interrupted uploads use the
existing checkpoint/retry path. Jobs are not blindly regenerated or re-uploaded.

The YouTube feed retains only recent entries (currently 15). The five-minute backup
handles short webhook outages; a prolonged outage covering more uploads than the
feed retains requires manual recovery of the missed URLs.

Back up `source_watches` and `source_videos` together with the existing database.
Restart `genz-studio` after deploying server code; no OpenCode configuration change
is needed. New sessions already load `.skills/` through the existing config.

## Webhook diagnostics

Official YouTube documentation: https://developers.google.com/youtube/v3/guides/push_notifications
Google's hub and protocol: https://pubsubhubbub.appspot.com/ and
https://pubsubhubbub.github.io/PubSubHubbub/pubsubhubbub-core-0.4.html

Subscription POSTs use `https://pubsubhubbub.appspot.com/`, form encoding, an exact
`https://www.youtube.com/feeds/videos.xml?channel_id=UC…` topic, and the HTTPS
`/webhooks/youtube/<private token>` callback. The channel's /shorts page is not the topic.
Verification (GET challenge) proves reachability, not upload-event delivery.
The dashboard reports verification and received notifications separately.

Run `node scripts/webhook_doctor.mjs status` to inspect Google's per-subscription
delivery diagnostics without exposing secrets. `probe` sends a signed test over
public HTTPS; it records a separate test timestamp and never queues a video or
increments notification counts. `renew` requests fresh Google verification.

Notification receipts are saved before acknowledgement. Pending feed checks survive
restarts. Invalid signatures are ignored and counted, with a 204 acknowledgement as
specified by PubSubHubbub 0.4 §8. Feed fetch and subscription errors are separate.
Polling uses a cache-busting query and revalidation headers; the subscribed topic
never includes that query. This reduces shared-cache staleness but cannot guarantee
YouTube publishes its feed or sends its hub notification immediately.

The Fetched Shorts table includes **Captured by**: Webhook or Polling. This records
the trigger of the feed check that first queued the Short, not every later delivery.
Webhook-triggered checks run immediately and survive restarts. Initial channel
checks are Polling. Duplicates never overwrite the first capture source. Older
rows with no evidence remain Unknown; channels with no webhook history can have
their older captures identified as Polling.
