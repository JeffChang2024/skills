---
name: video-from-script
version: "1.0.0"
displayName: "Video from Script — Turn Any Written Script into a Complete Video with AI"
description: >
  Turn any written script into a complete video using AI — paste your script and NemoVideo produces a finished video with matching visuals, voiceover narration, background music, captions, transitions, and professional pacing. Works for YouTube scripts, ad copy, educational outlines, presentation notes, blog posts, social media threads, and any written content. Script to video converter, text to video maker, turn text into video, make video from script, AI video from text, script to YouTube video, automated video production from writing.
metadata: {"openclaw": {"emoji": "📜", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
---

# Video from Script — Paste a Script, Get a Finished Video

The script is the hardest part of making a video. Finding the right words, structuring the argument, writing the hook, building to the conclusion — that creative work takes hours. But after the script is done, the creator still faces the production work: finding or filming visuals for every sentence, recording voiceover (or hiring voice talent), editing clips to match the narration, adding music, syncing captions, and exporting. The production work takes longer than the writing. NemoVideo eliminates the gap between script and video. Paste your finished script — whether it's a YouTube video script, an ad copy, a blog post, presentation notes, or a social media thread — and the AI produces a complete video: visuals selected or generated to match each sentence, voiceover narration with appropriate tone and pacing, background music that complements the content's mood, word-by-word captions for silent viewing, smooth transitions between sections, and professional formatting for the target platform. The writer's job ends at the script. NemoVideo handles everything between the last sentence and the upload button.

## Use Cases

1. **YouTube Script → Complete Video (5-20 min)** — A creator wrote a 2,000-word YouTube script about investing. NemoVideo: breaks the script into visual segments (each 2-3 sentences), selects stock footage and generates graphics matching each concept (stock market charts, wallet close-ups, calculator animations), records AI voiceover with confident-friendly male tone at 150 wpm, adds lo-fi background music at -20dB with speech ducking, generates word-by-word captions (white text, yellow highlight), creates chapter timestamps at each major topic, and extracts the strongest 55 seconds as a Shorts clip. A 2,000-word script becomes a 13-minute YouTube video with chapters, captions, music, and a bonus Short.
2. **Ad Copy → Video Ad (15-45s)** — A marketing team has ad copy: "Tired of slow WiFi? MeshPro covers every corner of your home with blazing-fast internet. No dead zones. No buffering. Just fast, reliable WiFi everywhere. Try it risk-free for 30 days." NemoVideo: produces a 30-second video ad with frustrated person (slow loading screen), product reveal (MeshPro device), benefit visuals (person streaming in every room), price/offer overlay, and CTA button placement. Three formats: 16:9 for YouTube pre-roll, 9:16 for Stories, 1:1 for Facebook Feed. Written ad copy becomes multi-format video creative.
3. **Blog Post → Video Summary (3-5 min)** — A company blog post about "5 Remote Work Productivity Tips" needs a video version. NemoVideo: converts the 1,200-word article into a structured video script (intro hook → 5 tips with examples → conclusion), generates visuals for each tip (home office setups, calendar apps, Pomodoro timer), adds professional narration, captions, and chapter markers. The blog post reaches a new audience through video without rewriting a single word.
4. **Presentation Notes → Explainer Video (2-5 min)** — A consultant has bullet-point presentation notes for a client deliverable. NemoVideo: expands bullet points into smooth narration, creates animated slides matching each point, adds data visualization for statistics, includes branded intro and outro, and exports as a shareable video. Rough notes become a polished client-facing deliverable.
5. **Social Thread → Video Content (60-90s)** — A creator wrote a viral Twitter/X thread with 12 tweets about productivity. NemoVideo: converts each tweet into a visual scene (1 tweet = 5-8 seconds of video), adds dynamic text animations matching the thread's punchy style, voiceover with energetic pacing, trending background music, and vertical 9:16 format for TikTok/Reels. A text thread becomes a video that reaches an entirely different audience.

## How It Works

### Step 1 — Paste Your Script
Paste the complete text. It can be: a structured video script with section headers, raw ad copy, a blog post, presentation bullet points, or any written content.

### Step 2 — Set Production Parameters
Choose: voiceover style, visual approach, music mood, caption format, target platform, and duration.

### Step 3 — Generate
```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "video-from-script",
    "prompt": "Turn this YouTube script into a complete video. Script: [paste 2000-word script here]. Voice: confident male, conversational, 150 wpm. Visuals: mix of stock footage and generated graphics matching each concept. Music: lo-fi at -20dB with speech ducking. Captions: word-highlight (white text, yellow active word, dark pill). Chapters: auto from section headers. Shorts: extract best 55-sec segment (9:16). Format: 16:9 1080p for YouTube.",
    "voice": "confident-male-conversational",
    "voice_speed": "150 wpm",
    "visuals": "auto-match",
    "music": "lo-fi",
    "music_volume": "-20dB",
    "captions": {"style": "word-highlight", "text": "#FFFFFF", "highlight": "#FFD700", "bg": "pill-dark"},
    "chapters": true,
    "shorts": {"duration": "55 sec", "hook": "auto"},
    "format": "16:9"
  }'
```

### Step 4 — Review and Publish
Preview the video. Check: voice-visual sync, music mood, caption accuracy. Adjust any element. Export and upload.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|:--------:|-------------|
| `prompt` | string | ✅ | Script text and production requirements |
| `voice` | string | | "confident-male", "warm-female", "energetic", "authoritative" |
| `voice_speed` | string | | "130 wpm" (slow), "150 wpm" (natural), "170 wpm" (fast) |
| `visuals` | string | | "auto-match", "stock-footage", "generated-graphics", "mixed" |
| `music` | string | | "lo-fi", "cinematic", "upbeat", "corporate", "none" |
| `music_volume` | string | | "-14dB" to "-22dB" |
| `captions` | object | | {style, text, highlight, bg} |
| `chapters` | boolean | | Auto-detect from script sections (default: true) |
| `shorts` | object | | {duration, hook} for Shorts extraction |
| `format` | string | | "16:9", "9:16", "1:1" |
| `brand` | object | | {logo, colors, intro, outro} |
| `batch_scripts` | array | | Multiple scripts for batch production |

## Output Example

```json
{
  "job_id": "vfs-20260328-001",
  "status": "completed",
  "script_words": 2048,
  "duration_seconds": 818,
  "format": "mp4",
  "resolution": "1920x1080",
  "outputs": {
    "main_video": {
      "file": "investing-basics.mp4",
      "duration": "13:38",
      "voice": "confident-male at 150 wpm",
      "visuals": "42 scenes (28 stock, 14 generated)",
      "captions": "word-highlight (486 lines)",
      "music": "lo-fi at -20dB with ducking"
    },
    "chapters": [
      {"title": "Why Most People Never Start Investing", "timestamp": "0:00"},
      {"title": "The Power of Compound Interest", "timestamp": "2:45"},
      {"title": "Index Funds vs Individual Stocks", "timestamp": "5:20"},
      {"title": "How to Open Your First Account", "timestamp": "8:10"},
      {"title": "The $100 Starter Portfolio", "timestamp": "10:55"}
    ],
    "shorts": {
      "file": "shorts-investing.mp4",
      "duration": "0:55",
      "hook": "Your bank savings account is losing you money every single day"
    }
  }
}
```

## Tips

1. **150 words per minute is the golden pace** — Faster sounds rushed and loses comprehension. Slower sounds patronizing. 150 wpm is conversational and matches how people naturally listen to narration.
2. **Section headers in the script become video chapters** — If your script has clear sections ("Part 1: Why This Matters"), NemoVideo automatically creates chapter timestamps. Structure your script with headers for better video navigation.
3. **2-3 sentences per visual scene prevents monotony** — A single visual held for 30+ seconds feels static. Breaking visuals into 2-3 sentence segments keeps the visual pace engaging without being chaotic.
4. **Ad scripts need different pacing than YouTube scripts** — Ads: 170 wpm, 2-3 second cuts, front-loaded benefit. YouTube: 150 wpm, 5-8 second scenes, hook-then-build structure. Specify the platform for optimal pacing.
5. **Batch script processing is the content calendar cheat code** — Write 10 scripts on Sunday. Batch-process all 10 into videos. Schedule uploads across the week. A full week of content from one writing session.

## Output Formats

| Format | Resolution | Use Case |
|--------|-----------|----------|
| MP4 16:9 | 1080p / 4K | YouTube / website / presentation |
| MP4 9:16 | 1080x1920 | TikTok / Reels / Shorts |
| MP4 1:1 | 1080x1080 | Instagram / Facebook / LinkedIn |
| SRT | — | Closed captions |
| JSON | — | Chapter metadata |

## Related Skills

- [video-idea-generator](/skills/video-idea-generator) — Generate video ideas
- [generate-ai-video](/skills/generate-ai-video) — AI video generation
- [generate-video-ai](/skills/generate-video-ai) — AI video creation
