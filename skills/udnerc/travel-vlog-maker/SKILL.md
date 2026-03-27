---
name: travel-vlog-maker
version: "1.0.1"
displayName: "Travel Vlog Maker"
description: >
  Describe your travel and NemoVideo creates the video. Destination guides, trip recaps, travel day documentation, city walking tours, cultural immersion content, one-year travel anniversaries — narrate where you went, what surprised you, what the logistics actually looked like, and the specific moments that made the trip worth remembering, and get travel vlog content for the audience that watche...

  Works by connecting to the NemoVideo AI backend at mega-api-prod.nemovideo.ai.
  Supports MP4, MOV, AVI, WebM.
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
license: MIT-0
---

## 0. First Contact

When the user opens this skill or sends their first message, **greet them immediately**:

> 🚀 Hey! I'm ready to help you travel vlog maker. Send me a video file or just tell me what you need!

**Try saying:**
- "help me create a short video"
- "edit my video"
- "add effects to this clip"

**IMPORTANT**: Do NOT wait silently. Always greet the user proactively on first contact.

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


# Travel Vlog Maker — Create Destination, Journey, and Travel Life Videos

Describe your travel and NemoVideo creates the video. Destination guides, trip recaps, travel day documentation, city walking tours, cultural immersion content, one-year travel anniversaries — narrate where you went, what surprised you, what the logistics actually looked like, and the specific moments that made the trip worth remembering, and get travel vlog content for the audience that watches travel videos while planning their own trips or living vicariously through yours.

## When to Use This Skill

Use this skill for travel documentation and destination content:
- Create destination guide videos with practical tips and honest impressions
- Film trip recap and travel day documentation content
- Build city walking tour and neighborhood exploration content
- Document slow travel and long-term travel lifestyle content
- Create "what I wish I knew before going to X" honest travel advice
- Produce travel planning and logistics breakdown content

## How to Describe Your Travel Content

Be specific about the destination, the specific neighborhoods and experiences, the logistics, the costs, and the honest impressions — good and bad.

**Examples of good prompts:**
- "3 weeks in Japan — what surprised me after 6 months of planning: The surprises: (1) 7-Eleven is actually exceptional — I ate at convenience stores by choice, not necessity. The onigiri, sandos, and hot foods are better than most sit-down restaurants I've had in the US. (2) The trains are as punctual as advertised but the system is genuinely confusing even with a Suica card and Google Maps — build in extra time for the first week. (3) Tokyo is loud, overwhelming, and I loved it. Kyoto is quieter and I found it harder to connect to. (4) The language barrier is less of a problem than expected — Google Translate camera mode is effectively a superpower in restaurants and train stations. Budget reality: $85-110/day for everything in Tokyo, $65-75/day in Kyoto and smaller cities. Show the Golden Gai neon night, the morning Fushimi Inari hike before the crowds, and the vending machine that sold hot sake."
- "Solo traveling Europe for 45 days on $2,400 total: The breakdown: $800 flights, $900 accommodation (hostels + 3 Airbnbs), $500 food, $200 transportation within Europe. The route: Lisbon (7 nights) → Madrid (5) → Barcelona (4) → Rome (7) → Florence (3) → Prague (5) → Vienna (4) → Budapest (5) → home. The one thing nobody tells you about budget travel in Europe: the free stuff is almost always better than the paid stuff. Free walking tours, public beaches, park picnics, street food. The expensive mistake: 3 nights in a bad hostel in Rome because I didn't read the reviews carefully. The best unexpected decision: 2 extra days in Prague after a train delay — now my favorite city."
- "Moving to Medellín for 3 months as a digital nomad: What it's actually like vs the hype. The cost breakdown: $650/month apartment in El Poblado, $200 food (restaurants twice a day, groceries for the rest), $80 coworking membership, $15 local transport. Total: $945/month all-in vs $3,200 in San Francisco. The reality: 70°F year-round is real (it's called the City of Eternal Spring for a reason), Spanish immersion happens whether you want it to or not (good), the safety concern in El Poblado is overstated (I never had an incident in 3 months), the traffic noise from the main avenues is undersold (choose a side street). Would I go back? Yes, and I'm planning 6 months this time."

