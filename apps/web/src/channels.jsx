import React, { useEffect, useState } from 'react';
import { Plus, Radio, Youtube, Download, ArrowUpRight, RefreshCw, Pause, Play, Clock, Trash2 } from 'lucide-react';
import './channels.css';

const date = value => value ? new Date(value).toLocaleString() : 'Not yet';
const webhook = channel => !channel.enabled ? 'Paused' : channel.lease_expires_at && new Date(channel.lease_expires_at) > new Date() ? (channel.last_webhook_at ? 'Receiving notifications' : 'Verified · awaiting first notification') : 'Subscription pending';

export function Channels({ api, open }) {
 const [data,setData]=useState(null),[error,setError]=useState(''),[url,setUrl]=useState(''),[busy,setBusy]=useState(''),[notice,setNotice]=useState(''),[confirmDelete,setConfirmDelete]=useState('');
 const load=async()=>setData(await api('/channels'));
 useEffect(()=>{
  let live=true;
  const refresh=()=>api('/channels').then(value=>{if(live)setData(value);}).catch(e=>{if(live)setError(e.message);});
  refresh();const timer=setInterval(refresh,10000);
  return ()=>{live=false;clearInterval(timer);};
 },[]);
 const add=async event=>{
  event.preventDefault();setBusy('add');setError('');setNotice('');
  try{
   const result=await api('/channels',{url});
   setNotice(result.created ? `${result.channel.title} added. Watching new Shorts from now.` : `${result.channel.title} is already in your channels.`);
   setUrl('');await load();
  }catch(e){setError(e.message);}finally{setBusy('');}
 };
 const toggle=async channel=>{
  setBusy(channel.channel_id);setError('');
  try{await api(`/channels/${channel.channel_id}`,{enabled:!channel.enabled},'PATCH');await load();}
  catch(e){setError(e.message);}finally{setBusy('');}
 };
 const remove=async channel=>{
  setBusy(channel.channel_id);setError('');setNotice('');
  try{
   await api(`/channels/${channel.channel_id}`,null,'DELETE');
   setConfirmDelete('');
   setNotice(`${channel.title} removed from your channels.`);
   await load();
  }catch(e){setError(e.message);}finally{setBusy('');}
 };
 return <div className="channel-page">
  <div className="page-heading">
   <div><p className="eyebrow">AUTOMATED SOURCE CHANNELS</p><h1>Channels on your radar<span>.</span></h1><p>Every new Short. Your skill. A fresh OpenCode session.</p></div>
   <button className="secondary" onClick={()=>load().catch(e=>setError(e.message))}><RefreshCw size={16}/> Refresh</button>
  </div>
  {error && <p className="error" role="alert">{error}</p>}
  {notice && <p className="success" role="status">{notice}</p>}
  <section className="stats" aria-label="Channel totals">
   {[
    ['Shorts fetched',data?.totals.fetched,Download],['Last 24 hours',data?.totals.fetched_today,Clock],
    ['In production',data?.totals.in_progress,Radio],['Published',data?.totals.published,Youtube]
   ].map(([label,value,Icon])=><div key={label}><span>{label}<Icon size={18}/></span><strong>{value ?? '—'}</strong></div>)}
  </section>
  <section className="channel-add">
   <div><h2>Add a YouTube channel</h2><p>Paste a channel URL, @handle or channel ID. New Shorts will follow your current pipeline and automatically upload to @genzshotnews as Public.</p></div>
   <form onSubmit={add}><label htmlFor="channel-url">YouTube channel</label><div className="channel-input-row"><input id="channel-url" value={url} onChange={e=>setUrl(e.target.value)} placeholder="https://www.youtube.com/@NeonManShorts/shorts" required maxLength={500}/><button className="primary" disabled={!!busy}><Plus size={18}/>{busy==='add'?'Adding…':'Add channel'}</button></div></form>
   <small>Watching starts when added. Webhook deliveries trigger an immediate check; backup polling runs every {data ? data.pollSeconds / 60 : 5} minutes. Counts include unique new Shorts accepted into the pipeline, not the channel’s old uploads.</small>
  </section>
  <div className="section-heading"><h2>Source channels <span>{data?.channels.length ?? '—'}</span></h2><span>{data?.totals.active ?? 0} watching</span></div>
  {!data ? <p>Loading channels…</p> : !data.channels.length ? <div className="empty"><Youtube size={30}/><h3>No source channels</h3><p>Add a YouTube channel above to start watching for new Shorts.</p></div> : <div className="source-channel-grid">{data.channels.map(channel=><article className="source-channel-card" key={channel.channel_id}>
   <div className="source-channel-heading"><div className="source-channel-icon"><Youtube size={24}/></div><div><h3>{channel.title}</h3><a href={channel.channel_url} target="_blank" rel="noreferrer">View source channel <ArrowUpRight size={13}/></a></div><span className={`badge ${channel.enabled?'verified':'paused'}`}><i/>{channel.enabled?'watching':'paused'}</span></div>
   <div className="source-channel-counts"><div><strong>{channel.fetched}</strong><span>Shorts fetched</span></div><div><strong>{channel.in_progress}</strong><span>In production</span></div><div><strong>{channel.published}</strong><span>Published</span></div></div>
   <dl><div><dt>Delivery</dt><dd>{webhook(channel)}</dd></div><div><dt>Last feed check</dt><dd>{date(channel.last_poll_at)}</dd></div><div><dt>Last webhook</dt><dd>{date(channel.last_webhook_at)}</dd></div><div><dt>Watching since</dt><dd>{date(channel.started_at)}</dd></div></dl>
   <p className="muted">{channel.webhook_count ?? 0} signed notifications · {channel.rejected_webhook_count ?? 0} rejected requests<br/>Callback test: {date(channel.last_probe_at)}</p>
   {channel.subscription_error && <p className="error" role="alert">{channel.subscription_error}</p>}
   {channel.last_webhook_error && <p className="error" role="alert">{channel.last_webhook_error}</p>}
   {channel.last_error && <p className="error" role="alert">{channel.last_error}</p>}
   {channel.needs_attention>0 && <p>{channel.needs_attention} session(s) need attention. Open the session to resume or retry.</p>}
   <div className="source-channel-actions">
    <button className="secondary" disabled={!!busy} onClick={()=>toggle(channel)} aria-label={`${channel.enabled?'Pause':'Resume'} ${channel.title}`}>{channel.enabled?<Pause size={15}/>:<Play size={15}/>} {channel.enabled?'Pause watcher':'Resume watcher'}</button>
    {confirmDelete === channel.channel_id ? (
     <div className="confirm-delete-group">
      <button className="secondary danger-confirm-btn" disabled={!!busy} onClick={()=>remove(channel)} aria-label={`Confirm delete ${channel.title}`}><Trash2 size={15}/> {busy===channel.channel_id?'Deleting…':'Confirm delete'}</button>
      <button className="secondary cancel-btn" disabled={!!busy} onClick={()=>setConfirmDelete('')} aria-label={`Cancel delete ${channel.title}`}>Cancel</button>
     </div>
    ) : (
     <button className="secondary danger-btn" disabled={!!busy} onClick={()=>setConfirmDelete(channel.channel_id)} aria-label={`Delete ${channel.title}`}><Trash2 size={15}/> Delete channel</button>
    )}
   </div>
  </article>)}</div>}
  <p className="muted channel-explainer">Pausing stops discovery; existing jobs continue. Resuming catches up on unseen Shorts still in the recent feed. Public is the requested visibility; YouTube’s actual result is recorded in each session.</p>
  <div className="section-heading"><h2>Fetched Shorts <span>{data?.totals.fetched ?? 0}</span></h2><span>Latest 100</span></div>
   <p className="muted">Captured by identifies the check that first queued the Short: a webhook-triggered feed check or backup polling. Later duplicate notifications do not change it.</p>
   {data && !data.recent.length ? <div className="empty"><Radio size={30}/><h3>Listening for the next Short</h3><p>New source videos will appear here with their generation session and published video.</p></div> : <div className="channel-table-wrap"><table className="channel-table"><thead><tr><th>Source Short</th><th>Channel</th><th>Fetched</th><th>Captured by</th><th>Pipeline</th><th>Output</th></tr></thead><tbody>{data?.recent.map(video=><tr key={`${video.channel_id}:${video.video_id}`}>
   <td><a href={`https://www.youtube.com/shorts/${video.video_id}`} target="_blank" rel="noreferrer">{video.title}<ArrowUpRight size={13}/></a></td><td>{video.channel_title}</td><td>{date(video.created_at)}</td><td><span className={`badge ${video.capture_source==='webhook'?'verified':''}`}>{video.capture_source==='webhook'?'Webhook':video.capture_source==='polling'?'Polling':'Unknown'}</span></td><td><span className={`badge ${video.status}`}><i/>{video.status}</span><button className="text-button" onClick={()=>open(video.session_id)}>Open session <ArrowUpRight size={13}/></button></td><td>{video.youtube_id?<a href={`https://www.youtube.com/shorts/${video.youtube_id}`} target="_blank" rel="noreferrer">View upload <ArrowUpRight size={13}/></a>:'—'}</td>
  </tr>)}</tbody></table></div>}
 </div>;
}
