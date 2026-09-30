import express from 'express';
import cookieParser from 'cookie-parser';
import rateLimit from 'express-rate-limit';
import { randomUUID } from 'node:crypto';
import { mkdir, readFile, writeFile, stat, readdir, copyFile, realpath } from 'node:fs/promises';
import path from 'node:path';
import { z } from 'zod';
import { pool, query, transaction } from '@genz/db';
import { migrate } from '../../../packages/db/migrate.js';
import { config, root } from './config.js';
import { initAuth, issueCookie, verifyPassword, requireAuth, sameOrigin, authenticated } from './auth.js';
import { safeFile, contained } from './files.js';
import { startWorker, stopWorker, cancelActive, event } from './worker.js';
import { execute } from './process.js';
import { initializeSourceWatch, sourceWebhookRouter, sourceWatchStatus, setSourceWatchEnabled, startSourceWatch, stopSourceWatch, wakeSourceWatch, channelDashboard, addSourceChannel } from './source-watch.js';

const app=express();
app.disable('x-powered-by');
app.use('/webhooks/youtube',sourceWebhookRouter());
app.use(express.json({limit:'100kb'}));
app.use(cookieParser());
app.use((req,res,next)=>{
 res.setHeader('X-Content-Type-Options','nosniff');res.setHeader('Referrer-Policy','no-referrer');
 res.setHeader('X-Frame-Options','DENY');
 res.setHeader('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; media-src 'self'; connect-src 'self'; frame-ancestors 'none'");
 if(req.path.startsWith('/api'))res.setHeader('Cache-Control','no-store');
 next();
});
app.use('/api',sameOrigin);
app.get('/healthz',async(req,res)=>{await query('SELECT 1');res.json({ok:true,service:'genz-news-studio'});});
app.get('/api/auth', (req,res)=>res.json({authenticated:authenticated(req)}));
app.post('/api/login',rateLimit({windowMs:15*60*1000,limit:15,standardHeaders:true,legacyHeaders:false}), (req,res)=>{
 const {password}=z.object({password:z.string().max(200)}).parse(req.body);
 if(!verifyPassword(password))return res.status(401).json({error:'Incorrect studio password.'});
 issueCookie(res);res.json({ok:true});
});
app.post('/api/logout',(req,res)=>{res.clearCookie('genz_session');res.json({ok:true});});
app.use('/api',requireAuth);
app.get('/api/channels',async(req,res)=>res.json(await channelDashboard()));
app.post('/api/channels',rateLimit({windowMs:60000,limit:15,standardHeaders:true,legacyHeaders:false}),async(req,res)=>{
 const {url}=z.object({url:z.string().trim().min(3).max(500)}).parse(req.body);
 const result=await addSourceChannel(url);
 res.status(result.created?201:200).json(result);
 void wakeSourceWatch(true,result.channel.channel_id);
});
app.patch('/api/channels/:id',async(req,res)=>{
 const id=z.string().regex(/^UC[\w-]{22}$/).parse(req.params.id);
 const {enabled}=z.object({enabled:z.boolean()}).parse(req.body);
 res.json(await setSourceWatchEnabled(enabled,id));
 void wakeSourceWatch();
});
app.get('/api/source-watch',async(req,res)=>res.json(await sourceWatchStatus()));
app.post('/api/source-watch',async(req,res)=>{
 const {enabled}=z.object({enabled:z.boolean()}).parse(req.body);
 res.json(await setSourceWatchEnabled(enabled));
 void wakeSourceWatch();
});
const uuid=z.string().uuid();
const privacy=z.enum(['private','unlisted','public']);
const sessionInput=z.object({input:z.string().trim().min(5).max(10000),title:z.string().trim().min(1).max(120),autoPublish:z.boolean().default(false),privacy:privacy.default('private')});
app.get('/api/sessions',async(req,res)=>{
 const {rows}=await query(`SELECT s.*, (SELECT count(*)::int FROM artifacts a WHERE a.session_id=s.id AND a.kind='final') AS revisions,
 (SELECT youtube_id FROM publications p WHERE p.session_id=s.id AND p.status='published' ORDER BY created_at DESC LIMIT 1) AS youtube_id
 FROM sessions s WHERE s.duplicate_of IS NULL ORDER BY updated_at DESC LIMIT 200`);res.json(rows);
});
app.post('/api/sessions',async(req,res)=>{
 const input=sessionInput.parse(req.body);const id=randomUUID(),jobId=randomUUID();
 let sourceType='topic';
 if(/^https?:\/\//i.test(input.input)) {
  const url=new URL(input.input);
  if(!['youtube.com','www.youtube.com','m.youtube.com','youtu.be'].includes(url.hostname))return res.status(400).json({error:'Use a YouTube video/Short URL or enter a topic as text.'});
  sourceType='youtube';
 }
 await transaction(async client=>{
  await client.query('INSERT INTO sessions(id,title,input,source_type,auto_publish,privacy) VALUES($1,$2,$3,$4,$5,$6)',[id,input.title,input.input,sourceType,input.autoPublish,input.privacy]);
  await client.query("INSERT INTO jobs(id,session_id,kind) VALUES($1,$2,'generate')",[jobId,id]);
 });
 await event(id,jobId,'queued','New session queued');res.status(201).json({id});
});
app.get('/api/sessions/:id',async(req,res)=>{
 const id=uuid.parse(req.params.id);
 const {rows:[session]}=await query('SELECT * FROM sessions WHERE id=$1',[id]);
 if(!session)return res.status(404).json({error:'Session not found.'});
 const [jobs,artifacts,events,publications]=await Promise.all([
  query('SELECT * FROM jobs WHERE session_id=$1 ORDER BY created_at DESC',[id]),
  query('SELECT id,name,mime,size_bytes,kind,metadata,job_id,created_at FROM artifacts WHERE session_id=$1 ORDER BY created_at DESC',[id]),
  query('SELECT * FROM (SELECT * FROM events WHERE session_id=$1 ORDER BY id DESC LIMIT 300) recent ORDER BY id',[id]),
  query('SELECT * FROM publications WHERE session_id=$1 ORDER BY created_at DESC',[id])]);
 res.json({...session,jobs:jobs.rows,artifacts:artifacts.rows,events:events.rows,publications:publications.rows});
});
app.post('/api/sessions/:id/resume',async(req,res)=>{
 const id=uuid.parse(req.params.id);
 const {instructions}=z.object({instructions:z.string().trim().min(3).max(10000)}).parse(req.body);
 const jobId=randomUUID();
 await transaction(async client=>{
  const {rows:[session]}=await client.query('SELECT * FROM sessions WHERE id=$1 FOR UPDATE',[id]);
  if(!session)throw Object.assign(new Error('Session not found.'),{status:404});
  await client.query("INSERT INTO jobs(id,session_id,kind,input) VALUES($1,$2,'generate',$3)",[jobId,id,{instructions}]);
  await client.query("UPDATE sessions SET status='queued',updated_at=now() WHERE id=$1",[id]);
 });
 await event(id,jobId,'user',instructions);res.status(202).json({jobId});
});
async function projectConversations(){
 const output=await execute(config.opencode,['session','list','--format','json'],{cwd:root,timeout:30000});
 return JSON.parse(output).filter(item=>item.directory===root).map(({id,title,updated})=>({id,title,updated}));
}
app.get('/api/opencode/sessions',async(req,res)=>res.json(await projectConversations()));
app.post('/api/sessions/:id/link-opencode',async(req,res)=>{
 const id=uuid.parse(req.params.id);
 const sessionId=z.string().regex(/^ses_[a-zA-Z0-9]+$/).parse(req.body.sessionId);
 if(!(await projectConversations()).some(s=>s.id===sessionId))return res.status(400).json({error:'Select an existing OpenCode session from this project.'});
 await transaction(async client=>{
  const {rows:[session]}=await client.query('SELECT * FROM sessions WHERE id=$1 FOR UPDATE',[id]);
  if(!session)throw Object.assign(new Error('Session not found.'),{status:404});
  if(session.opencode_session_id)throw Object.assign(new Error('This video already has its OpenCode session linked.'),{status:409});
  const {rows}=await client.query("SELECT id FROM jobs WHERE session_id=$1 AND status IN ('queued','running')",[id]);
  if(rows.length)throw Object.assign(new Error('Wait for the active job to finish before linking.'),{status:409});
  await client.query('UPDATE sessions SET opencode_session_id=$1,updated_at=now() WHERE id=$2',[sessionId,id]);
 });
 await event(id,null,'session',`Original OpenCode session linked: ${sessionId}`);res.json({ok:true});
});
app.post('/api/jobs/:id/cancel',async(req,res)=>{
 const id=uuid.parse(req.params.id);
 await transaction(async client=>{
  const {rows:[job]}=await client.query('SELECT * FROM jobs WHERE id=$1 FOR UPDATE',[id]);
  if(!job)throw Object.assign(new Error('Job not found.'),{status:404});
  if(job.status==='queued') {
   await client.query("UPDATE jobs SET status='cancelled',finished_at=now() WHERE id=$1",[id]);
   await client.query("UPDATE sessions SET status='paused',updated_at=now() WHERE id=$1",[job.session_id]);
   await client.query("UPDATE publications SET status='failed',error='Upload cancelled before start.' WHERE job_id=$1",[id]);
  }
 });
 cancelActive(id);res.json({ok:true});
});
app.post('/api/sessions/:id/publish',async(req,res)=>{
 const sessionId=uuid.parse(req.params.id);
 const input=z.object({artifactId:uuid,title:z.string().trim().min(1).max(100).optional(),description:z.string().max(5000).optional(),privacy:privacy.default('public'),madeForKids:z.boolean().default(false)}).parse(req.body);
 const jobId=randomUUID();
 await transaction(async client=>{
  const {rows:[artifact]}=await client.query("SELECT * FROM artifacts WHERE id=$1 AND session_id=$2 AND kind='final'",[input.artifactId,sessionId]);
  if(!artifact)throw Object.assign(new Error('Select a final video from this session.'),{status:400});
  if(!artifact.metadata.publishingCopyReady)throw Object.assign(new Error('Prepare caption and description before publishing.'),{status:409});
  await client.query("INSERT INTO jobs(id,session_id,kind) VALUES($1,$2,'publish')",[jobId,sessionId]);
  await client.query('INSERT INTO publications(id,session_id,artifact_id,job_id,title,description,privacy,made_for_kids) VALUES($1,$2,$3,$4,$5,$6,$7,$8)',[randomUUID(),sessionId,input.artifactId,jobId,input.title || artifact.metadata.title || 'GENZ SHORT NEWS',input.description ?? artifact.metadata.description ?? '',input.privacy,input.madeForKids]);
  await client.query("UPDATE sessions SET status='queued',updated_at=now() WHERE id=$1",[sessionId]);
 });res.status(202).json({jobId});
});
app.post('/api/sessions/:id/prepare-copy',async(req,res)=>{
 const id=uuid.parse(req.params.id),artifactId=uuid.parse(req.body.artifactId),jobId=randomUUID();
 await transaction(async client=>{
  const {rows:[artifact]}=await client.query("SELECT * FROM artifacts WHERE id=$1 AND session_id=$2 AND kind='final'",[artifactId,id]);
  if(!artifact)throw Object.assign(new Error('Video not found.'),{status:404});
  await client.query("INSERT INTO jobs(id,session_id,kind,input) VALUES($1,$2,'copy',$3)",[jobId,id,{artifactId}]);
  await client.query("UPDATE sessions SET status='queued',updated_at=now() WHERE id=$1",[id]);
 });res.status(202).json({jobId});
});
app.post('/api/publications/:id/retry',async(req,res)=>{
 const id=uuid.parse(req.params.id),jobId=randomUUID();
 await transaction(async client=>{
  const {rows:[publication]}=await client.query('SELECT * FROM publications WHERE id=$1 FOR UPDATE',[id]);
  if(!publication || publication.status!=='failed')throw Object.assign(new Error('Only failed uploads can be retried.'),{status:400});
  await client.query("INSERT INTO jobs(id,session_id,kind) VALUES($1,$2,'publish')",[jobId,publication.session_id]);
  await client.query("UPDATE publications SET job_id=$1,status='queued',error=NULL,updated_at=now() WHERE id=$2",[jobId,id]);
  await client.query("UPDATE sessions SET status='queued',updated_at=now() WHERE id=$1",[publication.session_id]);
 });res.json({jobId});
});
app.get('/api/artifacts/:id/content',async(req,res)=>{
 const {rows:[artifact]}=await query('SELECT * FROM artifacts WHERE id=$1',[uuid.parse(req.params.id)]);
 if(!artifact)return res.status(404).json({error:'Artifact not found.'});
 const {file}=await safeFile(artifact.path);
 res.setHeader('Content-Type',artifact.mime);
 if(req.query.download==='1')res.attachment(artifact.name);
 res.sendFile(file); // Express handles byte ranges for video seeking.
});
app.get('/api/settings',async(req,res)=>{
 let token=false;try{await stat(config.tokenFile);token=true;}catch{}
 res.json({channel:config.channelHandle,model:config.model,tokenPresent:token,origin:config.origin,storage:'PostgreSQL + local media',pipeline:'indian-news-shorts / FFmpeg / ElevenLabs'});
});
app.post('/api/youtube/check',async(req,res)=>{
 const output=await execute(config.python,[path.join(root,'scripts/youtube_publish.py'),'--token-file',config.tokenFile,'--check'],{timeout:60000});
 res.json(JSON.parse(output.trim().split('\n').at(-1)));
});

// Import an existing episode as a dashboard session without regenerating it.
app.get('/api/library',async(req,res)=>{
 const results=[];
 const {rows:imports}=await query(`
  SELECT i.source_path, i.session_id, s.status, s.title, s.input, s.created_at, s.updated_at,
         (SELECT p.youtube_id FROM publications p WHERE p.session_id=s.id AND p.status='published' ORDER BY p.created_at DESC LIMIT 1) AS youtube_id,
         (SELECT p.status FROM publications p WHERE p.session_id=s.id ORDER BY p.created_at DESC LIMIT 1) AS publication_status,
         (SELECT j.status FROM jobs j WHERE j.session_id=s.id AND j.status IN ('queued','running') ORDER BY j.created_at DESC LIMIT 1) AS active_job_status
  FROM episode_imports i
  JOIN sessions s ON s.id=i.session_id
 `);
 const imported=new Map(imports.map(item=>[item.source_path,item]));
 for(const entry of await readdir(path.join(root,'episodes'),{withFileTypes:true})) {
  if(!entry.isDirectory() || entry.isSymbolicLink())continue;
  for(const name of await readdir(path.join(root,'episodes',entry.name))) {
    if(/^final.*\.mp4$/i.test(name)) {
      const sourcePath=`episodes/${entry.name}/${name}`;
      const match=imported.get(sourcePath);
      let mtime=null, size=0;
      try {
        const st=await stat(path.join(root,'episodes',entry.name,name));
        mtime=st.mtime;
        size=st.size;
      } catch {}
      let status='unimported';
      if(match){
        if(match.youtube_id || match.status==='published' || match.publication_status==='published'){
          status='published';
        } else if(match.active_job_status==='running'){
          status='generating';
        } else if(match.active_job_status==='queued'){
          status='queued';
        } else {
          status=match.status;
        }
      }
      const refMatch=entry.name.match(/[-_]([a-zA-Z0-9_-]{10,12})$/);
      const isRefYt=refMatch && (/[0-9]/.test(refMatch[1]) || (/[A-Z]/.test(refMatch[1]) && /[a-z]/.test(refMatch[1])));
      const refUrl=isRefYt ? `https://youtu.be/${refMatch[1]}` : null;
      const youtubeUrl=match?.youtube_id
        ? `https://youtu.be/${match.youtube_id}`
        : (refUrl || (match?.input && /^https?:\/\//i.test(match.input) ? match.input : null));
      const youtubeType=match?.youtube_id ? 'published' : (youtubeUrl ? 'reference' : null);
      results.push({
        episode:entry.name,
        file:name,
        sessionId:match?.session_id || null,
        status,
        youtubeId:match?.youtube_id || (isRefYt ? refMatch[1] : null),
        youtubeUrl,
        youtubeType,
        createdAt:match?.created_at || mtime,
        updatedAt:match?.updated_at || mtime,
        size
      });
    }
  }
 }
 res.json(results);
});
app.post('/api/library/import',async(req,res)=>{
 const input=z.object({episode:z.string().regex(/^[a-zA-Z0-9_.-]+$/),file:z.string().regex(/^final[a-zA-Z0-9_.-]*\.mp4$/)}).parse(req.body);
 if(input.episode==='..')throw Object.assign(new Error('Invalid episode.'),{status:400});
 const source=await realpath(path.join(root,'episodes',input.episode,input.file));
 if(!contained(await realpath(path.join(root,'episodes')),source))throw Object.assign(new Error('Invalid episode path.'),{status:400});
  const sourcePath=path.relative(root,source);
  const result=await transaction(async client=>{
  await client.query('SELECT pg_advisory_xact_lock(hashtextextended($1,0))',[sourcePath]);
  const {rows:[existing]}=await client.query('SELECT session_id FROM episode_imports WHERE source_path=$1',[sourcePath]);
  if(existing)return {id:existing.session_id,existing:true};
  const id=randomUUID(),artifactId=randomUUID();
 const destination=path.join(config.data,'sessions',id,'imported');
 await mkdir(destination,{recursive:true});
 const file=path.join(destination,'final.mp4');await copyFile(source,file);
 const probe=JSON.parse(await execute('ffprobe',['-v','error','-show_streams','-show_format','-of','json',file],{timeout:30000}));
 const video=probe.streams.find(s=>s.codec_type==='video');
 if(!video || video.width!==1080 || video.height!==1920)throw new Error('Imported video must be 1080×1920.');
 const info=await stat(file);
  await client.query("INSERT INTO sessions(id,title,input,source_type,status) VALUES($1,$2,$3,'import','ready')",[id,input.episode,`Existing episode at episodes/${input.episode}. Use its source records and assets for future edits.`]);
  await client.query("INSERT INTO artifacts(id,session_id,name,path,mime,size_bytes,kind,metadata) VALUES($1,$2,'final.mp4',$3,'video/mp4',$4,'final',$5)",[artifactId,id,path.relative(config.data,file),info.size,{title:input.episode,description:'',duration:Number(probe.format.duration),importedFrom:`episodes/${input.episode}`}]);
   await client.query('INSERT INTO episode_imports(source_path,session_id) VALUES($1,$2)',[sourcePath,id]);
   await client.query("INSERT INTO jobs(id,session_id,kind,input) VALUES($1,$2,'copy',$3)",[randomUUID(),id,{artifactId}]);
   await client.query("UPDATE sessions SET status='queued' WHERE id=$1",[id]);
   await client.query("INSERT INTO events(session_id,kind,message) VALUES($1,'imported',$2)",[id,`Imported ${input.episode}/${input.file}`]);
   return {id,existing:false};
  });res.status(result.existing?200:201).json(result);
});
app.post('/api/library/prompt',async(req,res)=>{
 const input=z.object({
  episode:z.string().regex(/^[a-zA-Z0-9_.-]+$/),
  file:z.string().regex(/^final[a-zA-Z0-9_.-]*\.mp4$/),
  prompt:z.string().trim().min(1).max(10000)
 }).parse(req.body);
 if(input.episode==='..')throw Object.assign(new Error('Invalid episode.'),{status:400});
 const source=await realpath(path.join(root,'episodes',input.episode,input.file));
 if(!contained(await realpath(path.join(root,'episodes')),source))throw Object.assign(new Error('Invalid episode path.'),{status:400});
 const sourcePath=path.relative(root,source);
 let sessionId;
 const {rows:[existing]}=await query('SELECT session_id FROM episode_imports WHERE source_path=$1',[sourcePath]);
 if(existing){
  sessionId=existing.session_id;
 } else {
  const imp=await transaction(async client=>{
   await client.query('SELECT pg_advisory_xact_lock(hashtextextended($1,0))',[sourcePath]);
   const {rows:[doubleCheck]}=await client.query('SELECT session_id FROM episode_imports WHERE source_path=$1',[sourcePath]);
   if(doubleCheck) return {id:doubleCheck.session_id};
   const id=randomUUID(),artifactId=randomUUID();
   const destination=path.join(config.data,'sessions',id,'imported');
   await mkdir(destination,{recursive:true});
   const file=path.join(destination,'final.mp4');await copyFile(source,file);
   const probe=JSON.parse(await execute('ffprobe',['-v','error','-show_streams','-show_format','-of','json',file],{timeout:30000}));
   const info=await stat(file);
   await client.query("INSERT INTO sessions(id,title,input,source_type,status) VALUES($1,$2,$3,'import','ready')",[id,input.episode,`Existing episode at episodes/${input.episode}. Use its source records and assets for future edits.`]);
   await client.query("INSERT INTO artifacts(id,session_id,name,path,mime,size_bytes,kind,metadata) VALUES($1,$2,'final.mp4',$3,'video/mp4',$4,'final',$5)",[artifactId,id,path.relative(config.data,file),info.size,{title:input.episode,description:'',duration:Number(probe.format.duration),importedFrom:`episodes/${input.episode}`}]);
   await client.query('INSERT INTO episode_imports(source_path,session_id) VALUES($1,$2)',[sourcePath,id]);
   return {id};
  });
  sessionId=imp.id;
 }
 const jobId=randomUUID();
 await transaction(async client=>{
  await client.query("INSERT INTO jobs(id,session_id,kind,input) VALUES($1,$2,'generate',$3)",[jobId,sessionId,{instructions:input.prompt}]);
  await client.query("UPDATE sessions SET status='queued',updated_at=now() WHERE id=$1",[sessionId]);
 });
 await event(sessionId,jobId,'user',input.prompt);
 res.status(202).json({sessionId,jobId});
});

const brandingFiles={ 'profile.png':'genz-short-news-profile-800.png', 'banner.png':'banner-mobile-preview.png' };
app.get('/branding/:name',(req,res)=>{
 const filename=brandingFiles[req.params.name];
 if(!filename)return res.sendStatus(404);
 res.sendFile(path.join(root,'output/branding',filename));
});

const web=path.join(root,'apps/web/dist');
app.use(express.static(web));
app.get('/{*path}',(req,res)=>{
 if(req.path.startsWith('/api/'))return res.status(404).json({error:'Not found.'});
 res.sendFile(path.join(web,'index.html'));
});
app.use((error,req,res,next)=>{
 if(res.headersSent)return next(error);
 if(error instanceof z.ZodError)return res.status(400).json({error:error.issues.map(i=>i.message).join('; ')});
 if(error.code==='23505')return res.status(409).json({error:'A job is already active, or this revision already has an upload. Resume the existing upload instead.'});
 console.error('Request failed:',error.code || error.name);
 res.status(error.status || 500).json({error:error.status?error.message:'Operation failed. Check service availability and try again.'});
});
await mkdir(config.data,{recursive:true});await initAuth();await migrate();await initializeSourceWatch();await startWorker();
const server=app.listen(config.port,config.host,()=>{console.log(`GENZ Studio ready at ${config.origin}. Run npm run access for the password.`);startSourceWatch();});
async function shutdown(){server.close();await stopSourceWatch();await stopWorker();await pool.end();process.exit(0);}
process.once('SIGTERM',shutdown);process.once('SIGINT',shutdown);
