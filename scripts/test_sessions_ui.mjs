import {chromium} from '@playwright/test';
import {spawn} from 'node:child_process';
import assert from 'node:assert/strict';
import {root} from '../packages/db/index.js';
const child=spawn(process.execPath,[`${root}/node_modules/vite/bin/vite.js`,'preview','--host','127.0.0.1','--port','4180','--strictPort'],{cwd:`${root}/apps/web`,stdio:'ignore'});
let browser;
try{
 for(let i=0;i<50;i++){try{if((await fetch('http://127.0.0.1:4180/sessions')).ok)break;}catch{}await new Promise(r=>setTimeout(r,100));}
 browser=await chromium.launch({headless:true});const page=await browser.newPage({viewport:{width:1440,height:1000}}),errors=[];
 page.on('pageerror',e=>errors.push(e.message));
 const sessions=[{id:'session-one',title:'Alpha story',input:'Original topic',status:'ready',source_type:'youtube',opencode_session_id:'ses_original',revisions:1,updated_at:'2026-09-30T12:00:00Z'},{id:'session-two',title:'Zulu story',input:'Other topic',status:'failed',source_type:'topic',revisions:0,updated_at:'2026-09-30T13:00:00Z'}];
 const library=[{sessionId:'session-one',episode:'alpha',file:'final.mp4',status:'ready'},{sessionId:null,episode:'Unimported episode',file:'final.mp4',status:'unimported'}];
 let resumed=false,imported=false;
 await page.route('**/api/**',async route=>{
  const req=route.request(),url=new URL(req.url());let data={};
  if(url.pathname==='/api/auth')data={authenticated:true};
  if(url.pathname==='/api/settings')data={channel:'@genzshotnews',tokenPresent:true};
  if(url.pathname==='/api/sessions')data=sessions;
  if(url.pathname==='/api/library')data=library;
  if(url.pathname==='/api/library/import'){imported=true;library[1].sessionId='session-import';data={id:'session-import'};}
  if(url.pathname==='/api/sessions/session-one/resume'){resumed=true;assert.equal(req.postDataJSON().instructions,'Make the intro punchier');data={jobId:'new-job'};}
  else if(url.pathname.startsWith('/api/sessions/'))data={...(sessions.find(s=>url.pathname.endsWith(s.id))||{id:'session-import',title:'Unimported episode',source_type:'import',status:'ready'}),artifacts:[],jobs:[],events:[],publications:[]};
  await route.fulfill({json:data});
 });
 await page.goto('http://127.0.0.1:4180/sessions');
 await page.getByRole('heading',{name:'Sessions & videos.'}).waitFor();
 await page.getByRole('heading',{name:'Unimported episode',exact:true}).waitFor();
 assert.equal(await page.locator('.unified-session-row').count(),3,'Imported episode must merge into its session');
 assert.equal(await page.getByRole('button',{name:'Media library',exact:true}).count(),0);
 await page.getByLabel('Sort by',{exact:true}).selectOption('name-asc');
 assert.equal(await page.locator('.session-row-main h3').first().textContent(),'Alpha story');
 await page.getByLabel('Search sessions and videos').fill('Alpha');
 assert.equal(await page.locator('.unified-session-row').count(),1);
 await page.getByRole('button',{name:'Chat / edit',exact:true}).click();
 await page.getByPlaceholder('Make the opening punchier, replace the third image, fix a name…').fill('Make the intro punchier');
 await page.getByRole('button',{name:'Resume',exact:true}).click();
 await page.waitForTimeout(100);assert.equal(resumed,true);
 await page.getByRole('button',{name:'Close',exact:true}).click();
 await page.getByLabel('Search sessions and videos').fill('Unimported');
 await page.getByRole('button',{name:'Import / edit',exact:true}).click();
 await page.getByRole('button',{name:'Find original session',exact:true}).waitFor();assert.equal(imported,true);
 await page.setViewportSize({width:390,height:844});
 assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth),true);
 await page.reload();await page.getByRole('heading',{name:'Sessions & videos.'}).waitFor();
 assert.deepEqual(errors,[]);console.log('PASS: /sessions rows, deduplication, sorting, search, inline original-session chat, import/link workflow, mobile and reload.');
}finally{await browser?.close();child.kill('SIGTERM');}
