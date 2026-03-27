import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const TOOL_NAME = "q-wms-flow";
const PLUGIN_VERSION = readPluginVersion();
const VERSION_CHECK_CACHE = new Map();
const AUTH_STATE_CACHE = new Map();
const INTERACTION_STATE_CACHE = new Map();
const FAILURE_GUARD_CACHE = new Map();
const AUTH_STATE_FILE =
  process.env.QWMS_AUTH_STATE_FILE ||
  path.resolve(__dirname, ".state/q-wms-auth-state.json");
const FAILURE_GUARD_WINDOW_MS = 90 * 1000;
const FAILURE_GUARD_THRESHOLD = 2;
const FAILURE_GUARD_COOLDOWN_MS = 60 * 1000;
const SCENE_ALIASES = Object.freeze({
  "wms.owner.query": "wms.owner.options",
  "wms.warehouse.query": "wms.warehouse.options",
  "wms.order.status.query": "wms.order.query",
  "wms.task.status.query": "wms.task.query",
  "wms.ios.query": "wms.ios.new.query",
  "wms.ios.report.query": "wms.ios.new.query",
});

// 读取运行时配置（打包时注入）
let RUNTIME_CONFIG = null;
try {
  const configPath = path.resolve(__dirname, "config.runtime.json");
  if (fs.existsSync(configPath)) {
    RUNTIME_CONFIG = JSON.parse(fs.readFileSync(configPath, "utf-8"));
  }
} catch {
  // 配置文件不存在或解析失败，使用默认值
}

// ─── 工具函数 ────────────────────────────────────────────────

function readPluginVersion() {
  try {
    const pkg = JSON.parse(
      fs.readFileSync(path.resolve(__dirname, "package.json"), "utf-8")
    );
    return typeof pkg?.version === "string" ? pkg.version : "0.0.0";
  } catch {
    return "0.0.0";
  }
}

function asString(value, fallback = "") {
  return typeof value === "string" ? value.trim() : fallback;
}

function asNumber(value, fallback) {
  if (typeof value === "number" && Number.isFinite(value)) return value;
  if (typeof value === "string" && value.trim()) {
    const n = Number(value);
    if (Number.isFinite(n)) return n;
  }
  return fallback;
}

function normalizeScene(scene) {
  const raw = asString(scene);
  return SCENE_ALIASES[raw] || raw;
}

function normalizeClawBaseUrl(value) {
  const raw = asString(value);
  if (!raw) return "";
  const normalized = raw.replace(/\/$/, "");
  return /\/q-claw(?:\/|$)/.test(normalized) ? normalized : `${normalized}/q-claw`;
}

function buildExternalSubject(identity) {
  const openId = asString(identity?.openId);
  if (!openId) return "";
  const tenantKey = asString(identity?.tenantKey) || "_";
  return `feishu:${tenantKey}:${openId}`;
}

function buildIdentityKey(identity) {
  const openId = asString(identity?.openId) || "_";
  // tenantKey 在部分回合可能缺失，使用 openId 作为稳定主键避免多轮丢授权。
  return `feishu:${openId}`;
}

function buildInteractionKey(identity, rawParams, ctx) {
  const identityKey = buildIdentityKey(identity);
  const sessionCandidates = [
    rawParams?.sessionKey,
    rawParams?.session_key,
    rawParams?.conversationId,
    rawParams?.conversation_id,
    rawParams?.threadId,
    rawParams?.thread_id,
    ctx?.sessionKey,
    ctx?.SessionKey,
    ctx?.conversationId,
    ctx?.conversation_id,
    ctx?.chatId,
    ctx?.chat_id,
    ctx?.channelContext?.sessionKey,
    ctx?.channelContext?.conversationId,
    ctx?.channelContext?.conversation_id,
  ];
  for (const candidate of sessionCandidates) {
    const key = asString(candidate);
    if (key) return `${identityKey}:${key}`;
  }
  return `${identityKey}:default`;
}

function parseTimeMillis(value) {
  if (typeof value === "number" && Number.isFinite(value)) return value;
  if (typeof value === "string") {
    const ts = Date.parse(value);
    if (Number.isFinite(ts)) return ts;
  }
  return 0;
}

function unwrapPayload(res) {
  if (!res || typeof res !== "object") return null;
  if (res.success === true && res.result && typeof res.result === "object") return res.result;
  if (res.result && typeof res.result === "object") return res.result;
  return res;
}

