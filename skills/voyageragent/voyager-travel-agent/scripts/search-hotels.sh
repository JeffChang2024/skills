#!/usr/bin/env node

/**
 * Usage:
 *   node search-hotels.sh '[{"subQuery":"大阪酒店推荐","checkInDate":"2026-04-01","checkOutDate":"2026-04-07","city":"大阪","country":"日本","nearby":"梅田"}]'
 */

const { execSync } = require('child_process');

if (process.argv.length < 3) {
  console.error('❌ Please provide query JSON array parameter');
  process.exit(1);
}

const queryString = process.argv[2];

const cmd = `curl -sS -X POST 'https://ivguserprod-pre.alipay.com/ivgavatarcn/api/v1/voyager/mcp/RECALL_hotel' \
  -H 'apiKey: test1' \
  -H 'Content-Type: application/json' \
  --data-raw '${queryString.replace(/'/g, `'\''`)}'`;

process.stdout.write(execSync(cmd, { stdio: ['ignore', 'pipe', 'inherit'] }));
