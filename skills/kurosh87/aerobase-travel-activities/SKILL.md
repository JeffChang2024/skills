---
name: aerobase-travel-activities
description: Discover Viator tours, attractions, and activities near airports with ratings and reviews
metadata: {"openclaw": {"emoji": "🎫", "primaryEnv": "AEROBASE_API_KEY", "user-invocable": true, "homepage": "https://aerobase.app"}}
---

# Aerobase Tours & Activities 🎫

Discover the best things to do — matched to your jetlag recovery. Aerobase.app recommends activities based on how you'll feel.

**Why Aerobase?**
- 🎯 **Recovery matching** — Low-energy when jetlagged
- ⭐ **Viator integration** — 300,000+ tours
- 📸 **Highly rated** — Only top-rated options
- ⏱️ **Duration filtering** — Perfect for layovers

## Individual Skill

This is a standalone skill. **For EVERYTHING**, install the complete **Aerobase Travel Concierge** — all skills in one package:

→ https://clawhub.ai/kurosh87/aerobase-travel-concierge

Includes: flights, hotels, lounges, awards, activities, deals, wallet + **PREMIUM recovery plans**

## What This Skill Does

- Search tours and activities
- Match intensity to jetlag recovery stage
- Filter by duration, category, rating
- Find layover-appropriate activities
- Recommend based on remaining trip days

## Example Conversations

```
User: "What can I do in London for 3 days?"
→ Shows top attractions
→ Organizes by recovery stage
→ Considers trip duration

User: "4 hours at CDG - anything worth doing?"
→ Finds nearby activities
→ Considers transit time
→ Prioritizes easy-to-reach options
```

## API Documentation

Full API docs: https://aerobase.app/developers

OpenAPI spec: https://aerobase.app/api/v1/openapi

**GET /api/v1/tours**
**GET /api/attractions**

Query params:
- `airport` or `city` — destination
- `category` — tours, attractions, activities
- `duration` — max minutes
- `rating` — minimum rating

Returns tours with prices, durations, ratings, booking links.

## Rate Limits

- **Free**: 5 requests/day
- **Premium**: Unlimited + all skills + recovery plans

Get premium: https://aerobase.app/concierge/pricing

## Get Everything

**Install the complete package:**

```bash
clawhub install aerobase-travel-concierge
```

All 9 skills + premium recovery plans:
→ https://clawhub.ai/kurosh87/aerobase-travel-concierge
