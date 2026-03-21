#!/usr/bin/env bash
set -euo pipefail

# benchmark — Performance Benchmark Testing Tool
# Version: 1.0.0
# Powered by BytesAgain | bytesagain.com | hello@bytesagain.com

DATA_DIR="${HOME}/.benchmark"
DATA_FILE="${DATA_DIR}/data.jsonl"
CONFIG_FILE="${DATA_DIR}/config.json"
REPORT_DIR="${DATA_DIR}/reports"

mkdir -p "${DATA_DIR}" "${REPORT_DIR}"
touch "${DATA_FILE}"

if [ ! -f "${CONFIG_FILE}" ]; then
  echo '{"default_duration": 10, "default_type": "cpu", "default_threads": 1}' > "${CONFIG_FILE}"
fi

COMMAND="${1:-help}"

case "${COMMAND}" in

  run)
    python3 << 'PYEOF'
import os, sys, json, time, uuid, datetime, hashlib, multiprocessing

data_file = os.environ.get("DATA_FILE", os.path.expanduser("~/.benchmark/data.jsonl"))
bench_type = os.environ.get("BENCH_TYPE", "cpu")
tag = os.environ.get("BENCH_TAG", "default")
duration = int(os.environ.get("BENCH_DURATION", "10"))

ts = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
short_id = uuid.uuid4().hex[:8]
bench_id = f"bench_{ts}_{short_id}"

metrics = {}
start = time.time()

if bench_type == "cpu":
    ops = 0
    end_time = start + duration
    while time.time() < end_time:
        hashlib.sha256(str(ops).encode()).hexdigest()
        ops += 1
    elapsed = time.time() - start
    metrics = {
        "operations": ops,
        "ops_per_second": round(ops / elapsed, 2),
        "elapsed_seconds": round(elapsed, 3)
    }
    score = round(ops / elapsed, 2)

elif bench_type == "memory":
    import resource
    blocks = []
    ops = 0
    end_time = start + duration
    while time.time() < end_time:
        blocks.append(bytearray(1024 * 100))  # 100KB blocks
        ops += 1
        if len(blocks) > 500:
            blocks = blocks[-100:]
    elapsed = time.time() - start
    total_mb = (ops * 100 * 1024) / (1024 * 1024)
    metrics = {
        "allocations": ops,
        "total_allocated_mb": round(total_mb, 2),
        "alloc_per_second": round(ops / elapsed, 2),
        "elapsed_seconds": round(elapsed, 3)
    }
    score = round(ops / elapsed, 2)
    del blocks

elif bench_type == "disk":
    import tempfile
    tmpfile = tempfile.mktemp(prefix="bench_disk_")
    block_size = 1024 * 1024  # 1MB
    blocks_written = 0
    end_time = start + min(duration, 10)
    while time.time() < end_time:
        with open(tmpfile, "ab") as f:
            f.write(os.urandom(block_size))
        blocks_written += 1
    elapsed = time.time() - start
    total_mb = blocks_written
    if os.path.exists(tmpfile):
        os.remove(tmpfile)
    metrics = {
        "blocks_written": blocks_written,
        "total_mb": total_mb,
        "write_speed_mbps": round(total_mb / elapsed, 2),
        "elapsed_seconds": round(elapsed, 3)
    }
    score = round(total_mb / elapsed, 2)

else:
    # Generic benchmark
    ops = 0
    end_time = start + duration
    while time.time() < end_time:
        sorted(list(range(1000, 0, -1)))
        ops += 1
    elapsed = time.time() - start
    metrics = {
        "operations": ops,
        "ops_per_second": round(ops / elapsed, 2),
        "elapsed_seconds": round(elapsed, 3)
    }
    score = round(ops / elapsed, 2)

record = {
    "id": bench_id,
    "type": bench_type,
    "tag": tag,
    "score": score,
    "duration_seconds": duration,
    "metrics": metrics,
    "cpu_count": multiprocessing.cpu_count(),
    "created_at": datetime.datetime.utcnow().isoformat() + "Z"
}

with open(data_file, "a") as f:
    f.write(json.dumps(record) + "\n")

print(json.dumps({"status": "success", "command": "run", "data": record}, indent=2))
PYEOF
    ;;

  compare)
    python3 << 'PYEOF'
import os, sys, json

data_file = os.environ.get("DATA_FILE", os.path.expanduser("~/.benchmark/data.jsonl"))
id1 = os.environ.get("BENCH_ID", "")
id2 = os.environ.get("BENCH_ID2", "")

