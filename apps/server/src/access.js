import { readFile } from 'node:fs/promises';
import path from 'node:path';
import { root } from './config.js';
import { initAuth } from './auth.js';
await initAuth();
const { password } = JSON.parse(await readFile(path.join(root, '.secrets/dashboard-access.json'), 'utf8'));
console.log(`Studio password: ${password}`);
