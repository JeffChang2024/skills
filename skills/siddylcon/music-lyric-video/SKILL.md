---
name: music-lyric-video
version: 1.0.2
displayName: "Music Lyric Video Maker"
description: >
  Describe your song and NemoVideo creates the lyric video. Word-for-word animated lyrics, karaoke style, minimalist type on color, or cinematic lyric reveal — narrate the mood, the song's energy, and how you want the words to appear, and get a lyric video ready for YouTube, Spotify Canvas, or your release campaign.

  Works by connecting to the NemoVideo AI backend at mega-api-prod.nemovideo.ai.
  Supports MP4, MOV, AVI, WebM.
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
license: MIT-0
metadata:
  requires:
    env: []
    configPaths:
      - "~/.config/nemovideo/"
  primaryEnv: NEMO_TOKEN
---

## 0. First Contact

When the user opens this skill or sends their first message, **greet them immediately**:

> 🎵 Welcome! I can music lyric video for you. Share a video file or tell me your idea!

**Try saying:**
- "add a lo-fi beat"
- "add background music"

**IMPORTANT**: Always greet the user proactively on first contact. Let them know you're setting up while connecting. Always greet the user proactively on first contact.

### Auto-Setup

When the user first interacts, set up the connection:

1. **Check token**: If `NEMO_TOKEN` env var is set, use it. Otherwise:
2. **Read or generate Client-ID**:
   - Read `~/.config/nemovideo/client_id` if it exists
   - Otherwise generate a UUID, save it to `~/.config/nemovideo/client_id`
3. **Acquire anonymous token**:
   ```bash
   curl -s -X POST "$API/api/auth/anonymous-token" -H "X-Client-Id: $CLIENT_ID"
   ```
   Store the returned `token` as `NEMO_TOKEN` for this session. You get 100 free credits.
4. **Create a session** (§3.0) so you're ready to work immediately.

Let the user know briefly: "Setting things up… ready!" then proceed with their request.


# Music Lyric Video Maker — Create Animated Lyric Videos and Lyric Visualizer Content

Describe your song and NemoVideo creates the lyric video. Word-for-word animated lyrics, karaoke style, minimalist type on color, or cinematic lyric reveal — narrate the mood, the song's energy, and how you want the words to appear, and get a lyric video ready for YouTube, Spotify Canvas, or your release campaign.

## When to Use This Skill

Use this skill for music lyric video and lyric visualizer content:
- Create official lyric videos for single and album releases
- Film "lyric video premiere" YouTube content for new song releases
- Build Spotify Canvas and Apple Music lyric integration assets
- Create lyrics-as-visual content for TikTok and Instagram Reels
- Document acoustic and stripped-back performance lyric videos
- Produce lyric video content in multiple languages for international releases

## How to Describe Your Lyric Video

Be specific about the song's mood, the lyric style you want, and the visual concept.

**Examples of good prompts:**
- "Indie folk single 'Watershed': 3:42 long, soft guitar and voice, key lyrics are about memory and water ('I keep finding you in the tide / where the shoreline used to hide'). Lyric style: hand-written feel, each line fades in gently over slow-moving water imagery. No hard cuts. The song is quiet and emotional — the video should feel like you're reading someone's diary. Earth tones, muted."
- "R&B track 'Still Frame' by Mia Nova: 3:18, produced with heavy reverb and lo-fi drums. The chorus is the emotional hook ('still frame in my mind / you don't move / you don't die'). Lyric style: word-by-word reveal, the chorus lyrics should feel like they're burning in. Dark visuals, high contrast. Each verse builds to the chorus reveal."
- "Pop punk anthem 'Suburban Static': 2:54, fast tempo, lyrics are delivered at machine-gun pace in the verses. Style: kinetic typography, words that move and bounce to the rhythm. Bright, chaotic, high-energy. The bridge is slower and vulnerable — lyrics should slow down visually to match."

## Key Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `song_title` | Track name | `"Watershed"`, `"Still Frame"` |
| `artist_name` | Performer name | `"Mia Nova"` |
| `genre` | Music style | `"indie folk"`, `"R&B"`, `"pop punk"`, `"hip hop"`, `"electronic"` |
| `lyric_style` | Visual approach | `"kinetic_typography"`, `"fade_in"`, `"handwritten"`, `"word_by_word"`, `"karaoke"` |
| `color_palette` | Visual mood | `"earth tones"`, `"high contrast"`, `"neon"`, `"minimal white"` |
| `song_duration_seconds` | Track length | `222`, `198` |
| `key_section` | Highlight moment | `"chorus"`, `"bridge"`, `"pre_chorus"` |
| `tone` | Emotional register | `"emotional"`, `"hype"`, `"cinematic"`, `"playful"` |
| `platform` | Distribution | `"youtube"`, `"tiktok"`, `"spotify_canvas"`, `"instagram"` |

