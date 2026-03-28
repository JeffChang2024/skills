---
name: ai-video-from-text
version: "1.0.0"
displayName: "AI Video from Text — Turn Any Text into a Professional Video with AI Automatically"
description: >
  Turn any text into a finished video using AI — paste a script, article, blog post, product description, or rough idea and NemoVideo generates a complete video with scene-matched visuals, voiceover narration, animated text overlays, background music, transitions, and subtitles. No filming needed, no footage library, no editing skills required. Write the words and NemoVideo produces the video — ready for YouTube, TikTok, Instagram, LinkedIn, or any platform.
metadata: {"openclaw": {"emoji": "📝", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
---

# AI Video from Text — Turn Written Content into Video Automatically

Written content is everywhere. Blog posts, scripts, product descriptions, newsletters, social media captions, meeting summaries, training documents, pitch decks — the world runs on text. But the world watches video. A blog post that reaches 300 readers would reach 3,000 viewers as a 90-second video. The product description that converts at 2.5% would convert at 7% as a 30-second video demo. The training document that 15% of employees actually read would be watched by 85% as a narrated video. The problem is production: turning text into video traditionally requires storyboarding, sourcing visuals for every scene, recording voiceover, editing everything on a timeline, adding music, and exporting for each platform. A 90-second video from an 800-word blog post takes 4-8 hours of human labor. NemoVideo collapses that into a single API call. Paste any text — structured or unstructured, long or short, formal or casual — and the AI produces a complete video: scene breakdown following the text's natural structure, AI-selected visuals for each scene, voiceover narration with natural human intonation, animated text overlays highlighting key phrases, mood-matched background music, smooth transitions, and burned-in subtitles. The text becomes a video without a human touching a timeline.

## Use Cases

1. **Blog Post → YouTube Video (2-5 min)** — An 800-word blog post about "5 Remote Work Productivity Hacks." NemoVideo: breaks it into 6 scenes (intro + 5 hacks), selects relevant visuals for each (home office, video call, calendar app, notification overload, peaceful workspace), narrates the full text with a warm conversational voice at 150 wpm, animates each hack's headline as bold text overlay, adds lo-fi music at -20dB with speech ducking, burns in subtitles, and exports 16:9 1080p. The blog post reaches a new audience as a YouTube video.
2. **Product Description → Ad Video (15-30s)** — A 120-word product description for a wireless earbuds launch. NemoVideo: condenses into a 25-second fast-paced video, shows product benefit per scene (noise cancellation, 30-hour battery, waterproof, one-touch pairing), displays each benefit as bold animated text synchronized to energetic voiceover, adds electronic music with beat-synced cuts, and ends with a CTA frame. The listing text becomes a conversion-driving ad.
3. **Newsletter → LinkedIn Video (60-90s)** — A weekly industry newsletter's lead article needs a LinkedIn video version. NemoVideo: extracts the 3 key insights, creates a scene for each with professional tech visuals, narrates in an authoritative tone, adds animated data visualizations for any statistics mentioned, and exports 16:9 with burned-in captions optimized for LinkedIn's silent autoplay. Newsletter subscribers become video viewers.
4. **Meeting Notes → Team Update (60-90s)** — A 400-word project meeting summary needs to reach the wider team. NemoVideo: converts into a narrator-led update with key decisions displayed as animated bullet points, action items shown with assignee names and deadlines, risk items highlighted in amber, and a professional but approachable tone. Distributed via Slack — watched instead of skimmed.
5. **Research Paper Abstract → Explainer (90-180s)** — A 300-word academic abstract needs a public-facing explainer. NemoVideo: translates academic language into accessible narration, generates diagrams for technical concepts, shows real-world applications as visual examples, adds chapter structure (Problem → Method → Results → Impact), and exports with subtitles. Peer-reviewed research reaches a general audience.

## How It Works

### Step 1 — Provide Text
Paste or upload any text. NemoVideo analyzes structure, tone, key phrases, and content type to plan the video's scene breakdown and visual approach.

### Step 2 — Set Video Style
Choose visual style (professional, playful, cinematic, minimal), voiceover character, music mood, target platform, and duration preference.

### Step 3 — Generate
```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "ai-video-from-text",
    "prompt": "Turn this blog post into a YouTube video. Text: [800-word blog post about remote work productivity]. Style: professional but friendly. Voice: warm male, conversational at 150 wpm. Music: lo-fi chill at -20dB with ducking. Text overlays: animate each section headline. Subtitles: burned-in white with dark shadow. Duration: natural pacing (~3 min). Format: 16:9 1080p. Also export a 55-second 9:16 Shorts version with the strongest segment.",
    "style": "professional-friendly",
    "voice": "warm-male-conversational",
    "music": "lo-fi-chill",
    "music_volume": "-20dB",
    "text_overlays": true,
    "subtitles": "burned-in",
    "exports": ["16:9-1080p-full", "9:16-55s-shorts"],
    "format": "16:9"
  }'
```

### Step 4 — Preview and Publish
Preview the video. Adjust scene visuals, voiceover pacing, music, or text overlay styling. Export for the target platform.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|:--------:|-------------|
| `prompt` | string | ✅ | Source text and production instructions |
| `style` | string | | "professional", "playful", "cinematic", "minimal", "bold" |
| `voice` | string | | "warm-male", "friendly-female", "authoritative", "energetic", "calm" |
| `music` | string | | "lo-fi", "corporate", "cinematic", "acoustic", "electronic", "none" |
| `music_volume` | string | | "-14dB" to "-22dB" (default: "-20dB") |
| `text_overlays` | boolean | | Animate key phrases as text (default: true) |
| `subtitles` | string | | "burned-in", "srt", "none" |
| `duration` | string | | "natural", "30 sec", "60 sec", "90 sec", "3 min" |
| `exports` | array | | Multiple format/duration exports |
| `format` | string | | "16:9", "9:16", "1:1" |

## Output Example

```json
{
  "job_id": "avft-20260328-001",
  "status": "completed",
  "source_words": 812,
  "scenes": 6,
  "outputs": [
    {
      "type": "full-video",
      "format": "16:9",
      "resolution": "1920x1080",
      "duration": "3:08",
      "file_size_mb": 52.4,
      "voice": "warm-male-conversational (en)",
      "music": "lo-fi-chill at -20dB",
      "text_overlays": 6,
      "subtitles": "burned-in (84 lines)"
    },
    {
      "type": "shorts",
      "format": "9:16",
      "resolution": "1080x1920",
      "duration": "0:55",
      "segment": "Hack #3 (strongest energy)",
      "captions": "word-highlight"
    }
  ]
}
```

## Tips

1. **Structured text produces better videos** — Headings, numbered lists, and clear paragraphs create natural scene boundaries. "5 Tips for..." converts more cleanly than stream-of-consciousness prose.
2. **Hook-first reordering boosts engagement** — NemoVideo can lead with the most compelling point instead of following the text's original order. The strongest insight becomes the first 5 seconds — critical for social media retention.
3. **Dual export maximizes reach** — 16:9 full video for YouTube + 9:16 Shorts from the strongest segment. One text source produces two platform-optimized videos.
4. **Statistics become animated visuals** — Numbers in the text ("saves 5 hours/week," "40% reduction") automatically generate counter animations and data visualizations. Quantified claims in video form are more credible and memorable.
5. **Subtitles double your audience** — 85% of social video plays on mute. Burned-in subtitles ensure the text-turned-video reaches sound-off viewers too.

## Output Formats

| Format | Resolution | Use Case |
|--------|-----------|----------|
| MP4 16:9 | 1080p / 4K | YouTube / website / presentations |
| MP4 9:16 | 1080x1920 | TikTok / Reels / Shorts |
| MP4 1:1 | 1080x1080 | Instagram feed / LinkedIn |
| SRT | — | Separate subtitle file |

## Related Skills

- [ai-story-video-maker](/skills/ai-story-video-maker) — Story video generation
- [ai-faceless-video](/skills/ai-faceless-video) — Faceless video creation
- [ai-avatar-video-maker](/skills/ai-avatar-video-maker) — AI avatar videos
