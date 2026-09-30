import { randomBytes, scryptSync, timingSafeEqual, createHmac } from 'node:crypto';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { config, root } from './config.js';
const location = path.join(root, '.secrets/dashboard-access.json');
let access;
export async function initAuth() {
 await mkdir(path.dirname(location), { recursive: true, mode: 0o700 });
 try { access = JSON.parse(await readFile(location, 'utf8')); }
 catch (e) {
  if (e.code !== 'ENOENT') throw e;
  const password = randomBytes(18).toString('base64url');
  const salt = randomBytes(16).toString('hex');
  access = { password, salt, hash: scryptSync(password, salt, 64).toString('hex'), signingKey: randomBytes(32).toString('hex') };
  await writeFile(location, JSON.stringify(access), { mode: 0o600, flag: 'wx' });
 }
 const configured = process.env.DASHBOARD_PASSWORD;
 if (configured && configured !== access.password) {
  const salt = randomBytes(16).toString('hex');
  access = { password:configured, salt, hash:scryptSync(configured,salt,64).toString('hex'), signingKey:randomBytes(32).toString('hex') };
  await writeFile(location,JSON.stringify(access),{mode:0o600});
 }
}
export function verifyPassword(value) {
 const hash = scryptSync(String(value || ''), access.salt, 64);
 return timingSafeEqual(hash, Buffer.from(access.hash, 'hex'));
}
const sign = text => createHmac('sha256', access.signingKey).update(text).digest('base64url');
export function issueCookie(res) {
 const expiry = String(Date.now() + 7 * 86400000);
 res.cookie('genz_session', `${expiry}.${sign(expiry)}`, { httpOnly: true, secure: config.origin.startsWith('https:'), sameSite: 'strict', maxAge: 7 * 86400000 });
}
export function authenticated(req) {
 const [expiry, signature] = String(req.cookies?.genz_session || '').split('.');
 if (!expiry || !signature || Number(expiry) < Date.now()) return false;
 const expected = sign(expiry);
 return expected.length === signature.length && timingSafeEqual(Buffer.from(expected), Buffer.from(signature));
}
export function requireAuth(req, res, next) { if (!authenticated(req)) return res.status(401).json({ error: 'Sign in to the studio.' }); next(); }
export function sameOrigin(req, res, next) {
 if (['GET', 'HEAD', 'OPTIONS'].includes(req.method)) return next();
 const origin = req.headers.origin;
 if (origin && origin !== config.origin) return res.status(403).json({ error: 'Origin does not match DASHBOARD_ORIGIN.' });
 if (req.headers['sec-fetch-site'] === 'cross-site') return res.status(403).json({ error: 'Cross-site request rejected.' });
 next();
}