function normalizeAuthResult(raw) {
  const payload = unwrapPayload(raw);
  if (!payload || typeof payload !== "object") return null;
  const verificationUri = asString(payload.verificationUri || payload.verification_uri);
  const deviceCode = asString(payload.deviceCode || payload.device_code);
  const userCode = asString(payload.userCode || payload.user_code);
  if (!verificationUri || !deviceCode) return null;
  return {
    verificationUri,
    deviceCode,
    userCode,
    expiresIn: asNumber(payload.expiresIn || payload.expires_in, 600),
    intervalSeconds: asNumber(payload.intervalSeconds || payload.interval_seconds, 3),
  };
}

function extractTokens(payload) {
  if (!payload || typeof payload !== "object") return null;
  const accessToken = asString(
    payload.accessToken ||
      payload.access_token ||
      payload?.token?.accessToken ||
      payload?.token?.access_token ||
      payload?.grant?.accessToken ||
      payload?.grant?.access_token ||
      payload?.credentials?.accessToken ||
      payload?.credentials?.access_token
  );
  if (!accessToken) return null;
  return {
    accessToken,
    refreshCredential: asString(
      payload.refreshCredential ||
        payload.refresh_credential ||
        payload?.token?.refreshCredential ||
        payload?.token?.refresh_credential ||
        payload?.grant?.refreshCredential ||
        payload?.grant?.refresh_credential ||
        payload?.credentials?.refreshCredential ||
        payload?.credentials?.refresh_credential
    ),
    accessTokenExpiresAtMs: parseTimeMillis(
      payload.expiresAt ||
        payload.expires_at ||
        payload?.token?.expiresAt ||
        payload?.token?.expires_at ||
        payload?.grant?.expiresAt ||
        payload?.grant?.expires_at
    ),
  };
}

function loadAuthStateFromFile() {
  try {
    if (!fs.existsSync(AUTH_STATE_FILE)) return {};
    const raw = fs.readFileSync(AUTH_STATE_FILE, "utf-8");
    const parsed = JSON.parse(raw);
    return parsed && typeof parsed === "object" ? parsed : {};
  } catch {
    return {};
  }
}

function saveAuthStateToFile(data) {
  try {
    fs.mkdirSync(path.dirname(AUTH_STATE_FILE), { recursive: true });
    fs.writeFileSync(AUTH_STATE_FILE, JSON.stringify(data));
  } catch {
    // ignore persistence errors; in-memory cache still works
  }
}

function getCachedAuth(identityKey) {
  if (AUTH_STATE_CACHE.has(identityKey)) {
    return AUTH_STATE_CACHE.get(identityKey) || {};
  }
  const fileMap = loadAuthStateFromFile();
  const state = fileMap?.[identityKey] && typeof fileMap[identityKey] === "object" ? fileMap[identityKey] : {};
  AUTH_STATE_CACHE.set(identityKey, state);
  return state;
}

function setCachedAuth(identityKey, state) {
  AUTH_STATE_CACHE.set(identityKey, state);
  const fileMap = loadAuthStateFromFile();
  fileMap[identityKey] = state;
  saveAuthStateToFile(fileMap);
}

function parseOpenIdFromText(value) {
  const text = asString(value);
  if (!text) return "";
  if (text.startsWith("ou_")) return text;
  const matched = text.match(/(?:^|:)(ou_[A-Za-z0-9_-]+)/);
  return matched?.[1] || "";
}

function isAuthPendingError(payload, res) {
  const status = asString(payload?.status).toLowerCase();
  const error = asString(res?.error || payload?.error || payload?.code || payload?.message).toLowerCase();
  return (
    status === "pending" ||
    error === "authorization_pending" ||
    error.includes("authorization_pending")
  );
}

function isAuthRequestMissingError(payload, res) {
  const text = asString(
    res?.error || payload?.error || payload?.code || payload?.message || res?.message
  ).toLowerCase();
  return (
    text.includes("request not found") ||
    text.includes("authorization request not found") ||
    text.includes("device code not found") ||
    text.includes("invalid device code")
  );
}

async function postJson(url, body, timeoutMs = 8000) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      signal: controller.signal,
    });
    return await res.json().catch(() => null);
  } catch {
    return null;
  } finally {
    clearTimeout(timer);
  }
}

// ─── 渠道身份解析 ─────────────────────────────────────────────