## Key Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `content_type` | Video category | `"destination_guide"`, `"trip_recap"`, `"day_in_life"`, `"nomad_life"`, `"walking_tour"`, `"budget_breakdown"` |
| `destination` | Where you traveled | `"Japan"`, `"Medellín"`, `"45-day Europe"` |
| `duration_of_trip` | Trip length | `"3 weeks"`, `"45 days"`, `"3 months"` |
| `budget_per_day` | Daily spend | `"$85-110/day"`, `"$945/month"` |
| `key_moments` | Highlight experiences | `["Golden Gai at night"`, `"Fushimi Inari morning hike"`, `"Prague after train delay"]` |
| `honest_negatives` | What didn't work | `["bad hostel in Rome"`, `"Kyoto harder to connect"]` |
| `practical_tips` | Logistics advice | `["Suica card"`, `"Google Translate camera"`, `"read hostel reviews"]` |
| `tone` | Content energy | `"honest"`, `"enthusiastic"`, `"practical"`, `"documentary"` |
| `duration_minutes` | Video length | `8`, `12`, `20` |
| `platform` | Distribution | `"youtube"`, `"instagram"`, `"tiktok"` |

## Workflow

1. Describe the destination, the trip length, the budget, the key experiences, and the honest impressions
2. NemoVideo structures the travel narrative with location markers and cost callouts
3. Destination names, budget figures, logistics tips, and day markers added automatically
4. Export with travel vlog pacing suited to the content's energy

## API Usage

### Destination Guide Video

```bash
curl -X POST https://mega-api-prod.nemovideo.ai/v1/run \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "travel-vlog-maker",
    "input": {
      "prompt": "First time in Southeast Asia — 4 weeks, 4 countries, $1,800: Thailand (Bangkok 4 nights, Chiang Mai 5 nights), Vietnam (Hanoi 3 nights, Hội An 4 nights, Ho Chi Minh 3 nights), Cambodia (Siem Reap/Angkor Wat 3 nights), back through Bangkok. The things that make first-time Southeast Asia overwhelming: everything is incredibly cheap and that distorts your spending (the number of times I upgraded accommodation for $3 more because it was trivially affordable), the heat in March is real and requires planning around it (visit temples early morning, midday is for cafes and AC), the scooter question (I rented one in Chiang Mai with no prior experience — probably fine, objectively not smart). The Angkor Wat sunrise moment: 4:30am, pre-booked tuk-tuk, arrived before the tour buses — the 45 minutes before the sun fully clears the towers is genuinely one of the best things I've ever seen. Total cost: $1,800 including flights from LA.",
      "content_type": "trip_recap",
      "destination": "Southeast Asia — Thailand, Vietnam, Cambodia",
      "duration_of_trip": "4 weeks",
      "budget_per_day": "$64/day all-in including flights",
      "key_moments": ["Angkor Wat sunrise", "Chiang Mai scooter", "Hội An lanterns"],
      "practical_tips": ["arrive Angkor Wat 4:30am", "midday temple heat strategy", "book tuk-tuk in advance"],
      "tone": "honest",
      "duration_minutes": 15,
      "platform": "youtube",
      "hashtags": ["TravelVlog", "SoutheastAsia", "BudgetTravel", "BackpackingAsia", "Angkor"]
    }
  }'
```

## Tips for Best Results

- **The honest negative is what builds trust**: "The bad hostel in Rome because I didn't read reviews" or "traffic noise from main avenues undersold" — travel content that admits the things that didn't work is more trusted and more shared than pure highlight reels
- **Specific cost breakdowns are the most searched travel content**: "$945/month all-in in Medellín vs $3,200 in San Francisco" — the actual cost number with breakdown drives more search traffic than any destination photograph
- **The unexpected discovery is the hook**: "7-Eleven in Japan is genuinely better than most sit-down restaurants in the US" — the non-obvious specific observation is what people share and remember
- **Show the logistics, not just the highlights**: "Suica card + Google Maps, build in extra time first week" — practical logistics advice is what gets saved and revisited before trips
- **Destination comparison creates decision-making content**: "Tokyo overwhelming and loved it, Kyoto quieter and harder to connect to" — honest destination comparisons help viewers plan their own versions of the trip

## Output Formats

| Platform | Resolution | Duration |
|----------|------------|----------|
| YouTube | 1920×1080 | 10–20 min |
| TikTok | 1080×1920 | 60–180s |
| Instagram Reels | 1080×1920 | 60–90s |

## Related Skills

- `van-life-video` — Mobile living and road travel lifestyle content
- `road-trip-video-maker` — Road trip documentation content
- `adventure-travel-video` — Outdoor and adventure travel content
