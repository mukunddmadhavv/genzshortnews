import React, { useEffect, useState } from 'react';
import { Plus, Film, Search, X, MessageSquare, ChevronDown, ChevronUp, ArrowUpRight, Radio, Youtube, Layers, RefreshCw } from 'lucide-react';
import './sessions.css';

// An imported episode and its production session are one row. Unimported files
// remain available until the existing idempotent import endpoint links them.
export function mergeSessions(sessions, library) {
 const bySession=new Map(sessions.map(s=>[s.id,{...s,key:s.id,episodes:[]}]));
 const unimported=[];
 for(const item of library){
  if(item.sessionId){
   if(!bySession.has(item.sessionId))bySession.set(item.sessionId,{id:item.sessionId,key:item.sessionId,title:item.episode,input:'',status:item.status,created_at:item.createdAt,updated_at:item.updatedAt,youtube_id:item.youtubeType==='published'?item.youtubeId:null,source_type:'import',episodes:[]});
   bySession.get(item.sessionId).episodes.push(item);
  }else unimported.push({key:`episode:${item.episode}/${item.file}`,title:item.episode,input:item.file,status:'unimported',source_type:'import',created_at:item.createdAt,updated_at:item.updatedAt,episodes:[item],revisions:1});
 }
 return [...bySession.values(),...unimported];
}

const priorities={generating:0,publishing:1,queued:2,failed:3,paused:4,ready:5,published:6,unimported:7};
export function filterSessions(rows,search,status,sort){
 const text=search.trim().toLowerCase();
 return rows.filter(row=>(status==='all'||row.status===status)&&(!text||[row.title,row.input,row.status,row.opencode_session_id,...row.episodes.map(e=>`${e.episode} ${e.file}`)].join(' ').toLowerCase().includes(text))).sort((a,b)=>{
  if(sort==='name-asc')return a.title.localeCompare(b.title);
  if(sort==='name-desc')return b.title.localeCompare(a.title);
  if(sort==='status')return (priorities[a.status]??99)-(priorities[b.status]??99)||a.title.localeCompare(b.title);
  const time=row=>new Date((sort==='created'?row.created_at:row.updated_at)||row.created_at||0).getTime();
  return sort==='oldest'?time(a)-time(b):time(b)-time(a);
 });
}
const date=value=>value?new Date(value).toLocaleString('en-GB',{timeZone:'Asia/Kolkata'})+' IST':'—';

function SessionEditor({id,api,render}){
 const [detail,setDetail]=useState(null),[error,setError]=useState('');
 const refresh=async()=>setDetail(await api(`/sessions/${id}`));
 useEffect(()=>{
  let live=true;
  const load=()=>api(`/sessions/${id}`).then(s=>{if(live){setDetail(s);setError('');}}).catch(e=>{if(live)setError(e.message);});
  load();const timer=setInterval(load,2500);return()=>{live=false;clearInterval(timer);};
 },[id]);
 return <div className="session-inline-editor">{error&&<p className="error" role="alert">{error}</p>}{detail?render(detail,refresh):<p>Loading video, chat and revisions…</p>}</div>;
}