function resolveIdentity(params, ctx) {
  const tenantKey =
    asString(params?.tenantKey) ||
    asString(params?.tenant_key) ||
    asString(ctx?.tenantKey) ||
    asString(ctx?.tenant_key) ||
    asString(ctx?.TenantKey) ||
    asString(ctx?.channelContext?.tenantKey) ||
    asString(ctx?.channelContext?.tenant_key) ||
    asString(ctx?.identity?.tenantKey) ||
    asString(ctx?.identity?.tenant_key) ||
    asString(ctx?.identity?.TenantKey) ||
    "";
  const openIdCandidates = [
    params?.openId,
    params?.open_id,
    ctx?.openId,
    ctx?.open_id,
    ctx?.senderOpenId,
    ctx?.sender_open_id,
    ctx?.senderId,
    ctx?.sender_id,
    ctx?.SenderId,
    ctx?.SenderOpenId,
    ctx?.channelContext?.openId,
    ctx?.channelContext?.open_id,
    ctx?.channelContext?.senderOpenId,
    ctx?.channelContext?.sender_open_id,
    ctx?.channelContext?.senderId,
    ctx?.channelContext?.sender_id,
    ctx?.channelContext?.userId,
    ctx?.channelContext?.user_id,
    ctx?.identity?.openId,
    ctx?.identity?.open_id,
    ctx?.identity?.senderOpenId,
    ctx?.identity?.sender_open_id,
    ctx?.identity?.userId,
    ctx?.identity?.user_id,
    ctx?.identity?.channelUserId,
    ctx?.identity?.externalUserId,
    ctx?.From,
    ctx?.from,
    ctx?.OriginatingTo,
    ctx?.originatingTo,
    ctx?.SessionKey,
    ctx?.sessionKey,
  ];
  let openId = "";
  for (const candidate of openIdCandidates) {
    openId = parseOpenIdFromText(candidate);
    if (openId) break;
  }
  return { tenantKey, openId };
}

// ─── 版本检查 ─────────────────────────────────────────────────

async function checkVersion(baseUrl, payload, timeoutMs, cacheTtlMs) {
  const cacheKey = JSON.stringify(payload);
  const cached = VERSION_CHECK_CACHE.get(cacheKey);
  if (cached && cached.expiresAt > Date.now()) return cached.result;

  const res = await postJson(
    `${baseUrl.replace(/\/$/, "")}/v1/runtime/version-check`,
    payload,
    timeoutMs
  );
  const result = res?.success ? res.result : null;
  if (result) {
    VERSION_CHECK_CACHE.set(cacheKey, {
      result,
      expiresAt: Date.now() + (cacheTtlMs || 60_000),
    });
  }
  return result;
}

// ─── 授权流程 ─────────────────────────────────────────────────

async function startAuth(baseUrl, identity, openclawInstanceId, timeoutMs = 12000) {
  const res = await postJson(
    `${baseUrl.replace(/\/$/, "")}/v1/auth/start`,
    {
      externalSubject: buildExternalSubject(identity),
      openclawInstanceId,
      requestedProducts: ["Q-WMS"],
      requestedScopes: ["identity.read", "wms.inventory.read", "tool.execute"],
    },
    timeoutMs
  );
  return normalizeAuthResult(res);
}

async function pollAuth(baseUrl, deviceCode, timeoutMs = 5000) {
  const res = await postJson(
    `${baseUrl.replace(/\/$/, "")}/v1/auth/poll`,
    { deviceCode },
    timeoutMs
  );
  return res;
}

async function refreshAuth(baseUrl, refreshCredential, timeoutMs = 5000) {
  const res = await postJson(
    `${baseUrl.replace(/\/$/, "")}/v1/auth/refresh`,
    { refreshCredential },
    timeoutMs
  );
  return res;
}

// ─── 工具执行转发 ─────────────────────────────────────────────

async function forwardToBackend(baseUrl, scene, params, identity, accessToken, timeoutMs, userInput = "") {
  const res = await postJson(
    `${baseUrl.replace(/\/$/, "")}/v1/tool/execute`,
    {
      scene,
      accessToken,
      userInput,
      context: {
        tenantKey: identity.tenantKey,
        openId: identity.openId,
        channel: "feishu",
      },
      params,
    },
    timeoutMs
  );
  return res;
}

// ─── 工具结果包装 ─────────────────────────────────────────────

function ok(scene, data, assistantReplyLines = []) {
  return {
    success: true,
    scene,
    code: "OK",
    assistantReplyLines,
    assistantReplyText: assistantReplyLines.join("\n"),
    data,
  };
}

function fail(scene, code, message, extra = {}) {
  return {
    success: false,
    scene,
    code,
    message,
    assistantReplyLines: [],
    ...extra,
  };
}

function formatAuthLinkLine(url) {
  const u = asString(url);
  return u ? `[点击登录授权](${u})` : "";
}

