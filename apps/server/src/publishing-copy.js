const required = ['#shorts', '#genzshortnews'];
export function publishingCopy(input) {
 const clean = value => String(value || '').replace(/[<>]/g, '').trim();
 const title = clean(input.caption || input.title).replace(/#[\p{L}\p{N}_]+/gu, '').replace(/\s+/g, ' ').trim();
 if (!title || !clean(input.description)) throw new Error('Caption and description are required before publishing.');
 const candidates = [...(Array.isArray(input.hashtags) ? input.hashtags : []), ...(clean(input.description).match(/#[\p{L}\p{N}_]+/gu) || [])];
 const hashtags = [...required];
 for (const value of candidates) {
  const tag = '#' + String(value).replace(/^#/, '').replace(/[^\p{L}\p{N}_]/gu, '');
  if (tag.length > 1 && tag.length <= 60 && !hashtags.some(x => x.toLowerCase() === tag.toLowerCase())) hashtags.push(tag);
 }
 const selected = hashtags.slice(0, 8);
 const body = clean(input.description).replace(/#[\p{L}\p{N}_]+/gu, '').trim();
 const ending = `\n\nFollow GENZ SHORT NEWS for more!\n\n${selected.join(' ')}`;
 return { title: `${title.slice(0, 92).trim()} #shorts`, caption:title, description:body.slice(0,5000-ending.length)+ending, hashtags:selected, publishingCopyReady:true };
}
