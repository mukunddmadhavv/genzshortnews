import path from 'node:path';
import { root } from '@genz/db';
export { root };
export const config = {
 port: Number(process.env.PORT || 6969), host: process.env.HOST || '127.0.0.1',
 origin: process.env.DASHBOARD_ORIGIN || 'http://localhost:6969',
 model: process.env.OPENCODE_MODEL || 'google/gemini-3.8-flash',
 concurrency: Number(process.env.CONCURRENT_JOBS || process.env.MAX_CONCURRENT_JOBS || 3),
 opencode: process.env.OPENCODE_BIN || 'opencode',
 python: process.env.YOUTUBE_PYTHON || path.join(root, '.venv/bin/python'),
 tokenFile: process.env.YOUTUBE_TOKEN_FILE || path.join(root, '.secrets/youtube-genzshotnews-token.json'),
  channelHandle: '@genzshotnews', data: process.env.MEDIA_ROOT || path.join(root, 'data'),
  maxJobMs: Number(process.env.GENERATION_TIMEOUT_MS || 90 * 60 * 1000),
  instagramAppId: process.env.INSTAGRAM_APP_ID || '1736345594332140',
  instagramAppSecret: process.env.INSTAGRAM_APP_SECRET || '59ae7b5b3662810ec883abb048e6aa94',
  instagramToken: process.env.INSTAGRAM_API_TOKEN || process.env.INSTAGRAM_ACCESS_TOKEN || '',
  supabaseUrl: process.env.SUPABASE_URL || '',
  supabaseServiceRoleKey: process.env.SUPABASE_SERVICE_ROLE_KEY || ''
};
