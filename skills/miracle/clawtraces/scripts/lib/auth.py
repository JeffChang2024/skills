"""Authentication flow for ClawTraces: phone + SMS verification code → API key."""

import json
import os
import sys
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

ENV_FILE_PATH = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
KEY_ENV_VAR = "CLAWTRACES_SECRET_KEY"
SERVER_URL_ENV_VAR = "CLAWTRACES_SERVER_URL"
DEFAULT_SERVER_URL = "https://api.clawd.how"


def _load_env_file() -> dict[str, str]:
    """Load key=value pairs from the skill .env file."""
    env = {}
    if os.path.isfile(ENV_FILE_PATH):
        with open(ENV_FILE_PATH, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, value = line.split("=", 1)
                    env[key.strip()] = value.strip().strip('"').strip("'")
    return env


def _save_to_env_file(key: str, value: str):
    """Save or update a key=value pair in the .env file."""
    lines = []
    found = False

    if os.path.isfile(ENV_FILE_PATH):
        with open(ENV_FILE_PATH, "r") as f:
            for line in f:
                if line.strip().startswith(f"{key}="):
                    lines.append(f"{key}={value}\n")
                    found = True
                else:
                    lines.append(line)

    if not found:
        lines.append(f"{key}={value}\n")

    os.makedirs(os.path.dirname(ENV_FILE_PATH), exist_ok=True)
    with open(ENV_FILE_PATH, "w") as f:
        f.writelines(lines)


def _remove_from_env_file(key: str):
    """Remove a key from the .env file."""
    if not os.path.isfile(ENV_FILE_PATH):
        return
    lines = []
    with open(ENV_FILE_PATH, "r") as f:
        for line in f:
            if not line.strip().startswith(f"{key}="):
                lines.append(line)
    with open(ENV_FILE_PATH, "w") as f:
        f.writelines(lines)


class ConfigError(Exception):
    """Raised when required configuration is missing."""
    pass


def get_server_url() -> str:
    """Get server URL from env var, .env file, or default.

    Falls back to DEFAULT_SERVER_URL if not explicitly configured.
    """
    url = os.environ.get(SERVER_URL_ENV_VAR)
    if url:
        return url.rstrip("/")
    dotenv = _load_env_file()
    url = dotenv.get(SERVER_URL_ENV_VAR, "")
    if url:
        return url.rstrip("/")
    return DEFAULT_SERVER_URL


def get_stored_key() -> str | None:
    """Get API key from env var or .env file. Returns None if not found."""
    key = os.environ.get(KEY_ENV_VAR)
    if key:
        return key
    dotenv = _load_env_file()
    return dotenv.get(KEY_ENV_VAR)


def clear_stored_key():
    """Remove stored API key (called on 401)."""
    _remove_from_env_file(KEY_ENV_VAR)


def save_key(key: str):
    """Save API key to .env file."""
    _save_to_env_file(KEY_ENV_VAR, key)


def _api_call(server_url: str, path: str, body: dict | None = None,
              method: str = "POST", secret_key: str | None = None) -> dict:
    """Make an API call to the server. Returns parsed JSON response."""
    url = f"{server_url}{path}"
    headers: dict[str, str] = {
        "Content-Type": "application/json",
        "User-Agent": "ClawTraces/1.0",
        "X-Client-Id": "clawtraces-skill",
    }
    if secret_key:
        headers["X-Secret-Key"] = secret_key

    data = json.dumps(body).encode("utf-8") if body else None
    req = Request(url, data=data, headers=headers, method=method)

    try:
        with urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        try:
            return json.loads(error_body)
        except (json.JSONDecodeError, ValueError):
            return {"error": f"HTTP {e.code}", "detail": error_body}
    except URLError as e:
        return {"error": f"Connection failed: {e.reason}"}


def _normalize_phone(phone: str) -> str:
    """Normalize phone number to +86XXXXXXXXXXX format.

    Handles common input variants:
      13800008888      → +8613800008888
      +8613800008888   → +8613800008888
      86 138 0000 8888 → +8613800008888
      +86-138-0000-8888 → +8613800008888
    """
    import re
    # Strip whitespace, dashes, dots, parentheses
    cleaned = re.sub(r"[\s\-\.\(\)]+", "", phone.strip())

    # Remove leading + for uniform processing
    if cleaned.startswith("+"):
        cleaned = cleaned[1:]

    # Remove leading 86 country code if present
    if cleaned.startswith("86") and len(cleaned) == 13:
        cleaned = cleaned[2:]

    # Validate: must be 11 digits starting with 1
    if not re.match(r"^1\d{10}$", cleaned):
        raise ValueError(f"Invalid phone number: {phone}. Expected 11-digit Chinese mobile number.")

    return f"+86{cleaned}"


def send_code(server_url: str, phone: str) -> dict:
    """Request SMS verification code. Normalizes phone number before sending."""
    try:
        phone = _normalize_phone(phone)
    except ValueError as e:
        return {"error": str(e)}
    return _api_call(server_url, "/auth/send-code", {"phone": phone})


def verify_code(server_url: str, phone: str, code: str) -> dict:
    """Verify SMS code and get API key. Normalizes phone number before sending."""
    try:
        phone = _normalize_phone(phone)
    except ValueError as e:
        return {"error": str(e)}
    return _api_call(server_url, "/auth/verify", {"phone": phone, "code": code})


def check_key_valid(server_url: str, key: str) -> bool:
    """Check if a stored key is still valid by calling /count."""
    result = _api_call(server_url, "/count", method="GET", secret_key=key)
    return "error" not in result


def handle_401():
    """Handle 401 response: clear key and notify."""
    clear_stored_key()
    print("API key is invalid or expired. Please re-authenticate.", file=sys.stderr)


def main():
    """Check authentication status and print result as JSON."""
    key = get_stored_key()
    if not key:
        result = {"authenticated": False, "reason": "no_key"}
        print(json.dumps(result, indent=2))
        return

    server_url = get_server_url()
    valid = check_key_valid(server_url, key)
    if valid:
        result = {"authenticated": True, "key_prefix": key[:12] + "..."}
    else:
        clear_stored_key()
        result = {"authenticated": False, "reason": "key_invalid"}
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
