#!/usr/bin/env node
/**
 * Standalone agentar CLI — search, list, install, and export agentars.
 *
 * Works independently of the OpenClaw gateway, so skill installation and
 * agentar operations can happen without requiring a gateway restart.
 * Uses only Node.js built-in modules (no third-party dependencies).
 */

import fs from "node:fs";
import http from "node:http";
import https from "node:https";
import os from "node:os";
import path from "node:path";
import readline from "node:readline";
import { inflateRawSync, deflateRawSync } from "node:zlib";
import { createRequire } from "node:module";

// Lazy-loaded child_process — only imported when openclaw CLI interaction is needed
let _spawnSync;
function getSpawnSync() {
  if (!_spawnSync) {
    const _require = createRequire(import.meta.url);
    _spawnSync = _require("node:child_process").spawnSync;
  }
  return _spawnSync;
}

// ─── Constants ───────────────────────────────────────────────────────────────

const CLI_VERSION = "3.3.0";
const CLI_CONFIG_NAME = "config.json";
const DEFAULT_API_BASE_URL = "https://catchclaw.me";

const HOME = os.homedir();
const OPENCLAW_HOME = path.join(HOME, ".openclaw");
const MAIN_WORKSPACE = path.join(OPENCLAW_HOME, "workspace");
const WORKSPACES_DIR = path.join(OPENCLAW_HOME, "agentar-workspaces");

const WORKSPACE_FILES = [
  "SOUL.md", "USER.md", "IDENTITY.md", "TOOLS.md",
  "HEARTBEAT.md", "MEMORY.md",
];
const SKIP_FILES = ["AGENTS.md", "BOOTSTRAP.md"];
const EXPORT_SKIP_DIRS = [".git", ".openclaw", "__MACOSX", "memory"];
const SENSITIVE_PATTERNS = [".credentials", ".env", ".secret", ".key", ".pem"];

// ─── Config ──────────────────────────────────────────────────────────────────

function cliHome() {
  return process.env.AGENTAR_HOME || path.join(HOME, ".agentar");
}

function loadConfig() {
  const cfgPath = path.join(cliHome(), CLI_CONFIG_NAME);
  try {
    return JSON.parse(fs.readFileSync(cfgPath, "utf-8"));
  } catch {
    return {};
  }
}

function getApiBaseUrl(cliArg) {
  if (cliArg) return cliArg.replace(/\/+$/, "");
  const envUrl = process.env.AGENTAR_API_BASE_URL;
  if (envUrl) return envUrl.replace(/\/+$/, "");
  const cfg = loadConfig();
  return (cfg.api_base_url || DEFAULT_API_BASE_URL).replace(/\/+$/, "");
}

// ─── HTTP helpers ────────────────────────────────────────────────────────────

function httpGetJson(url) {
  return new Promise((resolve, reject) => {
    const mod = url.startsWith("https") ? https : http;
    const req = mod.get(url, { timeout: 30000 }, (res) => {
      if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
        return httpGetJson(res.headers.location).then(resolve, reject);
      }
      if (res.statusCode !== 200) {
        res.resume();
        return reject(new Error(`HTTP ${res.statusCode} for ${url}`));
      }
      let data = "";
      res.on("data", (chunk) => (data += chunk));
      res.on("end", () => {
        try { resolve(JSON.parse(data)); }
        catch (e) { reject(e); }
      });
    });
    req.on("error", reject);
    req.on("timeout", () => { req.destroy(); reject(new Error("Request timeout")); });
  });
}

function httpDownload(url, dest) {
  return new Promise((resolve, reject) => {
    const mod = url.startsWith("https") ? https : http;
    const req = mod.get(url, { timeout: 120000 }, (res) => {
      if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
        return httpDownload(res.headers.location, dest).then(resolve, reject);
      }
      if (res.statusCode !== 200) {
        res.resume();
        return reject(new Error(`HTTP ${res.statusCode} for ${url}`));
      }
      const ws = fs.createWriteStream(dest);
      res.pipe(ws);
      ws.on("finish", () => ws.close(resolve));
      ws.on("error", reject);
    });
    req.on("error", reject);
    req.on("timeout", () => { req.destroy(); reject(new Error("Download timeout")); });
  });
}

// ─── Interactive prompt ──────────────────────────────────────────────────────

function prompt(question) {
  return new Promise((resolve) => {
    const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
    rl.question(question, (answer) => { rl.close(); resolve(answer.trim()); });
  });
}

