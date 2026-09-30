import { randomUUID } from 'node:crypto';
import path from 'node:path';
import { mkdir, readFile, writeFile, access } from 'node:fs/promises';
import { pool, query, transaction } from '@genz/db';
import { config, root } from './config.js';
import { collectFiles, safeFile, contained } from './files.js';
import { execute } from './process.js';
import { generationPrompt } from './prompt.js';
import { publishingCopy } from './publishing-copy.js';

const active = new Map();
let stopping = false, timer, lock;
const clean = text => String(text).replace(/(?:ya29\.|GOCSPX-|sk-)[A-Za-z0-9_.-]+/g, '[redacted]').slice(0, 4000);
export async function event(sessionId, jobId, kind, message) { await query('INSERT INTO events(session_id,job_id,kind,message) VALUES($1,$2,$3,$4)', [sessionId,jobId,kind,clean(message)]); }
export function cancelActive(jobId) {
 const item = active.get(jobId);
 if (item) item.controller.abort();
}

async function generate(job, session, signal) {
 const directory = path.join(config.data, 'sessions', session.id, job.id);
 await mkdir(directory, { recursive:true });
 const previousResult = await query("SELECT path FROM artifacts WHERE session_id=$1 AND kind='final' ORDER BY created_at DESC LIMIT 1", [session.id]);
 const previous = previousResult.rows[0] ? path.dirname(path.join(config.data, previousResult.rows[0].path)) : null;
 const prompt = generationPrompt({session, job, revision:directory, previous});
 await writeFile(path.join(directory, 'request.txt'), prompt);
 const args = ['run', '--auto', '--format','json','--model',config.model,'--title',`GENZ: ${session.title}`];
 if (session.opencode_session_id) args.push('--session',session.opencode_session_id);
 args.push(prompt);
 let chain = Promise.resolve(), agentError = false, lastStage = '', boundSessionId=session.opencode_session_id;
 const enqueue = fn => { chain = chain.then(fn); };
 const watcher = setInterval(async () => {
  try {
   const progress = JSON.parse(await readFile(path.join(directory,'progress.json'),'utf8'));
   if (typeof progress.stage === 'string' && progress.stage !== lastStage) {
    lastStage = progress.stage;
    enqueue(() => event(session.id,job.id,'stage',`${progress.stage}: ${progress.detail || ''}`));
   }
  } catch {}
 }, 2000);
 watcher.unref();
 try {
  await execute(config.opencode, args, {cwd:root, signal, timeout:config.maxJobMs,
   env:{...process.env, OPENCODE_PERMISSION:JSON.stringify({question:'deny'})},
   onLine: line => {
    let payload; try { payload = JSON.parse(line); } catch { return; }
    const sessionId = payload.sessionID || payload.sessionId || payload.part?.sessionID;
    if (typeof sessionId === 'string' && /^ses_[a-zA-Z0-9]+$/.test(sessionId)) {
     if(boundSessionId && boundSessionId!==sessionId){agentError=true;return;}
     if(!boundSessionId){boundSessionId=sessionId;enqueue(() => query('UPDATE sessions SET opencode_session_id=$1 WHERE id=$2 AND opencode_session_id IS NULL', [sessionId, session.id]));}
    }
    if (payload.type === 'text' && payload.part?.text) enqueue(() => event(session.id,job.id,'assistant',payload.part.text));
    if (payload.type === 'tool_use') enqueue(() => event(session.id,job.id,'tool',`${payload.part?.tool || 'tool'}: ${payload.part?.state?.status || 'running'}`));
    if (payload.type === 'error') { agentError = true; enqueue(() => event(session.id,job.id,'error','OpenCode reported an error. Check model access or resume the session.')); }
   }});
 } finally { clearInterval(watcher); await chain; }
  if (agentError) throw new Error('Generation agent reported an error. Resume to continue.');
  if(!boundSessionId)throw new Error('OpenCode did not return a session ID; cannot save a resumable revision.');
 const result = JSON.parse(await readFile(path.join(directory,'dashboard-result.json'),'utf8'));
 const copy = publishingCopy(result);
 await writeFile(path.join(directory,'publishing-copy.json'),JSON.stringify(copy,null,2));
 await writeFile(path.join(directory,'dashboard-result.json'),JSON.stringify({...result,...copy},null,2));
 if (result.video !== 'final.mp4') throw new Error('Generation did not provide final.mp4. Resume to complete the export.');
 const { file } = await safeFile(path.relative(config.data,path.join(directory,result.video)));
 const probe = JSON.parse(await execute('ffprobe',['-v','error','-show_streams','-show_format','-of','json',file],{timeout:30000}));
 const video = probe.streams.find(s => s.codec_type === 'video');
 const audio = probe.streams.find(s => s.codec_type === 'audio');
 if (!video || video.width !== 1080 || video.height !== 1920 || !audio || !(Number(probe.format.duration) > 0)) throw new Error('Final export must be 1080×1920 with an audio track.');
 await execute('ffmpeg',['-v','error','-xerror','-i',file,'-f','null','-'],{timeout:180000,signal});
 let finalId;
 const files = await collectFiles(directory);
 for (const item of files) {
  const id = randomUUID();
  const kind = item.absolute === path.join(directory,'final.mp4') ? 'final' : item.mime.startsWith('video/') ? 'video' : item.mime.startsWith('image/') ? 'image' : item.mime.startsWith('audio/') ? 'audio' : 'document';
   const metadata = kind === 'final' ? {...copy,summary:result.summary,duration:Number(probe.format.duration),width:1080,height:1920,decodeVerified:true} : {};
  await query('INSERT INTO artifacts(id,session_id,job_id,name,path,mime,size_bytes,kind,metadata) VALUES($1,$2,$3,$4,$5,$6,$7,$8,$9) ON CONFLICT(session_id,path) DO NOTHING',[id,session.id,job.id,item.name,item.path,item.mime,item.size,kind,metadata]);
  if (kind === 'final') finalId = id;
 }
 if (!finalId) throw new Error('Final video could not be indexed.');
 await event(session.id,job.id,'complete',`Revision ready. ${Number(probe.format.duration).toFixed(1)}s · 1080×1920 · full decode passed.`);
 return finalId;
}

