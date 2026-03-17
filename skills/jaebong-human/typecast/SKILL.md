---
name: cast
description: Multilingual TTS via Typecast CLI with emotion control. Plays audio aloud or saves to file.
metadata: {"clawdbot":{"emoji":"💬","requires":{"bins":["cast"],"env":["TYPECAST_API_KEY"]},"primaryEnv":"TYPECAST_API_KEY","install":[{"id":"brew","kind":"brew","formula":"neosapience/tap/cast","bins":["cast"],"label":"Install cast (brew)"}]}}
---

# cast — Typecast TTS CLI

## Quick start

```bash
cast "Hello!"                                # play immediately
cast "Hello" --out hello.mp3 --format mp3   # save to file
cast "I can't believe it!" --emotion smart  # AI emotion inference
```

## Voices

```bash
cast voices list                            # list all voices
cast voices list --gender female
cast voices list --model ssfm-v30
cast voices get <voice_id>                  # voice details
cast config set voice-id <tc_xxx>           # set default voice
```

## Emotions

- `--emotion smart` — AI infers emotion from text (ssfm-v30 only)
- `--emotion preset --emotion-preset <preset>` — explicit preset

| preset | model |
|--------|-------|
| normal / happy / sad / angry | ssfm-v21, ssfm-v30 |
| whisper / toneup / tonedown | ssfm-v30 only |

```bash
cast "I'm so happy!" --emotion preset --emotion-preset happy --emotion-intensity 1.5
cast "I just got promoted!" --emotion smart \
  --prev-text "I worked so hard." --next-text "Let's celebrate!"
```

## Key flags

| flag | default | description |
|------|---------|-------------|
| `--voice-id` | — | voice ID |
| `--model` | ssfm-v30 | ssfm-v30 (quality) / ssfm-v21 (low latency) |
| `--tempo` | 1.0 | speed (0.5–2.0) |
| `--pitch` | 0 | pitch (–12 ~ +12) |
| `--volume` | 100 | volume (0–200) |
| `--out` | — | output file path |
| `--format` | wav | wav / mp3 |
| `--seed` | — | reproducible output |

## Recipes

```bash
echo "System ready." | cast
cast "$(cat script.txt)"
cast "Hello!" --out /tmp/hi.mp3 --format mp3
cast "Hello" --tempo 1.2 --pitch 2 --emotion preset --emotion-preset happy
```

## Auth / config

```bash
cast login <api_key>     # save API key
cast config list         # show current config
cast config set model ssfm-v21
```

Env vars (TYPECAST_ prefix):

| Variable | Flag |
|----------|------|
| `TYPECAST_API_KEY` | `--api-key` |
| `TYPECAST_VOICE_ID` | `--voice-id` |
| `TYPECAST_MODEL` | `--model` |
| `TYPECAST_LANGUAGE` | `--language` |
| `TYPECAST_EMOTION` | `--emotion` |
| `TYPECAST_EMOTION_PRESET` | `--emotion-preset` |
| `TYPECAST_EMOTION_INTENSITY` | `--emotion-intensity` |
| `TYPECAST_FORMAT` | `--format` |
| `TYPECAST_VOLUME` | `--volume` |
| `TYPECAST_PITCH` | `--pitch` |
| `TYPECAST_TEMPO` | `--tempo` |