// ─── OpenClaw CLI helper ─────────────────────────────────────────────────────

function findOpenclawBin() {
  const isWin = process.platform === "win32";
  const name = "openclaw";
  const pathExts = isWin
    ? (process.env.PATHEXT || ".CMD;.EXE;.BAT;.PS1").split(";").map(e => e.toLowerCase())
    : [""];
  const pathDirs = (process.env.PATH || "").split(isWin ? ";" : ":");

  for (const dir of pathDirs) {
    if (!dir) continue;
    for (const ext of pathExts) {
      const candidate = path.join(dir, name + ext);
      try { if (fs.existsSync(candidate)) return candidate; } catch { /* skip */ }
    }
  }

  const fallbacks = isWin
    ? [path.join(process.env.LOCALAPPDATA || path.join(HOME, "AppData", "Local"), "pnpm", "openclaw.cmd")]
    : [path.join(HOME, ".local/share/pnpm/openclaw")];
  for (const p of fallbacks) {
    if (fs.existsSync(p)) return p;
  }
  return null;
}

// ─── File utilities ──────────────────────────────────────────────────────────

function mkdtemp(prefix) {
  return fs.mkdtempSync(path.join(os.tmpdir(), prefix));
}

function rmrf(dir) {
  try { fs.rmSync(dir, { recursive: true, force: true }); } catch { /* ignore */ }
}

function cpSync(src, dest) {
  fs.cpSync(src, dest, { recursive: true });
}

function copyFile(src, dest) {
  fs.copyFileSync(src, dest);
}

function mkdirp(dir) {
  fs.mkdirSync(dir, { recursive: true });
}

function readdirEntries(dir) {
  return fs.readdirSync(dir, { withFileTypes: true });
}

function isSensitiveFile(name) {
  return SENSITIVE_PATTERNS.some((p) => name === p || name.endsWith(p));
}

function cpSyncFiltered(src, dest, skipped) {
  mkdirp(dest);
  for (const entry of readdirEntries(src)) {
    const s = path.join(src, entry.name);
    const d = path.join(dest, entry.name);
    if (isSensitiveFile(entry.name)) {
      skipped.push(path.relative(src, s));
      continue;
    }
    if (entry.isDirectory()) {
      cpSyncFiltered(s, d, skipped);
    } else {
      copyFile(s, d);
    }
  }
}

// ─── Core install logic ──────────────────────────────────────────────────────

function backupDirectory(dirPath, reason = "") {
  if (!fs.existsSync(dirPath)) return null;
  const backupsDir = path.join(cliHome(), "backups");
  mkdirp(backupsDir);
  const ts = new Date().toISOString().replace(/[:.]/g, "-").slice(0, 19);
  const tag = reason ? `.${reason}` : "";
  const backup = path.join(backupsDir, `workspace.${ts}${tag}`);
  cpSync(dirPath, backup);
  return backup;
}

function mergeSkills(srcSkillsDir, destSkillsDir) {
  if (!fs.existsSync(srcSkillsDir)) return [];
  mkdirp(destSkillsDir);
  const merged = [];
  for (const entry of readdirEntries(srcSkillsDir)) {
    const src = path.join(srcSkillsDir, entry.name);
    const dest = path.join(destSkillsDir, entry.name);
    if (entry.isDirectory()) {
      if (fs.existsSync(dest)) rmrf(dest);
      cpSync(src, dest);
    } else {
      copyFile(src, dest);
    }
    merged.push(entry.name);
  }
  return merged;
}

function writeCredentials(workspace, apiKey) {
  const skillsDir = path.join(workspace, "skills");
  mkdirp(skillsDir);
  fs.writeFileSync(path.join(skillsDir, ".credentials"), `apiKey=${apiKey}\n`);

  const gitignore = path.join(workspace, ".gitignore");
  const entry = "skills/.credentials";
  if (fs.existsSync(gitignore)) {
    const content = fs.readFileSync(gitignore, "utf-8");
    if (!content.includes(entry)) {
      fs.appendFileSync(gitignore, `\n${entry}\n`);
    }
  } else {
    fs.writeFileSync(gitignore, `${entry}\n`);
  }
}