async function prepareCopy(job, session, signal) {
 const {rows:[artifact]}=await query("SELECT * FROM artifacts WHERE id=$1 AND session_id=$2 AND kind='final'",[job.input.artifactId,session.id]);
 if(!artifact)throw new Error('Video not found.');
 const {file}=await safeFile(artifact.path);
  await event(session.id,job.id,'caption','Writing caption, description and relevant hashtags for this video.');
  const copyDirectory=path.join(config.data,'sessions',session.id,`${job.id}-copy`);
  await mkdir(copyDirectory,{recursive:true});
  const outputFile=path.join(copyDirectory,'publishing-copy.json');
  const sourceDirectory=artifact.metadata.importedFrom ? path.resolve(root,artifact.metadata.importedFrom) : path.dirname(file);
  if(!contained(root,sourceDirectory))throw new Error('Invalid source directory.');
  const prompt=`Create YouTube and Instagram publishing copy for the existing video at ${file}.
Read .skills/indian-news-shorts/references/youtube-publishing.md and references/instagram-publishing.md and the episode narration, README, source records and manifests at ${sourceDirectory}.
Do not regenerate or upload the video. Do not change any existing files or read secrets.
Write only ${outputFile} with JSON {
  "caption":"Accurate engaging Hinglish title under 92 characters",
  "description":"Original summary of the actual video with source attribution",
  "hashtags":["#shorts","#genzshortnews","#TopicSpecific"],
  "instagram":{
    "caption":"Separate punchy hook line for Instagram Reels",
    "description":"Separate story description with viewer prompt and attribution for Instagram",
    "hashtags":["#reels","#reelsindia","#genzshortnews","#TopicSpecific"]
  }
}.
Include 3–6 relevant additional hashtags. No invented claims. This is publishing copy, not subtitles.
Use the actual episode content, not its folder name. Complete this task autonomously.`;
  await execute(config.opencode,['run','--auto','--format','json','--model',config.model,prompt],{cwd:root,signal,timeout:10*60*1000});
  const copy=publishingCopy(JSON.parse(await readFile(outputFile,'utf8')));
  await writeFile(outputFile,JSON.stringify(copy,null,2));
  await query('UPDATE artifacts SET metadata=metadata || $1::jsonb WHERE id=$2',[JSON.stringify(copy),artifact.id]);
  await event(session.id,job.id,'complete','Caption, description and hashtags are ready to review. No upload was started.');
}

