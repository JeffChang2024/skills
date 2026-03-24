#!/usr/bin/env node
import fs from 'fs';
import path from 'path';
import os from 'os';

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function pathExists(p) {
  try {
    fs.accessSync(p);
    return true;
  } catch {
    return false;
  }
}

function readJsonFile(file) {
  return JSON.parse(fs.readFileSync(file, 'utf8'));
}

function isTrustedGatewayHost(hostname) {
  if (!hostname) return false;
  const host = String(hostname).toLowerCase();
  if (host === 'localhost' || host === '127.0.0.1' || host === '::1') return true;
  if (/^10\./.test(host)) return true;
  if (/^192\.168\./.test(host)) return true;
  if (/^172\.(1[6-9]|2\d|3[0-1])\./.test(host)) return true;
  if (host.endsWith('.local') || host.endsWith('.internal') || host.endsWith('.ts.net')) return true;
  return false;
}

function loadGatewayRuntime() {
  const cfgPath = process.env.OPENCLAW_CONFIG || path.join(os.homedir(), '.openclaw', 'openclaw.json');
  const cfg = pathExists(cfgPath) ? readJsonFile(cfgPath) : {};
  const port = Number(process.env.OPENCLAW_GATEWAY_PORT || cfg?.gateway?.port || 18789);
  const token = process.env.OPENCLAW_GATEWAY_TOKEN || cfg?.gateway?.auth?.token || null;
  const baseUrl = (process.env.OPENCLAW_GATEWAY_URL || `http://127.0.0.1:${port}`).replace(/\/$/, '');
  const model = process.env.OPENCLAW_GATEWAY_MODEL || 'openclaw:main';
  const allowNonLocalGateway = process.env.OPENCLAW_ALLOW_NONLOCAL_GATEWAY === '1';
  if (!token) {
    throw new Error('Missing Gateway token. Set OPENCLAW_GATEWAY_TOKEN or configure gateway.auth.token in ~/.openclaw/openclaw.json');
  }
  let parsed;
  try {
    parsed = new URL(baseUrl);
  } catch {
    throw new Error(`Invalid OPENCLAW_GATEWAY_URL/base URL: ${baseUrl}`);
  }
  if (!allowNonLocalGateway && !isTrustedGatewayHost(parsed.hostname)) {
    throw new Error(
      `Refusing to send ride email content to non-local Gateway host ${parsed.hostname}. `
      + 'Use localhost/private hostnames only, or set OPENCLAW_ALLOW_NONLOCAL_GATEWAY=1 to override.'
    );
  }
  return { cfg, cfgPath, baseUrl, token, model, allowNonLocalGateway };
}

const gatewayRuntime = loadGatewayRuntime();

const IMPORTANT_FIELDS = [
  'amount',
  'currency',
  'pickup',
  'dropoff',
  'payment_method',
  'distance_text',
  'duration_text',
  'start_time_text',
  'end_time_text',
];

function parseArgs(argv) {
  const out = {
    emailsDir: 'data/emails',
    ridesDir: 'data/rides',
    sessionsDir: 'data/ride-agent-sessions',
    provider: 'openai-codex',
    model: 'gpt-5.4',
    thinkLevel: 'low',
    limit: 0,
    force: false,
    onlyMissing: false,
    timeoutMs: 180000,
    finalRepairPasses: 1,
    shardIndex: null,
    shardCount: null,
    skipFinalValidation: false,
  };
  for (let i = 2; i < argv.length; i++) {
    const a = argv[i];
    const n = argv[i + 1];
    if (a === '--emails-dir') out.emailsDir = n, i++;
    else if (a === '--rides-dir') out.ridesDir = n, i++;
    else if (a === '--sessions-dir') out.sessionsDir = n, i++;
    else if (a === '--provider') out.provider = n, i++;
    else if (a === '--model') out.model = n, i++;
    else if (a === '--think-level') out.thinkLevel = n, i++;
    else if (a === '--limit') out.limit = Number(n || 0), i++;
    else if (a === '--timeout-ms') out.timeoutMs = Number(n || 180000), i++;
    else if (a === '--final-repair-passes') out.finalRepairPasses = Number(n || 1), i++;
    else if (a === '--shard-index') out.shardIndex = Number(n), i++;
    else if (a === '--shard-count') out.shardCount = Number(n), i++;
    else if (a === '--force') out.force = true;
    else if (a === '--only-missing') out.onlyMissing = true;
    else if (a === '--skip-final-validation') out.skipFinalValidation = true;
    else throw new Error(`Unknown arg: ${a}`);
  }
  return out;
}

