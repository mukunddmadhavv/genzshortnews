CREATE TABLE IF NOT EXISTS sessions (
 id uuid PRIMARY KEY, title text NOT NULL, input text NOT NULL, source_type text NOT NULL,
 status text NOT NULL DEFAULT 'queued', opencode_session_id text,
 auto_publish boolean NOT NULL DEFAULT false, privacy text NOT NULL DEFAULT 'private',
 created_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS jobs (
 id uuid PRIMARY KEY, session_id uuid NOT NULL REFERENCES sessions(id), kind text NOT NULL,
 status text NOT NULL DEFAULT 'queued', input jsonb NOT NULL DEFAULT '{}', error text,
 created_at timestamptz NOT NULL DEFAULT now(), started_at timestamptz, finished_at timestamptz
);
CREATE UNIQUE INDEX IF NOT EXISTS one_active_job_per_session ON jobs(session_id) WHERE status IN ('queued','running');
CREATE TABLE IF NOT EXISTS events (
 id bigserial PRIMARY KEY, session_id uuid NOT NULL REFERENCES sessions(id), job_id uuid REFERENCES jobs(id),
 kind text NOT NULL, message text NOT NULL, created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS events_session ON events(session_id,id);
CREATE TABLE IF NOT EXISTS artifacts (
 id uuid PRIMARY KEY, session_id uuid NOT NULL REFERENCES sessions(id), job_id uuid REFERENCES jobs(id),
 name text NOT NULL, path text NOT NULL, mime text NOT NULL, size_bytes bigint NOT NULL,
 kind text NOT NULL, metadata jsonb NOT NULL DEFAULT '{}', created_at timestamptz NOT NULL DEFAULT now(),
 UNIQUE(session_id,path)
);
CREATE TABLE IF NOT EXISTS publications (
 id uuid PRIMARY KEY, session_id uuid NOT NULL REFERENCES sessions(id), artifact_id uuid NOT NULL REFERENCES artifacts(id),
 job_id uuid NOT NULL REFERENCES jobs(id), status text NOT NULL DEFAULT 'queued', title text NOT NULL,
 description text NOT NULL DEFAULT '', privacy text NOT NULL, made_for_kids boolean NOT NULL DEFAULT false,
 youtube_id text, channel_id text, error text, created_at timestamptz NOT NULL DEFAULT now(),
 updated_at timestamptz NOT NULL DEFAULT now(), UNIQUE(artifact_id)
);
CREATE TABLE IF NOT EXISTS episode_imports (
 source_path text PRIMARY KEY,
 session_id uuid NOT NULL REFERENCES sessions(id),
 created_at timestamptz NOT NULL DEFAULT now()
);
-- Existing imports already recorded their exact source in an event. Retain the
-- earliest session as the canonical import without deleting anyone's revisions.
INSERT INTO episode_imports(source_path,session_id)
SELECT DISTINCT ON (message) 'episodes/' || substring(message FROM 10), session_id
FROM events WHERE kind='imported' AND message LIKE 'Imported %/%.mp4'
ORDER BY message,created_at,id
ON CONFLICT(source_path) DO NOTHING;
ALTER TABLE sessions ADD COLUMN IF NOT EXISTS duplicate_of uuid REFERENCES sessions(id);
-- Prefer a session with publishing/edit history over an unused duplicate.
WITH candidates AS (
 SELECT DISTINCT ON (e.message) 'episodes/' || substring(e.message FROM 10) AS source_path,e.session_id
 FROM events e JOIN sessions s ON s.id=e.session_id
 WHERE e.kind='imported' AND e.message LIKE 'Imported %/%.mp4'
 ORDER BY e.message,
 EXISTS(SELECT 1 FROM publications p WHERE p.session_id=s.id) DESC,
 EXISTS(SELECT 1 FROM jobs j WHERE j.session_id=s.id) DESC,e.created_at,e.id
)
UPDATE episode_imports i SET session_id=c.session_id FROM candidates c WHERE c.source_path=i.source_path;
-- Hide only redundant, untouched imports; retain all files and records.
UPDATE sessions s SET duplicate_of=i.session_id
FROM events e JOIN episode_imports i ON i.source_path='episodes/' || substring(e.message FROM 10)
WHERE s.id=e.session_id AND e.kind='imported' AND s.source_type='import'
 AND s.id<>i.session_id AND s.opencode_session_id IS NULL
 AND NOT EXISTS(SELECT 1 FROM jobs j WHERE j.session_id=s.id)
 AND NOT EXISTS(SELECT 1 FROM publications p WHERE p.session_id=s.id);
UPDATE sessions SET duplicate_of=NULL WHERE id IN(SELECT session_id FROM episode_imports);

CREATE TABLE IF NOT EXISTS source_watches (
 channel_id text PRIMARY KEY, enabled boolean NOT NULL DEFAULT false,
 started_at timestamptz, callback_token text NOT NULL, hub_secret text NOT NULL,
 last_poll_at timestamptz, last_webhook_at timestamptz, lease_expires_at timestamptz,
 next_subscribe_at timestamptz, last_error text
);
CREATE TABLE IF NOT EXISTS source_videos (
 channel_id text NOT NULL REFERENCES source_watches(channel_id) ON DELETE CASCADE, video_id text NOT NULL,
 session_id uuid NOT NULL UNIQUE REFERENCES sessions(id), published_at timestamptz NOT NULL,
 created_at timestamptz NOT NULL DEFAULT now(), PRIMARY KEY(channel_id,video_id)
);
ALTER TABLE source_watches ADD COLUMN IF NOT EXISTS title text NOT NULL DEFAULT 'YouTube channel';
ALTER TABLE source_watches ADD COLUMN IF NOT EXISTS channel_url text;
ALTER TABLE source_watches ADD COLUMN IF NOT EXISTS created_at timestamptz NOT NULL DEFAULT now();
UPDATE source_watches SET title='Neon Man Shorts',channel_url='https://www.youtube.com/@NeonManShorts/shorts'
WHERE channel_id='UCg48OIfYWyNrUAIM2CLeWLg' AND channel_url IS NULL;
CREATE UNIQUE INDEX IF NOT EXISTS source_watch_callback ON source_watches(callback_token);
CREATE TABLE IF NOT EXISTS system_flags (
 key text PRIMARY KEY,
 value text NOT NULL
);
INSERT INTO system_flags(key, value)
SELECT 'source_watch_initialized', 'true'
WHERE EXISTS (SELECT 1 FROM source_watches)
ON CONFLICT (key) DO NOTHING;
DO $$ BEGIN
 IF EXISTS (
  SELECT 1 FROM information_schema.table_constraints
  WHERE constraint_name = 'source_videos_channel_id_fkey'
 ) AND NOT EXISTS (
  SELECT 1 FROM information_schema.referential_constraints
  WHERE constraint_name = 'source_videos_channel_id_fkey' AND delete_rule = 'CASCADE'
 ) THEN
  ALTER TABLE source_videos DROP CONSTRAINT source_videos_channel_id_fkey;
  ALTER TABLE source_videos ADD CONSTRAINT source_videos_channel_id_fkey FOREIGN KEY (channel_id) REFERENCES source_watches(channel_id) ON DELETE CASCADE;
 END IF;
END $$;

ALTER TABLE source_watches ADD COLUMN IF NOT EXISTS last_verified_at timestamptz;
ALTER TABLE source_watches ADD COLUMN IF NOT EXISTS last_probe_at timestamptz;
ALTER TABLE source_watches ADD COLUMN IF NOT EXISTS webhook_count integer NOT NULL DEFAULT 0;
ALTER TABLE source_watches ADD COLUMN IF NOT EXISTS rejected_webhook_count integer NOT NULL DEFAULT 0;
ALTER TABLE source_watches ADD COLUMN IF NOT EXISTS last_webhook_error text;
ALTER TABLE source_watches ADD COLUMN IF NOT EXISTS subscription_error text;
ALTER TABLE source_videos ADD COLUMN IF NOT EXISTS capture_source text
 CHECK (capture_source IN ('webhook','polling'));
-- Only infer older polling captures when no webhook had arrived by capture time.
-- Other historical rows remain NULL (shown as Unknown), rather than guessing.
UPDATE source_videos v SET capture_source='polling' FROM source_watches w
WHERE v.channel_id=w.channel_id AND v.capture_source IS NULL
 AND w.last_webhook_at IS NULL;

-- Multi-platform publishing (YouTube Shorts, Instagram Reels, or Both)
ALTER TABLE sessions ADD COLUMN IF NOT EXISTS publish_target text NOT NULL DEFAULT 'both';
ALTER TABLE publications ADD COLUMN IF NOT EXISTS platform text NOT NULL DEFAULT 'both';
ALTER TABLE publications ADD COLUMN IF NOT EXISTS instagram_media_id text;
ALTER TABLE publications ADD COLUMN IF NOT EXISTS instagram_url text;
ALTER TABLE publications ADD COLUMN IF NOT EXISTS instagram_caption text;
