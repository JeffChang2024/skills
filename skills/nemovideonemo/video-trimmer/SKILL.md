---
name: video-trimmer
version: "1.0.4"
displayName: "Video Trimmer — Cut, Trim and Split Video Clips with AI Chat"
description: >
  Video Trimmer — Cut, Trim and Split Video Clips with AI Chat.
  Too much footage, not enough patience for a full edit. Video Trimmer handles precise cuts through conversation: specify timestamps, describe the section you want to keep, or tell the AI what to remove. 'Cut the first 30 seconds and everything after 2:15' or 'remove the section where the speaker pauses' — the AI handles the frame-accurate cut and delivers the trimmed output. Works for removing dead air from recordings, cutting interview footage to the key moments, extracting highlight clips from long videos, and preparing raw footage for distribution. Batch trim multiple clips in one session. Combine trimming with color correction, subtitles, and music in the same chat. Export as MP4. Supports mp4, mov, avi, webm, mkv.
  
  Works by connecting to the NemoVideo AI backend at mega-api-prod.nemovideo.ai.
  Supports MP4, MOV, AVI, WebM.
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
license: MIT-0
---

# Video Trimmer — Cut, Trim and Split Video Clips with AI Chat

Cut and trim videos through chat commands. Remove unwanted sections and split clips without timeline editing.

## Quick Start
Ask the agent to trim or cut your video using plain language.

## What You Can Do
- Trim videos by specifying start and end times
- Cut out unwanted sections from the middle
- Split long videos into multiple shorter clips
- Extract specific segments or highlights
- Remove intro/outro sections automatically

## API
Uses NemoVideo API (mega-api-prod.nemovideo.ai) for all video processing.