if not id1 or not id2:
    print(json.dumps({"status": "error", "message": "BENCH_ID and BENCH_ID2 are required"}), file=sys.stderr)
    sys.exit(2)

records = {}
with open(data_file, "r") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        entry = json.loads(line)
        if entry["id"] in (id1, id2):
            records[entry["id"]] = entry

if id1 not in records or id2 not in records:
    missing = id1 if id1 not in records else id2
    print(json.dumps({"status": "error", "message": f"Benchmark not found: {missing}"}), file=sys.stderr)
    sys.exit(3)

r1, r2 = records[id1], records[id2]
s1, s2 = r1.get("score", 0), r2.get("score", 0)
diff_pct = round(((s2 - s1) / s1 * 100) if s1 != 0 else 0, 2)

print(json.dumps({
    "status": "success",
    "command": "compare",
    "data": {
        "benchmark_1": {"id": id1, "type": r1.get("type"), "score": s1, "tag": r1.get("tag")},
        "benchmark_2": {"id": id2, "type": r2.get("type"), "score": s2, "tag": r2.get("tag")},
        "difference_percent": diff_pct,
        "winner": id2 if s2 > s1 else id1 if s1 > s2 else "tie"
    }
}, indent=2))
PYEOF
    ;;

  history)
    python3 << 'PYEOF'
import os, sys, json

data_file = os.environ.get("DATA_FILE", os.path.expanduser("~/.benchmark/data.jsonl"))
bench_type = os.environ.get("BENCH_TYPE", "")
tag = os.environ.get("BENCH_TAG", "")

records = []
if os.path.exists(data_file):
    with open(data_file, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            entry = json.loads(line)
            if bench_type and entry.get("type") != bench_type:
                continue
            if tag and entry.get("tag") != tag:
                continue
            records.append(entry)

records.sort(key=lambda x: x.get("created_at", ""), reverse=True)

print(json.dumps({
    "status": "success",
    "command": "history",
    "data": {
        "count": len(records),
        "benchmarks": records
    }
}, indent=2))
PYEOF
    ;;

  report)
    python3 << 'PYEOF'
import os, sys, json, datetime

data_file = os.environ.get("DATA_FILE", os.path.expanduser("~/.benchmark/data.jsonl"))
report_dir = os.environ.get("REPORT_DIR", os.path.expanduser("~/.benchmark/reports"))
bench_id = os.environ.get("BENCH_ID", "")

records = []
target = None
with open(data_file, "r") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        entry = json.loads(line)
        records.append(entry)
        if bench_id and entry["id"] == bench_id:
            target = entry

if bench_id and not target:
    print(json.dumps({"status": "error", "message": f"Benchmark not found: {bench_id}"}), file=sys.stderr)
    sys.exit(3)

if target:
    same_type = [r for r in records if r.get("type") == target.get("type")]
    scores = [r.get("score", 0) for r in same_type]
    avg_score = sum(scores) / len(scores) if scores else 0
    percentile = sum(1 for s in scores if s <= target.get("score", 0)) / len(scores) * 100 if scores else 0

    report = {
        "benchmark": target,
        "analysis": {
            "average_score_for_type": round(avg_score, 2),
            "percentile": round(percentile, 1),
            "total_runs_same_type": len(same_type),
            "best_score": max(scores) if scores else 0,
            "worst_score": min(scores) if scores else 0
        }
    }
else:
    by_type = {}
    for r in records:
        t = r.get("type", "unknown")
        by_type.setdefault(t, []).append(r.get("score", 0))
    summary = {}
    for t, scores in by_type.items():
        summary[t] = {
            "count": len(scores),
            "avg": round(sum(scores)/len(scores), 2),
            "best": max(scores),
            "worst": min(scores)
        }
    report = {"summary": summary, "total_runs": len(records)}

report_file = os.path.join(report_dir, f"report_{datetime.datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json")
os.makedirs(report_dir, exist_ok=True)
with open(report_file, "w") as f:
    json.dump(report, f, indent=2)

print(json.dumps({
    "status": "success",
    "command": "report",
    "data": {"report_file": report_file, "report": report}
}, indent=2))
PYEOF
    ;;

  profile)
    python3 << 'PYEOF'
import os, sys, json, time, uuid, datetime, hashlib