function extractWorkspaceFiles(contentDir, targetDir) {
  mkdirp(targetDir);
  const copied = [];

  for (const fname of WORKSPACE_FILES) {
    const src = path.join(contentDir, fname);
    if (fs.existsSync(src)) {
      copyFile(src, path.join(targetDir, fname));
      copied.push(fname);
    }
  }

  for (const entry of readdirEntries(contentDir)) {
    if (entry.name === "skills" && entry.isDirectory()) continue;
    if (SKIP_FILES.includes(entry.name) || WORKSPACE_FILES.includes(entry.name)) continue;
    if (entry.name.startsWith(".")) continue;
    const src = path.join(contentDir, entry.name);
    const dest = path.join(targetDir, entry.name);
    if (entry.isDirectory()) {
      if (fs.existsSync(dest)) rmrf(dest);
      cpSync(src, dest);
    } else {
      copyFile(src, dest);
    }
    copied.push(entry.name);
  }
  return copied;
}

function resolveContentDir(extractDir) {
  const entries = readdirEntries(extractDir)
    .filter((e) => !e.name.startsWith(".") && e.name !== "__MACOSX");
  if (entries.length === 1 && entries[0].isDirectory()) {
    return path.join(extractDir, entries[0].name);
  }
  return extractDir;
}

function extractZip(zipPath, destDir) {
  const buf = fs.readFileSync(zipPath);
  let offset = 0;
  while (offset < buf.length - 4) {
    if (buf.readUInt32LE(offset) !== 0x04034b50) break; // local file header signature
    const flags = buf.readUInt16LE(offset + 6);
    const method = buf.readUInt16LE(offset + 8);
    const compSize = buf.readUInt32LE(offset + 18);
    const uncompSize = buf.readUInt32LE(offset + 22);
    const nameLen = buf.readUInt16LE(offset + 26);
    const extraLen = buf.readUInt16LE(offset + 28);
    const nameBytes = buf.subarray(offset + 30, offset + 30 + nameLen);
    const isUtf8 = (flags & 0x800) !== 0;
    const entryName = isUtf8 ? nameBytes.toString("utf-8") : nameBytes.toString("ascii");
    const dataStart = offset + 30 + nameLen + extraLen;
    const rawData = buf.subarray(dataStart, dataStart + compSize);
    offset = dataStart + compSize;

    // skip data descriptor if present
    if ((flags & 0x08) !== 0 && offset + 12 <= buf.length) {
      if (buf.readUInt32LE(offset) === 0x08074b50) offset += 16;
      else offset += 12;
    }

    // sanitize path: reject absolute or traversal paths
    const normalized = path.normalize(entryName);
    if (path.isAbsolute(normalized) || normalized.startsWith("..")) continue;
    const dest = path.join(destDir, normalized);

    if (entryName.endsWith("/")) {
      mkdirp(dest);
      continue;
    }

    mkdirp(path.dirname(dest));
    if (method === 0) {
      fs.writeFileSync(dest, rawData);
    } else if (method === 8) {
      const inflated = inflateRawSync(rawData);
      fs.writeFileSync(dest, inflated);
    } else {
      throw new Error(`unsupported compression method ${method} for ${entryName}`);
    }
  }
}

