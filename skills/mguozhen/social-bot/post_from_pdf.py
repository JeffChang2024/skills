#!/usr/bin/env python3
"""
直接按 PDF 里的 URL + 回复文案逐一发帖，不走关键词过滤。
"""
import sys, time, re, logging
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")
sys.path.insert(0, str(Path(__file__).parent))

from bot import browser as B
from bot.db import init_db, log_reply, already_replied

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("pdf_poster")

# ── 从 PDF 提取的帖子列表 ────────────────────────────────────────────
POSTS = [
    # ── Reddit ──────────────────────────────────────────────────────
    {
        "platform": "reddit",
        "url": "https://old.reddit.com/r/SaaS/comments/1rvswsh/at_what_stage_should_a_startup_actually_add_ai/",
        "title": "At what stage should a startup actually add AI customer support?",
        "product": "Solvea",
        "reply": (
            "Love this take! So many founders wait too long and just drown in the inbox. "
            "Connecting to Shopify/Stripe is definitely the game-changer here.\n\n"
            "If you're ever looking to upgrade from a basic knowledge-base bot to something more 'agentic', "
            "check out Solvea (solvea.cx). It doesn't just read your docs — it actually takes actions on Shopify "
            "(processing returns, updating shipping addresses) so you don't even have to touch those 20-30% edge cases."
        ),
    },
    {
        "platform": "reddit",
        "url": "https://old.reddit.com/r/SaaS/comments/1rwu5eg/i_built_an_ai_customer_support_agent_for_shopify/",
        "title": "I built an AI customer support agent for Shopify stores as a solo dev",
        "product": "Solvea",
        "reply": (
            "Spot on! The LLM part is easy; the orchestration, edge cases, and actual reliability are the real nightmare.\n\n"
            "We went through this exact same learning curve when building Solvea (solvea.cx). "
            "We ended up focusing entirely on making it a true autonomous agent for Shopify that handles all those "
            "messy edge cases (refunds, angry customers, complex order tracking) reliably out of the box. "
            "Gorgias is definitely too bloated for most!"
        ),
    },
    {
        "platform": "reddit",
        "url": "https://old.reddit.com/r/SaaS/comments/1rwnow1/saas_idea_an_ai_sales_agent_for_shopify_that_only/",
        "title": "SaaS idea: An AI Sales Agent for Shopify that only charges per successful sale",
        "product": "Solvea",
        "reply": (
            "The performance-based pricing is an interesting hook! The core idea — that AI should be actively "
            "closing sales and not just acting as a glorified FAQ bot — is exactly where the market is heading.\n\n"
            "We built Solvea (solvea.cx) with this exact philosophy: it's an AI agent that handles support but "
            "also actively guides purchasing decisions. Store owners definitely want ROI, not just another subscription."
        ),
    },
    {
        "platform": "reddit",
        "url": "https://old.reddit.com/r/FulfillmentByAmazon/comments/1rsfdwq/are_you_worried_ai_shopping_agents_are_now/",
        "title": "Are you worried AI shopping agents are now deciding what gets bought on Amazon?",
        "product": "VOC.ai",
        "reply": (
            "This is a huge shift. AI agents don't just read your keywords — they synthesize your actual customer "
            "reviews to decide if your product is worth recommending. If your reviews mention specific flaws, the AI knows.\n\n"
            "That's why tools like VOC.ai are becoming essential right now. It uses AI to deeply analyze your "
            "(and your competitors') reviews to extract the exact sentiment and pain points. "
            "If you optimize your product and listing based on what customers actually care about, "
            "the AI agents will naturally favor you."
        ),
    },
    {
        "platform": "reddit",
        "url": "https://old.reddit.com/r/smallbusiness/comments/1rvc62f/heads_up_ai_assistants_are_now_recommending_your/",
        "title": "Heads up: AI assistants are now recommending your competitors to your potential customers",
        "product": "Solvea",
        "reply": (
            "This is the new reality of 'Agentic SEO.' If your business isn't easily understandable by an AI, "
            "you don't exist.\n\n"
            "Beyond making sure your site is crawlable, having your own AI agent on your site dramatically "
            "improves how customers interact with your brand. We built Solvea (solvea.cx) to be that front-line "
            "agent for ecommerce — it understands your entire business context and makes sure customers get the "
            "exact right answers, rather than bouncing to Google or Perplexity to find a competitor."
        ),
    },
    {
        "platform": "reddit",
        "url": "https://old.reddit.com/r/FulfillmentByAmazon/comments/1rssrcu/software_stacks_for_678figure_sellers/",
        "title": "Software Stacks for 6/7/8-Figure Sellers",
        "product": "VOC.ai",
        "reply": (
            "Solid stack! One area that seems to be missing is deep Review Analysis / Voice of Customer.\n\n"
            "For 7/8-figure brands, manually reading reviews to find product iteration opportunities is impossible. "
            "A lot of top sellers are using VOC.ai right now — it uses AI to instantly break down thousands of reviews "
            "into actionable insights (pain points, feature requests, sentiment trends). "
            "Definitely worth adding to the stack for product development and listing optimization!"
        ),
    },
    {
        "platform": "reddit",
        "url": "https://old.reddit.com/r/Figsscrubs/comments/1rssb19/does_this_company_still_have_cs_representatives/",
        "title": "Does this company still have CS representatives?",
        "product": "Solvea",
        "reply": (
            "This is exactly what happens when brands just slap a cheap AI chatbot on their site to cut costs "
            "without actually integrating it properly. It destroys the premium brand experience.\n\n"
            "A real AI agent shouldn't just be a wall to block you from humans. Platforms like Solvea (solvea.cx) "
            "are built to actually resolve the issue (pulling real-time tracking, processing a return autonomously) "
            "and seamlessly hand off to a human with full context when it can't. "
            "It's wild that billion-dollar brands are still using broken bots."
        ),
    },
    # ── X / Twitter ─────────────────────────────────────────────────
    {
        "platform": "x",
        "url": "https://x.com/HamptonAc_/status/2032086324770193614",
        "title": "The Laziest 2026 Shopify Blueprint",
        "product": "Solvea",
        "reply": (
            "100% this. The leverage you get from AI agents in 2026 is insane. "
            "When it comes to the customer support piece of this blueprint, Solvea (solvea.cx) is the cheat code. "
            "It's an autonomous agent that plugs right into Shopify and handles the entire support inbox "
            "(tracking, returns, product questions) so you can actually focus on scaling ads and finding winners "
            "instead of answering emails."
        ),
    },
    {
        "platform": "x",
        "url": "https://x.com/jasonlk/status/2032991149322072517",
        "title": "20+ AI Agents in production — unification not orchestration (Jason Lemkin)",
        "product": "Solvea",
        "reply": (
            "Spot on, Jason. We saw this exact friction in the ecommerce support space. "
            "Having multiple agents handling different parts of the customer journey creates a fragmented mess.\n\n"
            "That's why with Solvea (solvea.cx), we built the agent to not only act autonomously on Shopify tickets, "
            "but to have a unified inbox where the human can seamlessly step in, review the agent's context, "
            "and take over without the customer ever feeling the handoff. Unification is the only way to scale this."
        ),
    },
]


