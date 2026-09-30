import { randomBytes, randomUUID, createHmac, timingSafeEqual } from 'node:crypto';
import express from 'express';
import { XMLParser, XMLValidator } from 'fast-xml-parser';
import { query, transaction } from '@genz/db';
import { config } from './config.js';

export const SOURCE_CHANNEL = 'UCg48OIfYWyNrUAIM2CLeWLg';
export const SOURCE_TOPIC = `https://www.youtube.com/feeds/videos.xml?channel_id=${SOURCE_CHANNEL}`;
export const channelTopic = id => `https://www.youtube.com/feeds/videos.xml?channel_id=${id}`;
const HUB = 'https://pubsubhubbub.appspot.com/subscribe';
const POLL_MS = 120000;
const parser = new XMLParser({ignoreAttributes:false,parseTagValue:false,processEntities:false});
let timer, current, stopping = false;
const pending = new Set();

export function feedEntries(xml, channelId=SOURCE_CHANNEL) {
 if (Buffer.byteLength(xml)>1000000 || /<!DOCTYPE|<!ENTITY/i.test(xml) || XMLValidator.validate(xml)!==true) throw new Error('Invalid YouTube feed.');
 const feed=parser.parse(xml).feed;
 if(!feed || feed.id!==`yt:channel:${channelId.slice(2)}` && feed.id!==`yt:channel:${channelId}`) throw new Error('Unexpected source feed.');
 const entries=feed.entry ? (Array.isArray(feed.entry)?feed.entry:[feed.entry]) : [];
 return entries.flatMap(entry=>{
  const id=entry['yt:videoId'], published=new Date(entry.published);
   if(entry['yt:channelId']!==channelId || !/^[\w-]{11}$/.test(id) || !Number.isFinite(published.getTime())) return [];
  const links=Array.isArray(entry.link)?entry.link:[entry.link];
  const isShort=links.some(link=>link?.['@_rel']==='alternate' && link['@_href']===`https://www.youtube.com/shorts/${id}`);
  return [{id,published,isShort,title:String(entry.title || 'YouTube Short').slice(0,120),url:`https://www.youtube.com/shorts/${id}`}];
 }).sort((a,b)=>a.published-b.published);
}

export function validSignature(body, signature, secret) {
 const match=/^(sha1|sha256)=([a-f0-9]+)$/.exec(signature || '');
 if(!match || !Buffer.isBuffer(body))return false;
 const expected=createHmac(match[1],secret).update(body).digest('hex');
 return expected.length===match[2].length && timingSafeEqual(Buffer.from(expected),Buffer.from(match[2]));
}

export async function initializeSourceWatch() {
 await query(`INSERT INTO source_watches(channel_id,callback_token,hub_secret,title,channel_url) VALUES($1,$2,$3,'Neon Man Shorts','https://www.youtube.com/@NeonManShorts/shorts') ON CONFLICT DO NOTHING`,[SOURCE_CHANNEL,randomBytes(24).toString('hex'),randomBytes(32).toString('hex')]);
}

export async function sourceWatchStatus(channelId=SOURCE_CHANNEL) {
 const {rows:[watch]}=await query(`SELECT channel_id,title,channel_url,enabled,started_at,last_poll_at,last_webhook_at,lease_expires_at,last_error FROM source_watches WHERE channel_id=$1`,[channelId]);
 if(!watch)throw Object.assign(new Error('Channel not found.'),{status:404});
 const {rows:recent}=await query(`SELECT v.video_id,v.session_id,v.published_at,s.status,s.opencode_session_id,
 (SELECT youtube_id FROM publications p WHERE p.session_id=s.id AND p.status='published' ORDER BY created_at DESC LIMIT 1) AS youtube_id,
 (SELECT privacy FROM publications p WHERE p.session_id=s.id AND p.status='published' ORDER BY created_at DESC LIMIT 1) AS actual_privacy
 FROM source_videos v JOIN sessions s ON s.id=v.session_id WHERE v.channel_id=$1 ORDER BY v.published_at DESC LIMIT 30`,[channelId]);
 return {...watch,channelUrl:watch.channel_url,pollSeconds:POLL_MS/1000,autoPublish:true,privacy:'public',recent};
}

