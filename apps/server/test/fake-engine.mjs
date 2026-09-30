#!/usr/bin/env node
// Integration fixture: deterministic real MP4, no model/API calls.
import {writeFile,copyFile,readFile} from 'node:fs/promises';
import path from 'node:path';
const args=process.argv.slice(2);
if(args.includes('--token-file')) {
 const spec=JSON.parse(await readFile(args[args.indexOf('--spec')+1],'utf8'));
 console.log(JSON.stringify({type:'published',youtubeId:'test-video-id',channelId:'test-channel',privacy:spec.privacy}));
 process.exit(0);
}
if(args.includes('--video') || args.includes('--caption')) {
 console.log(JSON.stringify({type:'published',platform:'instagram',instagramMediaId:'test-ig-media-id',mediaId:'test-ig-media-id'}));
 process.exit(0);
}
const prompt=args.at(-1);
if(prompt.startsWith('Create YouTube publishing copy')) {
 const file=prompt.match(/Write only (.+) with JSON/)[1];
 await writeFile(file,JSON.stringify({caption:'Existing episode',description:'Existing story with source attribution',hashtags:['#shorts','#genzshortnews','#News']}));
 process.exit(0);
}
const directory=prompt.match(/Write ALL NEW episode files, source records, images, audio and renders inside:\n([^\n]+)/)[1];
const index=args.indexOf('--session');
const sessionID=index>=0?args[index+1]:'ses_integration123';
console.log(JSON.stringify({type:'step_start',sessionID}));
console.log(JSON.stringify({type:'text',sessionID,part:{text:index>=0?'Resuming existing session':'Starting session'}}));
if(prompt.includes('CANCEL_FIXTURE'))await new Promise(resolve=>setTimeout(resolve,60000));
await copyFile(process.env.TEST_VIDEO,path.join(directory,'final.mp4'));
await writeFile(path.join(directory,'dashboard-result.json'),JSON.stringify({video:'final.mp4',title:'Integration test video',description:'Test only',summary:'Fixture render',checks:{decode:true,dimensions:true}}));
