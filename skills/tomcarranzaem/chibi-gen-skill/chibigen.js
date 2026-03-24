#!/usr/bin/env node
import { readFileSync } from "fs";
import { homedir } from "os";
import { join } from "path";

// --- Argument parsing ---
const args = process.argv.slice(2);
let prompt = null;
let size = "square";
let token = null;
let refUuid = null;

for (let i = 0; i < args.length; i++) {
  if (args[i] === "--size" && args[i + 1]) {
    size = args[++i];
  } else if (args[i] === "--token" && args[i + 1]) {
    token = args[++i];
  } else if (args[i] === "--ref" && args[i + 1]) {
    refUuid = args[++i];
  } else if (!args[i].startsWith("--") && prompt === null) {
    prompt = args[i];
  }
}

if (!prompt) {
  prompt =
    "full body chibi character, big head small body proportions, adorable kawaii style, expressive large eyes, pastel color palette, clean line art, white background, high quality anime illustration";
}

// --- Token resolution ---
function readEnvFile(filePath) {
  try {
    const content = readFileSync(filePath, "utf8");
    const match = content.match(/NETA_TOKEN=(.+)/);
    return match ? match[1].trim() : null;
  } catch {
    return null;
  }
}

if (!token) {
  token = process.env.NETA_TOKEN || null;
}
if (!token) {
  token = readEnvFile(join(homedir(), ".openclaw", "workspace", ".env"));
}
if (!token) {
  token = readEnvFile(join(homedir(), "developer", "clawhouse", ".env"));
}

if (!token) {
  console.error(
    "Error: NETA_TOKEN not found. Provide via --token, NETA_TOKEN env var, ~/.openclaw/workspace/.env, or ~/developer/clawhouse/.env"
  );
  process.exit(1);
}

// --- Size mapping ---
const sizes = {
  square: { width: 1024, height: 1024 },
  portrait: { width: 832, height: 1216 },
  landscape: { width: 1216, height: 832 },
  tall: { width: 704, height: 1408 },
};

const { width, height } = sizes[size] ?? sizes.square;

// --- Headers ---
const headers = {
  "x-token": token,
  "x-platform": "nieta-app/web",
  "content-type": "application/json",
};

// --- Build request body ---
const body = {
  storyId: "DO_NOT_USE",
  jobType: "universal",
  rawPrompt: [{ type: "freetext", value: prompt, weight: 1 }],
  width,
  height,
  meta: { entrance: "PICTURE,CLI" },
  context_model_series: "8_image_edit",
};

if (refUuid) {
  body.inherit_params = {
    collection_uuid: refUuid,
    picture_uuid: refUuid,
  };
}

// --- Submit job ---
async function main() {
  const makeRes = await fetch(`${process.env.NETA_API_URL || 'https://api.talesofai.cn'}/v3/make_image`, {
    method: "POST",
    headers,
    body: JSON.stringify(body),
  });

  if (!makeRes.ok) {
    const text = await makeRes.text();
    console.error(`Error submitting job (${makeRes.status}): ${text}`);
    process.exit(1);
  }

  const makeData = await makeRes.json();
  const taskUuid =
    typeof makeData === "string" ? makeData : makeData.task_uuid;

  if (!taskUuid) {
    console.error("Error: no task_uuid in response:", JSON.stringify(makeData));
    process.exit(1);
  }

  // --- Poll for result ---
  const maxAttempts = 90;
  for (let attempt = 0; attempt < maxAttempts; attempt++) {
    await new Promise((r) => setTimeout(r, 2000));

    const pollRes = await fetch(
      `${process.env.NETA_API_URL || 'https://api.talesofai.cn'}/v1/artifact/task/${taskUuid}`,
      { headers }
    );

    if (!pollRes.ok) {
      const text = await pollRes.text();
      console.error(`Error polling task (${pollRes.status}): ${text}`);
      process.exit(1);
    }

    const pollData = await pollRes.json();
    const status = pollData.task_status;

    if (['PENDING', 'MODERATION'].includes(status)) { continue; }
  if (['FAILURE', 'TIMEOUT', 'DELETED', 'ILLEGAL_IMAGE'].includes(status)) {
    console.error('Error: generation failed with status ' + status + (pollData.err_msg ? ' — ' + pollData.err_msg : ''));
    process.exit(1);
  }

    // Done — extract image URL
    const url =
      pollData.artifacts?.[0]?.url ?? pollData.result_image_url ?? null;

    if (!url) {
      console.error("Error: no image URL in response:", JSON.stringify(pollData));
      process.exit(1);
    }

    console.log(url);
    process.exit(0);
  }

  console.error("Error: timed out waiting for image generation.");
  process.exit(1);
}

main().catch((err) => {
  console.error("Unexpected error:", err);
  process.exit(1);
});
