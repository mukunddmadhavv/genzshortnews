// Operator-only diagnostics. Callback tokens and signing secrets never leave stdout.
import {createHmac} from 'node:crypto';
import {query,pool} from '../packages/db/index.js';
import {config} from '../apps/server/src/config.js';
import {channelTopic,subscribe,WEBHOOK_PROBE} from '../apps/server/src/source-watch.js';

const command=process.argv[2] || 'status';
if(!['status','probe','renew'].includes(command))throw new Error('Usage: node scripts/webhook_doctor.mjs [status|probe|renew]');
try{
 for(const watch of (await query('SELECT * FROM source_watches WHERE enabled=true ORDER BY created_at')).rows){
  if(command==='renew'){
   await subscribe(watch);
   console.log(JSON.stringify({channel:watch.title,renewal:'requested',topic:channelTopic(watch.channel_id)}));
   continue;
  }
  if(command==='probe'){
   const signature='sha1='+createHmac('sha1',watch.hub_secret).update(WEBHOOK_PROBE).digest('hex');
   const response=await fetch(`${new URL(config.origin).origin}/webhooks/youtube/${watch.callback_token}`,{method:'POST',redirect:'manual',signal:AbortSignal.timeout(20000),headers:{'Content-Type':'application/atom+xml','X-Hub-Signature':signature},body:WEBHOOK_PROBE});
   const {rows:[result]}=await query('SELECT last_probe_at,webhook_count FROM source_watches WHERE channel_id=$1',[watch.channel_id]);
   console.log(JSON.stringify({channel:watch.title,probeHttp:response.status,...result}));
   if(response.status!==204 || !result.last_probe_at)throw new Error('Public callback probe failed');
   continue;
  }
  const url=new URL('https://pubsubhubbub.appspot.com/subscription-details');
  url.searchParams.set('hub.callback',`${new URL(config.origin).origin}/webhooks/youtube/${watch.callback_token}`);
  url.searchParams.set('hub.topic',channelTopic(watch.channel_id));url.searchParams.set('hub.secret',watch.hub_secret);
  const response=await fetch(url,{signal:AbortSignal.timeout(20000)});
  const html=(await response.text()).replaceAll(watch.callback_token,'[redacted]').replaceAll(watch.hub_secret,'[redacted]');
  const text=html.replace(/<[^>]+>/g,' ').replace(/\s+/g,' ');
  const start=text.indexOf('Subscription Details'),end=text.indexOf('These legal disclaimers');
  console.log(JSON.stringify({channel:watch.title,http:response.status,hubReport:text.slice(Math.max(0,start),end>start?end:undefined),local:{lastVerified:watch.last_verified_at,lastDelivery:watch.last_webhook_at,deliveries:watch.webhook_count,rejected:watch.rejected_webhook_count,lastProbe:watch.last_probe_at}}));
 }
}finally{await pool.end();}