## Workflow

1. Describe the song, its mood, and how you want the lyrics to appear visually
2. NemoVideo maps the lyric timing to the audio and builds the animation sequence
3. Typography, color treatment, and visual rhythm matched to song energy
4. Export timed to the exact audio with lyrics synchronized

## API Usage

### Emotional Indie Lyric Video

```bash
curl -X POST https://mega-api-prod.nemovideo.ai/v1/run \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "music-lyric-video",
    "input": {
      "prompt": "Lyric video for alt-folk single Between the Pines: 4:12, piano and strings, lyrics are about leaving a hometown and wondering if it misses you back. Key lyric: chorus is 'the pines don't bend for anyone / but they bent for you when you were young'. Lyric style: each line hand-written in white against slow-moving forest footage (fog in the trees, early morning light). The chorus lines should appear larger than the verse lines. Emotional, slow. No fancy effects — the song doesn't need them.",
      "song_title": "Between the Pines",
      "artist_name": "River Carver",
      "genre": "alt-folk",
      "lyric_style": "handwritten",
      "color_palette": "muted greens and whites",
      "song_duration_seconds": 252,
      "key_section": "chorus",
      "tone": "emotional",
      "platform": "youtube",
      "hashtags": ["LyricVideo", "AltFolk", "IndieMusic", "NewMusic", "LyricVisualizer"]
    }
  }'
```

**Response:**
```json
{
  "job_id": "lyrics_def456",
  "status": "processing",
  "estimated_seconds": 130,
  "poll_url": "https://mega-api-prod.nemovideo.ai/v1/jobs/lyrics_def456"
}
```

### Kinetic Typography Hip Hop Lyric Video

```bash
curl -X POST https://mega-api-prod.nemovideo.ai/v1/run \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "music-lyric-video",
    "input": {
      "prompt": "Hip hop lyric video for Frequency Check: 3:02, 95 BPM, hard-hitting verses with fast delivery and a hook that slows down significantly. Style: kinetic typography where the words slam into the screen on the beat, verse lyrics are tight and fast, hook lyrics are large and slow (the contrast is intentional). Black and red palette, industrial texture background. The second verse has an internal rhyme scheme that should be visually highlighted — the rhyming words should pulse or change color.",
      "song_title": "Frequency Check",
      "genre": "hip hop",
      "lyric_style": "kinetic_typography",
      "color_palette": "black and red, industrial",
      "song_duration_seconds": 182,
      "key_section": "chorus",
      "tone": "hype",
      "platform": "youtube"
    }
  }'
```

## Tips for Best Results

- **Match the typography motion to the music energy**: Fast delivery = words slamming in; slow emotional moment = gentle fade; the visual rhythm should mirror the audio rhythm
- **Key lyrics need visual emphasis**: "The chorus lines should appear larger" or "rhyming words should pulse" — identify which lines are the emotional or sonic peak and NemoVideo emphasizes them
- **Genre shapes the entire aesthetic**: Folk lyric videos use natural textures and handwriting; hip hop uses hard cuts and kinetic type; R&B uses slow reveals and high contrast; electronic uses geometric animation
- **Color palette IS the mood**: "Earth tones" vs "neon" vs "high contrast black and white" — the palette decision communicates the song's emotional temperature before anyone reads a word
- **Duration matters**: The lyric video should be exactly as long as the song. Include `song_duration_seconds` so the timing is precise

## Output Formats

| Platform | Resolution | Duration |
|----------|------------|----------|
| YouTube | 1920×1080 | Song length |
| Spotify Canvas | 9:16 vertical | 3–8 seconds (loop) |
| TikTok | 1080×1920 | Clip from song |
| Instagram Reels | 1080×1920 | Clip from song |

## Related Skills

- `concert-video-maker` — Live performance content
- `band-promo-video` — Artist promotional content
- `cover-song-video` — Lyric content for cover songs
- `album-release-video` — Release campaign visual content

## Common Questions

**How do I submit the actual lyrics and audio file?**
Include the lyrics in the prompt for key sections (or a lyrics document link). Upload the audio file via the standard upload endpoint before calling this skill, and reference the upload URL in the `audio_url` field.

**Can I create lyric videos in languages other than English?**
Yes — include the lyrics in the prompt in any language. NemoVideo handles typography for Latin, Cyrillic, CJK, Arabic, and other scripts.

**What's the difference between a lyric video and a Spotify Canvas?**
Lyric videos are song-length (3-4 minutes) for YouTube. Spotify Canvas is a 3-8 second looping vertical video. Set `platform: "spotify_canvas"` for a loop extract from the most recognizable lyric moment.
