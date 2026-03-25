// License verification module.
// File reads are delegated to state-io.mjs.
// This module only handles network re-verification logic.
// Only sends { key, device_id } to the vendor API — no user data.

import { readJsonSafe, atomicWriteJson, existsSync } from "./state-io.mjs";

const VERIFY_URL = "https://openclaw-api.apptah.com/api/verify";
const VERIFY_INTERVAL = 604_800_000;  // 7 days ms
const GRACE_TOTAL = 864_000_000;      // 10 days ms

/**
 * Check license validity from local state file.
 * Triggers background re-verification if stale.
 * @param {string} licensePath - Path to license.json
 * @param {{ error: Function }} logger
 * @returns {boolean}
 */
export function checkLicense(licensePath, logger) {
  if (!existsSync(licensePath)) {
    logger.error("License not found. Purchase at https://openclaw-memory.apptah.com");
    return false;
  }
  const license = readJsonSafe(licensePath);
  if (!license) {
    logger.error("License file is corrupt.");
    return false;
  }
  if (license.revoked) {
    logger.error("License has been revoked.");
    return false;
  }
  const lastVerified = license.last_verified ? new Date(license.last_verified).getTime() : 0;
  if (lastVerified > 0 && (Date.now() - lastVerified) > GRACE_TOTAL) {
    logger.error("License expired. Please connect to the internet to re-verify.");
    return false;
  }
  if (lastVerified === 0 || (Date.now() - lastVerified) > VERIFY_INTERVAL) {
    reverifyInBackground(license, licensePath);
  }
  return true;
}

function reverifyInBackground(license, licensePath) {
  (async () => {
    try {
      const controller = new AbortController();
      const timer = setTimeout(() => controller.abort(), 5000);
      const res = await fetch(VERIFY_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ key: license.key, device_id: license.device_id }),
        signal: controller.signal,
      });
      clearTimeout(timer);
      if (!res.ok) return;
      const data = await res.json();
      if (data.valid) {
        license.last_verified = new Date().toISOString();
        atomicWriteJson(licensePath, license);
      } else if (data.reason === "revoked") {
        license.revoked = true;
        atomicWriteJson(licensePath, license);
      }
    } catch {}
  })();
}