async function publish(job, session, signal) {
 const {rows:[publication]} = await query('SELECT p.*,a.path,a.metadata FROM publications p JOIN artifacts a ON a.id=p.artifact_id WHERE p.job_id=$1',[job.id]);
 if (!publication) throw new Error('Publication not found.');
 if(!publication.metadata.publishingCopyReady)throw new Error('Prepare publishing copy before uploading.');
 const {file} = await safeFile(publication.path);
 const directory = path.join(root,'.secrets','uploads');
 await mkdir(directory,{recursive:true,mode:0o700});
 const platform = publication.platform || session.publish_target || 'both';

 await query("UPDATE publications SET status='uploading',updated_at=now() WHERE id=$1",[publication.id]);

 let ytResult = null, ytError = null, igResult = null, igError = null, chain = Promise.resolve();

 // YouTube upload
 if (['both', 'youtube'].includes(platform)) {
  if (publication.youtube_id) {
   ytResult = { youtubeId: publication.youtube_id, channelId: publication.channel_id, privacy: publication.privacy };
  } else {
   const spec = path.join(directory,`${publication.id}.spec.json`);
   await writeFile(spec,JSON.stringify({file,title:publication.title,description:publication.description,privacy:publication.privacy,madeForKids:publication.made_for_kids}),{mode:0o600});
   try {
    await execute(config.python,[path.join(root,'scripts/youtube_publish.py'),'--token-file',config.tokenFile,'--spec',spec,'--checkpoint',path.join(directory,`${publication.id}.checkpoint.json`)],{cwd:root,signal,timeout:60*60*1000,onLine:line=>{
     let item; try { item=JSON.parse(line); } catch {return;}
     if(item.type==='published') ytResult=item;
     if(item.type==='error') ytError=item.message;
     if(item.type==='progress') chain=chain.then(()=>event(session.id,job.id,'upload',`YouTube: ${item.percent}%`));
    }});
   } catch(e) { throw new Error(ytError || e.message); } finally { await chain; }
   if(!ytResult?.youtubeId) throw new Error('YouTube completion not confirmed. Retry resumes the existing upload.');
  }
 }

 // Instagram Reel upload
 if (['both', 'instagram'].includes(platform)) {
  if (publication.instagram_media_id) {
   igResult = { instagramMediaId: publication.instagram_media_id };
  } else {
   const igCaption = publication.instagram_caption || publication.metadata.instagram?.fullCaption || publication.metadata.instagram_caption || `${publication.title}\n\n${publication.description}`;
   const bucket = process.env.SUPABASE_BUCKET || 'genz-video';
   try {
    await execute(config.python,[path.join(root,'scripts/instagram_publish.py'),'--video',file,'--caption',igCaption,'--bucket',bucket],{cwd:root,signal,timeout:30*60*1000,onLine:line=>{
     let item; try { item=JSON.parse(line); } catch {return;}
     if(item.type==='published') igResult=item;
     if(item.type==='error') igError=item.message;
     if(item.type==='status' || item.type==='progress') {
      chain=chain.then(()=>event(session.id,job.id,'upload',`Instagram: ${item.message || item.status || ''}`));
     }
    }});
   } catch(e) { throw new Error(igError || e.message); } finally { await chain; }
   if(!igResult?.instagramMediaId && !igResult?.mediaId) throw new Error('Instagram Reel completion not confirmed. Retry resumes the existing upload.');
   if(!igResult.instagramMediaId && igResult.mediaId) igResult.instagramMediaId = igResult.mediaId;
  }
 }

 const ytId = ytResult?.youtubeId || publication.youtube_id || null;
 const ytChannel = ytResult?.channelId || publication.channel_id || null;
 const ytPrivacy = ytResult?.privacy || publication.privacy;
 const igId = igResult?.instagramMediaId || publication.instagram_media_id || null;
 const igUrl = igResult?.instagramMediaId ? `https://www.instagram.com/reel/${igResult.instagramMediaId}/` : (publication.instagram_url || null);

 await query(
  "UPDATE publications SET status='published',platform=$1,youtube_id=$2,channel_id=$3,privacy=$4,instagram_media_id=$5,instagram_url=$6,error=NULL,updated_at=now() WHERE id=$7",
  [platform, ytId, ytChannel, ytPrivacy, igId, igUrl, publication.id]
 );

 await query(
  "UPDATE artifacts SET metadata=metadata || jsonb_build_object('youtube_id', $1::text, 'instagram_media_id', $2::text, 'instagram_url', $3::text) WHERE id=$4",
  [ytId, igId, igUrl, publication.artifact_id]
 );

 const msgs = [];
 if (ytId) msgs.push(`YouTube: https://youtu.be/${ytId} (${ytPrivacy})`);
 if (igId) msgs.push(`Instagram Reels: ${igUrl || igId}`);
 await event(session.id,job.id,'published',`Published to ${msgs.join(' & ')}`);
}

