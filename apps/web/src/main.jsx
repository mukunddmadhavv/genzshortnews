import React, { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  Plus,
  ArrowUpRight,
  Play,
  Film,
  Radio,
  Settings,
  FolderOpen,
  ChevronRight,
  ArrowLeft,
  Send,
  Download,
  Check,
  RefreshCw,
  Pause,
  LogOut,
  Clapperboard,
  Youtube,
  Link,
  FileText,
  LoaderCircle,
  Layers,
  Search,
  X,
  Clock,
} from "lucide-react";
import "./style.css";
import "./light-theme.css";
import "./mobile.css";
import { Channels } from "./channels.jsx";
import { Sessions } from "./sessions.jsx";

async function api(url, body, method) {
  const response = await fetch(`/api${url}`, {
    method: method || (body ? "POST" : "GET"),
    headers: body ? { "Content-Type": "application/json" } : {},
    body: body ? JSON.stringify(body) : undefined,
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "Request failed");
  return data;
}
const activeStates = ["queued", "generating", "publishing"];
const ago = (date) => {
  const mins = Math.floor((Date.now() - new Date(date)) / 60000);
  return mins < 1
    ? "Just now"
    : mins < 60
      ? `${mins}m ago`
      : mins < 1440
        ? `${Math.floor(mins / 60)}h ago`
        : new Date(date).toLocaleDateString();
};
const duration = (value) =>
  value
    ? `${Math.floor(value / 60)}:${String(Math.round(value % 60)).padStart(2, "0")}`
    : "—";
const media = (id) => `/api/artifacts/${id}/content`;
function Badge({ status }) {
  return (
    <span className={`badge ${status}`}>
      <i />
      {status}
    </span>
  );
}
function App() {
  const [auth, setAuth] = useState(null),
    [password, setPassword] = useState(""),
    [error, setError] = useState(""),
    [page, updatePage] = useState(() => ["/channel","/channels"].includes(window.location.pathname) ? "channel" : window.location.pathname === "/connections" ? "settings" : "sessions"),
    [sessions, setSessions] = useState([]),
    [detail, setDetail] = useState(null),
    [selected, setSelected] = useState(null),
    [settings, setSettings] = useState(null),
    [modal, setModal] = useState(false),
    [busy, setBusy] = useState(false),
    [search, setSearch] = useState("");
  const fail = (e) => setError(e.message);
  const setPage = (value) => {
    updatePage(value);
    window.history.pushState({}, "", value === "channel" ? "/channel" : value === "settings" ? "/connections" : "/sessions");
  };
  useEffect(() => {
    const pop = () => { updatePage(["/channel","/channels"].includes(window.location.pathname) ? "channel" : window.location.pathname === "/connections" ? "settings" : "sessions"); setSelected(null); };
    window.addEventListener("popstate", pop);
    return () => window.removeEventListener("popstate", pop);
  }, []);
  useEffect(() => {
    api("/auth")
      .then((x) => setAuth(x.authenticated))
      .catch(fail);
  }, []);
  const refresh = async () => {
    const [s, c] = await Promise.all([api("/sessions"), api("/settings")]);
    setSessions(s);
    setSettings(c);
  };
  useEffect(() => {
    if (!auth) return;
    refresh().catch(fail);
    const t = setInterval(() => refresh().catch(() => {}), 4000);
    return () => clearInterval(t);
  }, [auth]);
  useEffect(() => {
    if (!selected) {
      setDetail(null);
      return;
    }
    setDetail(null);
    let live = true;
    const load = () =>
      api(`/sessions/${selected}`)
        .then((x) => {
          if (live) setDetail(x);
        })
        .catch(fail);
    load();
    const t = setInterval(load, 2500);
    return () => {
      live = false;
      clearInterval(t);
    };
  }, [selected]);
  const action = async (fn) => {
    setBusy(true);
    setError("");
    try {
      await fn();
    } catch (e) {
      fail(e);
    } finally {
      setBusy(false);
    }
  };
  if (auth === null)
    return (
      <div className="loading">
        <LoaderCircle className="spin" /> Opening the studio
      </div>
    );
  if (!auth)
    return (
      <main className="login">
        <div className="brand">
          <img src="/branding/profile.png" alt="GENZ SHORT NEWS logo" />
          <div>
            GENZ<span>PRODUCTION STUDIO</span>
          </div>
        </div>
        <h1>
          Your next story
          <br />
          starts here.
        </h1>
        <p>Sign in to your private production workspace.</p>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            action(async () => {
              await api("/login", { password });
              setAuth(true);
            });
          }}
        >
          <label>
            Studio password
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              autoFocus
            />
          </label>
          <button className="primary" disabled={busy}>
            Enter studio <ArrowUpRight size={18} />
          </button>
        </form>
        {error && <p className="error">{error}</p>}
        <small>
          Sign in with your configured studio password.
        </small>
      </main>
    );
  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="brand">
          <img src="/branding/profile.png" alt="GENZ SHORT NEWS logo" />
          <div>
            GENZ<span>PRODUCTION STUDIO</span>
          </div>
        </div>
        <div className="workspace">
          <img className="channel-logo" src="/branding/profile.png" alt="Your channel" />
          <div>
            GENZ SHORT NEWS<small>Your channel · @genzshotnews</small>
          </div>
          <ChevronRight size={14} />
        </div>
        <p className="nav-label">WORKSPACE</p>
        <nav>
          {[
            ["sessions", Layers, "Sessions"],
            ["channel", Radio, "Channels"],
            ["settings", Settings, "Connections"],
          ].map(([id, Icon, label]) => (
            <button
              key={id}
              aria-label={label}
              aria-current={page === id ? "page" : undefined}
              className={page === id ? "active" : ""}
              onClick={() => {
                setPage(id);
                setSelected(null);
              }}
            >
              <Icon size={18} />
              {label}
              {id === "sessions" && <em>{sessions.length}</em>}
            </button>
          ))}
        </nav>
        <div className="pipeline-note">
          <Radio size={19} />
          <h4>Your pipeline. Automated.</h4>
          <p>Research to render, powered by your custom news skills.</p>
          <span>FFmpeg + ElevenLabs</span>
        </div>
        <div className="sidebar-bottom">
          <div className="avatar red">
            <Youtube size={19} />
          </div>
          <div>
            @genzshotnews
            <small>
              {settings?.tokenPresent
                ? "Credentials configured"
                : "Connect YouTube"}
            </small>
          </div>
          <button
            aria-label="Sign out"
            className="icon"
            onClick={() =>
              action(async () => {
                await api("/logout", {});
                setAuth(false);
              })
            }
          >
            <LogOut size={16} />
          </button>
        </div>
      </aside>
      <div className="main">
        <header>
          <div>
            Workspace <ChevronRight size={13} />{" "}
            <strong>
              {selected
                ? "Session"
                : page === "sessions"
                  ? "Sessions"
                  : page === "library"
                    ? "Media library"
                    : page === "channel" ? "Channels" : "Connections"}
            </strong>
          </div>
          <div className="server-status">
            <i />
            Local studio <span>•</span> @genzshotnews
          </div>
          <button className="icon mobile-signout" aria-label="Sign out on mobile" onClick={()=>action(async()=>{await api('/logout',{});setAuth(false);})}><LogOut size={19}/></button>
        </header>
        {error && (
          <div className="error toast">
            {error}
            <button className="icon" onClick={() => setError("")}>
              <X size={16} />
            </button>
          </div>
        )}
        <main className="content">
          {selected ? (
            detail ? (
              <Session
                key={selected}
                session={detail}
                action={action}
                busy={busy}
                back={() => setSelected(null)}
                refresh={async () =>
                  setDetail(await api(`/sessions/${selected}`))
                }
              />
            ) : (
              <div className="loading">
                <LoaderCircle className="spin" /> Loading session
              </div>
            )
           ) : page === "sessions" || page === "library" ? (
             <Sessions sessions={sessions} api={api} create={()=>setModal(true)} refresh={refresh}
               renderSession={(session,reload,close)=><Session key={session.id} session={session} action={action} busy={busy} back={close} refresh={reload}/>} />
           ) : page === "legacy-sessions" ? (
            <>
              <div className="channel-banner"><img src="/branding/banner.png" alt="GENZ SHORT NEWS — Big stories. Short takes." /></div>
              <div className="page-heading">
                <div>
                  <p className="eyebrow">GENZ SHORT NEWS STUDIO</p>
                  <h1>
                    Stories in the making<span>.</span>
                  </h1>
                  <p>One topic. One link. Your next great Short.</p>
                </div>
                <button className="primary" onClick={() => setModal(true)}>
                  <Plus size={18} />
                  New session
                </button>
              </div>
              <section className="stats">
                {[
                  ["Total sessions", sessions.length, Layers],
                  [
                    "In production",
                    sessions.filter((s) => activeStates.includes(s.status))
                      .length,
                    Radio,
                  ],
                  [
                    "Ready to review",
                    sessions.filter((s) => s.status === "ready").length,
                    Film,
                  ],
                  [
                    "Published",
                    sessions.filter((s) => s.youtube_id).length,
                    Youtube,
                  ],
                ].map(([label, value, Icon]) => (
                  <div key={label}>
                    <span>
                      {label}
                      <Icon size={18} />
                    </span>
                    <strong>{value.toString().padStart(2, "0")}</strong>
                  </div>
                ))}
              </section>
              <section className="create-banner">
                <div className="banner-icon">
                  <Clapperboard size={32} />
                </div>
                <div>
                  <h3>From an idea to a finished Short.</h3>
                  <p>
                    Drop a YouTube link or a topic. Your skills take it from
                    there.
                  </p>
                </div>
                <button onClick={() => setModal(true)}>
                  Let’s create <ArrowUpRight size={17} />
                </button>
              </section>
              <div className="section-heading">
                <h2>
                  All sessions <span>{sessions.length}</span>
                </h2>
                <div className="search">
                  <Search size={16} />
                  <input
                    placeholder="Search your stories…"
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                  />
                </div>
              </div>
              {sessions.length === 0 ? (
                <div className="empty">
                  <div className="empty-icon">
                    <Film size={32} />
                  </div>
                  <h3>A fresh slate for your next big story</h3>
                  <p>
                    Create your first session or bring in an existing video.
                    <br />
                    Every script, revision, and render stays together.
                  </p>
                  <button className="primary" onClick={() => setModal(true)}>
                    <Plus size={17} />
                    Create first session
                  </button>
                  <button
                    className="text-button"
                    onClick={() => setPage("library")}
                  >
                    Import an existing episode <ArrowUpRight size={14} />
                  </button>
                </div>
              ) : (
                <div className="session-grid">
                  {sessions
                    .filter((s) =>
                      (s.title + " " + s.input)
                        .toLowerCase()
                        .includes(search.toLowerCase()),
                    )
                    .map((s) => (
                      <button
                        className="session-card"
                        key={s.id}
                        onClick={() => setSelected(s.id)}
                      >
                        <div className="card-visual">
                          <span className="visual-lines" />
                          <span className="card-type">
                            {s.source_type === "youtube" ? (
                              <Youtube size={16} />
                            ) : (
                              <FileText size={16} />
                            )}{" "}
                            {s.source_type === "youtube"
                              ? "FROM YOUTUBE"
                              : s.source_type === "import"
                                ? "IMPORTED EPISODE"
                                : "ORIGINAL STORY"}
                          </span>
                          <strong>{s.title}</strong>
                          <span className="play-circle">
                            <ArrowUpRight size={24} />
                          </span>
                        </div>
                        <div className="card-body">
                          <Badge status={s.status} />
                          <h3>{s.title}</h3>
                          <p>{s.input}</p>
                          <footer>
                            <span>
                              {s.revisions}{" "}
                              {s.revisions === 1 ? "revision" : "revisions"}
                            </span>
                            <span>{ago(s.updated_at)}</span>
                          </footer>
                        </div>
                      </button>
                    ))}
                </div>
              )}
              <div className="bottom-note">
                <i /> Your work is saved automatically. Pick up where you left
                off, anytime.
              </div>
            </>
           ) : page === "channel" ? (
             <Channels api={api} open={id => setSelected(id)} />
           ) : page === "library" ? (
            <Library
              action={action}
              open={(id) => {
                setSelected(id);
                setPage("sessions");
              }}
            />
          ) : (
            <Connections settings={settings} action={action} />
          )}
        </main>
      </div>
      {modal && (
        <NewSession
          busy={busy}
          close={() => setModal(false)}
          create={(input) =>
            action(async () => {
              const result = await api("/sessions", input);
              await refresh();
              setModal(false);
              setSelected(result.id);
              setPage("sessions");
            })
          }
        />
      )}
    </div>
  );
}
function NewSession({ close, create, busy }) {
  const [title, setTitle] = useState(""),
    [input, setInput] = useState(""),
    [autoPublish, setAuto] = useState(false),
    [privacy, setPrivacy] = useState("private");
  return (
    <div className="overlay" onClick={close}>
      <form
        className="modal"
        onClick={(e) => e.stopPropagation()}
        onSubmit={(e) => {
          e.preventDefault();
          create({ title, input, autoPublish, privacy });
        }}
      >
        <div className="modal-heading">
          <div className="eyebrow">LET’S MAKE SOMETHING</div>
          <button type="button" className="icon" onClick={close}>
            <X />
          </button>
        </div>
        <h2>Start a new story.</h2>
        <p>
          Your custom skills handle research, narration, visuals, and rendering.
        </p>
        <label>
          Session name
          <input
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
            maxLength={120}
            placeholder="Give your story a name"
          />
        </label>
        <label>
          Topic or YouTube link
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            required
            minLength={5}
            maxLength={10000}
            rows={5}
            placeholder="Paste a YouTube video / Short URL, or describe the story you want to tell…"
          />
        </label>
        <div className="format-chips">
          <span>9:16 vertical</span>
          <span>Hinglish</span>
          <span>35–55 seconds</span>
          <span>Approved voice</span>
        </div>
        <label className="check-label">
          <input
            type="checkbox"
            checked={autoPublish}
            onChange={(e) => setAuto(e.target.checked)}
          />
          Automatically upload after a successful render
        </label>
        {autoPublish && (
          <label>
            YouTube visibility
            <select
              value={privacy}
              onChange={(e) => setPrivacy(e.target.value)}
            >
              <option value="private">Private</option>
              <option value="unlisted">Unlisted</option>
              <option value="public">Public</option>
            </select>
          </label>
        )}
        <div className="modal-footer">
          <span>Uses your configured model & ElevenLabs account.</span>
          <button className="primary" disabled={busy}>
            {busy ? (
              <LoaderCircle className="spin" size={17} />
            ) : (
              <Plus size={17} />
            )}
            Create session
          </button>
        </div>
      </form>
    </div>
  );
}
function Session({ session: s, back, action, busy, refresh }) {
  const finals = s.artifacts.filter((a) => a.kind === "final");
  const [selected, setSelected] = useState(null),
    [instructions, setInstructions] = useState(""),
    [tab, setTab] = useState("activity"),
    [publish, setPublish] = useState(false),
    [document, setDocument] = useState(null);
  const current = finals.find((a) => a.id === selected) || finals[0];
  const active = s.jobs.find((j) => ["queued", "running"].includes(j.status));
  const needsOriginal=s.source_type==='import'&&!s.opencode_session_id;
  const [conversations,setConversations]=useState(null),[original,setOriginal]=useState('');
  const publication =
    current && s.publications.find((p) => p.artifact_id === current.id);
  return (
    <>
      <button className="text-button back" onClick={back}>
        <ArrowLeft size={16} />
        All sessions
      </button>
      <div className="page-heading detail-heading">
        <div>
          <div className="eyebrow">
            {s.source_type === "youtube"
              ? "YOUTUBE REFERENCE"
              : "PRODUCTION SESSION"}{" "}
            <Badge status={s.status} />
          </div>
          <h1>{s.title}</h1>
          <p className="session-id">
            {s.opencode_session_id
              ? `OpenCode · ${s.opencode_session_id}`
              : needsOriginal ? "Original OpenCode session not linked" : "OpenCode session ID is saved when generation starts"}
          </p>
        </div>
        {active && (
          <button
            className="secondary"
            disabled={busy}
            onClick={() =>
              action(async () => {
                await api(`/jobs/${active.id}/cancel`, {});
                await refresh();
              })
            }
          >
            <Pause size={16} />
            Pause job
          </button>
        )}
      </div>
      {needsOriginal&&<section className="publishing-copy"><h2>Resume the conversation that created this video</h2><p>This video was imported. Link its original OpenCode conversation once; every edit will continue that same session.</p>{conversations===null?<button className="secondary" disabled={busy||!!active} onClick={()=>action(async()=>setConversations(await api('/opencode/sessions')))}>Find original session</button>:<div><label>Original OpenCode conversation<select style={{width:'100%'}} value={original} onChange={e=>setOriginal(e.target.value)}><option value="">Select the conversation that made this video</option>{conversations.map(c=><option value={c.id} key={c.id}>{c.title} · {c.id}</option>)}</select></label><button className="primary" disabled={!original||busy||!!active} onClick={()=>action(async()=>{await api(`/sessions/${s.id}/link-opencode`,{sessionId:original});await refresh();})}>Link original session</button></div>}</section>}
      <div className="detail-layout">
        <section className="preview-panel">
          <div className="panel-heading">
            <h2>Preview</h2>
            {finals.length > 0 && (
              <select
                value={current?.id}
                onChange={(e) => setSelected(e.target.value)}
              >
                {finals.map((a, i) => (
                  <option key={a.id} value={a.id}>
                    Revision {finals.length - i} ·{" "}
                    {duration(a.metadata.duration)}
                  </option>
                ))}
              </select>
            )}
          </div>
          <div className="video-stage">
            {current ? (
              <video
                key={current.id}
                src={media(current.id)}
                controls
                preload="metadata"
                playsInline
              />
            ) : (
              <div className="render-placeholder">
                {active ? (
                  <LoaderCircle size={36} className="spin" />
                ) : (
                  <Film size={36} />
                )}
                <h3>
                  {active ? "Your story is taking shape" : "No render yet"}
                </h3>
                <p>
                  {active
                    ? "Follow the live activity to see each step."
                    : "Resume this session to finish your video."}
                </p>
              </div>
            )}
          </div>
          {current && (
            <>
              <div className="video-details">
                <span>1080 × 1920</span>
                <span>{duration(current.metadata.duration)}</span>
                <a href={`${media(current.id)}?download=1`}>
                  <Download size={15} /> Download
                </a>
              </div>
              <p className="summary">
                {current.metadata.summary ||
                  "Your rendered episode is ready to preview."}
              </p>
              <button
                className="primary full"
                disabled={busy || !!active || !!publication || !current.metadata.publishingCopyReady}
                onClick={() => action(async () => {
                  await api(`/sessions/${s.id}/publish`, {artifactId:current.id});
                  await refresh();
                })}
              >
                <Youtube size={18} />
                {publication?.status === "published"
                  ? "Uploaded to YouTube"
                  : publication
                    ? "Upload already created"
                    : "Post to YouTube"}
              </button>
              <p className="muted small">One click · public upload to @genzshotnews · caption, description and hashtags included.</p>
              {current.metadata.publishingCopyReady ? <section className="publishing-copy"><h2>YouTube publishing copy</h2><label>Caption / title</label><p>{current.metadata.title}</p><label>Description</label><p className="copy-description">{current.metadata.description}</p><label>Hashtags</label><div className="format-chips">{current.metadata.hashtags?.map(tag=><span key={tag}>{tag}</span>)}</div></section> : <section className="publishing-copy"><h2>Publishing copy pending</h2><p className="muted small">Caption, description and hashtags must be ready before posting. New videos include them during generation.</p><button className="secondary" disabled={busy || !!active} onClick={()=>action(async()=>{await api(`/sessions/${s.id}/prepare-copy`,{artifactId:current.id});await refresh();})}>Prepare copy for this older video</button></section>}
              <p className="muted small">Not made for kids. Comments follow your YouTube channel defaults.</p>
              {!publication && current.metadata.publishingCopyReady && <button className="text-button" disabled={busy || !!active} onClick={()=>setPublish(true)}>Edit publishing options</button>}
              {publication && (
                <div className="publication">
                  <Badge status={publication.status} />
                  {publication.youtube_id ? (
                    <a
                      href={`https://youtu.be/${publication.youtube_id}`}
                      target="_blank"
                      rel="noreferrer"
                    >
                      Open video <ArrowUpRight size={14} />
                    </a>
                  ) : (
                    <span>{publication.error}</span>
                  )}
                  {publication.status === "failed" && (
                    <button
                      onClick={() =>
                        action(async () => {
                          await api(
                            `/publications/${publication.id}/retry`,
                            {},
                          );
                          await refresh();
                        })
                      }
                      disabled={busy || !!active}
                    >
                      Retry upload
                    </button>
                  )}
                </div>
              )}
            </>
          )}
        </section>
        <section className="work-panel">
          <div className="tabs">
            {["activity", "files", "brief"].map((t) => (
              <button
                key={t}
                className={tab === t ? "active" : ""}
                onClick={() => setTab(t)}
              >
                {t === "activity" ? (
                  <Radio size={16} />
                ) : t === "files" ? (
                  <FolderOpen size={16} />
                ) : (
                  <FileText size={16} />
                )}{" "}
                {t}
              </button>
            ))}
          </div>
          <div className="work-body">
            {tab === "activity" ? (
              <div className="timeline">
                {s.events.length === 0 ? (
                  <p className="muted">Waiting for the worker…</p>
                ) : (
                  [...s.events].reverse().map((e) => (
                    <div className={`event ${e.kind}`} key={e.id}>
                      <span className="event-dot" />
                      <div>
                        <header>
                          <strong>{e.kind}</strong>
                          <time>
                            {new Date(e.created_at).toLocaleTimeString([], {
                              hour: "2-digit",
                              minute: "2-digit",
                            })}
                          </time>
                        </header>
                        <p>{e.message}</p>
                      </div>
                    </div>
                  ))
                )}
              </div>
            ) : tab === "files" ? (
              <>
                {s.artifacts.length === 0 ? (
                  <p className="muted">
                    Artifacts appear here when a revision completes.
                  </p>
                ) : (
                  s.artifacts.map((a) => (
                    <div className="file-row" key={a.id}>
                      <FileText size={17} />
                      <button
                        className="file-name"
                        onClick={() =>
                          action(async () => {
                            if (
                              a.mime.startsWith("text/") ||
                              a.mime === "application/json"
                            ) {
                              const r = await fetch(media(a.id));
                              setDocument({
                                name: a.name,
                                text: (await r.text()).slice(0, 60000),
                              });
                            } else
                              window.open(media(a.id), "_blank", "noopener");
                          })
                        }
                      >
                        {a.name}
                        <small>
                          {a.kind} ·{" "}
                          {(Number(a.size_bytes) / 1024 / 1024).toFixed(1)} MB
                        </small>
                      </button>
                      <a
                        href={`${media(a.id)}?download=1`}
                        aria-label={`Download ${a.name}`}
                      >
                        <Download size={15} />
                      </a>
                    </div>
                  ))
                )}
              </>
            ) : (
              <div className="brief">
                <p className="eyebrow">ORIGINAL INPUT</p>
                <p>{s.input}</p>
                <hr />
                <p>Pipeline: indian-news-shorts</p>
                <p>
                  Auto-upload: {s.auto_publish ? `On · ${s.privacy}` : "Off"}
                </p>
                <p className="muted">Session: {s.id}</p>
              </div>
            )}
          </div>
          <form
            className="composer"
            onSubmit={(e) => {
              e.preventDefault();
              action(async () => {
                await api(`/sessions/${s.id}/resume`, { instructions });
                setInstructions("");
                await refresh();
              });
            }}
          >
            <label>
              {finals.length ? "Refine this story" : "Continue the session"}
              <textarea
                rows={3}
                placeholder="Make the opening punchier, replace the third image, fix a name…"
                value={instructions}
                onChange={(e) => setInstructions(e.target.value)}
                minLength={3}
                required
                disabled={!!active}
              />
            </label>
            <div>
              <span>Same OpenCode conversation and session ID. New files preserve each revision.</span>
              <button
                className="primary"
                disabled={busy || !!active || needsOriginal || instructions.trim().length < 3}
              >
                <Send size={15} />
                Resume
              </button>
            </div>
          </form>
        </section>
      </div>
      {publish && (
        <Publish
          artifact={current}
          busy={busy}
          close={() => setPublish(false)}
          submit={(input) =>
            action(async () => {
              await api(`/sessions/${s.id}/publish`, input);
              setPublish(false);
              await refresh();
            })
          }
        />
      )}{" "}
      {document && (
        <div className="overlay" onClick={() => setDocument(null)}>
          <div className="modal document" onClick={(e) => e.stopPropagation()}>
            <div className="modal-heading">
              <h3>{document.name}</h3>
              <button className="icon" onClick={() => setDocument(null)}>
                <X />
              </button>
            </div>
            <pre>{document.text}</pre>
          </div>
        </div>
      )}
    </>
  );
}
function Publish({ artifact, busy, close, submit }) {
  const [title, setTitle] = useState(artifact.metadata.title || ""),
    [description, setDescription] = useState(
      artifact.metadata.description || "",
    ),
    [privacy, setPrivacy] = useState("private"),
    [madeForKids, setKids] = useState(false);
  return (
    <div className="overlay">
      <form
        className="modal"
        onSubmit={(e) => {
          e.preventDefault();
          submit({
            artifactId: artifact.id,
            title,
            description,
            privacy,
            madeForKids,
          });
        }}
      >
        <div className="modal-heading">
          <p className="eyebrow">YOUTUBE · @GENZSHOTNEWS</p>
          <button type="button" className="icon" onClick={close}>
            <X />
          </button>
        </div>
        <h2>Ready for the world?</h2>
        <label>
          Video title
          <input
            maxLength={100}
            required
            value={title}
            onChange={(e) => setTitle(e.target.value)}
          />
        </label>
        <label>
          Description
          <textarea
            rows={5}
            maxLength={5000}
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />
        </label>
        <label>
          Visibility
          <select value={privacy} onChange={(e) => setPrivacy(e.target.value)}>
            {["private", "unlisted", "public"].map((p) => (
              <option key={p}>{p}</option>
            ))}
          </select>
        </label>
        <label className="check-label">
          <input
            type="checkbox"
            checked={madeForKids}
            onChange={(e) => setKids(e.target.checked)}
          />
          This video is made for kids
        </label>
        <p className="muted small">
          YouTube may restrict unaudited API projects to private uploads. The
          actual visibility is recorded after upload.
        </p>
        <button className="primary full" disabled={busy}>
          <Youtube size={18} />
          Upload video
        </button>
      </form>
    </div>
  );
}
function formatBytes(bytes) {
  if (!bytes || bytes <= 0) return "";
  const mb = bytes / (1024 * 1024);
  return `${mb.toFixed(1)} MB`;
}