function createZip(srcDir, outputPath) {
  const entries = [];

  function walk(dir, base) {
    for (const ent of readdirEntries(dir)) {
      const rel = base ? base + "/" + ent.name : ent.name;
      const full = path.join(dir, ent.name);
      if (ent.isDirectory()) {
        entries.push({ name: rel + "/", data: Buffer.alloc(0), method: 0, size: 0, crc: 0 });
        walk(full, rel);
      } else {
        const raw = fs.readFileSync(full);
        const fileCrc = crc32(raw);
        const compressed = deflateRawSync(raw);
        if (compressed.length < raw.length) {
          entries.push({ name: rel, data: compressed, method: 8, size: raw.length, crc: fileCrc });
        } else {
          entries.push({ name: rel, data: raw, method: 0, size: raw.length, crc: fileCrc });
        }
      }
    }
  }
  walk(srcDir, "");

  const parts = [];
  const centralDir = [];
  let offset = 0;

  for (const entry of entries) {
    const nameBuf = Buffer.from(entry.name, "utf-8");
    const compSize = entry.data.length;
    const uncompSize = entry.size ?? entry.data.length;
    const crc = entry.crc;

    // local file header
    const lh = Buffer.alloc(30 + nameBuf.length);
    lh.writeUInt32LE(0x04034b50, 0);
    lh.writeUInt16LE(20, 4);         // version needed
    lh.writeUInt16LE(0x800, 6);      // flags: UTF-8
    lh.writeUInt16LE(entry.method, 8);
    lh.writeUInt32LE(crc, 14);
    lh.writeUInt32LE(compSize, 18);
    lh.writeUInt32LE(uncompSize, 22);
    lh.writeUInt16LE(nameBuf.length, 26);
    nameBuf.copy(lh, 30);
    parts.push(lh, entry.data);

    // central directory entry
    const cd = Buffer.alloc(46 + nameBuf.length);
    cd.writeUInt32LE(0x02014b50, 0);
    cd.writeUInt16LE(20, 4);         // version made by
    cd.writeUInt16LE(20, 6);         // version needed
    cd.writeUInt16LE(0x800, 8);      // flags: UTF-8
    cd.writeUInt16LE(entry.method, 10);
    cd.writeUInt32LE(crc, 16);
    cd.writeUInt32LE(compSize, 20);
    cd.writeUInt32LE(uncompSize, 24);
    cd.writeUInt16LE(nameBuf.length, 28);
    if (entry.name.endsWith("/")) cd.writeUInt32LE(0x10, 38); // external attr: directory
    cd.writeUInt32LE(offset, 42);
    nameBuf.copy(cd, 46);
    centralDir.push(cd);

    offset += lh.length + entry.data.length;
  }

  const cdBuf = Buffer.concat(centralDir);
  // end of central directory
  const eocd = Buffer.alloc(22);
  eocd.writeUInt32LE(0x06054b50, 0);
  eocd.writeUInt16LE(entries.length, 8);
  eocd.writeUInt16LE(entries.length, 10);
  eocd.writeUInt32LE(cdBuf.length, 12);
  eocd.writeUInt32LE(offset, 16);

  mkdirp(path.dirname(outputPath));
  fs.writeFileSync(outputPath, Buffer.concat([...parts, cdBuf, eocd]));
}

function crc32(buf) {
  let crc = 0xFFFFFFFF;
  for (let i = 0; i < buf.length; i++) {
    crc ^= buf[i];
    for (let j = 0; j < 8; j++) {
      crc = (crc >>> 1) ^ (crc & 1 ? 0xEDB88320 : 0);
    }
  }
  return (crc ^ 0xFFFFFFFF) >>> 0;
}

function validateSlug(slug) {
  if (!slug || !/^[a-zA-Z0-9][a-zA-Z0-9_-]*$/.test(slug)) {
    console.error(`Error: invalid slug "${slug}". Only alphanumeric characters, hyphens, and underscores are allowed.`);
    process.exit(1);
  }
}