export async function channelDashboard() {
 const {rows:channels}=await query(`SELECT w.channel_id,w.title,w.channel_url,w.enabled,w.started_at,w.last_poll_at,w.last_webhook_at,w.lease_expires_at,w.last_error,
 count(v.video_id)::int AS fetched,
 count(v.video_id) FILTER (WHERE v.created_at>=now()-interval '24 hours')::int AS fetched_today,
 count(v.video_id) FILTER (WHERE s.status IN ('queued','generating','publishing'))::int AS in_progress,
 count(v.video_id) FILTER (WHERE s.status IN ('failed','paused'))::int AS needs_attention,
 count(v.video_id) FILTER (WHERE EXISTS(SELECT 1 FROM publications p WHERE p.session_id=s.id AND p.status='published'))::int AS published
 FROM source_watches w LEFT JOIN source_videos v ON v.channel_id=w.channel_id LEFT JOIN sessions s ON s.id=v.session_id
 GROUP BY w.channel_id ORDER BY w.created_at,w.channel_id`);
 const {rows:recent}=await query(`SELECT v.channel_id,v.video_id,v.session_id,v.published_at,v.created_at,s.title,s.status,s.opencode_session_id,w.title AS channel_title,
 (SELECT youtube_id FROM publications p WHERE p.session_id=s.id AND p.status='published' ORDER BY created_at DESC LIMIT 1) AS youtube_id
 FROM source_videos v JOIN sessions s ON s.id=v.session_id JOIN source_watches w ON w.channel_id=v.channel_id ORDER BY v.created_at DESC LIMIT 100`);
 const totals=channels.reduce((total,c)=>{
  for(const key of ['fetched','fetched_today','in_progress','published','needs_attention'])total[key]+=c[key];
  if(c.enabled)total.active++;
  return total;
 },{fetched:0,fetched_today:0,in_progress:0,published:0,needs_attention:0,active:0});
 return {channels,totals,recent,pollSeconds:POLL_MS/1000};
}

// Only construct requests to fixed YouTube hosts. Never fetch an arbitrary input URL.
export function channelLocator(input) {
 const value=String(input).trim();
 if(/^UC[\w-]{22}$/.test(value))return {id:value};
 if(/^@[\p{L}\p{N}_.-]{3,100}$/u.test(value))return {handle:value};
 let url;try{url=new URL(value);}catch{throw Object.assign(new Error('Enter a YouTube channel URL, @handle or UC channel ID.'),{status:400});}
 if(!['https:','http:'].includes(url.protocol) || !['youtube.com','www.youtube.com','m.youtube.com'].includes(url.hostname) || url.port || url.username || url.password)throw Object.assign(new Error('Use a youtube.com channel URL.'),{status:400});
 let parts;try{parts=decodeURIComponent(url.pathname).split('/').filter(Boolean);}catch{throw Object.assign(new Error('Invalid channel URL encoding.'),{status:400});}
 if(parts.length>2 && !(parts.length===3 && parts[0]==='channel' && ['shorts','videos','featured'].includes(parts[2])))throw Object.assign(new Error('Use a channel page, not a video URL.'),{status:400});
 if(parts[0]==='channel' && /^UC[\w-]{22}$/.test(parts[1]))return {id:parts[1]};
 if(/^@[\p{L}\p{N}_.-]{3,100}$/u.test(parts[0]) && (parts.length===1 || ['shorts','videos','featured'].includes(parts[1])))return {handle:parts[0]};
 throw Object.assign(new Error('Use a /@handle or /channel/UC… URL.'),{status:400});
}

