const requiredYoutube = ['#shorts', '#genzshortnews'];
const requiredInstagram = ['#reels', '#reelsindia', '#genzshortnews'];

function extractHashtags(candidates, required, max = 8) {
 const hashtags = [...required];
 for (const value of candidates) {
  const tag = '#' + String(value).replace(/^#/, '').replace(/[^\p{L}\p{N}_]/gu, '');
  if (tag.length > 1 && tag.length <= 60 && !hashtags.some(x => x.toLowerCase() === tag.toLowerCase())) {
   hashtags.push(tag);
  }
 }
 return hashtags.slice(0, max);
}

export function publishingCopy(input) {
 const clean = value => String(value || '').replace(/[<>]/g, '').trim();
 const title = clean(input.caption || input.title).replace(/#[\p{L}\p{N}_]+/gu, '').replace(/\s+/g, ' ').trim();
 if (!title || !clean(input.description)) throw new Error('Caption and description are required before publishing.');

 const candidates = [
  ...(Array.isArray(input.hashtags) ? input.hashtags : []),
  ...(clean(input.description).match(/#[\p{L}\p{N}_]+/gu) || [])
 ];
 const selected = extractHashtags(candidates, requiredYoutube, 8);
 const body = clean(input.description).replace(/#[\p{L}\p{N}_]+/gu, '').trim();
 const ending = `\n\nFollow GENZ SHORT NEWS for more!\n\n${selected.join(' ')}`;

 // Dedicated Instagram Reel copy
 const igInput = input.instagram || {};
 const igCaption = clean(igInput.caption || input.instagram_caption || title);
 const igBody = clean(igInput.description || input.instagram_description || body);
 const igCandidates = [
  ...(Array.isArray(igInput.hashtags) ? igInput.hashtags : []),
  ...(Array.isArray(input.instagram_hashtags) ? input.instagram_hashtags : []),
  ...(clean(igInput.description || '').match(/#[\p{L}\p{N}_]+/gu) || []),
  ...candidates.filter(t => !['#shorts'].includes(String(t).toLowerCase()))
 ];
 const igSelected = extractHashtags(igCandidates, requiredInstagram, 10);
 const igEnding = `\n\nFollow GENZ SHORT NEWS for more!\n\n${igSelected.join(' ')}`;
 const igCleanBody = igBody.replace(/#[\p{L}\p{N}_]+/gu, '').trim();
 const igFullCaption = `${igCaption}\n\n${igCleanBody.slice(0, 2200 - igEnding.length - igCaption.length)}${igEnding}`.trim();

 return {
  title: `${title.slice(0, 92).trim()} #shorts`,
  caption: title,
  description: body.slice(0, 5000 - ending.length) + ending,
  hashtags: selected,
  instagram: {
   caption: igCaption,
   description: igCleanBody,
   hashtags: igSelected,
   fullCaption: igFullCaption
  },
  instagram_caption: igCaption,
  instagram_description: igCleanBody,
  publishingCopyReady: true
 };
}

