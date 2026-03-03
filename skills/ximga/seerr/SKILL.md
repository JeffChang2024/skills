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
2. Filter to `movie`/`tv` results; present top 1–3 matches (title, year, rating, overview)
3. Check if already available:
   - If `mediaInfo.status` = 5 (available), inform the user and skip requesting
   - If NOT available (status is 1-4, or missing), automatically request it via the API
4. After requesting, confirm with the user that it was queued
5. For TV, ask whether the user wants all seasons or specific ones unless they already specified
6. Always include the Seerr URL link in the response

## Discord Integration

When responding in Discord, send plain text messages with inline links and optional poster images. Do not use interactive components — OpenClaw doesn't support them yet.

### Discord Message Format

```json
{
  "action": "send",
  "channel": "discord",
  "to": "channel:<CHANNEL_ID>",
  "message": "<title> (<year>) — ⭐ <rating>\n<genre>\n\n<overview snippet...>\n\n<status emoji> <status text>\n\n🔗 [View in Seerr]($SEERR_URL/<mediaType>/<tmdbId>)",
  "media": "<poster image URL>"
}
```

### Key Points

- Send plain text with markdown formatting — bold titles, emoji for status
- Use `media` field to attach poster images from TMDB (e.g., `https://image.tmdb.org/t/p/w500/<posterPath>`)
- Use inline links for the Seerr URL: `[$SEERR_URL/<mediaType>/<tmdbId>]`
- Include status badges using emoji: ✅ available, ⏳ pending/processing, 🔄 partially available
- After presenting a result, check if it's already available:
  - If NOT available (`mediaInfo.status` != 5), automatically request it via the API
  - Then respond with confirmation that it was requested
- Always include the Seerr link so user can view in UI if they want