async function runJob(job) {
 const controller = new AbortController();
 active.set(job.id, { id: job.id, sessionId: job.session_id, controller });
 try {
  const {rows:[session]} = await query('SELECT * FROM sessions WHERE id=$1', [job.session_id]);
  await event(session.id, job.id, 'started', job.kind==='publish' ? 'Publishing video to selected platforms' : job.kind==='copy' ? 'Preparing publishing copy before upload' : 'Starting skill-driven generation');
  const finalId = job.kind==='publish' ? await publish(job, session, controller.signal) : job.kind==='copy' ? await prepareCopy(job, session, controller.signal) : await generate(job, session, controller.signal);
  if (controller.signal.aborted) throw new Error('Job cancelled.');
  await transaction(async client => {
   await client.query("UPDATE jobs SET status='completed',finished_at=now() WHERE id=$1", [job.id]);
   await client.query('UPDATE sessions SET status=$1,updated_at=now() WHERE id=$2', [job.kind==='publish' ? 'published' : 'ready', session.id]);
   if (finalId && session.auto_publish) {
    const {rows:[artifact]} = await client.query('SELECT * FROM artifacts WHERE id=$1', [finalId]);
    const uploadJob = randomUUID();
    const target = session.publish_target || 'both';
    const igCaption = artifact.metadata.instagram?.fullCaption || artifact.metadata.instagram_caption || '';
    await client.query("INSERT INTO jobs(id,session_id,kind) VALUES($1,$2,'publish')", [uploadJob, session.id]);
    await client.query('INSERT INTO publications(id,session_id,artifact_id,job_id,title,description,privacy,platform,instagram_caption) VALUES($1,$2,$3,$4,$5,$6,$7,$8,$9)', [randomUUID(), session.id, finalId, uploadJob, artifact.metadata.title, artifact.metadata.description, session.privacy, target, igCaption]);
    await client.query("UPDATE sessions SET status='queued' WHERE id=$1", [session.id]);
   }
  });
 } catch(error) {
  const cancelled = controller.signal.aborted;
  await query('UPDATE jobs SET status=$1,error=$2,finished_at=now() WHERE id=$3', [cancelled ? 'cancelled' : 'failed', clean(error.message), job.id]);
  await query("UPDATE sessions SET status=$1,updated_at=now() WHERE id=$2", [cancelled ? 'paused' : 'failed', job.session_id]);
  await query("UPDATE publications SET status='failed',error=$1,updated_at=now() WHERE job_id=$2 AND status <> 'published'", [clean(error.message), job.id]);
  await event(job.session_id, job.id, cancelled ? 'paused' : 'error', error.message);
 } finally {
  active.delete(job.id);
  void tick().catch(err => console.error('Worker:', clean(err.message)));
 }
}

async function tick() {
 if (stopping) return;
 while (!stopping && active.size < config.concurrency) {
  const activeSessionIds = Array.from(active.values()).map(a => a.sessionId);
  const job = await transaction(async client => {
   const {rows:[job]} = await client.query(
    "SELECT * FROM jobs WHERE status='queued' AND NOT (session_id = ANY($1::uuid[])) ORDER BY created_at FOR UPDATE SKIP LOCKED LIMIT 1",
    [activeSessionIds]
   );
   if (!job) return;
   await client.query("UPDATE jobs SET status='running',started_at=now() WHERE id=$1", [job.id]);
   await client.query("UPDATE sessions SET status=$1,updated_at=now() WHERE id=$2", [job.kind==='publish' ? 'publishing' : 'generating', job.session_id]);
   return job;
  });
  if (!job) break;
  void runJob(job).catch(error => console.error('Job error:', clean(error.message)));
 }
}

export async function startWorker() {
 lock=await pool.connect();
 const {rows:[result]}=await lock.query('SELECT pg_try_advisory_lock(696969) AS locked');
 if(!result.locked)throw new Error('Another studio worker is already running.');
 await query("UPDATE jobs SET status='interrupted',error='Worker restarted. Resume this session.',finished_at=now() WHERE status='running'");
 await query("UPDATE sessions SET status='paused' WHERE status IN ('generating','publishing')");
 await query("UPDATE publications SET status='failed',error='Worker restarted. Retry to resume upload.' WHERE status='uploading'");
 timer=setInterval(()=>tick().catch(error=>console.error('Worker:',clean(error.message))),1000);
 void tick().catch(error=>console.error('Worker:',clean(error.message)));
}
export async function stopWorker() {
 stopping=true;
 clearInterval(timer);
 for (const item of active.values()) {
  item.controller.abort();
 }
 while(active.size > 0)await new Promise(resolve=>setTimeout(resolve,100));
 if(lock){await lock.query('SELECT pg_advisory_unlock(696969)');lock.release();}
}
