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
