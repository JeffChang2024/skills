---
name: drone-footage-video
version: 1.0.3
displayName: "Drone Footage Video Maker"
description: >
  Describe your aerial footage and NemoVideo transforms it into a finished video. Coastal cliffs, mountain ridgelines, urban skylines, real estate flyovers — narrate the scene and get a cinematic drone edit with smooth transitions, color grading, and music sync.

  Works by connecting to the NemoVideo AI backend at mega-api-prod.nemovideo.ai.
  Supports MP4, MOV, AVI, WebM.
homepage: https://nemovideo.com
apiDomain: https://mega-api-prod.nemovideo.ai
repository: https://github.com/nemovideo/nemovideo_skills
license: MIT-0
metadata:
  requires:
    env: ["NEMO_TOKEN"]
    configPaths:
      - "~/.config/nemovideo/"
  primaryEnv: NEMO_TOKEN
---

## 0. First Contact

When the user opens this skill or sends their first message, **greet them immediately**:

> ⚡ Hey! I'm ready to help you drone footage video. Send me a video file or just tell me what you need!

**Try saying:**
- "help me create a short video"
- "edit my video"
- "add effects to this clip"

**IMPORTANT**: Always greet the user proactively on first contact. Let them know you're setting up while connecting. Always greet the user proactively on first contact.

### Auto-Setup

When the user first interacts, set up the connection:

1. **Check token**: If `NEMO_TOKEN` env var is set, use it. Otherwise:
2. **Read or generate Client-ID**:
   - Read `~/.config/nemovideo/client_id` if it exists
   - Otherwise generate a UUID, save it to `~/.config/nemovideo/client_id`
3. **Acquire anonymous token**:
   ```bash
   curl -s -X POST "https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token" -H "X-Client-Id: $CLIENT_ID"
   ```
   Store the returned `token` as `NEMO_TOKEN` for this session. You get 100 free credits.
4. **Create a session** (§3.0) so you're ready to work immediately.

Let the user know briefly: "Setting things up… ready!" then proceed with their request.


# Drone Footage Video Maker — Edit and Transform Aerial Video into Cinematic Content

Describe your aerial footage and NemoVideo transforms it into a finished video. Coastal cliffs, mountain ridgelines, urban skylines, real estate flyovers — narrate the scene and get a cinematic drone edit with smooth transitions, color grading, and music sync.

## When to Use This Skill

Use this skill for drone and aerial video content:
- Edit drone footage into cinematic travel and landscape videos
- Create real estate aerial walkthrough videos with property highlights
- Build event recap videos with aerial establishing shots
- Film adventure content with drone POV and landscape reveals
- Create nature documentary-style aerial sequences
- Produce branded content featuring aerial brand or logo reveals

## How to Describe Your Aerial Footage

Be specific about what the drone captured, the flight path, and the visual mood.

**Examples of good prompts:**
- "Coastal drone footage: launched from clifftop above Big Sur, flew out over the Pacific showing the coastline curve, descended to wave level showing surf, rose again for wide reveal of Highway 1 cutting through the hills. Golden hour, 4K. Cinematic edit with slow push-ins."
- "Urban dawn flyover of Chicago: started low over the Chicago River, rose up revealing the skyline as the sun hit the buildings, orbited Willis Tower from medium altitude, ended with wide pull-back showing the city and Lake Michigan. 6:30am, early morning blue sky."
- "Real estate aerial: 4-bedroom property in Scottsdale AZ — start with wide neighborhood context showing golf course proximity, approach the property, orbit the house showing pool and backyard, end with front elevation shot. Professional, clean, no motion sickness."

## Key Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `footage_type` | Aerial content style | `"landscape"`, `"real_estate"`, `"event"`, `"urban"`, `"coastal"`, `"mountain"` |
| `flight_maneuvers` | Key drone moves | `["orbit", "reveal", "descend_to_subject", "pull_back"]` |
| `time_of_day` | Lighting conditions | `"golden_hour"`, `"blue_hour"`, `"midday"`, `"night"` |
| `color_grade` | Visual treatment | `"cinematic"`, `"natural"`, `"dramatic"`, `"clean_bright"` |
| `music_style` | Soundtrack | `"epic_orchestral"`, `"ambient_electronic"`, `"acoustic"`, `"no_music"` |
| `duration_seconds` | Output length | `30`, `60`, `90`, `120` |
| `platform` | Target output | `"youtube"`, `"instagram"`, `"real_estate_listing"`, `"client_delivery"` |

