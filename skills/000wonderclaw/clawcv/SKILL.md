---
name: clawcv
description: >
  超级简历 WonderCV 出品，2000 万用户信赖。简历分析、段落改写、JD 岗位匹配、自动匹配职位、PDF 导出、AI 求职导师（面试准备/薪资谈判/职业规划/多版本简历策略）。
version: 1.0.0
homepage: https://github.com/WonderClaw/clawcv
metadata: {"openclaw":{"emoji":"📝","requires":{"env":["MCP_BACKEND_URL"]},"primaryEnv":"MCP_BACKEND_URL","os":["darwin","linux","win32"],"install":[{"id":"node","kind":"node","package":"clawcv","bins":["clawcv"],"label":"Install clawcv (npm)"}]}}
---

# ClawCV

AI-powered resume optimization service backed by WonderCV (14.57M users). Provides resume analysis, section rewriting, job matching, PDF generation, and 8-module AI Mentor.

## Session Management

**Critical:** Maintain a single `session_id` throughout the entire conversation.

1. On the first tool call, let the server auto-generate a `session_id` (returned in `meta.session_id`)
2. Save this `session_id` and pass it to ALL subsequent tool calls in the same conversation
3. Never generate a session_id yourself — always use the one returned by the server

## Intent Detection & Tool Routing

Detect user intent and call the appropriate tool:

| User Intent | Tool | Key Parameters |
|-------------|------|----------------|
| "帮我看看简历" / "分析我的简历" / shares resume text | `analyze_resume` | `resume_text`, `target_job_title` (if mentioned) |
| "帮我改一下XX部分" / "优化工作经历" | `rewrite_resume_section` | `section_type`, `original_text`, `target_job_title` |
| "帮我生成PDF" / "导出简历" | `generate_one_page_pdf` | `resume_content`, `result_json` (structured), `session_id` |
| "这个职位匹不匹配" / shares job description | `match_resume_to_job` | `resume_text`, `job_description`, `target_job_title` |
| "面试怎么准备" / "职业规划" / "薪资怎么谈" | `get_ai_mentor_advice` | `module`, `resume_content`, `job_target` |
| Needs to classify a job title for other tools | `classify_job_title` | `job_title` |
| User wants more features / hits quota limit | `link_wondercv_account` | `session_id` |
| After user clicks auth link, check binding result | `check_link_status` | `link_token` |
| User asks about pricing / plans | `get_resume_upgrade_options` | `session_id` |

## Core Workflow

### Flow 1: Resume Analysis (most common entry point)

```
User provides resume
       ↓
  analyze_resume(resume_text, target_job_title?)
       ↓
  Format results for user:
  - Overall score (X/100) with 4 dimension scores
  - Top issues ranked by severity (high → medium → low)
  - Section-by-section feedback
  - Sample rewrites (if available)
       ↓
  Ask user: "需要我帮你改写哪个部分？"
```

### Flow 2: Section Rewriting

```
User specifies which section to improve
       ↓
  Determine section_type:
  - 个人总结/自我评价 → "summary"
  - 工作经历 → "work_experience"
  - 项目经历 → "project"
  - 技能 → "skills"
  - 教育经历 → "education"
       ↓
  rewrite_resume_section(section_type, original_text, target_job_title?)
       ↓
  Present rewrite versions to user (1-3 versions based on tier)
  Include editing_notes as actionable tips
```

### Flow 3: Job Matching

```
User provides job description (JD)
       ↓
  match_resume_to_job(resume_text, job_description, target_job_title?)
       ↓
  Format results:
  - Match score (X/100)
  - Strengths (what matches well)
  - Gaps with severity levels
  - Missing keywords (suggest user add these)
  - Recommended changes with priority
```

### Flow 4: AI Mentor (8 modules)

```
Detect which module the user needs:
  - 整体评价 → "overall_assessment"
  - 修改建议 → "optimization_suggestions"
  - 职位匹配 → "job_matching"
  - 面试问题 → "interview_questions"
  - 求职规划 → "career_planning"
  - 薪资谈判 → "salary_negotiation"
  - 多版本简历 → "multi_version"
  - 人工导师 → "human_mentor"
       ↓
  get_ai_mentor_advice(module, resume_content, job_target?, job_description?)
       ↓
  Present advice with next_steps and related_modules
```

### Flow 5: PDF Generation

```
User wants PDF output
       ↓
  Parse resume into structured JSON (result_json) with fields:
  - profile: { name, phone, email, job_target }
  - education: [{ school, major, degree, start_date: "YYYY-MM", end_date: "YYYY-MM" }]
  - work_experience: [{ company, title, start_date, end_date, bullets: [] }]
  - project_experience: [{ name, role, start_date, end_date, bullets: [] }]
  - skills: { text } or [{ category, items }]
  IMPORTANT: dates must use start_date/end_date format (YYYY-MM), NOT "period" field
       ↓
  generate_one_page_pdf(resume_content, result_json, template?, session_id)
  template options: "modern" (default) | "classic" | "minimal" | "professional"
       ↓
  Return PDF URL to user
  Note: Guest users cannot generate PDF — suggest linking account first
```

## Quota & Tier System

| Tier | Analyses | Rewrites | PDF | AI Mentor | How to Get |
|------|----------|----------|-----|-----------|------------|
| Guest | 3 total | 2 total | ✗ | Simplified only | Default |
| Pioneer | 20/day | 10/day | 10/day | Full 8 modules | Link WonderCV account (first 100 users) |
| Paid | Unlimited | Unlimited | Unlimited | Full | Subscribe |

**When quota is exhausted:**
1. Inform the user their free quota has been used up
2. Explain Pioneer benefits briefly
3. Call `link_wondercv_account` to start the binding flow
4. After user completes auth, call `check_link_status` with the `link_token` to verify

## Output Formatting Rules

### After analyze_resume
- Display scores in a table format
- List issues with severity indicators (🔴 high / 🟡 medium / 🟢 low)
- Provide actionable next steps, not just problems
- If the result quality is low (e.g., too generic), supplement with your own analysis based on the resume content

### After rewrite_resume_section
- Show each version clearly labeled (Version 1, Version 2, etc.)
- Include the reasoning for changes
- If only 1 version returned (Guest tier), add your own optimization suggestions as supplement
- Present editing_notes as practical tips

### After match_resume_to_job
- Display match score prominently
- Format gaps as a table with severity
- List missing keywords that user should add
- Provide specific, actionable recommendations for closing each gap

### General Rules
- Always respond in the same language as the user (default: Chinese)
- After presenting results, proactively suggest the logical next step
- If a tool returns low-quality results (generic / placeholder-heavy), use your own expertise to provide better analysis and clearly note what came from the tool vs. your supplementary analysis
- Never expose raw JSON to the user — always format into readable markdown

## Error Handling

| Scenario | Action |
|----------|--------|
| Tool returns empty or error data | Inform user, provide your own best-effort analysis |
| Quota exceeded | Explain limit, suggest `link_wondercv_account` |
| Resume text too short (< 50 chars) | Ask user to provide more complete resume content |
| Backend unavailable (local fallback) | Results may be simplified — note this to user and supplement with your own analysis |
| PDF generation fails | Check if user is Guest (not allowed), otherwise suggest retry |

## Setup

```bash
npm install -g clawcv
```

Add to MCP config:
```json
{
  "clawcv": {
    "type": "stdio",
    "command": "clawcv"
  }
}
```

Environment variable:
```bash
export MCP_BACKEND_URL=https://api.wondercv.com
```