function validatePath(p) {
  const dangerous = /[;|&`$(){}[\]!#~<>]/;
  if (dangerous.test(p)) {
    console.error(`Error: invalid path "${p}". Path contains disallowed characters.`);
    process.exit(1);
  }
}

async function installAgentar({ slug, mode, apiBaseUrl, agentName, apiKey }) {
  validateSlug(slug);
  const downloadUrl = `${apiBaseUrl}/api/v1/agentar/download?slug=${encodeURIComponent(slug)}`;
  const tmpDir = mkdtemp("agentar-");
  const zipPath = path.join(tmpDir, `${slug}.zip`);

  try {
    console.log(`  Downloading ${slug} ...`);
    await httpDownload(downloadUrl, zipPath);
  } catch (err) {
    rmrf(tmpDir);
    console.error(`Error: failed to download agentar "${slug}": ${err.message}`);
    process.exit(1);
  }

  const extractDir = path.join(tmpDir, "extracted");
  mkdirp(extractDir);
  try {
    extractZip(zipPath, extractDir);
  } catch {
    rmrf(tmpDir);
    console.error(`Error: failed to extract zip for "${slug}"`);
    process.exit(1);
  }

  const contentDir = resolveContentDir(extractDir);
  if (!fs.existsSync(path.join(contentDir, "SOUL.md"))) {
    rmrf(tmpDir);
    console.error(`Error: invalid agentar "${slug}": missing SOUL.md`);
    process.exit(1);
  }

  let targetWorkspace;
  if (mode === "overwrite") {
    const backup = backupDirectory(MAIN_WORKSPACE, `before-install-${slug}`);
    if (backup) console.log(`  Backed up main workspace to: ${backup}`);
    extractWorkspaceFiles(contentDir, MAIN_WORKSPACE);
    mergeSkills(path.join(contentDir, "skills"), path.join(MAIN_WORKSPACE, "skills"));
    targetWorkspace = MAIN_WORKSPACE;
  } else {
    const name = agentName || slug.replace(/[^a-zA-Z0-9_-]/g, "-");
    const workspaceDir = path.join(WORKSPACES_DIR, name);
    mkdirp(workspaceDir);

    const openclawBin = findOpenclawBin();
    if (openclawBin) {
      const result = getSpawnSync()(openclawBin, [
        "agents", "add", name, "--workspace", workspaceDir, "--non-interactive",
      ], { encoding: "utf-8", stdio: "pipe", shell: true });
      if (result.status !== 0 && !(result.stderr || "").includes("already exists")) {
        rmrf(tmpDir);
        console.error(`Error: failed to create agent "${name}": ${result.stderr || result.error?.message || "unknown error"}`);
        process.exit(1);
      }
    } else {
      console.log("  Warning: openclaw CLI not found, skipping agent registration");
    }

    extractWorkspaceFiles(contentDir, workspaceDir);
    mergeSkills(path.join(contentDir, "skills"), path.join(workspaceDir, "skills"));
    targetWorkspace = workspaceDir;
  }

  if (apiKey) writeCredentials(targetWorkspace, apiKey);
  rmrf(tmpDir);
  return targetWorkspace;
}

// ─── Client detection ────────────────────────────────────────────────────────

function detectClient() {
  if (process.env.OPENCLAW_HOME || process.env.OPENCLAW_SESSION) return "openclaw";
  if (process.env.CLAUDE_CODE || process.env.CLAUDE_DEV) return "claude-code";
  if (fs.existsSync(OPENCLAW_HOME)) return "openclaw";
  return "unknown";
}

// ─── Agent discovery ─────────────────────────────────────────────────────────

function discoverAgents() {
  const openclawBin = findOpenclawBin();
  if (openclawBin) {
    try {
      const result = getSpawnSync()(openclawBin, ["agents", "list", "--json"], {
        encoding: "utf-8", stdio: "pipe", timeout: 10000, shell: true,
      });
      if (result.status === 0) {
        const parsed = JSON.parse(result.stdout);
        const rawList = Array.isArray(parsed) ? parsed : (parsed.agents ?? []);
        const agents = rawList.map((e) => ({
          id: String(e.id ?? ""),
          name: e.name ?? e.identityName,
          workspace: String(e.workspace ?? ""),
          isDefault: Boolean(e.isDefault),
        }));
        if (agents.length > 0) return agents;
      }
    } catch { /* fallback below */ }
  }

  const agents = [];
  if (fs.existsSync(MAIN_WORKSPACE)) {
    agents.push({ id: "main", workspace: MAIN_WORKSPACE, isDefault: true });
  }
  if (fs.existsSync(WORKSPACES_DIR)) {
    for (const name of fs.readdirSync(WORKSPACES_DIR).sort()) {
      const d = path.join(WORKSPACES_DIR, name);
      if (fs.statSync(d).isDirectory() && fs.existsSync(path.join(d, "SOUL.md"))) {
        agents.push({ id: name, workspace: d, isDefault: false });
      }
    }
  }
  if (agents.length === 0) {
    agents.push({ id: "main", workspace: MAIN_WORKSPACE, isDefault: true });
  }
  return agents;
}

// ─── Export logic ────────────────────────────────────────────────────────────

function collectExportFiles(workspaceDir, includeMemory) {
  const tmp = mkdtemp("agentar-export-");
  const files = [];
  const allSkipped = [];

  for (const entry of readdirEntries(workspaceDir)) {
    if (entry.isDirectory() && EXPORT_SKIP_DIRS.includes(entry.name)) continue;
    if (entry.name === "skills" && entry.isDirectory()) continue;
    if (SKIP_FILES.includes(entry.name)) continue;
    if (entry.name === "MEMORY.md" && !includeMemory) continue;
    if (entry.name.startsWith(".")) continue;
    const src = path.join(workspaceDir, entry.name);
    const dest = path.join(tmp, entry.name);
    if (entry.isDirectory()) {
      const skipped = [];
      cpSyncFiltered(src, dest, skipped);
      for (const s of skipped) allSkipped.push(`${entry.name}/${s}`);
    } else {
      if (isSensitiveFile(entry.name)) { allSkipped.push(entry.name); continue; }
      copyFile(src, dest);
    }
    files.push(entry.name);
  }

  const skillsDir = path.join(workspaceDir, "skills");
  if (fs.existsSync(skillsDir)) {
    const skipped = [];
    cpSyncFiltered(skillsDir, path.join(tmp, "skills"), skipped);
    for (const s of skipped) allSkipped.push(`skills/${s}`);
    files.push("skills");
  }

  if (allSkipped.length > 0) {
    console.log(`        filtered sensitive files: ${allSkipped.join(", ")}`);
  }
  return { tmpDir: tmp, files };
}

function buildMeta() {
  return {
    exported_at: new Date().toISOString(),
    cli_version: CLI_VERSION,
    client: detectClient(),
  };
}

function exportAgentar({ agentId, outputPath, includeMemory = false }) {
  if (outputPath) validatePath(outputPath);
  const agents = discoverAgents();
  const agent = agents.find((a) => a.id === agentId);
  if (!agent) {
    const available = agents.map((a) => a.id).join(", ");
    console.error(`Error: agent "${agentId}" not found. Available: ${available}`);
    process.exit(1);
  }

  const workspaceDir = agent.workspace;
  if (!fs.existsSync(workspaceDir)) {
    console.error(`Error: workspace does not exist: ${workspaceDir}`);
    process.exit(1);
  }
  if (!fs.existsSync(path.join(workspaceDir, "SOUL.md"))) {
    console.error(`Error: invalid workspace: missing SOUL.md in ${workspaceDir}`);
    process.exit(1);
  }

  console.log("  [1/3] Validating workspace ...");
  console.log(`        workspace: ${workspaceDir}`);

  console.log("  [2/3] Collecting files ...");
  const { tmpDir, files } = collectExportFiles(workspaceDir, includeMemory);

  const skillsPath = path.join(tmpDir, "skills");
  const skillCount = fs.existsSync(skillsPath)
    ? readdirEntries(skillsPath).filter((e) => e.isDirectory()).length
    : 0;
  const nonSkill = files.filter((f) => f !== "skills");
  let desc = nonSkill.join(", ");
  if (skillCount > 0) desc += `, skills/ (${skillCount} skills)`;
  console.log(`        files: ${desc}`);

  const meta = buildMeta();
  fs.writeFileSync(path.join(tmpDir, ".agentar-meta.json"), JSON.stringify(meta, null, 2));

  console.log("  [3/3] Creating ZIP package ...");
  const exportsDir = path.join(HOME, "agentar-exports");
  mkdirp(exportsDir);
  const resolved = outputPath ? path.resolve(outputPath) : path.join(exportsDir, `${agentId}.zip`);
  console.log(`        output: ${resolved}`);

  try {
    createZip(tmpDir, resolved);
  } catch (err) {
    rmrf(tmpDir);
    console.error(`Error: failed to create ZIP: ${err.message}`);
    process.exit(1);
  }

  rmrf(tmpDir);
  return { agent: agentId, workspace: workspaceDir, output: resolved, files, includeMemory, meta };
}

// ─── CLI commands ────────────────────────────────────────────────────────────

async function cmdSearch(apiBaseUrl, args) {
  const query = args.join(" ");
  if (!query) { console.error("Error: search query required."); process.exit(1); }
  const limit = 20;
  const url = `${apiBaseUrl}/api/v1/agentar/search?q=${encodeURIComponent(query)}&limit=${limit}`;

  let data;
  try { data = await httpGetJson(url); }
  catch (err) { console.error(`Error: search failed: ${err.message}`); process.exit(1); }

  const results = data.results || [];
  if (results.length === 0) { console.log("No agentars found."); return; }

  console.log('Use "agentar install <slug>" to install.\n');
  for (const r of results) {
    console.log(`  ${r.slug ?? "?"}  ${r.displayName ?? ""}`);
    if (r.summary) console.log(`    ${r.summary}`);
    if (r.version) console.log(`    version: ${r.version}`);
  }
}

async function cmdList(apiBaseUrl) {
  const url = `${apiBaseUrl}/api/v1/agentar/index`;

  let data;
  try { data = await httpGetJson(url); }
  catch (err) { console.error(`Error: list failed: ${err.message}`); process.exit(1); }

  const agentars = data.agentars || [];
  if (agentars.length === 0) { console.log("No agentars available."); return; }

  console.log('Use "agentar install <slug>" to install.\n');
  for (const a of agentars) {
    console.log(`  ${a.slug ?? "?"}  ${a.name ?? ""}`);
    if (a.description) {
      const d = a.description.length > 80 ? a.description.slice(0, 77) + "..." : a.description;
      console.log(`    ${d}`);
    }
    if (a.version) console.log(`    version: ${a.version}`);
  }
}

async function cmdInstall(apiBaseUrl, opts) {
  const slug = opts.slug;
  if (!slug) { console.error("Error: slug required."); process.exit(1); }

  let mode;
  if (opts.overwrite) {
    mode = "overwrite";
  } else if (opts.name) {
    mode = "new";
  } else {
    const choice = await prompt(
      `Install agentar "${slug}":\n  [1] Overwrite main agent (~/.openclaw/workspace)\n  [2] Create a new agent\nChoice (1/2): `,
    );
    mode = choice === "1" ? "overwrite" : "new";
    if (mode === "new" && !opts.name) {
      const name = await prompt(`Agent name (default: ${slug}): `);
      opts.name = name || slug;
    }
  }

  console.log(`Installing agentar "${slug}" (mode: ${mode}) ...`);
  const workspace = await installAgentar({
    slug, mode, apiBaseUrl,
    agentName: opts.name,
    apiKey: opts.apiKey,
  });

  console.log("\nInstall complete.");
  console.log(`  agentar:   ${slug}`);
  console.log(`  mode:      ${mode}`);
  console.log(`  workspace: ${workspace}`);
  if (opts.apiKey) console.log(`  credentials: ${workspace}/skills/.credentials`);
  if (mode === "new") {
    const agent = opts.name || slug;
    console.log(`\nUse: openclaw agent --agent ${agent} --message "hello" --local`);
  }
}

async function cmdExport(opts) {
  let agentId = opts.agent;

  if (!agentId) {
    const agents = discoverAgents();
    console.log("\nAvailable agents:\n");
    agents.forEach((a, i) => {
      const defTag = a.isDefault ? "  [default]" : "";
      const exists = fs.existsSync(a.workspace);
      const status = exists ? "" : "  (not found)";
      console.log(`  [${i + 1}] ${a.id} (${a.workspace})${defTag}${status}`);
    });
    const choice = await prompt("\nSelect agent (default: 1): ");
    const idx = choice ? parseInt(choice, 10) - 1 : 0;
    if (idx < 0 || idx >= agents.length) { console.error("Error: invalid selection."); process.exit(1); }
    agentId = agents[idx].id;
  }

  console.log(`\nExporting agent "${agentId}" ...\n`);
  const result = exportAgentar({
    agentId,
    outputPath: opts.output,
    includeMemory: opts.includeMemory,
  });

  console.log("\n  Export complete.");
  console.log(`    agent:     ${result.agent}`);
  console.log(`    workspace: ${result.workspace}`);
  console.log(`    output:    ${result.output}`);
  if (result.files.length > 0) {
    const nonSkill = result.files.filter((f) => f !== "skills");
    let line = nonSkill.join(", ");
    if (result.files.includes("skills")) line += ", skills/";
    console.log(`    files:     ${line}`);
  }
  if (result.includeMemory) console.log("    memory:    included");
  console.log(`    client:    ${result.meta.client}`);
  console.log();
}

async function cmdRollback(flags) {
  const backupsDir = path.join(cliHome(), "backups");
  if (!fs.existsSync(backupsDir)) {
    console.log("No backups found.");
    return;
  }

  const entries = readdirEntries(backupsDir)
    .filter((e) => e.isDirectory() && e.name.startsWith("workspace."))
    .map((e) => e.name)
    .sort()
    .reverse();

  if (entries.length === 0) {
    console.log("No backups found.");
    return;
  }

  function parseBackupName(name) {
    const rest = name.replace("workspace.", "");
    const dotIdx = rest.indexOf(".", 0);
    if (dotIdx === -1) return { ts: rest, reason: "" };
    const ts = rest.slice(0, 19);
    const reason = rest.slice(20);
    return { ts, reason };
  }

  let selected;
  if (flags.latest) {
    selected = entries[0];
  } else {
    console.log("\nAvailable backups:\n");
    entries.forEach((name, i) => {
      const { ts, reason } = parseBackupName(name);
      const label = i === 0 ? "  (latest)" : "";
      const reasonTag = reason ? `  ${reason}` : "";
      console.log(`  [${i + 1}] ${ts}${reasonTag}${label}`);
    });
    const choice = await prompt(`\nSelect backup to restore (default: 1): `);
    const idx = choice ? parseInt(choice, 10) - 1 : 0;
    if (idx < 0 || idx >= entries.length) {
      console.error("Error: invalid selection.");
      process.exit(1);
    }
    selected = entries[idx];
  }

  const backupPath = path.join(backupsDir, selected);
  if (!fs.existsSync(path.join(backupPath, "SOUL.md"))) {
    console.error(`Error: backup "${selected}" appears invalid (missing SOUL.md).`);
    process.exit(1);
  }

  console.log(`\nRestoring backup: ${selected}`);

  const safetyBackup = backupDirectory(MAIN_WORKSPACE, "before-rollback");
  if (safetyBackup) {
    console.log(`  Safety backup of current workspace: ${safetyBackup}`);
  }

  rmrf(MAIN_WORKSPACE);
  mkdirp(MAIN_WORKSPACE);
  cpSync(backupPath, MAIN_WORKSPACE);

  console.log(`  Restored to: ${MAIN_WORKSPACE}`);
  console.log("\nRollback complete.");
}

// ─── Argument parsing ────────────────────────────────────────────────────────

function parseArgs(argv) {
  const args = argv.slice(2);
  let apiBaseUrl = null;
  const positional = [];
  const flags = {};

  let i = 0;
  while (i < args.length) {
    const arg = args[i];
    if (arg === "--api-base-url" && i + 1 < args.length) {
      apiBaseUrl = args[++i]; i++; continue;
    }
    if (arg === "--overwrite") { flags.overwrite = true; i++; continue; }
    if (arg === "--include-memory") { flags.includeMemory = true; i++; continue; }
    if (arg === "--name" && i + 1 < args.length) { flags.name = args[++i]; i++; continue; }
    if (arg === "--agent" && i + 1 < args.length) { flags.agent = args[++i]; i++; continue; }
    if (arg === "--api-key" && i + 1 < args.length) { flags.apiKey = args[++i]; i++; continue; }
    if (arg === "-o" || arg === "--output") {
      if (i + 1 < args.length) { flags.output = args[++i]; }
      i++; continue;
    }
    if (arg === "--latest") { flags.latest = true; i++; continue; }
    if (arg === "-l" || arg === "--limit") {
      if (i + 1 < args.length) { flags.limit = parseInt(args[++i], 10); }
      i++; continue;
    }
    if (arg === "-h" || arg === "--help") { flags.help = true; i++; continue; }
    positional.push(arg);
    i++;
  }

  const command = positional[0] || null;
  const rest = positional.slice(1);
  return { command, rest, flags, apiBaseUrl };
}

function printHelp() {
  console.log(`agentar-cli ${CLI_VERSION} — Search, list, install, and export agentars.

Usage: agentar <command> [options]

Commands:
  search <query>           Search for agentars
  list                     List all available agentars
  install <slug>           Install an agentar
  export                   Export an agent as agentar ZIP
  rollback                 Restore a workspace from backup
  version                  Show CLI version

Install options:
  --overwrite              Overwrite main agent workspace
  --name <name>            Create a new agent with this name
  --api-key <key>          API key to save into skills/.credentials

Export options:
  --agent <id>             Agent ID to export (interactive if omitted)
  -o, --output <path>      Output ZIP file path (default: ~/agentar-exports/)
  --include-memory         Include MEMORY.md in export (default: false)

Rollback options:
  --latest                 Restore the most recent backup without prompting

Global options:
  --api-base-url <url>     Backend API base URL
                           (env: AGENTAR_API_BASE_URL, default: ${DEFAULT_API_BASE_URL})
  -h, --help               Show this help message
`);
}

// ─── Main ────────────────────────────────────────────────────────────────────

async function main() {
  const { command, rest, flags, apiBaseUrl: cliApiBaseUrl } = parseArgs(process.argv);

  if (flags.help || !command) { printHelp(); process.exit(0); }

  const apiBaseUrl = getApiBaseUrl(cliApiBaseUrl);

  switch (command) {
    case "search":
      await cmdSearch(apiBaseUrl, rest);
      break;
    case "list":
      await cmdList(apiBaseUrl);
      break;
    case "install":
      await cmdInstall(apiBaseUrl, { slug: rest[0], ...flags });
      break;
    case "export":
      await cmdExport(flags);
      break;
    case "rollback":
      await cmdRollback(flags);
      break;
    case "version":
      console.log(`agentar-cli ${CLI_VERSION}`);
      break;
    default:
      console.error(`Error: unknown command "${command}"`);
      printHelp();
      process.exit(1);
  }
}

main().catch((err) => {
  console.error(`Error: ${err.message}`);
  process.exit(1);
});
