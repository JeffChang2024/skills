# q-wms-flow Plugin

`q-wms-flow` is a product-domain plugin for OpenClaw.

- Plugin id: `q-wms-flow`
- Tool name: `q-wms-flow`
- Current scenario: `inventory`
- Design goal: one plugin, multiple WMS scenarios (inventory first, then outbound/inbound/order flows).

## Why product-domain split (WMS vs ERP)

For your roadmap, use **separate plugins by product domain**:

- `q-wms-flow`: only WMS scenarios and permissions
- `q_erp_flow`: only ERP scenarios and permissions

This is better than a single mega plugin because:

- release isolation: WMS release does not risk ERP flows
- permission isolation: tool allowlist can be product-specific
- ownership isolation: different teams can maintain independently

If shared logic is needed (auth client, token cache, common formatter), extract a shared package later.

## 最简单安装（推荐）

终端用户不做任何操作，由网关管理员一次安装即可。

```bash
bash q-wms/plugin/q-wms-flow/scripts/install_q-wms-flow.sh
```

这个脚本会自动执行：

1. `plugins install`
2. `plugins enable`
3. `gateway restart`（自动重启）
4. 输出插件状态

## Install (local path)

```bash
openclaw plugins install ./q-wms/plugin/q-wms-flow
openclaw plugins enable q-wms-flow
openclaw plugins list
```

Then restart gateway.

## Tool schema (summary)

Use tool `q-wms-flow` with:

- `scenario`: must be `inventory`
- `tenantKey`, `openId`: channel identities
- `customerCode`: optional, default `YQN_UAT`
- `warehouseCode`, `skus`: optional, follow step-by-step flow
- `queryMode`: `normal` or `warehouse_all`
- `autoStartAuthorization`: default true

## Runtime dependency

This plugin currently executes python scripts from q-wms:

- `edi_inventory_entry.py`
- `openclaw_start_auth.py`

Script root resolution order:

1. plugin config `scriptRoot`
2. `<workspace>/skills/q-wms/scripts`
3. `<workspace>/q-wms/scripts`
4. `<plugin_root>/scripts`

For production rollout, recommend replacing script calls with direct QLINK API calls in plugin code.
