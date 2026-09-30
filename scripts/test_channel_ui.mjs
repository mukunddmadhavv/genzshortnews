// Browser regression test against a built frontend, with isolated API fixtures.
import {chromium} from '@playwright/test';
import {spawn} from 'node:child_process';
import assert from 'node:assert/strict';
import {root} from '../packages/db/index.js';
const child=spawn(process.execPath,[`${root}/node_modules/vite/bin/vite.js`,'preview','--host','127.0.0.1','--port','4179','--strictPort'],{cwd:`${root}/apps/web`,stdio:'ignore'});
let browser;
try {
 for(let i=0;i<50;i++){try{if((await fetch('http://127.0.0.1:4179/channel')).ok)break;}catch{}await new Promise(r=>setTimeout(r,100));}
 browser=await chromium.launch({headless:true});
 const page=await browser.newPage({viewport:{width:1440,height:1000}}),errors=[];
 page.on('pageerror',e=>errors.push(e.message));
 const channel={channel_id:'UCg48OIfYWyNrUAIM2CLeWLg',title:'Neon Man Shorts',channel_url:'https://www.youtube.com/@NeonManShorts/shorts',enabled:true,fetched:4,fetched_today:2,published:1,in_progress:3,needs_attention:0,lease_expires_at:new Date(Date.now()+86400000).toISOString()};
 const channels=[channel];
 await page.route('**/api/**',async route=>{
  const req=route.request(),url=new URL(req.url());let data={};
  if(url.pathname==='/api/auth')data={authenticated:true};
  if(url.pathname==='/api/sessions')data=[];
  if(url.pathname==='/api/library')data=[];
  if(url.pathname==='/api/settings')data={channel:'@genzshotnews',tokenPresent:true};
  if(url.pathname==='/api/channels'){
   if(req.method()==='POST'){
    const value={...channel,channel_id:'UCabcdefghijklmnopqrstuv',title:'Second channel',fetched:0,fetched_today:0,published:0,in_progress:0};channels.push(value);data={created:true,channel:value};
   }else data={channels,pollSeconds:300,totals:{fetched:4,fetched_today:2,published:1,in_progress:3,active:channels.filter(c=>c.enabled).length},recent:[{channel_id:channel.channel_id,video_id:'abcdefghijk',title:'Polling example',capture_source:'polling',status:'ready'},{channel_id:channel.channel_id,video_id:'lmnopqrstuv',title:'Webhook example',capture_source:'webhook',status:'ready'}]};
  }
  if(req.method()==='PATCH'){const c=channels.find(c=>url.pathname.endsWith(c.channel_id));c.enabled=req.postDataJSON().enabled;data=c;}
  await route.fulfill({json:data});
 });
 await page.goto('http://127.0.0.1:4179/channel');
 await page.getByRole('heading',{name:'Channels on your radar.'}).waitFor();
 assert.equal(await page.locator('.stats > div').first().locator('strong').textContent(),'4');
 await page.getByRole('columnheader',{name:'Captured by'}).waitFor();
 await page.getByText('Polling',{exact:true}).waitFor();
 await page.getByText('Webhook',{exact:true}).waitFor();
 await page.getByText(/backup polling runs every 5 minutes/).waitFor();
 await page.getByLabel('YouTube channel',{exact:true}).fill('@SecondChannel');
 await page.getByRole('button',{name:'Add channel',exact:true}).click();
 await page.getByRole('heading',{name:'Second channel',exact:true}).waitFor();
 await page.getByRole('button',{name:'Pause Second channel',exact:true}).click();
 await page.getByRole('button',{name:'Resume Second channel',exact:true}).waitFor();
 assert.equal(channels[0].enabled,true);
 await page.getByRole('button',{name:'Resume Second channel',exact:true}).click();
 await page.getByRole('button',{name:'Pause Second channel',exact:true}).waitFor();
 await page.reload();await page.getByRole('heading',{name:'Channels on your radar.'}).waitFor();
 await page.getByRole('button',{name:'Sessions',exact:true}).click();
 assert.equal(new URL(page.url()).pathname,'/sessions');
 await page.goBack();await page.getByRole('heading',{name:'Channels on your radar.'}).waitFor();
 await page.setViewportSize({width:390,height:844});
 assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth),true,'Mobile page must not overflow');
 assert.deepEqual(errors,[]);
 console.log('PASS: /channel deep link, counts, add channel, independent pause/resume, reload/back navigation, mobile layout.');
} finally {await browser?.close();child.kill('SIGTERM');}
