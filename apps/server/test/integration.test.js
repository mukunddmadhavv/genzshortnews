import {test} from 'node:test';
import assert from 'node:assert/strict';
import {spawn,execFileSync} from 'node:child_process';
import {mkdtemp,readFile,chmod,rm} from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import pg from 'pg';
import {root} from '../src/config.js';
import {contained} from '../src/files.js';

test('path containment rejects traversal and sibling prefixes',()=>{
 assert.equal(contained('/media','/media/x.mp4'),true);
 assert.equal(contained('/media','/media-other/x.mp4'),false);
 assert.equal(contained('/media','/etc/passwd'),false);
});

test('dashboard creates, resumes, previews, publishes and cancels durable sessions',{timeout:90000},async()=>{
 const name=`genz_test_${Date.now()}`;
 const admin=new pg.Client({connectionString:process.env.TEST_DATABASE_URL || (process.env.DATABASE_URL ? new URL('postgres',process.env.DATABASE_URL).href : 'postgresql://localhost:55432/postgres')});await admin.connect();
 await admin.query(`CREATE DATABASE ${name}`);
 const temporary=await mkdtemp(path.join(os.tmpdir(),'genz-test-'));
 const video=path.join(temporary,'fixture.mp4');
 execFileSync('ffmpeg',['-v','error','-f','lavfi','-i','color=c=black:s=1080x1920:r=1','-f','lavfi','-i','anullsrc=r=48000:cl=stereo','-t','1','-c:v','libx264','-preset','ultrafast','-c:a','aac','-shortest',video]);
 const engine=path.join(root,'apps/server/test/fake-engine.mjs');await chmod(engine,0o755);
 const url=new URL(process.env.TEST_DATABASE_URL || (process.env.DATABASE_URL ? new URL('postgres',process.env.DATABASE_URL).href : 'postgresql://localhost:55432/postgres'));url.pathname=`/${name}`;
 const child=spawn(process.execPath,[path.join(root,'apps/server/src/index.js')],{cwd:root,env:{...process.env,DATABASE_URL:url.href,PORT:'6970',DASHBOARD_ORIGIN:'http://localhost:6970',MEDIA_ROOT:path.join(temporary,'media'),OPENCODE_BIN:engine,YOUTUBE_PYTHON:engine,TEST_VIDEO:video},stdio:['ignore','pipe','pipe']});
 let log='';child.stdout.on('data',x=>log+=x);child.stderr.on('data',x=>log+=x);
 let cookie='';
 async function request(route,body,method){const res=await fetch(`http://localhost:6970${route}`,{method:method || (body?'POST':'GET'),headers:{'Content-Type':'application/json',cookie,Origin:'http://localhost:6970'},body:body?JSON.stringify(body):undefined});return res;}
 async function wait(fn){for(let i=0;i<100;i++){const result=await fn();if(result)return result;await new Promise(r=>setTimeout(r,200));}throw new Error(`Timed out. ${log}`);}
 try {
  await wait(async()=>{try{return(await request('/healthz')).ok;}catch{return false;}});
   assert.equal((await request('/api/sessions')).status,401);
   assert.equal((await request('/api/channels')).status,401);
   assert.equal((await fetch('http://localhost:6970/api/channels/UCg48OIfYWyNrUAIM2CLeWLg',{method:'DELETE'})).status,401);
  const {password}=JSON.parse(await readFile(path.join(root,'.secrets/dashboard-access.json'),'utf8'));
   const login=await request('/api/login',{password});assert.equal(login.status,200);cookie=login.headers.get('set-cookie').split(';')[0];
   const overview=await(await request('/api/channels')).json();
   assert.equal(overview.channels.length,1);assert.equal(overview.totals.fetched,0);
   assert.equal(overview.channels[0].hub_secret,undefined);
   assert.equal((await request('/api/channels',{url:'https://evil.example/@Creator'})).status,400);
   assert.equal((await request('/api/channels/not-valid-id',null,'DELETE')).status,400);
   assert.equal((await request('/api/channels/UCabcdefghijklmnopqrstuv',null,'DELETE')).status,404);
  const library=await(await request('/api/library')).json();
  assert.ok(library.length>0,'An existing episode is required for the import regression check');
  const source={episode:library[0].episode,file:library[0].file};
  const imports=await Promise.all([request('/api/library/import',source),request('/api/library/import',source)]);
  assert.deepEqual(imports.map(r=>r.status).sort(),[200,201]);
  const imported=await Promise.all(imports.map(r=>r.json()));
  assert.equal(imported[0].id,imported[1].id,'Concurrent imports reuse the same session');
  const again=await(await request('/api/library/import',source)).json();
  assert.equal(again.id,imported[0].id);
  const listed=await(await request('/api/library')).json();
  assert.equal(listed.find(x=>x.episode===source.episode&&x.file===source.file).sessionId,again.id);
  const rejected=await fetch('http://localhost:6970/api/sessions',{method:'POST',headers:{cookie,Origin:'https://other.example','Content-Type':'application/json'},body:'{}'});assert.equal(rejected.status,403);
  const created=await request('/api/sessions',{title:'Test story',input:'Integration test topic',autoPublish:false,privacy:'private'});assert.equal(created.status,201);const {id}=await created.json();
  const ready=await wait(async()=>{const s=await(await request(`/api/sessions/${id}`)).json();if(s.status==='failed')throw new Error(JSON.stringify(s.jobs));return s.status==='ready'&&s;});
  assert.equal(ready.opencode_session_id,'ses_integration123');assert.equal(ready.artifacts.filter(a=>a.kind==='final').length,1);
  const first=ready.artifacts.find(a=>a.kind==='final');
  assert.equal(first.metadata.publishingCopyReady,true);
  assert.ok(first.metadata.description.includes('#genzshortnews'));
  assert.ok(ready.artifacts.some(a=>a.name==='publishing-copy.json'));
  assert.equal(ready.publications.length,0,'Copy exists before any publish request');
  const range=await fetch(`http://localhost:6970/api/artifacts/${first.id}/content`,{headers:{cookie,Range:'bytes=0-99'}});assert.equal(range.status,206);assert.equal((await range.arrayBuffer()).byteLength,100);
  const resumed=await request(`/api/sessions/${id}/resume`,{instructions:'Make the headline clearer'});assert.equal(resumed.status,202);
  const revised=await wait(async()=>{const s=await(await request(`/api/sessions/${id}`)).json();return s.status==='ready'&&s.artifacts.filter(a=>a.kind==='final').length===2&&s;});
  assert.equal(revised.opencode_session_id,ready.opencode_session_id);
  assert.ok(revised.events.some(e=>e.message==='Resuming existing session'));
  const final=revised.artifacts.find(a=>a.kind==='final');
  assert.equal((await request(`/api/sessions/${id}/publish`,{artifactId:final.id})).status,202);
  const published=await wait(async()=>{const s=await(await request(`/api/sessions/${id}`)).json();return s.status==='published'&&s;});
  assert.equal(published.publications[0].youtube_id,'test-video-id');
  assert.ok(published.publications[0].title.includes('#shorts'));
  assert.ok(published.publications[0].description.includes('#genzshortnews'));
  assert.equal(published.publications[0].made_for_kids,false);
  assert.equal((await request(`/api/sessions/${id}/publish`,{artifactId:final.id,title:'Duplicate',privacy:'private'})).status,409);
  const queued=await(await request(`/api/sessions/${id}/resume`,{instructions:'CANCEL_FIXTURE'})).json();
  await wait(async()=>{const s=await(await request(`/api/sessions/${id}`)).json();return s.jobs.find(j=>j.id===queued.jobId)?.status==='running';});
  assert.equal((await request(`/api/jobs/${queued.jobId}/cancel`,{})).status,200);
  await wait(async()=>{const s=await(await request(`/api/sessions/${id}`)).json();return s.status==='paused';});
   const automatic=await(await request('/api/sessions',{title:'Automatic test',input:'Automatically generate and upload fixture',autoPublish:true,privacy:'public'})).json();
  const autoResult=await wait(async()=>{const s=await(await request(`/api/sessions/${automatic.id}`)).json();return s.status==='published'&&s;});
   assert.equal(autoResult.publications.length,1);
   assert.equal(autoResult.publications[0].privacy,'public');
  assert.equal(autoResult.jobs.filter(j=>j.status==='completed').length,2);
 } finally {
  child.kill('SIGTERM');await new Promise(resolve=>{child.once('exit',resolve);setTimeout(()=>{child.kill('SIGKILL');resolve();},5000).unref();});
  await admin.query(`DROP DATABASE ${name} WITH (FORCE)`);await admin.end();await rm(temporary,{recursive:true,force:true});
 }
});
