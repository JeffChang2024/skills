---
name: mobile-gaming-video
version: 1.0.2
displayName: "Mobile Gaming Video Maker"
description: >
  Describe your mobile gaming topic and NemoVideo creates the video. Mobile game reviews and recommendations, gacha game strategy content, mobile gaming tips and tricks, free-to-play vs pay-to-win analysis, mobile gaming setup content, game optimization guides — narrate the specific game, the mechanics that matter, the honest assessment of the monetization model, and the tips that help players pr...

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

> 📹 Ready to mobile gaming video! Just send me a video or describe your project.

**Try saying:**
- "edit my video"
- "add effects to this clip"
- "help me create a short video"

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


# Mobile Gaming Video Maker — Create Mobile Game Review, Tips, and Content

Describe your mobile gaming topic and NemoVideo creates the video. Mobile game reviews and recommendations, gacha game strategy content, mobile gaming tips and tricks, free-to-play vs pay-to-win analysis, mobile gaming setup content, game optimization guides — narrate the specific game, the mechanics that matter, the honest assessment of the monetization model, and the tips that help players progress without spending.

## When to Use This Skill

- Create mobile game review and recommendation content
- Film gacha game strategy and tier list content
- Build free-to-play guide and spending analysis content
- Document mobile gaming setup and controller content
- Create mobile game comparison and "worth playing" content
- Produce mobile gaming optimization and performance content

## How to Describe Your Mobile Gaming Content

Be specific about the game, the mechanics that matter, the monetization reality, and the honest assessment for players deciding whether to invest time.

**Examples of good prompts:**
- "Clash Royale F2P guide — what actually works in 2026 without spending: Clash Royale has a reputation as a pay-to-win game. This is partially true and partially not. The F2P reality in 2026: King has changed the progression system 3 times since launch. The current system (Path of Legends) separates player rating from card levels. What this means for F2P: you can climb to a high rating with underleveled cards because you play against similarly-leveled opponents. The specific strategy that works: pick one deck, upgrade those 8 cards only for the first 4 months, ignore everything else. The chest cycle is the most efficient gold source — open 4 chests daily, don't let them pile up. Pass Royale ($5/month): the one purchase that changes the F2P equation more than any other. The cards it's not worth chasing: the newest legendaries. They will be balanced down. Wait 3 months after launch."
- "Genshin Impact — honest guide for new players in 2026: Genshin Impact is 4 years old and has accumulated content that makes new players feel immediately behind. Here's what actually matters. What doesn't matter for new players: artifact stats (you'll replace them 4 times in your first month), the current banner characters (you don't have the Resin to build them yet), other players' accounts on social media (those are 3-4 year accounts). What matters for new players: finishing Archon Quests (the main story, which unlocks most game systems), building one or two characters from the free roster to a functional level (Bennett, Noelle, Xiangling, and Fischl are all top-tier and completely free), and spending Resin only on Ley Line Blossoms for the first month (the most efficient resource use before you have good artifacts to farm). The free currency situation: Genshin is more generous with free Primogems than its reputation suggests — completing quests and exploration gives substantial pulls over time."
- "Call of Duty Mobile versus Warzone Mobile — which is actually better in 2026: Both are free, both are mobile, both are made by Activision. The difference matters. COD Mobile: 6 years of content, larger map selection, slightly better optimization for mid-range phones, better classic COD multiplayer modes. Warzone Mobile: the actual Warzone experience on mobile, better graphics on high-end devices, cross-progression with console/PC Warzone. The honest verdict: COD Mobile if you want a complete mobile-native experience with breadth of content. Warzone Mobile if you want the full battle royale experience and have a phone released in the last 2 years. The overheating issue on Warzone Mobile: real on any phone below flagship tier. COD Mobile runs on 3-year-old phones without thermal throttling."

