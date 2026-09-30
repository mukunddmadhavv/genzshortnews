// Local operator CLI; credentials stay in memory and never enter argv or output.
import { readFile } from 'node:fs/promises';
import path from 'node:path';
import { config, root } from '../apps/server/src/config.js';
import { pool } from '../packages/db/index.js';

const command=process.argv[2] || 'status';
if(!['status','enable','pause','check-youtube'].includes(command))throw new Error('Usage: node scripts/source_watch.mjs [status|enable|pause|check-youtube]');
try {
 const {password}=JSON.parse(await readFile(path.join(root,'.secrets/dashboard-access.json'),'utf8'));
 const base=`http://127.0.0.1:${config.port}`;
 const login=await fetch(`${base}/api/login`,{method:'POST',headers:{'Content-Type':'application/json',Origin:config.origin},body:JSON.stringify({password})});
 if(!login.ok)throw new Error(`Studio login HTTP ${login.status}`);
 const headers={'Content-Type':'application/json',Origin:config.origin,Cookie:login.headers.get('set-cookie').split(';')[0]};
 const route=command==='check-youtube'?'/api/youtube/check':'/api/source-watch';
 const response=await fetch(base+route,{headers,method:command==='status'?'GET':'POST',body:command==='status'?undefined:JSON.stringify(command==='check-youtube'?{}:{enabled:command==='enable'})});
 if(!response.ok)throw new Error(`Studio request HTTP ${response.status}`);
 console.log(JSON.stringify(await response.json(),null,2));
} finally {await pool.end();}