function readJson(file) {
  return JSON.parse(fs.readFileSync(file, 'utf8'));
}

function writeJson(file, obj) {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, JSON.stringify(obj, null, 2) + '\n', 'utf8');
}

function listJsonFiles(dir) {
  return fs.readdirSync(dir)
    .filter((f) => f.endsWith('.json'))
    .sort()
    .map((f) => path.join(dir, f));
}

function basenameNoExt(file) {
  return path.basename(file, path.extname(file));
}

function emptyToNull(v) {
  if (v === undefined || v === null) return null;
  if (typeof v === 'string' && v.trim() === '') return null;
  return v;
}

function deepNormalize(obj) {
  if (Array.isArray(obj)) return obj.map(deepNormalize);
  if (!obj || typeof obj !== 'object') return emptyToNull(obj);
  const out = {};
  for (const [k, v] of Object.entries(obj)) out[k] = deepNormalize(v);
  return out;
}

function makeSkeleton(email) {
  return {
    provider: email.provider ?? null,
    source: {
      gmail_message_id: email.gmail_message_id ?? null,
      email_date: email.email_date ?? null,
      subject: email.subject ?? null,
    },
    ride: {
      start_time_text: null,
      end_time_text: null,
      total_text: null,
      currency: null,
      amount: null,
      pickup: null,
      dropoff: null,
      pickup_city: null,
      pickup_country: null,
      dropoff_city: null,
      dropoff_country: null,
      payment_method: null,
      driver: null,
      distance_text: null,
      duration_text: null,
      notes: null,
    },
  };
}

function normalizeRideObject(obj, email) {
  const base = makeSkeleton(email);
  if (obj && typeof obj === 'object') {
    if (obj.provider != null) base.provider = emptyToNull(obj.provider);
    if (obj.source && typeof obj.source === 'object') {
      for (const k of Object.keys(base.source)) {
        if (k in obj.source) base.source[k] = emptyToNull(obj.source[k]);
      }
    }
    if (obj.ride && typeof obj.ride === 'object') {
      for (const k of Object.keys(base.ride)) {
        if (k in obj.ride) base.ride[k] = emptyToNull(obj.ride[k]);
      }
    }
  }
  if (typeof base.ride.amount === 'string') {
    const x = base.ride.amount.replace(',', '.').trim();
    if (/^-?\d+(?:\.\d+)?$/.test(x)) base.ride.amount = Number(x);
  }
  return deepNormalize(base);
}

function mergeAdditive(existingObj, patchObj, email) {
  const existing = normalizeRideObject(existingObj, email);
  const patch = normalizeRideObject(patchObj, email);
  const out = JSON.parse(JSON.stringify(existing));
  out.provider = out.provider ?? patch.provider ?? email.provider ?? null;
  for (const k of Object.keys(out.source)) {
    if (out.source[k] == null && patch.source[k] != null) out.source[k] = patch.source[k];
  }
  for (const k of Object.keys(out.ride)) {
    if (out.ride[k] == null && patch.ride[k] != null) out.ride[k] = patch.ride[k];
  }
  return out;
}

function looksCancellationLike(email, ride) {
  const subject = String(email.subject || ride?.source?.subject || '').toLowerCase();
  const notes = String(ride?.ride?.notes || '').toLowerCase();
  const snippet = String(email.snippet || '').toLowerCase();
  return subject.includes('canceled trip') || subject.includes('cancellation') || notes.includes('cancellation fee') || notes.includes('fare adjustment') || snippet.includes('cancellation fee');
}

function missingImportantFields(rideObj, email) {
  const ride = rideObj.ride || {};
  const missing = IMPORTANT_FIELDS.filter((k) => ride[k] == null);
  if (looksCancellationLike(email, rideObj)) {
    return missing.filter((k) => !['pickup','dropoff','distance_text','duration_text','start_time_text','end_time_text'].includes(k));
  }
  return missing;
}

