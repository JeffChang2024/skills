import argparse
import subprocess
import json
import sys
import os
import datetime

def run_command(cmd, env=None):
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, env=env)
    if result.returncode != 0:
        print(f"Error executing command: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    return result.stdout

def main():
    parser = argparse.ArgumentParser(description="Run Meta Ads Audit Pipeline")
    parser.add_argument("--config", required=True, help="Path to config.json")
    args = parser.parse_args()

    # Load config to get account_id and days
    try:
        with open(args.config, 'r') as f:
            config = json.load(f)
    except Exception as e:
        print(f"Failed to load config: {e}", file=sys.stderr)
        sys.exit(1)

    account_id = config.get("meta", {}).get("account_id")
    days = config.get("meta", {}).get("evaluation_days", 7)
    
    if account_id == "YOUR_ACCOUNT_ID_OR_LEAVE_BLANK_TO_AUTO_RESOLVE" or account_id == "":
        account_id = None

    run_date = datetime.datetime.now().strftime("%Y-%m-%d")
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    report_path = os.path.join(output_dir, f"audit-{run_date}.json")

    # Step 1: Run Audit
    print("=== Stage 1: Running Audit ===")
    audit_cmd = [
        sys.executable, "scripts/audit.py",
        "--days", str(days)
    ]
    if account_id:
        audit_cmd.extend(["--account_id", account_id])
    # Security: Pass only the explicitly required variables to the child process.
    safe_env = {
        "PATH": os.environ.get("PATH", ""),
        "EONIK_API_KEY": os.environ.get("EONIK_API_KEY", "")
    }
    # Keep current environment minimal so only EONIK_API_KEY passes through
    audit_out = run_command(audit_cmd, env=safe_env)    
    with open(report_path, "w") as f:
        f.write(audit_out)
    
    print(f"Audit complete. Report saved to {report_path}")

    print("\n\n=== Eonik AI Audit Report ===")
    try:
        data = json.loads(audit_out)
        if data.get("status") != "success":
            print(f"Audit Status: {data.get('status', 'failed')}")
        print("\n💰 Overall Impact 💰")
        print(f"Flags Found: {data.get('flagged_ads_count', 0)}")
        spent = data.get('total_leaked_spend', 0.0)
        print(f"Wasted Spend Detected: ${spent:.2f}")
        
        pauses = data.get("pause_recommendations", [])
        if pauses:
            print("\n🚨 Urgent Leaks 🚨")
            for ad in pauses:
                reason = ad.get("recommendation", {}).get("reason", ad.get("category", "Burn"))
                print(f"• Ad [{ad.get('ad_id')} - {ad.get('ad_name', 'Unknown')}]: {reason}")
                signals = ad.get("signals", [])
                for sig in signals:
                    print(f"  └ {sig.get('detail')}")
        
        print("\n\n✅ Report dispatched to active OpenCLAW channel.")
    except Exception as e:
        print(f"Failed to parse or format the audit report: {e}")
        
    print("\nPipeline Complete!")

if __name__ == "__main__":
    main()
