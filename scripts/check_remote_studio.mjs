import {chromium} from '@playwright/test';
import assert from 'node:assert/strict';
const browser=await chromium.launch({headless:true,channel:'chrome'});
try {
 const page=await browser.newPage({viewport:{width:1440,height:1000}});
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto('https://u.trypitch.co');
 await page.getByLabel('Studio password').fill('yogi');
 await page.getByRole('button',{name:'Enter studio'}).click();
 await page.getByRole('heading',{name:'Stories in the making.'}).waitFor();
 await page.locator('.session-card').first().waitFor();
 await page.waitForFunction(()=>[...document.querySelectorAll('.brand img,.channel-banner img')].every(i=>i.complete&&i.naturalWidth));
 console.log('Remote sessions visible:',await page.locator('.session-card').count());
 await page.locator('.session-card').first().click();
 await page.locator('video').waitFor();
 await page.waitForFunction(()=>document.querySelector('video')?.readyState>=1);
 assert.equal(await page.locator('video').evaluate(v=>v.videoWidth),1080);
 const videoURL=await page.locator('video').getAttribute('src');
 const range=await page.request.get('https://u.trypitch.co'+videoURL,{headers:{Range:'bytes=0-99'}});
 assert.equal(range.status(),206);
 const sessions=await page.request.get('https://u.trypitch.co/api/opencode/sessions');
 const conversations=await sessions.json();assert.ok(conversations.length>=15);
 console.log('Migrated project conversations visible:',conversations.length);
 await page.getByRole('button',{name:'Connections',exact:true}).click();
 await page.getByRole('button',{name:'Verify connection'}).click();
 await page.getByText('Connected to GENZ SHORT NEWS (@genzshotnews)').waitFor({timeout:60000});
 assert.deepEqual(errors,[]);
 console.log('PASS: public HTTPS login, branding, database sessions, 1080p video, range seeking, OpenCode history and YouTube verification.');
} finally {await browser.close();}
