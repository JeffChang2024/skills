# Tool Orchestration Patterns & Tool Matrix

## Tool Landscape

| Layer | Tool | Role | Trigger |
|-------|------|------|---------|
| 🧠 Cognitive | Deep Thinking skill | Strategic advisor — complex reasoning, multi-angle analysis, challenge assumptions | Problem needs deep decomposition, hidden assumptions, multiple perspectives |
| 🧠 Cognitive | Scratchpad/thinking | Internal draft — mid-process reflection, divergent association, temp memory | Multi-step tasks, need to maintain thread |
| 🔍 Info | Info Gathering skill | Intelligence officer — parallel multi-source search, denoise, cross-validate | Facts, data, time-sensitive info, external verification needed |
| 🔍 Info | Document parsing | Translator — PDF/Word/Excel/PPT/TXT/video to processable text | User uploads file |
| 🔍 Info | Feishu doc read | Enterprise knowledge read interface | User provides Feishu doc link |
| 🔍 Info | Feishu doc write | Enterprise knowledge write interface | Need to export content to Feishu |
| 🎨 Creative | Image generation | Visual factory — text/image to images | Image generation needs |
| 🎨 Creative | Video generation | Video factory — image/video/text to video | Video generation needs |
| 🎨 Creative | EChart charts | Data visualization — 20+ chart types | Data needs chart presentation |
| 🔧 Utility | Math execution | Precise calculator (mental math forbidden) | Any numerical calculation |
| 📋 Management | Memory system | Long-term memory — cross-conversation experience | Project tracking, user preferences, experience reuse |
| 📋 Management | Task board | Project management — dynamic dependency network | Complex multi-step tasks |

## Five Orchestration Patterns

### Pattern A: Analyst (Search → Think → Output)
**For**: Research, analysis, fact-checking
```
Search: Divergent raw data collection
  → Clean: Denoise, verify sources (converge)
  → Think: Synthesize reasoning, build arguments
  → Output: Structured response
```

### Pattern B: Explorer (Think → Search → Re-think)
**For**: Open-ended problems, strategy formulation
```
Think: Define hypotheses and search parameters
  → Search: Validate/refute hypotheses
  → Think: Adjust strategy based on evidence
```

### Pattern C: Parallel Fan-out (Independent subtasks simultaneously)
**For**: Multi-dimensional information needs
```
┌→ Info Gathering A (dimension 1)
├→ Info Gathering B (dimension 2)  ──all complete──→ Deep Thinking (synthesize)
└→ Document Parsing (user file)
```

### Pattern D: Creative Pipeline (Search → Strategy → Create → Visualize)
**For**: Content production, marketing materials
```
Search: Inspiration materials and industry benchmarks
  → Think: Core concept and differentiation strategy
  → Create: Generate copy/text
  → Visualize: Generate supporting visual assets
```

### Pattern E: Iterative Refinement (Generate → Review → Fix loop)
**For**: High-quality requirement tasks
```
First draft → Quality gate check → Fail → Supplementary search/re-reason → Regenerate → Pass → Output
```
