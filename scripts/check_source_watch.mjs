import { chromium } from '@playwright/test';
import { readFile } from 'node:fs/promises';
import path from 'node:path';
import assert from 'node:assert/strict';
import { config, root } from '../apps/server/src/config.js';
import { pool } from '../packages/db/index.js';

const browser=await chromium.launch({headless:true});
try {
 const {password}=JSON.parse(await readFile(path.join(root,'.secrets/dashboard-access.json'),'utf8'));
 const page=await browser.newPage({viewport:{width:1440,height:1000}});
 const errors=[];page.on('pageerror',error=>errors.push(error.message));
 await page.goto(config.origin+'/channel');
 await page.getByLabel('Studio password').fill(password);
 await page.getByRole('button',{name:'Enter studio'}).click();
 await page.getByRole('heading',{name:'Channels on your radar.'}).waitFor();
 await page.getByRole('button',{name:'Pause Neon Man Shorts',exact:true}).waitFor();
 await page.getByText(/Verified · awaiting first notification|Receiving notifications/).first().waitFor();
 const dashboard=await(await page.request.get(config.origin+'/api/channels')).json();
 assert.equal(await page.locator('.stats > div').first().locator('strong').textContent(),String(dashboard.totals.fetched));
 await page.reload();await page.getByRole('heading',{name:'Channels on your radar.'}).waitFor();
 assert.deepEqual(errors,[]);
 console.log('PASS: public dashboard login, enabled channel watcher controls, confirmed webhook subscription, no browser errors.');
} finally {await browser.close();await pool.end();}
