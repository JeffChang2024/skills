---
slug: zke-trading
display_name: ZKE AI Master Trader (Official)
version: 1.0.7
tags: [crypto, trading, zke, aster, mcp]
attributes:
  requires_credentials: true
  env_vars: [ZKE_API_KEY, ZKE_SECRET_KEY]
---

# ZKE Exchange Trading Skill (Official)

**The Official OpenClaw (MCP) implementation for high-speed, conversational trading on ZKE.com.**

---

## 🔒 Security & Data Handling (Transparency Report)

* **Verified Local Code:** This package contains the full source code. All signing (HMAC-SHA256) happens locally.
* **Credential Storage:** To ensure persistent performance for AI agents, the included installer (`install_openclaw_plugin.sh`) creates a local configuration file at `~/.zke-trading/config.json`. 
* **Encryption Advisory:** API keys are stored in plaintext within your user home directory. We **strongly recommend** restricting filesystem permissions (`chmod 600 ~/.zke-trading/config.json`) and using API keys with **Withdrawals Disabled**.
* **IP Whitelisting:** ZKE API requires **IP Whitelisting**. Trading functions only execute if initiated from your authorized static IP.

---

## 🛠️ Configuration & Metadata

This skill recognizes both environment variables and local config files:
* `ZKE_API_KEY`: Your ZKE API Access Key.
* `ZKE_SECRET_KEY`: Your ZKE API Secret Key.

---

## ⚡️ Professional Installation (Automated)

We provide a Pro-grade installer to handle the complex environment required for high-frequency trading.

### Installation Steps:
1.  **Run the Local Installer:**
    ```bash
    bash install_openclaw_plugin.sh
    ```
2.  **What the script does:**
    * Creates a Python virtual environment (`.venv`).
    * Builds the OpenClaw TypeScript bridge.
    * **Configures Local Storage:** Prompts for your API keys and saves them to `~/.zke-trading/config.json`.
    * **Integrates with OpenClaw:** Automatically runs `openclaw plugins install` to register the tool.

---

## 🪄 Magic Prompts
* "What is the current market depth for **ASTER/USDT**?"
* "Place a limit sell order for 10 **ASTER** at 0.85."
* "Check my recent trade history on ZKE."

---

## 🔗 Official Resources
Website: https://zke.com
Interactive Guide: https://support.zke.com/skills/
GitHub Repository: https://github.com/ZKE-Exchange/zke-trading-sdk

Licensed under MIT-0. Developed by ZKE Exchange AI Division.