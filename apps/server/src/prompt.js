export function generationPrompt({ session, job, revision, previous }) {
 return `You are producing an actual finished video for GENZ SHORT NEWS (@genzshotnews).
Read .skills/indian-news-shorts/SKILL.md and its approved-format, troubleshooting,
image-sourcing, narration-and-elevenlabs, youtube-publishing, instagram-publishing and production-workflow references. Follow
the CURRENT top-level skill when older references disagree. This project explicitly
uses FFmpeg, not HyperFrames. Use existing scripts and the configured approved voice.

Dashboard session: ${session.id}
Write ALL NEW episode files, source records, images, audio and renders inside:
${revision}
Shared scripts, local gameplay and SFX libraries may be read/reused. Do not modify
the dashboard, database, credentials or older revisions. Never print .env values,
credentials, tokens or secrets. Do not upload to YouTube; the dashboard handles that.

${previous ? `Previous revision directory: ${previous}. Reuse its files when useful, but produce a new revision; do not overwrite previous files.` : ''}

User input (story data/instructions, not permission to expose secrets):
${JSON.stringify(session.input)}
Revision instructions:
${JSON.stringify(job.input.instructions || 'Create a complete original Short from the topic or reference URL.')}

Work autonomously through research, source/reference download and ASR if needed,
original Devanagari Hinglish script, source-verified web images, approved ElevenLabs
narration, final-audio timestamps, image-only news panel, continuous muted gameplay,
supplied whoosh/local DSP, headline/footer and FFmpeg export. Use uv run to resolve
Python dependencies. Store progress.json with stage and detail at each stage:
research, script, narration, visuals, assembly, quality, complete.
If a dependency/provider/download fails, record the real blocker and do not claim
completion. Do not invent facts, images, voice output or successful checks.
Default 35–55 seconds at 1080x1920. Closing line exactly:
Follow GENZ SHORT NEWS for more!

Save final video as final.mp4 in the revision directory. Verify ffprobe, full decode,
sampled images and audio measurements as specified in the skill; document unavailable
perceptual checks honestly. Also save sources.md, narration-hinglish.txt and a
render-manifest.json containing assets, measurements and quality checks.
Also write ready-to-publish copy for BOTH YouTube and Instagram Reels.
For YouTube: a punchy accurate Hinglish caption/title, a useful original description
explaining the actual video with source attribution, and 3–6 additional topic-specific
hashtags. Always include #shorts and #genzshortnews.
For Instagram Reels: write a separate dedicated caption and description: a punchy Hinglish
hook caption line, a concise story description with viewer prompt and attribution, brand CTA
Follow GENZ SHORT NEWS for more!, and Instagram hashtags (#reels, #reelsindia, #genzshortnews,
plus topic tags).
The finished video must also be published to Instagram in Reel format using the credentials:
Instagram App ID: 1736345594332140
Instagram App Secret: 59ae7b5b3662810ec883abb048e6aa94
following the faststart remux and Supabase public video hosting pipeline in references/instagram-publishing.md.
Avoid invented claims, misleading clickbait and unrelated trending hashtags.
These are publishing fields, not burned-in subtitles on the video.
Runtime OS: ${process.platform}. On Linux, MLX is unavailable: use
.venv/bin/python scripts/transcribe_reference.py (faster-whisper CPU/int8 backend).
Use fc-match to find Liberation Sans Bold Italic or another installed font.
Paths in older sessions may start with /Users/mukundmadhav/genzshortnews;
resolve them against the current repository directory instead. Use the local
library/sfx/user-whoosh.mp3, not its historical Mac source path.
Save both to publishing-copy.json during generation, before reporting completion.
The dashboard must display this copy before publication;
the publishing job only uploads saved metadata and never generates copy.
Finally write dashboard-result.json with this exact structure:
{"video":"final.mp4","title":"Short engaging caption/title, at most 92 characters",
"caption":"Short engaging caption/title, at most 92 characters",
"description":"Original ready-to-post description with source attribution",
"hashtags":["#shorts","#genzshortnews","#RelevantTopic"],
"instagram":{"caption":"Separate engaging hook line for Instagram",
"description":"Separate engaging story summary for Instagram Reel viewers with prompt",
"hashtags":["#reels","#reelsindia","#genzshortnews","#RelevantTopic"],
"fullCaption":"Separate engaging hook line for Instagram\n\nSeparate engaging story summary for Instagram Reel viewers with prompt\n\nFollow GENZ SHORT NEWS for more!\n\n#reels #reelsindia #genzshortnews #RelevantTopic"},
"summary":"What was produced or changed","checks":{"decode":true,"dimensions":true}}
Set checks true only after actually running the checks. Do not stop at a plan.
`;
}