## Key Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `content_type` | Content type | `"review"`, `"f2p_guide"`, `"gacha_strategy"`, `"comparison"`, `"setup"` |
| `game_title` | Mobile game | `"Clash Royale"`, `"Genshin Impact"`, `"COD Mobile"` |
| `monetization_reality` | Spending assessment | `"Pass Royale $5/mo changes F2P math"`, `"more generous than reputation"` |
| `f2p_strategy` | No-spend approach | `"one deck, 8 cards, 4 months"`, `"Ley Line Blossoms first month"` |
| `common_mistake` | What wastes time | `["chasing newest legendaries"`, `"building artifacts too early"`, `"comparing to 4-year accounts"]` |
| `honest_verdict` | Who should play it | `"mid-range phone: COD Mobile; flagship: Warzone Mobile"` |
| `duration_minutes` | Video length | `5`, `8`, `12` |
| `platform` | Distribution | `"youtube"`, `"tiktok"` |

## Workflow

1. Describe the game, the monetization reality, the F2P strategy, and the honest verdict
2. NemoVideo structures the mobile gaming content with tip callouts and verdict formatting
3. Game title, spending analysis, and F2P strategy markers added automatically
4. Export with mobile gaming pacing suited to the casual and competitive mobile audience

## API Usage

```bash
curl -X POST https://mega-api-prod.nemovideo.ai/v1/run \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "mobile-gaming-video",
    "input": {
      "prompt": "Brawl Stars — the tier list and what actually matters for F2P in ranked: Brawl Stars has one of the more F2P-friendly models in mobile gaming if you understand the mechanics. The ranking system: Trophy Road up to 500 trophies per Brawler is achievable for every F2P player. Above 500 is Ranked, where matchmaking becomes skill-weighted rather than power-weighted. What matters for ranked: mastering 3-4 Brawlers deeply beats owning 40 at mediocre level. The Brawl Pass ($5/month): doubles progression speed and is the one purchase that changes the game significantly — but it's not necessary to compete. The F2P path that works: focus on Brawlers from the starting pool (Shelly, Colt, Nita, Dynamike — free, viable, well-understood). Play ranked only with your best 2-3 Brawlers. Tier lists are largely irrelevant below Master tier — the Brawler you know beats the Brawler that's theoretically better. The meta shift reality: Brawl Stars patches every 2 months and the meta changes completely. Don't invest resources in a Brawler that was buffed last month.",
      "content_type": "f2p_guide",
      "game_title": "Brawl Stars",
      "monetization_reality": "Brawl Pass $5/mo doubles progression, not necessary to compete",
      "f2p_strategy": "3-4 Brawlers deep beats 40 at mediocre level, start with free pool",
      "common_mistake": ["investing in recently-buffed Brawlers before meta settles", "using tier lists below Master tier"],
      "honest_verdict": "one of the more F2P-friendly mobile games if you understand progression",
      "duration_minutes": 8,
      "platform": "youtube",
      "hashtags": ["MobileGaming", "BrawlStars", "F2PGuide", "MobileGames", "GamingTips"]
    }
  }'
```

## Tips for Best Results

- **The monetization reality is the most-searched mobile gaming content**: "Pass Royale $5/month changes the F2P equation more than any other purchase" — the specific spending threshold that meaningfully changes the game experience is the answer to the question every mobile gamer has
- **What doesn't matter for new players**: "Don't worry about artifact stats for your first month — you'll replace them 4 times" — the explicit list of things to ignore is as valuable as the things to focus on, and dramatically reduces new player overwhelm
- **The F2P strategy that requires one commitment**: "Pick one deck, upgrade only those 8 cards, ignore everything else for 4 months" — the specific single commitment that makes F2P work is more actionable than general efficiency tips
- **The comparison that answers the real question**: "Flagship phone: Warzone Mobile. Mid-range phone: COD Mobile — thermal throttling is real on Warzone" — the hardware-specific recommendation is the practical differentiator in mobile game comparison content
- **Meta shift awareness**: "Brawl Stars patches every 2 months — don't invest in a Brawler that was buffed last month" — the resource allocation timing advice is specific to mobile gaming and not covered in most guides

## Output Formats

| Platform | Resolution | Duration |
|----------|------------|----------|
| YouTube | 1920×1080 | 8–15 min |
| TikTok | 1080×1920 | 60–180s |

## Related Skills

- `gaming-video-maker` — General gaming content
- `game-tutorial-video` — Game guide and strategy content
- `gaming-highlights-video` — Gaming clip and moment content
