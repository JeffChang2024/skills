---
name: benchmark
version: "1.0.0"
description: "Run performance benchmarks and stress tests using Python profiling tools. Use when you need to measure, compare, or analyze system and application performance."
author: BytesAgain
homepage: https://bytesagain.com
source: https://github.com/bytesagain/ai-skills
tags: [benchmark, performance, profiling, stress-test, metrics]
---

# Benchmark — Performance Benchmark Testing Tool

A comprehensive performance benchmarking skill for running CPU, memory, disk, and network tests. Supports comparison between runs, historical tracking, profiling, and stress testing. All results are stored in JSONL format.

## Prerequisites

- `bash` (v4+)
- `python3` (v3.6+)
- Standard system utilities (`dd`, `time`, etc.)

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `BENCH_TYPE` | No | Benchmark type: cpu, memory, disk, network (default: cpu) |
| `BENCH_DURATION` | No | Duration in seconds for stress tests (default: 10) |
| `BENCH_THREADS` | No | Number of threads for parallel tests (default: 1) |
| `BENCH_ID` | No | Specific benchmark ID for comparison/lookup |
| `BENCH_TAG` | No | Tag for organizing benchmark runs |
| `BENCH_FORMAT` | No | Export format: json, csv (default: json) |

## Data Storage

- Results: `~/.benchmark/data.jsonl`
- Config: `~/.benchmark/config.json`
- Reports: `~/.benchmark/reports/`

## Commands

### `run`
Execute a benchmark test of the specified type.
```bash
BENCH_TYPE="cpu" BENCH_TAG="baseline" scripts/script.sh run
```

### `compare`
Compare two benchmark runs side by side.
```bash
BENCH_ID="bench_a" BENCH_ID2="bench_b" scripts/script.sh compare
```

### `history`
Show benchmark run history with optional filtering.
```bash
BENCH_TYPE="cpu" BENCH_TAG="baseline" scripts/script.sh history
```

### `report`
Generate a detailed performance report.
```bash
BENCH_ID="bench_abc123" scripts/script.sh report
```

### `profile`
Run a detailed profiling session with breakdown.
```bash
BENCH_TYPE="cpu" BENCH_DURATION="30" scripts/script.sh profile
```

### `stress`
Run a sustained stress test.
```bash
BENCH_TYPE="cpu" BENCH_DURATION="60" BENCH_THREADS="4" scripts/script.sh stress
```

### `config`
View or update benchmark configuration.
```bash
BENCH_KEY="default_duration" BENCH_VALUE="30" scripts/script.sh config
```

### `export`
Export benchmark data in various formats.
```bash
BENCH_FORMAT="csv" scripts/script.sh export
```

### `list`
List all benchmark runs.
```bash
scripts/script.sh list
```

### `status`
Show benchmarking system status and summary.
```bash
scripts/script.sh status
```

### `help`
Display usage information.
```bash
scripts/script.sh help
```

### `version`
Display current version.
```bash
scripts/script.sh version
```

## Output Format

All commands output structured JSON to stdout:

```json
{
  "status": "success",
  "command": "run",
  "data": {
    "id": "bench_20240101_120000_abc123",
    "type": "cpu",
    "score": 15234.5,
    "duration_ms": 10000,
    "metrics": {}
  }
}
```

## Error Handling

| Exit Code | Meaning |
|-----------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Missing required parameter |
| 3 | Benchmark not found |

---

Powered by BytesAgain | bytesagain.com | hello@bytesagain.com