export async function resolveChannel(input) {
 const locator=channelLocator(input);
 let id=locator.id;
 if(!id){
  const response=await fetch(`https://www.youtube.com/${encodeURIComponent(locator.handle)}/shorts`,{signal:AbortSignal.timeout(20000),redirect:'error'});
  if(!response.ok)throw Object.assign(new Error(`YouTube channel lookup returned HTTP ${response.status}.`),{status:502});
  const html=await response.text();
  // channelMetadataRenderer.externalId describes the page owner, not recommended channels.
  id=html.match(/"channelMetadataRenderer"\s*:\s*\{[\s\S]*?"externalId"\s*:\s*"(UC[\w-]{22})"/)?.[1];
  if(!id)throw Object.assign(new Error('Could not resolve this handle. Try its UC channel ID.'),{status:422});
 }
 const response=await fetch(channelTopic(id),{signal:AbortSignal.timeout(20000),redirect:'error'});
 if(!response.ok)throw Object.assign(new Error(`Channel feed returned HTTP ${response.status}. Check the channel URL and retry.`),{status:422});
 const xml=await response.text();feedEntries(xml,id);
 return {id,title:String(parser.parse(xml).feed.title || locator.handle || id).slice(0,160),url:`https://www.youtube.com/channel/${id}/shorts`};
}

export async function addSourceChannel(input) {
 const channel=await resolveChannel(input);
 const {rows}=await query(`INSERT INTO source_watches(channel_id,title,channel_url,enabled,started_at,callback_token,hub_secret)
 VALUES($1,$2,$3,true,now(),$4,$5) ON CONFLICT(channel_id) DO NOTHING RETURNING channel_id`,[channel.id,channel.title,channel.url,randomBytes(24).toString('hex'),randomBytes(32).toString('hex')]);
 return {channel:await sourceWatchStatus(channel.id),created:rows.length>0};
}

export async function setSourceWatchEnabled(enabled,channelId=SOURCE_CHANNEL) {
 // Re-enabling preserves the cutoff and ledger, allowing feed catch-up after downtime.
 await query(`UPDATE source_watches SET enabled=$2,started_at=CASE WHEN $2 THEN COALESCE(started_at,now()) ELSE started_at END,
  last_poll_at=NULL,next_subscribe_at=NULL WHERE channel_id=$1`,[channelId,enabled]);
 return sourceWatchStatus(channelId);
}

export async function ingestEntries(entries,channelId=SOURCE_CHANNEL) {
 return transaction(async client=>{
  const {rows:[watch]}=await client.query('SELECT * FROM source_watches WHERE channel_id=$1 FOR UPDATE',[channelId]);
  if(!watch?.enabled || !watch.started_at)return [];
  const created=[];
  for(const entry of entries) {
   if(!entry.isShort || entry.published<watch.started_at || entry.published>new Date())continue;
   const {rows}=await client.query('SELECT video_id FROM source_videos WHERE channel_id=$1 AND video_id=$2',[channelId,entry.id]);
   if(rows.length)continue;
   const sessionId=randomUUID(),jobId=randomUUID();
   await client.query(`INSERT INTO sessions(id,title,input,source_type,auto_publish,privacy) VALUES($1,$2,$3,'youtube',true,'public')`,[sessionId,entry.title,entry.url]);
   await client.query(`INSERT INTO jobs(id,session_id,kind) VALUES($1,$2,'generate')`,[jobId,sessionId]);
   await client.query(`INSERT INTO source_videos(channel_id,video_id,session_id,published_at) VALUES($1,$2,$3,$4)`,[channelId,entry.id,sessionId,entry.published]);
   await client.query(`INSERT INTO events(session_id,job_id,kind,message) VALUES($1,$2,'queued',$3)`,[sessionId,jobId,`Automatically detected ${watch.title} upload: ${entry.url}. New OpenCode session → indian-news-shorts → public upload.`]);
   created.push(sessionId);
  }
  return created;
 });
}

async function syncFeed(channelId) {
 const response=await fetch(channelTopic(channelId),{signal:AbortSignal.timeout(20000)});
 if(!response.ok)throw new Error(`YouTube feed HTTP ${response.status}`);
 // Only the channel's freshly fetched feed can enqueue work, never webhook-supplied URLs/titles.
 await ingestEntries(feedEntries(await response.text(),channelId),channelId);
 await query('UPDATE source_watches SET last_poll_at=now(),last_error=NULL WHERE channel_id=$1',[channelId]);
}

async function subscribe(watch) {
 const origin=new URL(config.origin);
 if(origin.protocol!=='https:')throw new Error('Webhook requires an HTTPS DASHBOARD_ORIGIN; feed polling remains active.');
 await query("UPDATE source_watches SET next_subscribe_at=now()+interval '10 minutes' WHERE channel_id=$1",[watch.channel_id]);
 const response=await fetch(HUB,{method:'POST',signal:AbortSignal.timeout(20000),body:new URLSearchParams({
  'hub.mode':'subscribe','hub.topic':channelTopic(watch.channel_id),'hub.callback':`${origin.origin}/webhooks/youtube/${watch.callback_token}`,
  'hub.verify':'async','hub.secret':watch.hub_secret,'hub.lease_seconds':'864000'
 })});
 if(!response.ok)throw new Error(`YouTube hub HTTP ${response.status}`);
}

async function tick() {
 const {rows:watches}=await query('SELECT * FROM source_watches WHERE enabled=true ORDER BY created_at');
 for(const watch of watches){
  if(stopping)break;
  try{
   const force=pending.delete(watch.channel_id);
   if(force || !watch.last_poll_at || Date.now()-watch.last_poll_at.getTime()>=POLL_MS)await syncFeed(watch.channel_id);
   if((!watch.lease_expires_at || watch.lease_expires_at.getTime()-Date.now()<86400000) && (!watch.next_subscribe_at || watch.next_subscribe_at<=new Date()))await subscribe(watch);
  }catch(error){
   const message=String(error.message).replace(/https?:\/\/\S+/g,'[url]').slice(0,500);
   console.error('Source watcher:',watch.channel_id,message);
   await query('UPDATE source_watches SET last_error=$2 WHERE channel_id=$1',[watch.channel_id,message]);
  }
 }
}

export function wakeSourceWatch(force=false,channelId=SOURCE_CHANNEL) {
 if(force)pending.add(channelId);
 if(stopping || current)return current;
 current=tick().catch(()=>console.error('Source watcher: database unavailable')).finally(()=>{current=null;});
 return current;
}

export function startSourceWatch() {
 stopping=false;
 timer=setInterval(()=>void wakeSourceWatch(),15000);
 void wakeSourceWatch();
}
export async function stopSourceWatch(){stopping=true;clearInterval(timer);await current;}

export function sourceWebhookRouter() {
 const router=express.Router();
 router.use('/:token',async(req,res,next)=>{
   const {rows:[watch]}=await query('SELECT * FROM source_watches WHERE callback_token=$1',[req.params.token]);
   if(!watch?.enabled)return res.sendStatus(404);
  req.sourceWatch=watch;next();
 });
 router.get('/:token',async(req,res)=>{
  const q=req.query,lease=Number(q['hub.lease_seconds']);
   if(q['hub.mode']!=='subscribe' || q['hub.topic']!==channelTopic(req.sourceWatch.channel_id) || typeof q['hub.challenge']!=='string' || q['hub.challenge'].length>1024 || !Number.isInteger(lease) || lease<=0 || lease>31536000)return res.sendStatus(400);
   await query("UPDATE source_watches SET lease_expires_at=now()+($2 * interval '1 second'),last_error=NULL WHERE channel_id=$1",[req.sourceWatch.channel_id,lease]);
  res.type('text/plain').send(q['hub.challenge']);
 });
 router.post('/:token',express.raw({type:()=>true,limit:'1mb'}),async(req,res)=>{
  if(!validSignature(req.body,req.get('x-hub-signature'),req.sourceWatch.hub_secret))return res.sendStatus(401);
   await query('UPDATE source_watches SET last_webhook_at=now() WHERE channel_id=$1',[req.sourceWatch.channel_id]);
  res.sendStatus(202);
   void wakeSourceWatch(true,req.sourceWatch.channel_id);
 });
 return router;
}
