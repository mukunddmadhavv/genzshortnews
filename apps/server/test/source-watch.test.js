import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createHmac } from 'node:crypto';
import { feedEntries, validSignature, SOURCE_CHANNEL, channelLocator } from '../src/source-watch.js';

const entry=(id,link,channel=SOURCE_CHANNEL)=>`<entry><yt:videoId>${id}</yt:videoId><yt:channelId>${channel}</yt:channelId><title>News</title><published>2026-09-30T12:00:00Z</published><link rel="alternate" href="${link}"/></entry>`;
const feed=entries=>`<feed xmlns:yt="http://www.youtube.com/xml/schemas/2015"><id>yt:channel:${SOURCE_CHANNEL.slice(2)}</id>${entries}</feed>`;

test('canonical channel feed identifies Shorts without relying on titles or duration',()=>{
 const entries=feedEntries(feed(
  entry('abcdefghijk','https://www.youtube.com/shorts/abcdefghijk')+
  entry('lmnopqrstuv','https://www.youtube.com/watch?v=lmnopqrstuv')+
  entry('badbadbad12','https://www.youtube.com/shorts/badbadbad12','UCwrong')+
  entry('not-an-id','https://www.youtube.com/shorts/not-an-id')+
  entry('zyxwvutsrqp','https://evil.example/shorts/zyxwvutsrqp')
 ));
 assert.deepEqual(entries.map(x=>[x.id,x.isShort]),[['abcdefghijk',true],['lmnopqrstuv',false],['zyxwvutsrqp',false]]);
 assert.equal(entries[0].url,'https://www.youtube.com/shorts/abcdefghijk');
 assert.equal(feedEntries(feed('')).length,0);
});
test('rejects malformed XML, entities, oversized payloads and other channel feeds',()=>{
 for(const xml of ['<feed>', '<!DOCTYPE feed><feed/>', feed('').replace(SOURCE_CHANNEL.slice(2),'wrong'), 'x'.repeat(1000001)])assert.throws(()=>feedEntries(xml));
});
test('webhooks require a valid HMAC over the exact raw bytes',()=>{
 const body=Buffer.from('<feed/>'),secret='test-only-secret';
 for(const algorithm of ['sha1','sha256']){
  const signature=`${algorithm}=${createHmac(algorithm,secret).update(body).digest('hex')}`;
  assert.equal(validSignature(body,signature,secret),true);
  assert.equal(validSignature(Buffer.from('<feed>changed</feed>'),signature,secret),false);
 }
 for(const signature of [undefined,'sha1=abc','sha256=zz','md5=000',''])assert.equal(validSignature(body,signature,secret),false);
});

test('channel inputs only allow supported YouTube channel pages',()=>{
 for(const value of [SOURCE_CHANNEL,`https://www.youtube.com/channel/${SOURCE_CHANNEL}/shorts`])assert.deepEqual(channelLocator(value),{id:SOURCE_CHANNEL});
 for(const value of ['@NeonManShorts','https://youtube.com/@NeonManShorts/shorts'])assert.deepEqual(channelLocator(value),{handle:'@NeonManShorts'});
 for(const value of ['https://evil.example/@Creator','https://youtube.com.evil.example/@Creator','https://youtube.com:8080/@Creator','https://user:pass@youtube.com/@Creator','https://youtube.com/watch?v=abcdefghijk','https://youtube.com/shorts/abcdefghijk','file:///etc/passwd','https://youtube.com/@Creator/anything','https://youtube.com/channel/'+SOURCE_CHANNEL+'/shorts/extra'])assert.throws(()=>channelLocator(value));
});
test('feed parsing is isolated to the requested channel',()=>{
 const other='UCabcdefghijklmnopqrstuv';
 const xml=feed(entry('abcdefghijk','https://www.youtube.com/shorts/abcdefghijk')).replaceAll(SOURCE_CHANNEL.slice(2),other.slice(2));
 assert.equal(feedEntries(xml,other)[0].isShort,true);
 assert.throws(()=>feedEntries(xml,SOURCE_CHANNEL));
});