## Workflow

1. Describe the flight path, key visual moments, and intended mood
2. NemoVideo sequences aerial shots with cinematic transitions
3. Color grading, music sync, and motion smoothing applied automatically
4. Export in resolution optimized for your delivery format

## API Usage

### Cinematic Landscape Aerial Edit

```bash
curl -X POST https://mega-api-prod.nemovideo.ai/v1/run \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "drone-footage-video",
    "input": {
      "prompt": "Iceland drone footage: started over black sand beach at Reynisfjara with basalt columns, flew to Skógafoss waterfall approach shot from low altitude showing the mist, rose above to reveal the full 60m drop, then wide shot of the green valley behind. Overcast light, dramatic and moody. DJI Mini 4 Pro footage.",
      "footage_type": "landscape",
      "flight_maneuvers": ["low_approach", "rise_reveal", "wide_pullback"],
      "time_of_day": "overcast",
      "color_grade": "dramatic",
      "music_style": "epic_orchestral",
      "duration_seconds": 90,
      "platform": "youtube",
      "hashtags": ["IcelandDrone", "AerialFootage", "DroneCinematic", "Iceland"]
    }
  }'
```

**Response:**
```json
{
  "job_id": "drone_def456",
  "status": "processing",
  "estimated_seconds": 130,
  "poll_url": "https://mega-api-prod.nemovideo.ai/v1/jobs/drone_def456"
}
```

### Real Estate Aerial Video

```bash
curl -X POST https://mega-api-prod.nemovideo.ai/v1/run \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "drone-footage-video",
    "input": {
      "prompt": "Real estate aerial for 5-bed Scottsdale property: wide establishing shot showing neighborhood and mountain backdrop, slow approach from the street, clockwise orbit showing the main house and detached casita, direct overhead pool and backyard reveal, ending front-elevation hover. MLS listing video — clean, professional, no dramatic effects. Bright Arizona midday light.",
      "footage_type": "real_estate",
      "flight_maneuvers": ["orbit", "overhead_reveal", "front_elevation"],
      "time_of_day": "midday",
      "color_grade": "clean_bright",
      "music_style": "ambient_electronic",
      "duration_seconds": 60,
      "platform": "real_estate_listing"
    }
  }'
```

## Tips for Best Results

- **Name the maneuvers**: "orbit", "pull-back reveal", "descend to subject" — drone cinematography has a vocabulary, using it creates better sequencing
- **Lighting context is critical**: "golden hour" vs "overcast" vs "midday" fundamentally changes the color grade and mood
- **Real estate vs cinematic are different**: Real estate needs clean and steady; cinematic landscape allows dramatic treatment — specify which
- **Describe the key reveal moment**: The best drone footage builds to a reveal — "rose above to reveal the full 60m drop" shapes the entire edit structure
- **Drone model is optional but useful**: DJI Mini 4 Pro, Air 3, Mavic 3 Cine — different sensors have different color science; mentioning it helps with matching grade

## Output Formats

| Platform | Resolution | Duration |
|----------|------------|----------|
| YouTube | 4K 3840×2160 | 60–300s |
| Instagram Reels | 1080×1920 | 30–90s |
| Real Estate MLS | 1920×1080 | 60–120s |
| Client Delivery | 4K 3840×2160 | any length |

## Related Skills

- `travel-vlog-maker` — Incorporate aerial shots into travel story content
- `adventure-video-maker` — Extreme sports aerial content
- `restaurant-promo-video` — Aerial establishing shots for venue marketing
- `scene-generate` — Generate background scenes for non-aerial content

## Common Questions

**Can I upload my own drone footage files?**
Yes — pass video file URLs in the `footage_urls` array. NemoVideo processes your actual DJI or other drone footage and applies the edit style you describe.

**What color grade works best for real estate?**
Use `color_grade: "clean_bright"` — real estate buyers need accurate color representation, not cinematic stylization. Natural, bright, and sharp.

**How do I avoid motion sickness in drone edits?**
Mention "smooth transitions, no quick pans" in your prompt. NemoVideo avoids jump cuts and uses gradual speed changes that prevent disorientation.