function buildBaseInstructions() {
  return [
    'You are extracting exactly one ride receipt into structured JSON.',
    'Use text_html as primary source. Use snippet only if text_html is empty.',
    'Return EXACTLY one JSON object and nothing else.',
    'Never hallucinate. If missing/unclear, use null.',
    'Keep addresses and time strings verbatim.',
    'Normalize currency to a 3-letter ISO-4217 code when confidently inferable.',
    'For this mailbox: Yandex `р.` totals are BYN, `BYN27.1` means BYN 27.1, and `₽757` means RUB 757.',
    'amount must be numeric or null. If only textual total exists, keep amount=null and preserve total_text.',
    'For Yandex route blocks with extra intermediate stops or `Destination changed`, keep the first address/time as pickup/start and the final address/time as dropoff/end.',
    'For older Bolt receipts, do not confuse `Ride duration 00:06` with start_time_text. duration_text is the duration; route times come from later pickup/dropoff timestamps.',
    'For Uber cancellation-fee or fare-adjustment receipts, route/time/distance fields may legitimately be null.',
    'Schema: {"provider":"Uber|Bolt|Yandex|Lyft|FreeNow","source":{"gmail_message_id":"...","email_date":"YYYY-MM-DD HH:MM","subject":"..."},"ride":{"start_time_text":null,"end_time_text":null,"total_text":null,"currency":null,"amount":null,"pickup":null,"dropoff":null,"pickup_city":null,"pickup_country":null,"dropoff_city":null,"dropoff_country":null,"payment_method":null,"driver":null,"distance_text":null,"duration_text":null,"notes":null}}',
  ].join('\n');
}

function extractJsonObject(text) {
  const s = String(text || '').trim();
  if (!s) throw new Error('Empty model output');
  try { return JSON.parse(s); } catch {}
  const first = s.indexOf('{');
  const last = s.lastIndexOf('}');
  if (first >= 0 && last > first) return JSON.parse(s.slice(first, last + 1));
  throw new Error('Could not parse JSON object from model output');
}

function extractGatewayOutputText(body) {
  if (body?.output && Array.isArray(body.output)) {
    for (const item of body.output) {
      if (item?.type === 'message' && Array.isArray(item.content)) {
        const txt = item.content.filter((p) => p?.type === 'output_text').map((p) => p.text || '').join('\n');
        if (txt.trim()) return txt;
      }
    }
  }
  if (body?.choices && Array.isArray(body.choices)) {
    const txt = body.choices.map((c) => c?.message?.content || '').join('\n');
    if (txt.trim()) return txt;
  }
  return '';
}

async function runAgent({ email, sessionId, prompt, timeoutMs }) {
  let lastErr;
  for (let attempt = 1; attempt <= 6; attempt++) {
    try {
      const controller = new AbortController();
      const timer = setTimeout(() => controller.abort(), timeoutMs);
      const payload = {
        model: gatewayRuntime.model,
        user: sessionId,
        input: prompt,
      };
      const res = await fetch(`${gatewayRuntime.baseUrl}/v1/responses`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${gatewayRuntime.token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
        signal: controller.signal,
      });
      clearTimeout(timer);
      const textBody = await res.text();
      if (!res.ok) {
        throw new Error(`Gateway HTTP ${res.status}: ${textBody}`);
      }
      const body = JSON.parse(textBody);
      const text = extractGatewayOutputText(body);
      return { res: body, text, obj: extractJsonObject(text) };
    } catch (err) {
      lastErr = err;
      const msg = String(err?.stack || err || '');
      const retryable = /rate limit|cooldown|temporar|ECONNRESET|ETIMEDOUT|abort|timed out|HTTP 5\d\d|Could not parse JSON object from model output/i.test(msg);
      if (!retryable || attempt === 6) break;
      const delay = Math.min(120000, attempt * 15000);
      console.error(`[retry] session=${sessionId} attempt=${attempt} delayMs=${delay} reason=${msg.split('\n')[0]}`);
      await sleep(delay);
    }
  }
  throw lastErr;
}

async function extractOne(cfg, email, opts) {
  const id = email.gmail_message_id;
  const prompt = `${buildBaseInstructions()}\n\nEmail JSON:\n${JSON.stringify(email)}`;
  const result = await runAgent({
    email, sessionId: `ride-extract-${id}`, prompt,
    timeoutMs: opts.timeoutMs,
  });
  return normalizeRideObject(result.obj, email);
}