function buildAuthRequiredResult(scene, authResult, message = "当前操作需要先完成授权。") {
  const verificationUri = asString(authResult.verificationUri);
  const authLine = verificationUri
    ? "当前操作需先完成授权，请使用下方链接完成登录："
    : "当前操作需先完成授权，请发送“授权”重试。";
  const authLinkLine = formatAuthLinkLine(verificationUri);
  return fail(scene, "AUTH_REQUIRED", message, {
    authRequired: true,
    authorizationGuide: {
      verificationUri,
      userCode: authResult.userCode,
      deviceCode: authResult.deviceCode,
      expiresIn: authResult.expiresIn,
      intervalSeconds: authResult.intervalSeconds,
    },
    assistantReplyLines: [
      authLine,
      authLinkLine,
      "完成后直接继续发送你的查询即可。",
    ].filter(Boolean),
  });
}

function isAuthSceneCode(result) {
  const code = asString(result?.code).toUpperCase();
  return code === "AUTH_REQUIRED" || code === "AUTH_EXPIRED";
}

function hasAuthLink(result) {
  const verificationUri = asString(result?.authorizationGuide?.verificationUri);
  if (verificationUri) return true;
  const lines = Array.isArray(result?.assistantReplyLines) ? result.assistantReplyLines : [];
  return lines.some((line) => /https?:\/\/\S+/i.test(asString(line)));
}

function getInteractionState(identityKey) {
  return INTERACTION_STATE_CACHE.get(identityKey) || null;
}

function setInteractionState(identityKey, state) {
  INTERACTION_STATE_CACHE.set(identityKey, state);
}

function clearInteractionState(identityKey) {
  INTERACTION_STATE_CACHE.delete(identityKey);
}

function normalizeForSignature(value) {
  if (Array.isArray(value)) return value.map(normalizeForSignature);
  if (!value || typeof value !== "object") return value;
  const out = {};
  for (const key of Object.keys(value).sort()) {
    out[key] = normalizeForSignature(value[key]);
  }
  return out;
}

function buildRequestSignature(scene, params) {
  return JSON.stringify({
    scene: asString(scene),
    params: normalizeForSignature(params || {}),
  });
}

function getFailureGuard(identityKey) {
  return FAILURE_GUARD_CACHE.get(identityKey) || null;
}

function clearFailureGuard(identityKey) {
  FAILURE_GUARD_CACHE.delete(identityKey);
}

function trackFailureGuard(identityKey, requestSignature, scene, code, message) {
  const now = Date.now();
  const prev = getFailureGuard(identityKey);
  const isConsecutive = Boolean(
    prev &&
    prev.requestSignature === requestSignature &&
    prev.code === code &&
    now - prev.lastAtMs <= FAILURE_GUARD_WINDOW_MS
  );
  const count = isConsecutive ? prev.count + 1 : 1;
  const state = {
    requestSignature,
    scene,
    code,
    message: asString(message),
    count,
    lastAtMs: now,
    untilMs: count >= FAILURE_GUARD_THRESHOLD ? now + FAILURE_GUARD_COOLDOWN_MS : 0,
  };
  FAILURE_GUARD_CACHE.set(identityKey, state);
  return state;
}

function isGuardBlocked(identityKey, requestSignature) {
  const state = getFailureGuard(identityKey);
  if (!state) return null;
  if (state.requestSignature !== requestSignature) return null;
  if (state.untilMs <= Date.now()) return null;
  return state;
}

function buildGenericGuardReply() {
  return [
    "检测到同一请求连续失败，已暂停自动重试。",
    "请调整查询条件后重试；若仍失败，请联系管理员排查后端 scene。",
  ];
}

function inferInteractionContext(scene, result) {
  const data = result?.data;
  if (!data || typeof data !== "object") return null;
  const stage = asString(data.stage);
  if (!/^choose_/i.test(stage)) return null;

  const token = asString(stage.replace(/^choose_/i, ""));
  if (!token) return null;
  const paramKey = `${token.charAt(0).toLowerCase()}${token.slice(1)}Code`;
  return {
    scene,
    stage,
    token,
    paramKey,
  };
}

function resolveInteractionInput(scene, interactionKey, rawParams) {
  const state = getInteractionState(interactionKey);
  const params = { ...(rawParams?.params || {}) };
  if (!state || state.scene !== scene) {
    if (state && state.scene !== scene) {
      clearInteractionState(interactionKey);
    }
    return { params };
  }
  if (!state.paramKey || asString(params[state.paramKey])) {
    return { params };
  }
  const userInput = asString(rawParams?.userInput);
  if (!userInput) {
    return { params };
  }
  params[state.paramKey] = userInput;
  return { params };
}

