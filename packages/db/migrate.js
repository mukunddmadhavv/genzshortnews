import { readFile } from 'node:fs/promises';
import { pool } from './index.js';
export async function migrate() { await pool.query(await readFile(new URL('./schema.sql', import.meta.url), 'utf8')); }
if (process.argv[1] === new URL(import.meta.url).pathname) { await migrate(); await pool.end(); console.log('PostgreSQL schema ready.'); }