export function Sessions({sessions,api,create,refresh,renderSession}){
 const [library,setLibrary]=useState([]),[loaded,setLoaded]=useState(false),[error,setError]=useState(''),[search,setSearch]=useState(''),[sort,setSort]=useState('newest'),[status,setStatus]=useState('all'),[expanded,setExpanded]=useState(null),[busy,setBusy]=useState(null);
 useEffect(()=>{
  let live=true;
  const load=()=>api('/library').then(items=>{if(live){setLibrary(items);setLoaded(true);setError('');}}).catch(e=>{if(live)setError(e.message);});
  load();const timer=setInterval(load,4000);return()=>{live=false;clearInterval(timer);};
 },[]);
 const rows=mergeSessions(sessions,library),filtered=filterSessions(rows,search,status,sort);
 const counts=rows.reduce((all,row)=>({...all,[row.status]:(all[row.status]||0)+1}),{});
 const open=async row=>{
  if(row.id){setExpanded(expanded===row.id?null:row.id);return;}
  setBusy(row.key);setError('');
  try{
   const item=row.episodes[0],result=await api('/library/import',{episode:item.episode,file:item.file});
   const items=await api('/library');setLibrary(items);await refresh();setExpanded(result.id);
  }catch(e){setError(e.message);}finally{setBusy(null);}
 };
 return <div className="sessions-page">
  <div className="channel-banner"><img src="/branding/banner.png" alt="GENZ SHORT NEWS — Big stories. Short takes."/></div>
  <div className="page-heading"><div><p className="eyebrow">YOUR COMPLETE VIDEO WORKSPACE</p><h1>Sessions & videos<span>.</span></h1><p>Generated stories and existing episodes, together. Preview, chat, revise and publish from any row.</p></div><button className="primary" onClick={create}><Plus size={18}/> New session</button></div>
  {error&&<p className="error" role="alert">{error}</p>}
  <section className="stats">{[['Total sessions & videos',rows.length,Layers],['In production',(counts.queued||0)+(counts.generating||0)+(counts.publishing||0),Radio],['Ready to review',counts.ready||0,Film],['Published',rows.filter(r=>r.youtube_id||r.status==='published').length,Youtube]].map(([label,value,Icon])=><div key={label}><span>{label}<Icon size={18}/></span><strong>{value}</strong></div>)}</section>
  <div className="library-controls"><div className="library-search"><Search size={16}/><input aria-label="Search sessions and videos" placeholder="Search stories, episodes, files or status…" value={search} onChange={e=>setSearch(e.target.value)}/>{search&&<button className="icon" aria-label="Clear search" onClick={()=>setSearch('')}><X size={15}/></button>}</div><div className="library-sort"><label htmlFor="sessions-sort">Sort by</label><select id="sessions-sort" value={sort} onChange={e=>setSort(e.target.value)}><option value="newest">Recently updated</option><option value="created">Newest created</option><option value="oldest">Oldest first</option><option value="name-asc">Title (A–Z)</option><option value="name-desc">Title (Z–A)</option><option value="status">Status</option></select></div><button className="secondary" aria-label="Refresh sessions" onClick={()=>Promise.all([refresh(),api('/library').then(setLibrary)]).catch(e=>setError(e.message))}><RefreshCw size={16}/></button></div>
  <div className="library-status-pills">{['all','queued','generating','publishing','ready','published','paused','failed','unimported'].map(value=><button key={value} className={`status-pill ${status===value?'active':''}`} onClick={()=>setStatus(value)}><span>{value==='all'?'All':value[0].toUpperCase()+value.slice(1)}</span><span className="status-pill-count">{value==='all'?rows.length:counts[value]||0}</span></button>)}</div>
  <p className="muted">{filtered.length} of {rows.length} sessions and videos · Times in IST</p>
  {!loaded&&!rows.length?<p>Loading sessions and library…</p>:!filtered.length?<div className="empty"><Film size={30}/><h3>No matching sessions or videos</h3><p>Adjust your filters or create a new session. Existing episode renders appear here automatically.</p></div>:<div className="unified-session-list">{filtered.map(row=>{
   const isOpen=expanded===row.id&&!!row.id;
   const source=/^https?:\/\//.test(row.input||'')?row.input:row.episodes.find(e=>e.youtubeType==='reference')?.youtubeUrl;
   const published=row.youtube_id?`https://youtu.be/${row.youtube_id}`:row.episodes.find(e=>e.youtubeType==='published')?.youtubeUrl;
   const instaUrl=row.instagram_url||(row.instagram_media_id?`https://www.instagram.com/reel/${row.instagram_media_id}/`:null);
   return <article className="unified-session-row" key={row.key}>
    <div className="session-row-summary"><div className="library-icon"><Film size={22}/></div><div className="session-row-main"><h3>{row.title}</h3><p>{row.input}</p><div className="session-row-meta"><span>{row.revisions??row.episodes.length} revision(s)</span><span>{date(row.updated_at||row.created_at)}</span>{row.episodes.map(e=><span key={`${e.episode}/${e.file}`}><code>{e.episode}/{e.file}</code>{e.size>0?` · ${(e.size/1048576).toFixed(1)} MB`:''}</span>)}</div><div className="session-row-links">{source&&<a href={source} target="_blank" rel="noreferrer">Reference <ArrowUpRight size={13}/></a>}{published&&<a href={published} target="_blank" rel="noreferrer">YouTube <ArrowUpRight size={13}/></a>}{instaUrl&&<a href={instaUrl} target="_blank" rel="noreferrer">Instagram Reel <ArrowUpRight size={13}/></a>}</div></div><span className={`badge ${row.status}`}><i/>{row.status}</span><button className="secondary" disabled={!!busy} aria-expanded={isOpen} onClick={()=>open(row)}>{isOpen?<ChevronUp size={16}/>:<MessageSquare size={16}/>} {isOpen?'Close':row.id?'Chat / edit':'Import / edit'}{!isOpen&&<ChevronDown size={14}/>}</button></div>
    {isOpen&&<SessionEditor id={row.id} api={api} render={(detail,reload)=>renderSession(detail,reload,()=>setExpanded(null))}/>}
   </article>;
  })}</div>}
 </div>;
}