data_file = os.environ.get("DATA_FILE", os.path.expanduser("~/.benchmark/data.jsonl"))
bench_type = os.environ.get("BENCH_TYPE", "cpu")
duration = int(os.environ.get("BENCH_DURATION", "10"))
tag = os.environ.get("BENCH_TAG", "profile")

ts = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
short_id = uuid.uuid4().hex[:8]
bench_id = f"prof_{ts}_{short_id}"

phases = []
total_ops = 0

# Phase 1: Warmup
start = time.time()
warmup_ops = 0
warmup_end = start + max(1, duration * 0.1)
while time.time() < warmup_end:
    hashlib.md5(str(warmup_ops).encode()).hexdigest()
    warmup_ops += 1
phases.append({"phase": "warmup", "ops": warmup_ops, "seconds": round(time.time() - start, 3)})
total_ops += warmup_ops

# Phase 2: Ramp-up
ramp_start = time.time()
ramp_ops = 0
ramp_end = ramp_start + max(1, duration * 0.2)
while time.time() < ramp_end:
    hashlib.sha256(str(ramp_ops).encode()).hexdigest()
    ramp_ops += 1
phases.append({"phase": "ramp_up", "ops": ramp_ops, "seconds": round(time.time() - ramp_start, 3)})
total_ops += ramp_ops

# Phase 3: Sustained
sustained_start = time.time()
sustained_ops = 0
sustained_end = sustained_start + max(1, duration * 0.5)
while time.time() < sustained_end:
    hashlib.sha512(str(sustained_ops).encode()).hexdigest()
    sustained_ops += 1
phases.append({"phase": "sustained", "ops": sustained_ops, "seconds": round(time.time() - sustained_start, 3)})
total_ops += sustained_ops

# Phase 4: Cool-down
cool_start = time.time()
cool_ops = 0
cool_end = cool_start + max(1, duration * 0.2)
while time.time() < cool_end:
    hashlib.sha256(str(cool_ops).encode()).hexdigest()
    cool_ops += 1
phases.append({"phase": "cool_down", "ops": cool_ops, "seconds": round(time.time() - cool_start, 3)})
total_ops += cool_ops

total_elapsed = time.time() - start

record = {
    "id": bench_id,
    "type": bench_type,
    "tag": tag,
    "mode": "profile",
    "score": round(total_ops / total_elapsed, 2),
    "total_ops": total_ops,
    "duration_seconds": round(total_elapsed, 3),
    "phases": phases,
    "created_at": datetime.datetime.utcnow().isoformat() + "Z"
}

with open(data_file, "a") as f:
    f.write(json.dumps(record) + "\n")

print(json.dumps({"status": "success", "command": "profile", "data": record}, indent=2))
PYEOF
    ;;

  stress)
    python3 << 'PYEOF'
import os, sys, json, time, uuid, datetime, hashlib, multiprocessing, threading

data_file = os.environ.get("DATA_FILE", os.path.expanduser("~/.benchmark/data.jsonl"))
bench_type = os.environ.get("BENCH_TYPE", "cpu")
duration = int(os.environ.get("BENCH_DURATION", "10"))
threads = int(os.environ.get("BENCH_THREADS", str(multiprocessing.cpu_count())))
tag = os.environ.get("BENCH_TAG", "stress")

ts = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
short_id = uuid.uuid4().hex[:8]
bench_id = f"stress_{ts}_{short_id}"

results = {}
lock = threading.Lock()

def worker(thread_id, duration_secs):
    ops = 0
    start = time.time()
    end_time = start + duration_secs
    while time.time() < end_time:
        if bench_type == "cpu":
            hashlib.sha256(str(ops).encode()).hexdigest()
        elif bench_type == "memory":
            _ = bytearray(1024 * 10)
        else:
            sorted(list(range(500, 0, -1)))
        ops += 1
    elapsed = time.time() - start
    with lock:
        results[thread_id] = {"ops": ops, "elapsed": round(elapsed, 3), "ops_per_second": round(ops/elapsed, 2)}

thread_list = []
start_all = time.time()
for i in range(threads):
    t = threading.Thread(target=worker, args=(i, duration))
    thread_list.append(t)
    t.start()

for t in thread_list:
    t.join()

total_elapsed = time.time() - start_all
total_ops = sum(r["ops"] for r in results.values())

