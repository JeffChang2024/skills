---
name: online-course-video
version: 1.0.2
displayName: "Online Course Video Maker — Create Educational Course and Lesson Videos"
description: >
  Online Course Video Maker — Create Educational Course and Lesson Videos.
metadata: {"openclaw": {"emoji": "🎓", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
---

# Online Course Video Maker — Educational Course and Lesson Videos

The slide deck has forty-seven slides, the instructor has been talking for twenty-two minutes, and the viewer — who paid actual money for this course — is on their phone because somewhere between slide 11 and slide 14 the presentation crossed the invisible line between "educational content" and "someone reading their own slides aloud," which is the adult-education equivalent of being read a bedtime story except the story is about quarterly sales methodology and nobody falls asleep because they're already checking email. Online course content fails when it forgets that the medium is video, not PowerPoint with narration, and succeeds when it treats each lesson as a production that earns the viewer's attention through visual variety, pacing, real-world demonstrations, and the understanding that a human being watching a screen has approximately ninety seconds of goodwill before they need a reason to keep watching. This tool transforms course material into polished educational videos — instructor talking-head segments intercut with screen recordings and slide animations, concept-visualization sequences that turn abstract ideas into visual diagrams, chapter-structured lessons with progress indicators and timestamp navigation, practice-exercise prompts that pause the passive watching and activate the learning, quiz-checkpoint overlays that test comprehension before moving forward, and the professional production quality that makes a course filmed in a spare bedroom indistinguishable from one produced in a studio. Built for online educators building course libraries on Udemy, Teachable, and Skillshare, corporate trainers producing internal learning modules, subject-matter experts monetizing their knowledge through video courses, coaches and consultants creating scalable client education, university professors recording lecture supplements, and anyone whose expertise deserves a better delivery vehicle than a slide deck and a monotone.

## Example Prompts

### 1. Full Lesson — Structured Course Module
"Create a 10-minute course lesson on 'Introduction to Data Analysis with Python.' Opening hook (0-20 sec): a messy spreadsheet with 10,000 rows — 'This spreadsheet contains a year of sales data. Finding the patterns in it manually would take three days. Python will do it in six lines of code. By the end of this lesson, you'll write those six lines.' Lesson objectives (20-40 sec): three bullet points on screen with the instructor. 'By the end of this lesson you will: 1) Load a dataset using pandas, 2) Clean missing values, 3) Generate a summary report.' Progress bar showing this is Lesson 3 of 12, Module 1. Concept explanation (40-160 sec): what is pandas? Instructor talking head with a diagram appearing beside them — 'Pandas is a Python library that turns messy data into structured tables called DataFrames. Think of a DataFrame as a spreadsheet that can be manipulated with code instead of mouse clicks.' Animated diagram: raw CSV file → pandas read_csv → structured DataFrame with labeled columns and rows. 'The DataFrame is the foundation. Every analysis starts here.' Live coding demo (160-360 sec): screen recording — VS Code or Jupyter Notebook. 'Let me show you what this looks like in practice.' Type the code in real time (or near-real-time with speed adjustments). Step 1: import pandas, load the CSV. Show the output — the DataFrame appearing. 'Ten thousand rows loaded in 0.3 seconds. Try that with copy-paste.' Step 2: check for missing values — df.isnull().sum(). Show the output: 47 nulls in the revenue column. 'Forty-seven missing values. In a spreadsheet you'd scroll through 10,000 rows looking for blanks. In pandas, one line.' Step 3: fill or drop the nulls — df.fillna(0) vs df.dropna(). 'The choice depends on your analysis. Filling with zero assumes no revenue. Dropping assumes the row is useless. Know your data before deciding.' Step 4: generate summary — df.describe(). The output: mean, median, min, max, standard deviation. 'Six lines of code. The same analysis that would take a data analyst an hour in Excel, done in under a minute.' Practice prompt (360-400 sec): screen shows a prompt — 'Your turn. Pause this video. Open the practice notebook (linked below). Load the customer_data.csv file and find: 1) How many missing values are in the age column? 2) What's the average order value?' Timer overlay: 'Take 5 minutes. Come back when you're done.' Knowledge check (400-440 sec): quiz overlay — 'Quick check: What does df.isnull().sum() return?' Options: A) The total rows, B) The count of missing values per column, C) The sum of all values, D) The column names. 'If you said B, you're ready for the next lesson.' Recap and next lesson preview (440-480 sec): three objectives revisited — checkmarks appearing. 'You loaded a dataset, cleaned it, and summarized it. Lesson 4 covers filtering and grouping — where the real analysis begins.' End card with lesson navigation."

### 2. Concept Explainer — Visual Learning Segment
"Build a 5-minute concept explainer for 'How Machine Learning Models Learn' — visual-heavy, minimal code. Opening: a child learning to identify animals — photos of cats and dogs flashing on screen. 'A child sees hundreds of cats before they can reliably identify one. Machine learning works the same way — it learns by example, not by instruction.' The analogy (0-60 sec): animated sequence — a model as a black box. Data goes in one side (photos of cats), a label comes out the other (cat/not cat). 'The model starts by guessing randomly. The first time it sees a cat, it might say "dog." That's fine. That's learning.' Training loop visualization (60-180 sec): animated training loop — input image → model prediction → comparison with correct answer → error calculation → adjustment. Show this loop repeating: guess 1 (wrong, big error), guess 2 (wrong, smaller error), guess 10 (closer), guess 100 (correct). 'Each loop is called an epoch. Each epoch reduces the error. The model doesn't understand what a cat is — it understands what patterns in the pixels correlate with the label "cat."' Show the error graph decreasing over epochs — the learning curve. 'This graph is the model getting smarter. The steep drop is rapid learning. The plateau is diminishing returns. Knowing when to stop is part of the art.' Overfitting explained (180-260 sec): the model performing perfectly on training data but failing on new data. Animated: a student who memorized the answers to a specific test but can't answer new questions on the same topic. 'Overfitting is the model memorizing instead of learning. It knows the training data perfectly and the real world not at all.' Show the two curves: training accuracy going up, validation accuracy going up then down. 'When these curves diverge, the model is memorizing. The fix: more data, simpler model, or regularization techniques we'll cover in Lesson 7.' Real-world application (260-300 sec): the same concept applied to practical examples. Email spam filter: 'The model saw 100,000 emails labeled spam or not-spam. Now it predicts with 98% accuracy on emails it's never seen.' Netflix recommendations: 'The model saw your viewing history and found patterns that match other viewers. The recommendation isn't magic — it's pattern matching at scale.' Closing: 'Machine learning is pattern recognition automated. The machine doesn't think. It correlates. Understanding that distinction is the foundation of everything we'll build in this course.'"

### 3. Screen Recording Lesson — Software Tutorial
"Produce a 6-minute screen-recording lesson teaching 'Pivot Tables in Excel.' Opening: a spreadsheet with raw sales data — 2,000 rows. 'Two thousand rows of sales data. Your boss wants a summary by region, by product, by quarter. Without a pivot table, you're spending an afternoon with SUMIF formulas. With a pivot table: 90 seconds.' Step 1 — Creating the pivot table (0-80 sec): select the data range → Insert → Pivot Table. 'Select ALL the data including headers. The most common pivot table mistake is selecting a partial range.' The pivot table dialog — place in a new worksheet. 'New worksheet keeps your raw data separate from your analysis. Always.' The empty pivot table appears with the field list on the right. 'This blank canvas and this field list are your entire toolkit. Drag fields to create the analysis.' Step 2 — Building the first view (80-170 sec): drag 'Region' to Rows, 'Revenue' to Values. The pivot table populates — revenue by region. 'Thirty seconds. A summary that would take 15 minutes of SUMIF formulas.' Add 'Product' to Rows (nested under Region). Now: revenue by region AND product. 'The nesting creates the hierarchy. Each region expands to show its products.' Drag 'Quarter' to Columns. Now: revenue by region, by product, by quarter — a full cross-tabulation. 'This is the view your boss actually wants. Two minutes of dragging fields replaced an afternoon of formula writing.' Step 3 — Formatting and filtering (170-260 sec): change the value field to Average instead of Sum — click the dropdown, Value Field Settings, Average. 'Sum tells you total revenue. Average tells you deal size. Same data, different insight, one click.' Add a filter: drag 'Sales Rep' to the Filter area. Select a specific rep — the table updates instantly. 'Now every manager can filter to their team without touching the underlying data.' Number formatting: right-click → Number Format → Currency. 'Make it readable. Numbers without formatting are data. Numbers with formatting are information.' Step 4 — Pivot chart (260-320 sec): click inside the pivot table → Insert → Pivot Chart. Bar chart appears showing the same data visually. 'The chart is linked to the pivot table. Filter the table, the chart updates. Change rows, the chart changes. They're connected.' Customize: add data labels, change colors by region. 'This chart goes directly into the presentation. No copying data to a separate chart — it's already done.' Common mistakes (320-360 sec): rapid-fire — 'Mistake 1: not refreshing after data changes. Right-click → Refresh. Mistake 2: editing the pivot table cells directly — you can't. Change the source data. Mistake 3: forgetting to include new rows in the source range. Fix: use a Table (Ctrl+T) as the source — it auto-expands.' Closing: the finished pivot table and chart. '90 seconds to create. Two minutes to customize. Infinite time saved every time the boss asks for "a different view" and you just drag a field.'"

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|:--------:|-------------|
| `prompt` | string | ✅ | Describe the lesson topic, learning objectives, and teaching approach |
| `duration` | string | | Target video length (e.g. "5 min", "6 min", "10 min") |
| `style` | string | | Video style: "full-lesson", "concept-explainer", "screen-recording", "talking-head", "workshop" |
| `music` | string | | Background audio: "focus-ambient", "none" |
| `format` | string | | Output ratio: "16:9", "9:16", "1:1" |
| `chapter_markers` | boolean | | Add chapter timestamps and progress indicators (default: true) |
| `quiz_overlay` | boolean | | Include knowledge-check quiz prompts between sections (default: false) |

## Workflow

1. **Describe** — Outline the lesson topic, objectives, and instructional approach
2. **Upload** — Add talking-head footage, screen recordings, slides, and diagrams
3. **Generate** — AI produces the lesson with chapter markers, visual intercuts, and pacing
4. **Review** — Verify content accuracy, code examples, and learning objectives
5. **Export** — Download in your chosen format and resolution

## API Example

```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "online-course-video",
    "prompt": "Create a 10-minute Python data analysis lesson: messy spreadsheet hook, 3 learning objectives with progress bar, pandas DataFrame concept diagram, live coding demo loading CSV cleaning nulls and generating summary, practice prompt with 5-minute pause, quiz checkpoint, recap with next-lesson preview",
    "duration": "10 min",
    "style": "full-lesson",
    "chapter_markers": true,
    "quiz_overlay": true,
    "music": "focus-ambient",
    "format": "16:9"
  }'
```

## Tips for Best Results

1. **Open with the outcome, not the theory** — "Six lines of code replace three days of work" hooks better than "Today we'll learn about pandas." The AI places outcome hooks before concept explanations.
2. **Intercut talking head with screen recordings** — Face for concepts, screen for demonstrations. The AI alternates between instructor and screen based on content type.
3. **Add practice prompts that pause the lesson** — "Your turn. Pause and try." converts passive watching to active learning. The AI inserts pause prompts when quiz_overlay is enabled.
4. **Use animated diagrams for abstract concepts** — Training loops, data flows, and system architectures need visuals. The AI generates concept animations from your descriptions.
5. **Include chapter markers for navigation** — Students rewatch specific sections, not entire lessons. The AI adds timestamp chapters when chapter_markers is enabled.

## Output Formats

| Format | Resolution | Use Case |
|--------|-----------|----------|
| MP4 16:9 | 1080p / 4K | Udemy / Teachable / YouTube course |
| MP4 9:16 | 1080p | TikTok / Instagram Reels lesson clip |
| MP4 1:1 | 1080p | Instagram post / LinkedIn learning |
| GIF | 720p | Concept animation loop / code demo |

## Related Skills

- [training-video-maker](/skills/training-video-maker) — Corporate training and onboarding videos
- [how-to-video-maker](/skills/how-to-video-maker) — How-to tutorial and step-by-step videos
- [webinar-recording-maker](/skills/webinar-recording-maker) — Webinar recording and presentation videos