function sanitizeResultData(result, state) {
  if (!Array.isArray(result?.assistantReplyLines) || result.assistantReplyLines.length === 0) {
    return result;
  }
  return { ...result, data: {}, assistantReplyLines: normalizeAssistantReplyLines(result.assistantReplyLines) };
}

function normalizeAssistantReplyLines(lines) {
  const src = Array.isArray(lines) ? lines.map((l) => asString(l)) : [];
  if (!src.length) return src;
  // Already markdown-like; keep as-is.
  if (src.some((l) => /^\s*\|.+\|\s*$/.test(l))) return src;

  const headerIdx = src.findIndex((line) =>
    /^序号\s+/.test(line) &&
    ((line.includes("选项") && line.includes("说明")) || (line.includes("编码") && line.includes("名称")))
  );
  if (headerIdx < 0) return src;

  const headerLine = src[headerIdx];
  const headers = (headerLine.includes("选项") && headerLine.includes("说明"))
    ? ["序号", "选项", "说明"]
    : ["序号", "编码", "名称"];

  const tableRows = [];
  let cursor = headerIdx + 1;
  for (; cursor < src.length; cursor++) {
    const line = asString(src[cursor]);
    if (!line) break;
    if (/^\d+\/\d+$/.test(line) || /^请回复/.test(line) || /^操作指引/.test(line) || /^- /.test(line)) break;
    const m = line.match(/^(\d+)\s+(\S+)\s+(.+)$/);
    if (!m) break;
    tableRows.push([m[1], m[2], m[3]]);
  }
  if (!tableRows.length) return src;

  const out = [];
  out.push(...src.slice(0, headerIdx));
  out.push(`| ${headers.join(" | ")} |`);
  out.push(`| ${headers.map(() => "---").join(" | ")} |`);
  for (const row of tableRows) {
    out.push(`| ${row.join(" | ")} |`);
  }
  out.push(...src.slice(cursor));
  return out;
}

// ─── 主工具逻辑 ───────────────────────────────────────────────