record = {
    "id": bench_id,
    "type": bench_type,
    "tag": tag,
    "mode": "stress",
    "threads": threads,
    "score": round(total_ops / total_elapsed, 2),
    "total_ops": total_ops,
    "duration_seconds": round(total_elapsed, 3),
    "thread_results": results,
    "created_at": datetime.datetime.utcnow().isoformat() + "Z"
}

with open(data_file, "a") as f:
    f.write(json.dumps(record) + "\n")

print(json.dumps({"status": "success", "command": "stress", "data": record}, indent=2))
PYEOF
    ;;

  config)
    python3 << 'PYEOF'
import os, sys, json

config_file = os.environ.get("CONFIG_FILE", os.path.expanduser("~/.benchmark/config.json"))
key = os.environ.get("BENCH_KEY", "")
value = os.environ.get("BENCH_VALUE", "")

config = {}
if os.path.exists(config_file):
    with open(config_file, "r") as f:
        config = json.load(f)

if key and value:
    try:
        config[key] = json.loads(value)
    except (json.JSONDecodeError, ValueError):
        config[key] = value
    with open(config_file, "w") as f:
        json.dump(config, f, indent=2)

print(json.dumps({
    "status": "success",
    "command": "config",
    "data": config
}, indent=2))
PYEOF
    ;;

  export)
    python3 << 'PYEOF'
import os, sys, json

data_file = os.environ.get("DATA_FILE", os.path.expanduser("~/.benchmark/data.jsonl"))
fmt = os.environ.get("BENCH_FORMAT", "json")

records = []
if os.path.exists(data_file):
    with open(data_file, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            records.append(json.loads(line))

if fmt == "csv":
    if records:
        print("id,type,tag,score,duration_seconds,created_at")
        for r in records:
            print(f"{r.get('id','')},{r.get('type','')},{r.get('tag','')},{r.get('score','')},{r.get('duration_seconds','')},{r.get('created_at','')}")
else:
    print(json.dumps({
        "status": "success",
        "command": "export",
        "data": {"format": fmt, "count": len(records), "benchmarks": records}
    }, indent=2))
PYEOF
    ;;

  list)
    python3 << 'PYEOF'
import os, sys, json

data_file = os.environ.get("DATA_FILE", os.path.expanduser("~/.benchmark/data.jsonl"))

records = []
if os.path.exists(data_file):
    with open(data_file, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            records.append(json.loads(line))

print(json.dumps({
    "status": "success",
    "command": "list",
    "data": {"count": len(records), "benchmarks": records}
}, indent=2))
PYEOF
    ;;

  status)
    python3 << 'PYEOF'
import os, sys, json

data_file = os.environ.get("DATA_FILE", os.path.expanduser("~/.benchmark/data.jsonl"))

records = []
if os.path.exists(data_file):
    with open(data_file, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            records.append(json.loads(line))

by_type = {}
for r in records:
    t = r.get("type", "unknown")
    by_type.setdefault(t, []).append(r.get("score", 0))

summary = {}
for t, scores in by_type.items():
    summary[t] = {"count": len(scores), "avg_score": round(sum(scores)/len(scores), 2) if scores else 0, "best": max(scores) if scores else 0}

print(json.dumps({
    "status": "success",
    "command": "status",
    "data": {"total_runs": len(records), "by_type": summary, "data_file": data_file}
}, indent=2))
PYEOF
    ;;

  help)
    cat << 'HELPEOF'
benchmark — Performance Benchmark Testing Tool v1.0.0

Usage: scripts/script.sh <command>

Commands:
  run       Execute a benchmark test (BENCH_TYPE, BENCH_DURATION)
  compare   Compare two benchmark runs (BENCH_ID, BENCH_ID2)
  history   Show run history (optional BENCH_TYPE, BENCH_TAG)
  report    Generate performance report (optional BENCH_ID)
  profile   Run detailed profiling session
  stress    Run multi-threaded stress test (BENCH_THREADS)
  config    View/update config (BENCH_KEY, BENCH_VALUE)
  export    Export data (BENCH_FORMAT: json|csv)
  list      List all benchmark runs
  status    Show system status and summary
  help      Show this help message
  version   Show version

Powered by BytesAgain | bytesagain.com | hello@bytesagain.com
HELPEOF
    ;;

  version)
    echo '{"name": "benchmark", "version": "1.0.0", "author": "BytesAgain"}'
    ;;

  *)
    echo "Unknown command: ${COMMAND}" >&2
    echo "Run 'scripts/script.sh help' for usage." >&2
    exit 1
    ;;
esac
