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
test('publishing copy generates separate Instagram Reel copy with required hashtags and fullCaption',()=>{
 const result=publishingCopy({
  caption: 'YouTube Headline Hook',
  description: 'Full YouTube description text with sources.',
  hashtags: ['#shorts', '#genzshortnews', '#IndiaNews'],
  instagram: {
   caption: 'Separate Instagram Reel Hook!',
   description: 'Dedicated Instagram context for Gen-Z audience. What are your thoughts?',
   hashtags: ['#reels', '#reelsindia', '#genzshortnews', '#Breaking']
  }
 });
 assert.equal(result.instagram.caption, 'Separate Instagram Reel Hook!');
 assert.equal(result.instagram.description, 'Dedicated Instagram context for Gen-Z audience. What are your thoughts?');
 assert.deepEqual(result.instagram.hashtags, ['#reels', '#reelsindia', '#genzshortnews', '#Breaking', '#IndiaNews']);
 assert.ok(result.instagram.fullCaption.includes('Separate Instagram Reel Hook!'));
 assert.ok(result.instagram.fullCaption.includes('Follow GENZ SHORT NEWS for more!'));
 assert.ok(result.instagram.fullCaption.includes('#reels #reelsindia #genzshortnews'));
});
test('publishing copy derives Instagram copy when only YouTube fields are provided',()=>{
 const result=publishingCopy({
  caption: 'Breaking News Story',
  description: 'Detailed report on recent events.',
  hashtags: ['#shorts', '#genzshortnews', '#Tech']
 });
 assert.equal(result.instagram.caption, 'Breaking News Story');
 assert.equal(result.instagram.description, 'Detailed report on recent events.');
 assert.deepEqual(result.instagram.hashtags, ['#reels', '#reelsindia', '#genzshortnews', '#Tech']);
 assert.ok(result.instagram.fullCaption.includes('Follow GENZ SHORT NEWS for more!'));
});
