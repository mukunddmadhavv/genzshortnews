import path from 'node:path';
import { realpath, stat, readdir } from 'node:fs/promises';
import { config } from './config.js';
const extensions = { '.mp4':'video/mp4', '.webm':'video/webm', '.wav':'audio/wav', '.mp3':'audio/mpeg', '.png':'image/png', '.jpg':'image/jpeg', '.jpeg':'image/jpeg', '.json':'application/json', '.txt':'text/plain', '.md':'text/plain' };
export function contained(base, candidate) { const relative = path.relative(base, candidate); return relative !== '..' && !relative.startsWith(`..${path.sep}`) && !path.isAbsolute(relative); }
export async function safeFile(relative) {
 const base = await realpath(config.data);
 const file = await realpath(path.resolve(config.data, relative));
 if (!contained(base, file)) throw new Error('File is outside media storage.');
 const info = await stat(file);
 if (!info.isFile()) throw new Error('Not a file.');
 return { file, info };
}
export async function collectFiles(directory) {
 const files = [];
 for (const entry of await readdir(directory, { withFileTypes: true })) {
  if (entry.name.startsWith('.') || entry.isSymbolicLink()) continue;
  const absolute = path.join(directory, entry.name);
  if (entry.isDirectory()) files.push(...await collectFiles(absolute));
  else if (extensions[path.extname(entry.name).toLowerCase()]) {
   const info = await stat(absolute);
   files.push({ absolute, name:entry.name, path:path.relative(config.data, absolute), mime:extensions[path.extname(entry.name).toLowerCase()], size:info.size });
  }
 }
 return files;
}