function createTool(api, ctx, toolName) {
  return {
    name: toolName,
    description:
      "Q-WMS 场景路由工具。通过 scene 参数指定业务场景，后端负责执行并返回结构化结果。" +
      "支持按用户语义路由到后端已注册的场景，具体能力以后端 scene 注册为准。",
    parameters: {
      type: "object",
      additionalProperties: false,
      required: ["scene"],
      properties: {
        scene: {
          type: "string",
          description:
            "业务场景标识，格式 {product}.{domain}.{action}。" +
            "示例格式：wms.{domain}.{action}（以服务端已注册 scene 为准）",
        },
        tenantKey: {
          type: "string",
          description: "飞书/钉钉渠道 tenantKey，优先从渠道上下文自动获取。",
        },
        openId: {
          type: "string",
          description: "飞书/钉钉渠道 openId，优先从渠道上下文自动获取。",
        },
        accessToken: {
          type: "string",
          description: "授权后的 access token，由授权流程自动填入。",
        },
        userInput: {
          type: "string",
          description: "用户原始消息，用于后端意图补充和多轮对话上下文。",
        },
        params: {
          type: "object",
          description: "场景参数，按 scene 不同传入不同字段。",
          additionalProperties: true,
        },
      },
    },

    async execute(_toolCallId, rawParams) {
      const cfg = api.pluginConfig || {};

      // 优先使用用户配置，否则使用运行时配置（打包时注入），最后使用默认值
      const baseUrl = normalizeClawBaseUrl(
        cfg.defaultAuthBaseUrl ||
        RUNTIME_CONFIG?.defaultAuthBaseUrl ||
        "http://qlink-portal-test.800best.com"
      );
      const openclawInstanceId = asString(
        cfg.openclawInstanceId ||
        RUNTIME_CONFIG?.openclawInstanceId ||
        "openclaw-q-wms-test"
      );
      const managedSkillId = asString(
        cfg.managedSkillId ||
        RUNTIME_CONFIG?.managedSkillId ||
        "q-wms-test"
      );

      const timeoutMs = asNumber(cfg.defaultTimeoutSeconds, 20) * 1000;
      const versionCheckTimeoutMs = asNumber(
        cfg.versionCheckTimeoutMs || RUNTIME_CONFIG?.versionCheckTimeoutMs,
        4000
      );
      const versionCheckCacheTtlMs = asNumber(
        cfg.versionCheckCacheTtlMs || RUNTIME_CONFIG?.versionCheckCacheTtlMs,
        60_000
      );

      const requestedScene = asString(rawParams?.scene);
      const scene = normalizeScene(requestedScene);
      if (!scene) {
        return fail("unknown", "SCENE_REQUIRED", "scene 参数必填。");
      }
      if (!baseUrl) {
        return fail(scene, "CONFIG_MISSING", "插件未配置 defaultAuthBaseUrl，请联系管理员。");
      }

      // 1. 版本检查
      const versionResult = await checkVersion(
        baseUrl,
        {
          pluginId: TOOL_NAME,
          pluginVersion: PLUGIN_VERSION,
          skillId: managedSkillId,
          skillInstalled: true,
        },
        versionCheckTimeoutMs,
        versionCheckCacheTtlMs
      );
      if (versionResult?.upgradeRequired) {
        return fail(scene, "UPGRADE_REQUIRED", versionResult.message || "请先升级插件。", {
          upgradeRequired: true,
          assistantReplyLines: versionResult.assistantReplyLines || [],
          upgradeGuide: versionResult.upgradeGuide || null,
        });
      }

      // 2. 解析身份
      const identity = resolveIdentity(rawParams, ctx);
      if (!identity.openId) {
        return fail(scene, "IDENTITY_MISSING", "无法获取渠道身份(openId)，请确认飞书/钉钉渠道配置正确。");
      }

      // 3. 检查 access token，没有则发起授权
      const authKey = buildIdentityKey(identity);
      const interactionKey = buildInteractionKey(identity, rawParams, ctx);
      const cachedAuth = getCachedAuth(authKey);
      // 优先使用插件缓存 token，避免模型携带的历史 accessToken 覆盖最新授权态。
      let accessToken =
        asString(cachedAuth.accessToken) ||
        asString(rawParams?.accessToken);
      // 优先轮询最新授权结果：用户完成授权后，必须先拿到新 token，避免继续使用旧 token。
      const deviceCode = asString(cachedAuth.deviceCode);
      const verificationUri = asString(cachedAuth.verificationUri);
      const expiresAtMs = asNumber(cachedAuth.expiresAtMs, 0);
      const notExpired = expiresAtMs > 0 && Date.now() < expiresAtMs;
      let authPending = false;
      if (deviceCode && notExpired) {
        const pollRes = await pollAuth(baseUrl, deviceCode, timeoutMs);
        const pollData = unwrapPayload(pollRes);
        const polledTokens = extractTokens(pollData);
        if (polledTokens?.accessToken) {
          accessToken = polledTokens.accessToken;
          setCachedAuth(authKey, {
            ...cachedAuth,
            ...polledTokens,
            deviceCode: "",
            userCode: "",
            verificationUri: "",
            expiresAtMs: 0,
          });
        } else {
          authPending = isAuthPendingError(pollData, pollRes);
          if (isAuthRequestMissingError(pollData, pollRes)) {
            setCachedAuth(authKey, {
              ...cachedAuth,
              deviceCode: "",
              userCode: "",
              verificationUri: "",
              expiresAtMs: 0,
            });
          }
        }
      }

      // 已进入授权流程且仍 pending 时，禁止继续复用旧 token，避免“选仓后再次过期”回环。
      if (authPending && verificationUri) {
        clearInteractionState(interactionKey);
        return buildAuthRequiredResult(scene, cachedAuth);
      }

      if (!accessToken) {
        const refreshCredential = asString(cachedAuth.refreshCredential);
        if (refreshCredential) {
          const refreshRes = await refreshAuth(baseUrl, refreshCredential, timeoutMs);
          const refreshedTokens = extractTokens(unwrapPayload(refreshRes));
          if (refreshedTokens?.accessToken) {
            accessToken = refreshedTokens.accessToken;
            setCachedAuth(authKey, {
              ...cachedAuth,
              ...refreshedTokens,
            });
          }
        }
      }

      if (!accessToken) {
        let authResult = await startAuth(baseUrl, identity, openclawInstanceId, Math.max(timeoutMs, 12000));
        if (!authResult) {
          authResult = await startAuth(baseUrl, identity, openclawInstanceId, Math.max(timeoutMs, 20000));
        }
        if (!authResult) {
          return fail(scene, "AUTH_START_FAILED", "授权发起失败，请稍后重试。");
        }
        setCachedAuth(authKey, {
          ...cachedAuth,
          accessToken: "",
          refreshCredential: "",
          accessTokenExpiresAtMs: 0,
          deviceCode: asString(authResult.deviceCode),
          userCode: asString(authResult.userCode),
          verificationUri: asString(authResult.verificationUri),
          expiresAtMs: Date.now() + asNumber(authResult.expiresIn, 600) * 1000,
        });
        clearInteractionState(interactionKey);
        return buildAuthRequiredResult(scene, authResult);
      }

      const interactionResolved = resolveInteractionInput(scene, interactionKey, rawParams);
      const effectiveParams = interactionResolved?.params || rawParams?.params || {};
      const requestSignature = buildRequestSignature(scene, effectiveParams);
      const blocked = isGuardBlocked(interactionKey, requestSignature);
      if (blocked) {
        clearInteractionState(interactionKey);
        return fail(scene, blocked.code || "RETRY_BLOCKED", blocked.message || "同一请求连续失败，请调整条件后重试。", {
          assistantReplyLines: buildGenericGuardReply(),
          loopGuard: {
            tripped: true,
            scene: blocked.scene,
            code: blocked.code,
            retryAfterMs: Math.max(0, blocked.untilMs - Date.now()),
          },
        });
      }

      // 4. 转发给后端执行
      let backendRes = await forwardToBackend(
        baseUrl,
        scene,
        effectiveParams,
        identity,
        accessToken,
        timeoutMs,
        asString(rawParams?.userInput)
      );

      if (!backendRes) {
        return fail(scene, "BACKEND_UNAVAILABLE", "后端服务暂时不可用，请稍后重试。");
      }

      // access token 过期，重新发起授权
      if (backendRes.error === "access_invalid" || backendRes.error === "access_required") {
        const refreshCredential = asString((getCachedAuth(authKey) || {}).refreshCredential);
        if (refreshCredential) {
          const refreshRes = await refreshAuth(baseUrl, refreshCredential, timeoutMs);
          const refreshedTokens = extractTokens(unwrapPayload(refreshRes));
          if (refreshedTokens?.accessToken) {
            setCachedAuth(authKey, {
              ...(getCachedAuth(authKey) || {}),
              ...refreshedTokens,
            });
            const retryRes = await forwardToBackend(
              baseUrl,
              scene,
              effectiveParams,
              identity,
              refreshedTokens.accessToken,
              timeoutMs,
              asString(rawParams?.userInput)
            );
            // 不管重试成功与否，统一走后面的 !backendRes?.success 判断
            backendRes = retryRes;
          }
        }

        if (!backendRes?.success) {
          let authResult = await startAuth(baseUrl, identity, openclawInstanceId, Math.max(timeoutMs, 12000));
          if (!authResult) {
            authResult = await startAuth(baseUrl, identity, openclawInstanceId, Math.max(timeoutMs, 20000));
          }
          if (!authResult) {
            return fail(scene, "AUTH_START_FAILED", "授权已过期，重新发起授权失败，请稍后重试。");
          }
          setCachedAuth(authKey, {
            ...(getCachedAuth(authKey) || {}),
            accessToken: "",
            refreshCredential: "",
            accessTokenExpiresAtMs: 0,
            deviceCode: asString(authResult.deviceCode),
            userCode: asString(authResult.userCode),
            verificationUri: asString(authResult.verificationUri),
            expiresAtMs: Date.now() + asNumber(authResult.expiresIn, 600) * 1000,
          });
          clearInteractionState(interactionKey);
          return fail(scene, "AUTH_EXPIRED", "授权已过期，请重新登录。", {
            authRequired: true,
            authorizationGuide: {
              verificationUri: authResult.verificationUri,
              userCode: authResult.userCode,
              deviceCode: authResult.deviceCode,
              expiresIn: authResult.expiresIn,
              intervalSeconds: authResult.intervalSeconds,
            },
            assistantReplyLines: [
              asString(authResult.verificationUri)
                ? "授权已过期，需要重新登录，请使用下方链接完成授权："
                : "授权已过期，需要重新登录，请发送“授权”重试。",
              formatAuthLinkLine(authResult.verificationUri),
              "完成后直接继续发送你的查询即可。",
            ].filter(Boolean),
          });
        }
      }

      // 5. 原样返回后端结果
      const finalResult = backendRes.result || backendRes;
      const finalCode = asString(finalResult?.code).toUpperCase();
      const hasAssistantReply = Array.isArray(finalResult?.assistantReplyLines) && finalResult.assistantReplyLines.length > 0;
      if (finalCode === "OK") {
        clearFailureGuard(interactionKey);
      } else if (!hasAssistantReply && !/^AUTH_/.test(finalCode)) {
        const guardState = trackFailureGuard(
          interactionKey,
          requestSignature,
          scene,
          finalCode,
          asString(finalResult?.message)
        );
        if (guardState.count >= FAILURE_GUARD_THRESHOLD) {
          clearInteractionState(interactionKey);
          return fail(scene, finalCode || "RETRY_BLOCKED", asString(finalResult?.message) || "同一请求连续失败，请调整条件后重试。", {
            assistantReplyLines: buildGenericGuardReply(),
            loopGuard: {
              tripped: true,
              scene: guardState.scene,
              code: guardState.code,
              count: guardState.count,
              retryAfterMs: Math.max(0, guardState.untilMs - Date.now()),
            },
          });
        }
      }

      if (isAuthSceneCode(finalResult) && !hasAuthLink(finalResult)) {
        let authResult = await startAuth(baseUrl, identity, openclawInstanceId, Math.max(timeoutMs, 12000));
        if (!authResult) {
          authResult = await startAuth(baseUrl, identity, openclawInstanceId, Math.max(timeoutMs, 20000));
        }
        if (authResult) {
          setCachedAuth(authKey, {
            ...(getCachedAuth(authKey) || {}),
            accessToken: "",
            refreshCredential: "",
            accessTokenExpiresAtMs: 0,
            deviceCode: asString(authResult.deviceCode),
            userCode: asString(authResult.userCode),
            verificationUri: asString(authResult.verificationUri),
            expiresAtMs: Date.now() + asNumber(authResult.expiresIn, 600) * 1000,
          });
          clearInteractionState(interactionKey);
          return fail(scene, "AUTH_EXPIRED", asString(finalResult?.message) || "授权已过期，请重新登录。", {
            authRequired: true,
            authorizationGuide: {
              verificationUri: authResult.verificationUri,
              userCode: authResult.userCode,
              deviceCode: authResult.deviceCode,
              expiresIn: authResult.expiresIn,
              intervalSeconds: authResult.intervalSeconds,
            },
            assistantReplyLines: [
              asString(authResult.verificationUri)
                ? "授权已过期，需要重新登录，请使用下方链接完成授权："
                : "授权已过期，需要重新登录，请发送“授权”重试。",
              formatAuthLinkLine(authResult.verificationUri),
              "完成后直接继续发送你的查询即可。",
            ].filter(Boolean),
          });
        }
        const cached = getCachedAuth(authKey) || {};
        const cachedUri = asString(cached.verificationUri);
        if (cachedUri) {
          clearInteractionState(interactionKey);
          return fail(scene, "AUTH_EXPIRED", asString(finalResult?.message) || "授权已过期，请重新登录。", {
            authRequired: true,
            authorizationGuide: {
              verificationUri: cachedUri,
              userCode: asString(cached.userCode),
              deviceCode: asString(cached.deviceCode),
              expiresIn: asNumber(cached.expiresIn, 600),
              intervalSeconds: asNumber(cached.intervalSeconds, 3),
            },
            assistantReplyLines: [
              "授权已过期，需要重新登录，请使用下方链接完成授权：",
              formatAuthLinkLine(cachedUri),
              "完成后直接继续发送你的查询即可。",
            ],
          });
        }
        clearInteractionState(interactionKey);
        return fail(scene, "AUTH_EXPIRED", asString(finalResult?.message) || "授权已过期，请重新登录。", {
          assistantReplyLines: [
            "授权已过期，需要先重新登录。",
            "请回复“授权”以获取最新授权链接。",
          ],
        });
      }
      const nextState = inferInteractionContext(scene, finalResult);
      if (nextState) {
        setInteractionState(interactionKey, nextState);
      } else if (asString(finalResult?.code).toUpperCase() === "OK") {
        clearInteractionState(interactionKey);
        clearFailureGuard(interactionKey);
      }
      const responseResult = sanitizeResultData(finalResult, nextState);
      console.log(`[q-wms-flow] scene=${scene} backendResult=${JSON.stringify(responseResult)}`);
      return responseResult;
    },
  };
}

// ─── 插件注册 ─────────────────────────────────────────────────

export default {
  id: RUNTIME_CONFIG?.pluginId || "q-wms-test",
  name: RUNTIME_CONFIG?.pluginName || "Q-WMS (Test)",
  description: "Q-WMS 场景路由插件，负责授权流程、版本检查和后端转发。",
  register(api) {
    api.registerTool((ctx) => createTool(api, ctx, TOOL_NAME));
  },
};
