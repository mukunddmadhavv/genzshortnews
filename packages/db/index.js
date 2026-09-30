import pg from 'pg';
import dotenv from 'dotenv';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
export const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const callerDb = process.env.DATABASE_URL;
dotenv.config({ path: path.join(root, '.env'), quiet: true });
dotenv.config({ path: path.join(root, '.env.dashboard'), override: true, quiet: true });
if (callerDb) process.env.DATABASE_URL = callerDb;
export const pool = new pg.Pool({ connectionString: process.env.DATABASE_URL || 'postgresql://localhost:55432/genz_studio', max: 10 });
export const query = (sql, params) => pool.query(sql, params);
export async function transaction(fn) {
  const client = await pool.connect();
  try { await client.query('BEGIN'); const result = await fn(client); await client.query('COMMIT'); return result; }
  catch (error) { await client.query('ROLLBACK'); throw error; }
  finally { client.release(); }
}
