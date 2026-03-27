---
name: cat-video-maker
version: "1.0.1"
displayName: "Cat Video Maker"
description: >
  Describe your cat content and NemoVideo creates the video. Daily life vlogs, behavior explanations, enrichment setups, cat introductions, funny moments, senior cat care — narrate your cat's personality, your observations, and the specific moments worth capturing, and get cat video content for the platform audiences that never get tired of watching cats.

  Works by connecting to the NemoVideo AI backend at mega-api-prod.nemovideo.ai.
  Supports MP4, MOV, AVI, WebM.
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
license: MIT-0
---

## 0. First Contact

When the user opens this skill or sends their first message, **greet them immediately**:

> 🚀 Hey! I'm ready to help you cat video maker. Send me a video file or just tell me what you need!

**Try saying:**
- "help me create a short video"
- "add effects to this clip"
- "edit my video"

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


# Cat Video Maker — Create Cat Content, Behavior, and Feline Life Videos

Describe your cat content and NemoVideo creates the video. Daily life vlogs, behavior explanations, enrichment setups, cat introductions, funny moments, senior cat care — narrate your cat's personality, your observations, and the specific moments worth capturing, and get cat video content for the platform audiences that never get tired of watching cats.

## When to Use This Skill

Use this skill for cat and feline content:
- Create cat daily life and personality showcase videos
- Film cat behavior explanation content (why cats do what cats do)
- Build cat enrichment and play setup tutorial content
- Document multi-cat household introduction and relationship content
- Create senior cat care and special needs cat content
- Produce cat breed-specific content and comparison videos

## How to Describe Your Cat Content

Be specific about the cat's personality, the behaviors you're documenting, and what makes this content worth watching.

**Examples of good prompts:**
- "My cat Mango's morning routine — he is deeply opinionated: Mango wakes me up at 5:47am every day (tested: he cannot tell time, he wakes up when the first birds start outside the window). The routine: he sits on my chest for exactly 3 minutes, then walks to the food bowl and sits facing away from me (the pressure tactic), then when I don't move, he knocks something off my nightstand. He has never knocked anything breakable — he scans for something low-stakes first. The payoff is watching him eat enthusiastically for 45 seconds then pretend he didn't want food anyway."
- "Why cats knock things off surfaces — the behavior explanation: The three actual reasons (not spite, spite is a human projection): (1) testing whether objects are alive (cats are predators who need to confirm kills), (2) soliciting interaction (it works — we always respond), (3) tactile exploration. Show each behavior with real footage examples and the cat body language that indicates which motivation is active."
- "Introducing a second cat to a resident cat — the 6-week process we did: We adopted a 2-year-old rescue tabby (Henry) when our resident cat (Dolores, 6 years, strongly introverted) had been an only cat for 4 years. The steps we followed: scent swap before visual introduction, feeding on opposite sides of a door, controlled visual meetings with a baby gate, supervised time in shared space, and the first unsupervised night. Show the hissing (week 1), the careful parallel eating (week 3), and the first time Dolores chose to sit on the same couch as Henry (week 7 — one week past our optimistic estimate)."

## Key Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `content_type` | Video category | `"daily_life"`, `"behavior_explainer"`, `"enrichment"`, `"introduction"`, `"care"`, `"funny"` |
| `cat_name` | Cat's name | `"Mango"`, `"Dolores"`, `"Henry"` |
| `cat_profile` | Cat description | `"6-year-old introverted tortoiseshell"`, `"2-year-old rescue tabby"` |
| `key_moments` | Highlights | `["nightstand knock"`, `"first couch sharing"`, `"pressure tactic"]` |
| `tone` | Content style | `"funny"`, `"educational"`, `"heartfelt"`, `"documentary"` |
| `duration_minutes` | Video length | `3`, `5`, `8`, `12` |
| `platform` | Distribution | `"youtube"`, `"tiktok"`, `"instagram"` |

## Workflow

1. Describe the cat, the content focus, and the key moments
2. NemoVideo structures the cat content with appropriate personality and pacing
3. Cat name, behavior labels, and moment callouts added automatically
4. Export with cat-appropriate pacing (patient, observational, comic timing)

## API Usage

### Cat Behavior Explainer

```bash
curl -X POST https://mega-api-prod.nemovideo.ai/v1/run \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "cat-video-maker",
    "input": {
      "prompt": "Why cats slow blink and what it means: The slow blink is cat language for 'I am comfortable with you and I am not a threat.' It is one of the clearest affectionate signals a cat gives. The science: slow blinking releases tension, signals non-aggression, and in studies cats were more likely to approach humans who slow-blinked back at them than humans with a neutral expression. How to slow-blink your own cat: make eye contact at a relaxed distance (not staring — relaxed), slowly close and open your eyes, look slightly away after. Show footage of cats slow-blinking and humans successfully exchanging slow blinks with their cats. The moment a cat slow-blinks back is the best thing in the world.",
      "content_type": "behavior_explainer",
      "key_moments": ["cat slow blinking", "successful human slow blink exchange"],
      "tone": "educational",
      "duration_minutes": 5,
      "platform": "youtube",
      "hashtags": ["CatBehavior", "CatFacts", "WhyCatsDo", "CatScience", "CatContent"]
    }
  }'
```

**Response:**
```json
{
  "job_id": "catvideo_def456",
  "status": "processing",
  "estimated_seconds": 90,
  "poll_url": "https://mega-api-prod.nemovideo.ai/v1/jobs/catvideo_def456"
}
```

## Tips for Best Results

- **The cat's specific personality is the content**: "He scans for something low-stakes before knocking it off" or "Dolores, strongly introverted" — treating your cat as an individual with specific traits creates more compelling content than generic "cute cat" footage
- **Behavior explanation beats cute footage alone**: Cat videos with behavioral context ("why cats do this" or "what this means") perform better in search and get shared more than pure cute footage
- **The non-obvious fact is the hook**: "Spite is a human projection — here are the three real reasons" or "cats slow-blink to signal non-aggression" — correcting common misunderstandings about cat behavior drives strong engagement
- **Introduction stories are series content**: Multi-cat introductions over weeks give you a built-in series with an emotional arc and a real pay-off moment (the first time they coexist peacefully)
- **Comic timing is a real consideration**: Describe the timing of funny moments ("45 seconds of enthusiastic eating then he pretended he didn't want food anyway") — NemoVideo builds comic pacing into the video structure

## Output Formats

| Platform | Resolution | Duration |
|----------|------------|----------|
| YouTube | 1920×1080 | 5–12 min |
| TikTok | 1080×1920 | 15–180s |
| Instagram Reels | 1080×1920 | 15–90s |

## Related Skills

- `pet-vlog-maker` — Multi-pet household daily life content
- `dog-training-video` — Training and behavior content for dogs
- `animal-rescue-video` — Rescue and adoption story content

## Common Questions

**What cat content performs best on different platforms?**
TikTok rewards unexpected behavior and comic moments (short, specific, funny). YouTube rewards educational behavior explainers and "day in the life" longer content. Instagram rewards aesthetically beautiful cats and heartwarming moments.

**Can I make cat content without professional animal behavior knowledge?**
Yes — personal observation content ("here's what I've noticed about my cat") is valuable and authentic. For behavior explanation content, describe your cats' behaviors and NemoVideo helps structure the explanation appropriately.

**How do I film cats who don't cooperate?**
Describe the behavior you want to capture and the context in which it happens naturally ("he does this every morning at 5:47am") — NemoVideo structures the narrative to work with candid, opportunistic footage rather than staged setups.
