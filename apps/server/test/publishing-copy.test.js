import {test} from 'node:test';
import assert from 'node:assert/strict';
import {publishingCopy} from '../src/publishing-copy.js';
test('publishing copy enforces required hashtags and API length limits',()=>{
 const result=publishingCopy({caption:'A'.repeat(130),description:'Story '.repeat(1000)+' #SHORTS',hashtags:['#AI','#Technology','#AI']});
 assert.ok(result.title.length<=100);
 assert.ok(result.description.length<=5000);
 assert.deepEqual(result.hashtags,['#shorts','#genzshortnews','#AI','#Technology']);
 assert.ok(result.description.endsWith('#shorts #genzshortnews #AI #Technology'));
});
test('missing description cannot silently become ready-to-publish metadata',()=>{
 assert.throws(()=>publishingCopy({title:'Headline'}),/description/);
});
