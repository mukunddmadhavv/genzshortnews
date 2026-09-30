import pg from 'pg';
import dotenv from 'dotenv';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
export const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
// Explicit service/test environment takes precedence over both dotenv files.
const callerEnv = {...process.env};
dotenv.config({ path: path.join(root, '.env'), quiet: true });
dotenv.config({ path: path.join(root, '.env.dashboard'), override: true, quiet: true });
Object.assign(process.env, callerEnv);
export const pool = new pg.Pool({ connectionString: process.env.DATABASE_URL || 'postgresql://localhost:55432/genz_studio', max: 10 });
export const query = (sql, params) => pool.query(sql, params);
export async function transaction(fn) {
  const client = await pool.connect();
  try { await client.query('BEGIN'); const result = await fn(client); await client.query('COMMIT'); return result; }
  catch (error) { await client.query('ROLLBACK'); throw error; }
  finally { client.release(); }
}