# ── Reddit 发评论 ────────────────────────────────────────────────────
def post_reddit_comment(reply_text: str) -> bool:
    tree = B.snapshot()
    textarea_refs = re.findall(r'\[(\d+-\d+)\] textbox(?!: search)', tree)
    if not textarea_refs:
        logger.warning("Reddit: no comment textarea found")
        return False

    B.click(textarea_refs[-1])
    B.wait_seconds(1)

    for i, para in enumerate(reply_text.split("\n\n")):
        safe = para.replace("$", "").strip()
        if safe:
            B.type_text(safe)
        if i < len(reply_text.split("\n\n")) - 1:
            B.press("Enter")
            B.press("Enter")

    B.wait_seconds(1)
    tree = B.snapshot()
    save_refs = re.findall(r'\[(\d+-\d+)\] button: save', tree, re.I)
    if not save_refs:
        return False

    B.click(save_refs[0])
    B.wait_seconds(4)
    confirm = B.snapshot()
    return "mguozhen" in confirm and ("just now" in confirm or "1 minute ago" in confirm)


# ── X 发回复 ─────────────────────────────────────────────────────────
def post_x_reply(reply_text: str) -> bool:
    tree = B.snapshot()
    boxes = re.findall(r'\[(\d+-\d+)\] textbox: Post text', tree)
    if not boxes:
        logger.warning("X: no reply textbox found")
        return False

    B.click(boxes[0])
    B.wait_seconds(1)

    for i, para in enumerate(reply_text.split("\n\n")):
        safe = para.replace("$", "").strip()
        if safe:
            B.type_text(safe)
        if i < len(reply_text.split("\n\n")) - 1:
            B.press("Enter")
            B.press("Enter")

    B.wait_seconds(1)
    tree = B.snapshot()
    reply_btns = re.findall(r'\[(\d+-\d+)\] button: Reply', tree)
    if len(reply_btns) >= 2:
        B.click(reply_btns[-1])
        B.wait_seconds(3)
        confirm = B.snapshot()
        return "Your post was sent" in confirm or "post was sent" in confirm.lower()
    return False


# ── 主流程 ────────────────────────────────────────────────────────────
def main():
    init_db()
    results = {"posted": 0, "skipped": 0, "failed": 0}

    for i, post in enumerate(POSTS):
        platform = post["platform"]
        url      = post["url"]
        title    = post["title"]
        reply    = post["reply"]
        product  = post["product"]

        logger.info(f"[{i+1}/{len(POSTS)}] {platform.upper()} — {title[:55]}")

        if already_replied(url):
            logger.info("  → already replied, skip")
            results["skipped"] += 1
            continue

        B.open_url(url)
        B.wait_seconds(4)

        if platform == "reddit":
            success = post_reddit_comment(reply)
        else:
            success = post_x_reply(reply)

        if success:
            log_reply(platform, url, title, "", reply, product, "posted")
            results["posted"] += 1
            logger.info(f"  ✓ posted ({product})")
            time.sleep(8)
        else:
            log_reply(platform, url, title, "", reply, product, "failed")
            results["failed"] += 1
            logger.warning(f"  ✗ failed")
            time.sleep(5)

    logger.info(f"\n=== 完成 === posted={results['posted']} failed={results['failed']} skipped={results['skipped']}")
    return results


if __name__ == "__main__":
    main()