function formatIST(dateStr) {
  if (!dateStr) return "—";
  const date = new Date(dateStr);
  if (isNaN(date.getTime())) return "—";
  const formatted = new Intl.DateTimeFormat("en-GB", {
    timeZone: "Asia/Kolkata",
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
  }).format(date);
  return formatted + " IST";
}

function Library({ action, open }) {
  const [items, setItems] = useState([]);
  const [search, setSearch] = useState("");
  const [sortBy, setSortBy] = useState("newest");
  const [statusFilter, setStatusFilter] = useState("all");
  const [chatInputs, setChatInputs] = useState({});
  const [submitting, setSubmitting] = useState(null);

  const loadLibrary = () => {
    api("/library")
      .then(setItems)
      .catch(() => {});
  };

  useEffect(() => {
    loadLibrary();
    const interval = setInterval(loadLibrary, 4000);
    return () => clearInterval(interval);
  }, []);

  const handleChatSubmit = async (e, item) => {
    e.preventDefault();
    const key = item.episode + "/" + item.file;
    const promptText = (chatInputs[key] || "").trim();
    if (!promptText) return;

    setSubmitting(key);
    try {
      const result = await api("/library/prompt", {
        episode: item.episode,
        file: item.file,
        prompt: promptText
      });
      setChatInputs(prev => ({ ...prev, [key]: "" }));
      open(result.sessionId);
    } catch (err) {
      action(() => { throw err; });
    } finally {
      setSubmitting(null);
    }
  };

  const handleOpenOrImport = async (item) => {
    if (item.sessionId) {
      open(item.sessionId);
      return;
    }
    const key = item.episode + "/" + item.file;
    setSubmitting(key);
    try {
      const result = await api("/library/import", {
        episode: item.episode,
        file: item.file
      });
      setItems(curr => curr.map(e => e.episode === item.episode && e.file === item.file ? { ...e, sessionId: result.id, status: 'queued' } : e));
      open(result.id);
    } catch (err) {
      action(() => { throw err; });
    } finally {
      setSubmitting(null);
    }
  };

  const statusPriority = {
    generating: 1,
    running: 1,
    queued: 2,
    ready: 3,
    published: 4,
    paused: 5,
    failed: 6,
    unimported: 7
  };

  const counts = items.reduce((acc, item) => {
    const s = item.status || "unimported";
    acc[s] = (acc[s] || 0) + 1;
    acc.all = (acc.all || 0) + 1;
    return acc;
  }, { all: 0 });

  const filtered = items.filter(item => {
    const q = search.trim().toLowerCase();
    const matchesSearch = !q ||
      item.episode.toLowerCase().includes(q) ||
      item.file.toLowerCase().includes(q) ||
      (item.status && item.status.toLowerCase().includes(q));
    const matchesStatus = statusFilter === "all" || item.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const sorted = [...filtered].sort((a, b) => {
    if (sortBy === "newest") {
      const ta = new Date(a.updatedAt || a.createdAt || 0).getTime();
      const tb = new Date(b.updatedAt || b.createdAt || 0).getTime();
      return tb - ta;
    }
    if (sortBy === "oldest") {
      const ta = new Date(a.updatedAt || a.createdAt || 0).getTime();
      const tb = new Date(b.updatedAt || b.createdAt || 0).getTime();
      return ta - tb;
    }
    if (sortBy === "name-asc") {
      return a.episode.localeCompare(b.episode);
    }
    if (sortBy === "name-desc") {
      return b.episode.localeCompare(a.episode);
    }
    if (sortBy === "status") {
      const pa = statusPriority[a.status] || 99;
      const pb = statusPriority[b.status] || 99;
      if (pa !== pb) return pa - pb;
      return a.episode.localeCompare(b.episode);
    }
    return 0;
  });

  return (
    <>
      <div className="page-heading">
        <div>
          <p className="eyebrow">ALREADY IN YOUR WORKSPACE</p>
          <h1>
            Your episode library<span>.</span>
          </h1>
          <p>
            Browse existing renders, inspect live status, and prompt AI directly from each episode.
          </p>
        </div>
      </div>

      <div className="library-controls">
        <div className="library-search">
          <Search size={15} />
          <input
            type="text"
            placeholder="Search episodes, files or status…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          {search && (
            <button type="button" className="icon-btn" onClick={() => setSearch("")} title="Clear search">
              <X size={13} />
            </button>
          )}
        </div>

        <div className="library-sort">
          <label htmlFor="library-sort-select">Sort by:</label>
          <select
            id="library-sort-select"
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
          >
            <option value="newest">Newest first</option>
            <option value="oldest">Oldest first</option>
            <option value="name-asc">Episode (A–Z)</option>
            <option value="name-desc">Episode (Z–A)</option>
            <option value="status">Status</option>
          </select>
        </div>
      </div>

      <div className="library-status-pills">
        {[
          { key: "all", label: "All" },
          { key: "queued", label: "Queued" },
          { key: "generating", label: "Generating" },
          { key: "ready", label: "Ready" },
          { key: "published", label: "Published" },
          { key: "unimported", label: "Unimported" }
        ].map(({ key, label }) => (
          <button
            key={key}
            type="button"
            className={`status-pill ${statusFilter === key ? "active" : ""}`}
            onClick={() => setStatusFilter(key)}
          >
            <span>{label}</span>
            <span className="status-pill-count">{counts[key] || 0}</span>
          </button>
        ))}
      </div>

      <div className="library-list-view">
        {sorted.length === 0 ? (
          <div className="empty">
            <FolderOpen size={32} />
            <h3>No matching episodes</h3>
            <p>{items.length === 0 ? "Existing episodes with final*.mp4 will appear here." : "Try adjusting your search or status filter."}</p>
          </div>
        ) : (
          sorted.map((item) => {
            const key = item.episode + "/" + item.file;
            const isSubmitting = submitting === key;
            return (
              <div key={key} className="library-row">
                <div className="library-row-header">
                  <div className="library-row-left">
                    <span className="library-icon">
                      <Film size={20} />
                    </span>
                    <div className="library-row-info">
                      <h3>{item.episode}</h3>
                      <div className="meta">
                        <code>{item.file}</code>
                        {(item.updatedAt || item.createdAt) && (
                          <span className="ist-time" title="Indian Standard Time">
                            <Clock size={12} />
                            {formatIST(item.updatedAt || item.createdAt)}
                          </span>
                        )}
                        {item.size > 0 && <span>{formatBytes(item.size)}</span>}
                      </div>

                      {item.youtubeUrl && (
                        <div className="library-yt-link-row">
                          <span className={`yt-type-tag ${item.youtubeType || 'reference'}`}>
                            <Youtube size={12} />
                            <span>{item.youtubeType === 'published' ? 'Published' : 'Reference'}</span>
                          </span>
                          <a
                            href={item.youtubeUrl}
                            target="_blank"
                            rel="noreferrer"
                            className="library-yt-url"
                            title={`Open YouTube: ${item.youtubeUrl}`}
                          >
                            <span>{item.youtubeUrl}</span>
                            <ArrowUpRight size={12} />
                          </a>
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="library-row-right">
                    <Badge status={item.status} />
                    <button
                      type="button"
                      className="secondary small-action-btn"
                      disabled={isSubmitting}
                      onClick={() => handleOpenOrImport(item)}
                    >
                      {item.sessionId ? <Check size={14} /> : <Plus size={14} />}
                      <span>{item.sessionId ? "Open session" : isSubmitting ? "Importing…" : "Open / Import"}</span>
                      <ChevronRight size={13} />
                    </button>
                  </div>
                </div>

                <form
                  className="library-chat-form"
                  onSubmit={(e) => handleChatSubmit(e, item)}
                >
                  <div className="library-chat-box">
                    <input
                      type="text"
                      placeholder={
                        item.sessionId
                          ? "Chat / type prompt to edit or regenerate this episode…"
                          : "Type prompt to import and edit with AI…"
                      }
                      value={chatInputs[key] || ""}
                      onChange={(e) =>
                        setChatInputs({ ...chatInputs, [key]: e.target.value })
                      }
                      disabled={isSubmitting}
                    />
                    <button
                      type="submit"
                      className="primary library-chat-send"
                      disabled={isSubmitting || !chatInputs[key]?.trim()}
                      title="Send prompt"
                    >
                      {isSubmitting ? (
                        <LoaderCircle size={14} className="spin" />
                      ) : (
                        <Send size={14} />
                      )}
                      <span>{isSubmitting ? "Sending…" : "Prompt"}</span>
                    </button>
                  </div>
                </form>
              </div>
            );
          })
        )}
      </div>
    </>
  );
}
function Connections({ settings, action }) {
  const [channel, setChannel] = useState(null);
  const [watch, setWatch] = useState(null);
  const [watchError, setWatchError] = useState("");
  const [watchBusy, setWatchBusy] = useState(false);
  useEffect(() => {
    let mounted = true;
    const load = () => api("/source-watch").then(value => {
      if (mounted) { setWatch(value); setWatchError(""); }
    }).catch(error => { if (mounted) setWatchError(error.message); });
    load();
    const timer = setInterval(load, 15000);
    return () => { mounted = false; clearInterval(timer); };
  }, []);
  return (
    <>
      <div className="page-heading">
        <div>
          <p className="eyebrow">WIRED FOR YOUR WORKFLOW</p>
          <h1>
            Connected & ready<span>.</span>
          </h1>
          <p>Your tools, credentials, and production defaults.</p>
        </div>
      </div>
      <div className="connections">
        <section>
          <Youtube size={28} />
          <h2>NeonManShorts automation</h2>
          <p>New Short → fresh OpenCode session → indian-news-shorts → public upload.</p>
          <Badge status={watch?.enabled ? "watching" : "paused"} />
          {watchError && <p role="alert">{watchError}</p>}
          {watch && <>
            <p className="muted">Webhook notifications with a {watch.pollSeconds}-second feed backup. Existing uploads before initial activation are excluded.</p>
            <p>Last feed check: {watch.last_poll_at ? formatIST(watch.last_poll_at) : "Waiting"}</p>
            <p>Webhook: {watch.lease_expires_at && new Date(watch.lease_expires_at) > new Date() ? "Subscribed" : "Awaiting subscription"}</p>
            {watch.last_error && <p role="alert">{watch.last_error}</p>}
            <button className="secondary" disabled={watchBusy} onClick={() => action(async () => {
              setWatchBusy(true);
              try { setWatch(await api("/source-watch", { enabled: !watch.enabled })); }
              finally { setWatchBusy(false); }
            })}>{watch.enabled ? "Pause channel watcher" : "Enable channel watcher"}</button>
            <p className="muted">Pausing stops discovery. Already queued sessions continue; cancel them from their session page.</p>
            <p>{watch.recent.length} recent detected Shorts. Follow generation and uploads in Sessions.</p>
          </>}
        </section>
        <section>
          <Youtube size={28} />
          <h2>YouTube</h2>
          <p>{settings?.channel}</p>
          <Badge
            status={
              channel
                ? "verified"
                : settings?.tokenPresent
                  ? "configured"
                  : "missing"
            }
          />
          <button
            className="secondary"
            onClick={() =>
              action(async () => setChannel(await api("/youtube/check", {})))
            }
          >
            <RefreshCw size={16} />
            Verify connection
          </button>
          {channel && (
            <p className="success">
              Connected to {channel.title} ({channel.handle})
            </p>
          )}
        </section>
        <section>
          <Layers size={28} />
          <h2>Generation engine</h2>
          <p>OpenCode · resumable sessions</p>
          <code>{settings?.model}</code>
          <p className="muted">
            Skills run in your repository using the approved voice, source
            verification, imagery, gameplay and FFmpeg pipeline.
          </p>
        </section>
        <section>
          <FolderOpen size={28} />
          <h2>Storage</h2>
          <p>{settings?.storage}</p>
          <code>data/sessions/</code>
          <p className="muted">
            Every edit resumes the same original OpenCode session ID and conversation.
            Only the output files get a new revision folder. PostgreSQL preserves
            that session link, revisions and upload history.
          </p>
        </section>
      </div>
    </>
  );
}
createRoot(document.getElementById("root")).render(<App />);
