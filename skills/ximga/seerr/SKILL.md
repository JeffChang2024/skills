---
name: seerr
description: Search for movies and TV shows via a Seerr instance and request them for download. Use when the user asks to download, find, request, or queue a movie or TV show. Requires a running Seerr instance with Sonarr/Radarr configured.
env:
  - SEERR_URL
  - SEERR_API_KEY
---

# Seerr Media Requests

Search and request movies/TV shows through Seerr's API. Seerr routes movie requests to Radarr and TV requests to Sonarr automatically.

## Setup

The agent needs two environment variables. Store them in your OpenClaw environment or `.env` file:

- `SEERR_URL` — Base URL of the Seerr instance (e.g. `http://localhost:5055` if running locally, or `http://<server-ip>:5055` for remote)
- `SEERR_API_KEY` — API key from Seerr → Settings → General

**Important:** Always use `$SEERR_URL` (not hardcoded localhost) in API calls so it works regardless of where Seerr is hosted.

## API Reference

All requests require the header `X-Api-Key: <SEERR_API_KEY>`.

### Search

```bash
curl -s -H "X-Api-Key: $SEERR_API_KEY" \
  "$SEERR_URL/api/v1/search?query=PERCENT_ENCODED_QUERY&page=1&language=en"
```

Results array. Key fields per result:
- `mediaType` — `movie`, `tv`, or `person`
- `id` — TMDB id (used for requests)
- `title` (movies) / `name` (TV)
- `releaseDate` / `firstAirDate`
- `overview`
- `mediaInfo.status` — `1` (unknown), `2` (pending), `3` (processing), `4` (partially available), `5` (available). Absent if never requested.

Filter results to `mediaType` of `movie` or `tv` only.

### Request a Movie

```bash
curl -s -X POST -H "X-Api-Key: $SEERR_API_KEY" -H "Content-Type: application/json" \
  "$SEERR_URL/api/v1/request" \
  -d '{"mediaType":"movie","mediaId":TMDB_ID}'
```

### Request a TV Show

All seasons:
```bash
curl -s -X POST -H "X-Api-Key: $SEERR_API_KEY" -H "Content-Type: application/json" \
  "$SEERR_URL/api/v1/request" \
  -d '{"mediaType":"tv","mediaId":TMDB_ID,"seasons":"all"}'
```

Specific seasons:
```bash
curl -s -X POST -H "X-Api-Key: $SEERR_API_KEY" -H "Content-Type: application/json" \
  "$SEERR_URL/api/v1/request" \
  -d '{"mediaType":"tv","mediaId":TMDB_ID,"seasons":[1,3]}'
```

### Check Status

```bash
# Movie
curl -s -H "X-Api-Key: $SEERR_API_KEY" "$SEERR_URL/api/v1/movie/TMDB_ID"

# TV
curl -s -H "X-Api-Key: $SEERR_API_KEY" "$SEERR_URL/api/v1/tv/TMDB_ID"
```

## Workflow

1. Search for the title
2. Filter to `movie`/`tv` results; present top 1–3 matches (title, year, brief overview)
3. If a single clear match exists, confirm with the user and request it
4. If multiple plausible matches, ask the user to pick
5. If already available (`mediaInfo.status` = 5), inform the user
6. After requesting, confirm it has been queued
7. For TV, ask whether the user wants all seasons or specific ones unless they already specified

## Discord Integration

When responding in Discord, use interactive cards with buttons instead of plain text. This gives the user a one-click experience.

### Discord Message Format

```json
{
  "action": "send",
  "channel": "discord",
  "to": "channel:<CHANNEL_ID>",
  "message": "<title> (<year>)\n<overview snippet...>",
  "components": {
    "type": "container",
    "blocks": [
      {
        "type": "text",
        "text": "**Results for:** <query>",
        "style": "rich"
      },
      {
        "type": "context",
        "content": "Each result: title, year, status badge, request button"
      },
      {
        "type": "action_row",
        "buttons": [
          {
            "type": "button",
            "label": "Request Movie",
            "style": "primary",
            "url": "$SEERR_URL/<mediaType>/<tmdbId>"
          }
        ]
      }
    ]
  }
}
```

### Key Points

- Use `components` (Discord v2) not `embeds` — they can't be combined
- Buttons use `url` field to link to Seerr's direct request page
- Build URL as: `$SEERR_URL/<mediaType>/<tmdbId>` (e.g., `$SEERR_URL/movie/550` or `$SEERR_URL/tv/1396`)
- For multiple results, use a `select` component or multiple button rows
- Keep message text brief — let the card carry the detail
- Include status badges (available/pending/processing) using emoji: ✅ available, ⏳ pending, 🔄 processing
