# Facebook Ads (Meta Ads) — Skill Manual
## Built from Social Media Agent Master Playbook (March 2026)

> Full Facebook/Meta Ads playbook for 2026. Facebook ads are AI-led. Your job: provide the best inputs (creative, data, signals) and let the machine optimize. The advertiser controls the levers; Meta's AI controls the distribution.

---

## The Three Pillars of Success

1. **Clean Data**: Accurate conversion tracking, first-party data, proper event setup
2. **Stand-Out Creative**: Authentic, varied, human-feeling content
3. **Responsible AI Usage**: Let Advantage+ work, but with proper guardrails

All three must be in place. Weak data starves the AI. Bad creative wastes spend. Ignoring AI wastes optimization potential.

---

## Campaign Architecture (TOF/MOF/BOF Funnel)

### Top of Funnel — Awareness
- **Objective**: Video views, reach campaigns
- **Targeting**: Broad (let Meta's AI find the right people)
- **Goal**: Introduce brand to new audiences
- **Content**: Entertaining or educational, zero sales pitch
- **Budget**: Lower investment, volume play

### Middle of Funnel — Consideration
- **Objective**: Engagement, traffic campaigns
- **Targeting**: Retarget video viewers (25%, 50%, 75% watch time)
- **Goal**: Build interest, deepen relationship
- **Content**: How-to, behind-the-scenes, social proof
- **Budget**: Medium investment

### Bottom of Funnel — Conversion
- **Objective**: Conversion, lead gen campaigns
- **Targeting**: Retarget website visitors, email list lookalikes
- **Goal**: Convert interested prospects
- **Content**: Testimonials, case studies, specific offers, free trials
- **Budget**: Highest investment, optimize for CPA/ROAS

### Retention
- **Objective**: Dynamic remarketing
- **Targeting**: Past customers
- **Goal**: Repeat purchase
- **Content**: New products, exclusive offers, loyalty rewards

---

## Campaign Setup Checklist

Before launching ANY campaign:

1. **Define ONE clear objective per campaign**: "Generate 50 leads at $35 CPA" — not vague goals
2. **Install Pixel + Conversions API (CAPI)**: Server-side tracking is mandatory in 2026 as cookies fade
3. **Set up proper conversion events**: Track all valuable actions with accurate values
4. **Separate brand vs non-brand campaigns**: Prevent brand terms from cannibalizing acquisition budgets
5. **Build audience segments**: First-party data (email lists, website visitors, purchasers)

### Pixel + CAPI Setup Requirement
- Browser-side Pixel alone is insufficient in 2026
- CAPI provides server-to-server data directly to Meta
- Combined, they improve attribution accuracy significantly
- Required for proper learning phase completion

---

## Advantage+ and Automation

Meta's AI automation (Advantage+) performs well when given clean inputs:

- **Advantage+ Shopping Campaigns**: For e-commerce — Meta finds buyers automatically
- **Advantage+ Audience**: For prospecting — provide seed audience, let AI expand
- **Rules for Advantage+**:
  - Let the AI optimize — don't micromanage targeting
  - Start broad, then narrow based on performance data
  - Provide diverse creative assets — the AI needs options to test
  - Monitor closely for brand safety and irrelevant placements
  - Don't set overly restrictive audience constraints

---

## Creative Best Practices

### The Authenticity Imperative
The single most important creative trend for 2026: **authenticity over production value**. Real imagery and authentic copy outperform AI-generated or overly polished content.

### Creative Best Practices
- **UGC-style content**: Real people, real stories, real results — always outperforms polished studio ads
- **Video dominates**: Reels ads show between organic Reels. Short, engaging, native-feeling.
- **3-5 creative variations minimum per ad set**: Let the algorithm find winners
- **Refresh creative every 2-3 weeks**: Prevents ad fatigue
- **Always A/B test**: Headlines, images, video hooks, CTAs

### Image Specifications
| Format | Dimensions |
|--------|-----------|
| Square | 1440x1440px |
| Vertical (4:5) | 1440x1800px |
| Stories/Reels (9:16) | 1440x2560px |

### Video Guidelines
- Keep under 15 seconds for best performance (longer works for some objectives)
- Native vertical (9:16) for Stories and Reels placements
- Hook in first 3 seconds — most people won't watch beyond that
- Captions always — most people watch on mute
- Keep text on images minimal (less = better CTR still holds true)

---

## Ad Copy Framework

Every ad should follow this structure:

1. **Hook (first line)**: Specific, relatable problem or bold claim
2. **Agitate**: Expand on the pain point — make it feel real
3. **Solution**: Introduce product/service as the answer
4. **Proof**: Social proof, results, testimonials, numbers
5. **CTA**: Clear, single action — "Get a free quote", "Download now", "Book a call"

### Facebook Ad Copy Rules
- Primary text under 125 characters for mobile visibility (longer is cut off)
- Use emoji sparingly — 1-2 max
- Be specific ("Save 30%" beats "Save Money")
- First line is all most people will read — make it do the work
- No corporate speak — sound like a person

---

## Lead Ads vs Website Conversion Campaigns

| Type | Volume | Quality | Use When |
|------|--------|---------|----------|
| Lead Ads | Higher | Lower | Broad lead gen, lower-ticket offers, testing |
| Website Conversions | Lower | Higher | High-ticket, long sales cycles, quality > quantity |

Use both strategically — they solve different problems.

---

## Budget and Bidding Progression

### Budget Guidelines
- **Conversion campaigns**: $20-30/day minimum per ad set (need ~50 conversions in 7 days to exit learning phase)
- **Brand awareness**: $10-15/day minimum
- **Testing budget**: Allocate 20% of total budget for testing new creative/audiences

### Bidding Strategy Progression
1. **Start**: Maximize Conversions — let Meta's AI learn your audience
2. **After 50+ conversions**: Transition to Target CPA (set slightly above current performance)
3. **For e-commerce**: Move to Target ROAS (start slightly below actual performance)
4. **Never set targets too aggressively early**: Starves the algorithm of data

---

## Optimization Rules

- **Don't touch a campaign for the first 3-5 days**: Learning phase — changes reset it
- **If 3-5x target CPA with zero conversions**: Pause and audit fundamentals (tracking, offer, landing page)
- **If CPA is 20-30% above target**: Give it time, make incremental adjustments
- **Review weekly**: Shift budget toward top performers
- **Kill underperformers after statistically significant data**: Not after 24 hours
- **Frequency over 3**: Ad fatigue territory. Refresh creative or expand audience.

---

## The Learning Phase

Meta's algorithm needs ~50 conversion events in 7 days to exit learning phase and optimize properly.

- During learning, performance will be inconsistent — this is normal
- Don't make significant changes during learning — it restarts the phase
- If stuck in learning: increase budget, broaden audience, or consolidate ad sets
- Exiting learning phase = algorithm has enough data to predict performance

---

## Key Metrics

| Metric | Description | Target |
|--------|-------------|--------|
| CPA | Cost Per Acquisition | Set by campaign objective |
| ROAS | Return on Ad Spend | 3x+ target typically |
| CTR | Click-Through Rate | 1-3% for cold traffic |
| Conversion Rate | Clicks to conversions | Depends on offer |
| Frequency | Average times someone sees your ad | Under 3 = fresh |
| Relevance Score | How well creative matches audience | 6+ |

---

## Red Flags

- **High clicks, low conversions**: Landing page problem or audience mismatch
- **High frequency (3+)**: Creative fatigue — refresh immediately
- **Rising CPA over time**: Audience saturation or creative fatigue
- **Learning phase won't complete**: Budget too low or not enough conversions
- **Policy violations**: Review all creative before scaling

---

## Getting Started (Limited Budget)

If you're just getting started with Meta Ads or have a limited budget:

1. **Install Pixel + CAPI NOW, before spending anything.** Data accumulates from organic traffic and builds your audience pools before the first dollar is spent. The more historical data Meta has, the better campaigns perform at launch.
2. **First paid spend: Retargeting** ($10-20/day). Run a small retargeting campaign to people who have already visited your website or engaged with your page. These are warm audiences and convert at dramatically lower CPAs than cold traffic.
3. **TOF awareness via organic, MOF/BOF via paid** — Use organic content for top-of-funnel brand awareness and paid ads to retarget the warm traffic you generate organically. This is the most cost-efficient path.
4. **Start with one objective** — Pick the single conversion action that matters most (lead form submit, purchase, booking). Focus everything there before adding complexity.

### Pixel Installation (Do This First)
```html
<!-- Add to <head> of every page on your website -->
<!-- Replace YOUR_PIXEL_ID with your actual Pixel ID from Meta Business Suite -->
<script>
!function(f,b,e,v,n,t,s)
{if(f.fbq)return;n=f.fbq=function(){n.callMethod?
n.callMethod.apply(n,arguments):n.queue.push(arguments)};
if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';
n.queue=[];t=b.createElement(e);t.async=!0;
t.src=v;s=b.getElementsByTagName(e)[0];
s.parentNode.insertBefore(t,s)}(window, document,'script',
'https://connect.facebook.net/en_US/fbevents.js');
fbq('init', 'YOUR_PIXEL_ID');
fbq('track', 'PageView');
</script>
```

### CAPI Implementation
Server-side Conversions API setup requires sending conversion events directly from your server to Meta. Use Meta's official Conversions API Gateway or implement directly via the Meta Business SDK for your backend language. Combined Pixel + CAPI improves attribution accuracy and is required for proper learning phase completion in 2026.

---

## Commands / Triggers
- **"Create a Facebook ad for [product/service]"** → Generate full ad copy using Hook-Agitate-Solution-Proof-CTA framework
- **"Write Facebook ad creative brief"** → Creative direction for image/video asset
- **"Review my ad performance"** → Audit key metrics and flag issues
- **"What's causing my high CPA?"** → Diagnostic checklist: tracking, creative, audience, landing page
- **"Generate 5 ad hook variations"** → Create A/B test hooks for a given offer
- **"Build a retargeting campaign plan"** → Outline full MOF/BOF retargeting funnel
- **"Check if my pixel is firing correctly"** → Guide through Meta Pixel Helper verification steps
- **"Plan a Facebook ads funnel"** → Generate full TOF/MOF/BOF campaign structure
