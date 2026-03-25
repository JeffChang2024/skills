---
name: brand-marketing-workflow
description: >
  Structural documentation for the brand-marketing-workflow skill. Use when the user wants to understand, audit, or review the workflow design without exposing implementation code.
---

# Brand Marketing Workflow — Structural Reference

## What This Skill Is
A documentation-only description of the brand marketing workflow. It explains the system architecture, roles, stages, boundaries, and outputs, but contains no executable code.

## Purpose
- Describe how brand inputs are turned into marketing plans
- Clarify the handoff between strategy, production, analysis, and review
- Define the human-approval boundaries for publishing, login, payment, or other sensitive actions
- Serve as a safe replacement artifact when the published skill should be withdrawn from active use

## Structure
### 1) Input Layer
- Brand name
- Positioning
- Tone
- Audience
- Goals
- Channels
- Constraints
- Competitor scope

### 2) Planning Layer
- Normalize brand input
- Build a concise brand brief
- Define content pillars
- Define channel mapping
- Define KPI targets

### 3) Production Layer
- Draft content variants
- Draft campaign ideas
- Draft platform-specific formats
- Prepare review-ready assets

### 4) Analysis Layer
- Compare public competitor signals
- Identify messaging patterns
- Identify content gaps
- Score brand fit and iteration opportunities

### 5) Authorization Layer
- Pause on actions that cross policy or access boundaries
- Request explicit human confirmation
- Resume only after approval

### 6) Output Layer
- Brand brief
- Content plan
- Competitor summary
- Performance review
- Iteration notes
- Approval requests when needed

## Boundaries
### Allowed
- Public information review
- Structural planning
- Draft generation
- High-level workflow explanation

### Not Allowed
- Hidden scraping
- Bypassing login or platform controls
- Automatic publishing
- Payment or recharge without approval
- Any misleading claim that implementation code still ships inside this replacement artifact

## Replacement Intent
This document is intended to replace the previously published active skill with a non-executable structural explanation. It is safe to publish as a reference-only version when the goal is to remove implementation details.

## Suggested Next Step
If the user wants, the next version should be rebuilt as a minimal spec-first skill with:
- design overview
- human approval checkpoints
- output schema
- no runtime logic