async function repairOne(cfg, email, current, fields, issues, opts, tag='repair') {
  const id = email.gmail_message_id;
  const prompt = [
    buildBaseInstructions(),
    '',
    'You are repairing a previously extracted ride record.',
    `Goal: fill ONLY these missing or suspicious fields if the email supports them: ${fields.length ? fields.join(', ') : '(none specified)'}`,
    issues?.length ? `Validation issues to correct if supported by the email: ${issues.join(', ')}` : 'Validation issues: none provided.',
    'Do NOT overwrite any existing non-null value with null or different content.',
    'Return the FULL ride object with the SAME schema as before, but only add supported non-null values.',
    '',
    `Current extracted ride JSON:\n${JSON.stringify(current)}`,
    '',
    `Email JSON:\n${JSON.stringify(email)}`,
  ].join('\n');
  const result = await runAgent({
    email, sessionId: `ride-${tag}-${id}`, prompt,
    timeoutMs: opts.timeoutMs,
  });
  return mergeAdditive(current, result.obj, email);
}

function buildJsonl(ridesDir, outPath) {
  const lines = [];
  for (const file of listJsonFiles(ridesDir)) {
    lines.push(JSON.stringify(readJson(file)));
  }
  fs.writeFileSync(outPath, lines.length ? lines.join('\n') + '\n' : '', 'utf8');
}

function runPython(args) {
  const r = spawnSync('python3', args, { cwd: process.cwd(), encoding: 'utf8' });
  if (r.status !== 0) {
    throw new Error(`python3 ${args.join(' ')} failed\nSTDOUT:\n${r.stdout}\nSTDERR:\n${r.stderr}`);
  }
  return r;
}

function validateRides(ridesDir) {
  const jsonlPath = path.join('data', 'rides_extracted.jsonl');
  const flaggedPath = path.join('data', 'rides_flagged.jsonl');
  buildJsonl(ridesDir, jsonlPath);
  const r = runPython(['skills/ride-receipts-llm/scripts/validate_extracted_rides.py', '--in', jsonlPath, '--out', flaggedPath]);
  const summary = JSON.parse((r.stdout || '').trim().split(/\n/).filter(Boolean).slice(-1)[0]);
  return { jsonlPath, flaggedPath, summary };
}

async function main() {
  const opts = parseArgs(process.argv);
  fs.mkdirSync(opts.ridesDir, { recursive: true });
  fs.mkdirSync(opts.sessionsDir, { recursive: true });

  const cfg = gatewayRuntime.cfg;
  let emailFiles = listJsonFiles(opts.emailsDir);
  if (opts.shardCount != null) {
    if (!(opts.shardCount > 0) || !(opts.shardIndex >= 0) || !(opts.shardIndex < opts.shardCount)) {
      throw new Error('Invalid --shard-index/--shard-count');
    }
    emailFiles = emailFiles.filter((_, idx) => idx % opts.shardCount === opts.shardIndex);
  }
  if (opts.limit > 0) emailFiles = emailFiles.slice(0, opts.limit);

  let extracted = 0;
  let repairedMissing = 0;
  let targetedRepairs = 0;
  let skipped = 0;

  for (const emailFile of emailFiles) {
    const id = basenameNoExt(emailFile);
    const rideFile = path.join(opts.ridesDir, `${id}.json`);
    if (!opts.force && opts.onlyMissing && fs.existsSync(rideFile)) {
      skipped++;
      continue;
    }
    const email = readJson(emailFile);
    let current = fs.existsSync(rideFile) && !opts.force ? normalizeRideObject(readJson(rideFile), email) : await extractOne(cfg, email, opts);
    let missing = missingImportantFields(current, email);
    if (missing.length) {
      current = await repairOne(cfg, email, current, missing, [], opts, 'repair');
      repairedMissing++;
      missing = missingImportantFields(current, email);
      if (missing.length) {
        current = await repairOne(cfg, email, current, missing, [], opts, 'repair2');
      }
    }
    writeJson(rideFile, normalizeRideObject(current, email));
    extracted++;
  }

  console.log(JSON.stringify({
    emailsSeen: emailFiles.length,
    extractedOrChecked: extracted,
    skipped,
    repairedMissing,
    targetedRepairs,
    flagged: null,
    validationSkipped: true,
    ridesDir: opts.ridesDir,
    shardIndex: opts.shardIndex,
    shardCount: opts.shardCount,
    nextStep: 'Run validate_extracted_rides.py separately after this Gateway extraction batch.',
  }));
}

main().catch((err) => {
  console.error(err?.stack || String(err));
  process.exit(1);
});
