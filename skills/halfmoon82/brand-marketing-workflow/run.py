#!/usr/bin/env python3
"""Brand Marketing Workflow — unified entry point.

Usage:
  echo '<json>' | python3 run.py
  python3 run.py --input path/to/brand.json
  python3 run.py --demo fashion|tech|local

Output:
  Full workflow result as JSON to stdout.
  Human-assist requests (login_gate, captcha_gate) printed to stderr as alerts.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).parent / "scripts"

DEMO_INPUTS = {
    "fashion": {
        "brand_name": "Aurora Lane",
        "brand_positioning": "minimal premium everyday wear",
        "brand_tone": "calm sharp poetic",
        "target_audience": ["urban professionals", "ages 25-40"],
        "use_cases": ["daily wear", "commute", "light social scenes"],
        "channels": ["xiaohongshu", "weibo", "douyin"],
        "content_goals": ["brand awareness", "community building", "content production"],
        "brand_dos": ["poetic short copy", "clean visual language"],
        "brand_donts": ["aggressive promotions"],
        "competitor_scope": ["UNIQLOZH public signals", "MINIMALAB public signals"],
        "kpis": ["reach", "saves", "engagement_rate", "conversion"],
        "constraints": {"budget": "medium", "region": "CN", "compliance": "public+authorized-only"},
        "execution_action": "draft_prepare",
        "browser_action": "collect_public_signals",
        "data_access": "public",
        "need_login": False,
    },
    "tech": {
        "brand_name": "ByteNest",
        "brand_positioning": "AI workflow tooling for small teams",
        "brand_tone": "direct technical practical",
        "target_audience": ["operators", "founders", "PMs"],
        "channels": ["wechat", "x", "linkedin"],
        "content_goals": ["thought leadership", "product awareness", "inbound leads"],
        "brand_dos": ["technical clarity", "use cases with data"],
        "brand_donts": ["hype language"],
        "competitor_scope": ["Notion public signals", "Linear public signals"],
        "kpis": ["impressions", "click_through", "signups"],
        "constraints": {"budget": "low", "region": "global", "compliance": "public+authorized-only"},
        "execution_action": "content_generate",
        "browser_action": "read_public_content",
        "data_access": "public",
        "need_login": False,
    },
    "local": {
        "brand_name": "River Tea",
        "brand_positioning": "local tea brand with modern lifestyle appeal",
        "brand_tone": "warm grounded friendly",
        "target_audience": ["nearby residents", "young shoppers 20-35"],
        "channels": ["xiaohongshu", "wechat", "local_community"],
        "content_goals": ["foot traffic", "social sharing", "brand affinity"],
        "brand_dos": ["authentic local story", "seasonal content"],
        "brand_donts": ["cold corporate tone"],
        "competitor_scope": ["local cafe public signals", "HeyTea public signals"],
        "kpis": ["store_visits", "shares", "follower_growth"],
        "constraints": {"budget": "low", "region": "CN-local", "compliance": "public+authorized-only"},
        "execution_action": "draft_prepare",
        "browser_action": "collect_public_signals",
        "data_access": "public",
        "need_login": False,
    },
}


def call(script: str, payload: dict) -> dict:
    proc = subprocess.run(
        ["python3", str(BASE / script)],
        input=json.dumps(payload).encode(),
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"{script} failed: {proc.stderr.decode()}")
    return json.loads(proc.stdout.decode())


def run_workflow(payload: dict) -> dict:
    # Step 1: normalize
    normalized = call("normalize_brand_input.py", payload)

    # Step 2: full orchestration (brief + strategy + parallel tasks + auth + browser)
    orchestrated = call("workflow_orchestrator.py", payload)

    # Step 3: content producer (real LLM generation)
    content = call("content_producer.py", {
        "brand_brief": orchestrated.get("brand_brief"),
        "content_strategy": orchestrated.get("content_strategy"),
        "competitor_insights": [],  # 将在 Step 4 填入，Step 3 先用空列表（保持顺序）
        "channels": payload.get("channels", []),
        "generate_count": 2,
    })

    # Step 4: competitor intelligence (fetch → analyze → cluster)
    raw_competitor_data = call("competitor_fetcher.py", {
        "competitor_scope": payload.get("competitor_scope") or [],
        "brand_name": payload.get("brand_name", ""),
    })
    analyzed_signals = call("competitor_ai_analyzer.py", {
        "raw_data": raw_competitor_data,
        "brand_brief": orchestrated.get("brand_brief"),
    }) if raw_competitor_data else []
    clusters = call("competitor_cluster.py", analyzed_signals) if analyzed_signals else {}

    # Step 5: score content
    score = call("score_content_effect.py", {"notes": f"initial run for {payload.get('brand_name','')}"})

    # Step 6: auth check
    auth = call("authorization_manager.py", {
        "action": payload.get("execution_action", "draft_prepare"),
        "data_access": payload.get("data_access", "public"),
        "requires_payment": payload.get("requires_payment", False),
        "human_response": payload.get("human_response", ""),
        "state": payload.get("state", "running"),
    })

    # Step 7: browser compliance check
    browser = call("browser_execution.py", {
        "action": payload.get("browser_action", "collect_public_signals"),
        "data_access": payload.get("data_access", "public"),
        "need_login": payload.get("need_login", False),
        "platform": (payload.get("channels") or ["unknown"])[0],
    })

    # Human-assist alert (login/captcha gate)
    if auth.get("human_assist"):
        print("\n[HUMAN ASSIST REQUIRED]", file=sys.stderr)
        print(auth["human_assist"]["message"], file=sys.stderr)
        print(f"Resume condition: {auth['human_assist']['resume_condition']}\n", file=sys.stderr)

    return {
        "brand_name": payload.get("brand_name"),
        "normalized_input": normalized,
        "brand_brief": orchestrated.get("brand_brief"),
        "content_strategy": orchestrated.get("content_strategy"),
        "content_assets": content,
        "competitor_clusters": clusters,
        "performance_score": score,
        "authorization": auth,
        "browser": browser,
        "iteration_plan": orchestrated.get("iteration_plan"),
        "status": orchestrated.get("status"),
        "low_confidence": orchestrated.get("low_confidence"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Brand Marketing Workflow")
    parser.add_argument("--input", help="Path to brand input JSON file")
    parser.add_argument("--demo", choices=["fashion", "tech", "local"], help="Run with demo input")
    args = parser.parse_args()

    if args.demo:
        payload = DEMO_INPUTS[args.demo]
    elif args.input:
        payload = json.loads(Path(args.input).read_text())
    else:
        raw = sys.stdin.read().strip()
        payload = json.loads(raw) if raw else DEMO_INPUTS["fashion"]

    result = run_workflow(payload)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
