import { spawn } from 'node:child_process';
export function execute(binary, args, { cwd, env, timeout = 60000, onLine, signal } = {}) {
 return new Promise((resolve, reject) => {
  const child = spawn(binary, args, { cwd, env:env || process.env, stdio:['ignore','pipe','pipe'], detached:true });
  let output = '', pending = '', settled = false;
  const kill = () => { try { process.kill(-child.pid, 'SIGTERM'); } catch {} };
  let forced;
  const abort = () => { kill(); forced = setTimeout(() => { try { process.kill(-child.pid, 'SIGKILL'); } catch {} }, 3000); forced.unref(); };
  signal?.addEventListener('abort', abort, { once:true });
  if (signal?.aborted) abort();
  let timedOut = false;
  const timer = setTimeout(() => { timedOut = true; abort(); }, timeout);
  const cleanup = () => { clearTimeout(timer); clearTimeout(forced); signal?.removeEventListener('abort', abort); };
  child.stdout.on('data', data => {
   const text = data.toString(); output = (output + text).slice(-2_000_000);
   pending += text;
   let index;
   while ((index = pending.indexOf('\n')) >= 0) { onLine?.(pending.slice(0,index)); pending = pending.slice(index+1); }
  });
  // Never persist raw stderr: provider errors can contain credentials.
  child.stderr.on('data', () => {});
  child.on('error', error => { settled = true; cleanup(); reject(new Error(`Unable to start ${binary}: ${error.code || 'process error'}`)); });
  child.on('close', code => {
   if (settled) return;
   cleanup(); if (pending) onLine?.(pending);
   if (signal?.aborted) reject(new Error('Job cancelled.'));
   else if (timedOut) reject(new Error('Job timed out. Resume the session to continue.'));
   else if (code !== 0) reject(new Error(`${binary.split('/').pop()} exited with code ${code}. Check provider authentication, permissions and dependencies.`));
   else resolve(output);
  });
 });
}
