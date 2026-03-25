---
name: mova-invoice-ocr
description: Process any financial document — invoice, bill, receipt, or purchase order — via MOVA OCR and human-in-the-loop approval. Trigger when the user shares a document image URL or asks to process, extract, or review a financial document. Always confirm before starting.
license: MIT-0
metadata: {"openclaw":{"primaryEnv":"MOVA_API_KEY","plugin":{"name":"MOVA","installCmd":"openclaw plugins install openclaw-mova","configKey":"plugins.entries.mova.config.apiKey"},"dataSentToExternalServices":[{"service":"MOVA API (api.mova-lab.eu)","data":"invoice image URL, extracted document fields, human decision, audit metadata"},{"service":"ERP connector (read-only mock by default)","data":"PO reference number for cross-reference lookup"}]}}
---

# MOVA Invoice OCR & Approval

Submit a supplier invoice to MOVA for automated OCR extraction, risk validation, and a human decision gate — all with a tamper-proof audit trail.

## What it does

1. **OCR extraction** — extracts vendor, IBAN/BIC, line items, totals, VAT, PO reference
2. **Risk validation** — checks for duplicate invoices, unknown vendors, IBAN changes, VAT mismatches
3. **Human decision gate** — you choose: approve / reject / escalate / request info
4. **Audit receipt** — every decision is signed, timestamped, and stored in an immutable compact journal

## Requirements

**Plugin:** MOVA OpenClaw plugin must be installed and configured with your API key.
Get your key at [mova-lab.eu/register](https://mova-lab.eu/register).

**Data flows:**
- Invoice image URL + extracted fields → `api.mova-lab.eu` (MOVA platform, EU-hosted)
- PO reference number → ERP connector (read-only lookup, no data stored)
- Audit journal → MOVA R2 storage, cryptographically signed, accessible only via your API key
- No data is sent to third parties beyond the above

## Quick start

Share any invoice image URL and say "process this invoice":

```
https://raw.githubusercontent.com/mova-compact/mova-bridge/main/test_invoice_INV-2026-0441.png
```

The agent submits it to MOVA, shows the extracted data with risk score and findings, then asks for your decision.

## Demo

**Step 1 — Task submitted with invoice image**
![Step 1](screenshots/01-input.jpg)

**Step 2 — AI analysis: vendor, line items, risk score 0.15, findings**
![Step 2](screenshots/02-analysis.jpg)

**Step 3 — Human decision gate**
![Step 3](screenshots/03-decision.jpg)

**Step 4 — Audit receipt + compact journal**
![Step 4](screenshots/04-audit.jpg)

## Why contract execution matters

A standard AI agent processes the invoice and tells you the result. MOVA does something different:

- **Every action is gated** — the agent cannot approve or reject without your explicit input
- **Policy is enforced** — IBAN changes, unknown vendors, and duplicate flags always route to human review, no exceptions
- **Immutable audit trail** — the compact journal records every event (OCR, validation, human decision) with cryptographic proof. When an auditor asks "who approved invoice INV-305B3FBF and why?" — the answer is already in the system with an exact timestamp and reason
- **EU AI Act ready** — high-risk financial decisions require human oversight and full explainability. MOVA provides both by design

## What the user receives

| Output | Description |
|--------|-------------|
| Extracted fields | Vendor, IBAN/BIC, Tax ID, line items, totals, VAT |
| PO match | Cross-referenced against ERP |
| Duplicate check | Detects re-submissions |
| OCR confidence | 0.0–1.0 accuracy score |
| Risk score | 0.0 (clean) – 1.0 (critical) |
| Anomaly flags | iban_change, unknown_vendor, duplicate, vat_mismatch |
| Findings | Structured list with severity codes |
| Decision options | approve / reject / escalate_accountant / request_info |
| Audit receipt ID | Permanent signed record of the AP decision |
| Compact journal | Full event log: OCR → validation → human decision |

## When to trigger

Activate when the user shares an image URL of a financial document or asks to process / OCR / approve an invoice.

**Before starting**, confirm: "Submit this document to MOVA for OCR and approval?"

If no URL provided — ask once for a direct HTTPS image link.

## Step 1 — Submit document

Call tool `mova_hitl_start` with:
- `file_url`: the HTTPS URL of the document image

## Step 2 — Show analysis and decision options

If `status = "waiting_human"` — show extracted data and ask user to choose:
- **approve** — process payment
- **reject** — notify vendor
- **escalate_accountant** — forward to accountant
- **request_info** — ask vendor for clarification

Call tool `mova_hitl_decide` with:
- `contract_id`: from the response above (NOT the invoice number)
- `option`: chosen decision
- `reason`: human reasoning

## Step 3 — Show audit receipt

Call tool `mova_hitl_audit` with `contract_id`.
Call tool `mova_hitl_audit_compact` with `contract_id` for the full signed event chain.

## Connect your real OCR and ERP systems

By default MOVA uses a sandbox mock. To use your live document processing and ERP, register your endpoints — see the **MOVA Connector Setup** skill or call `mova_list_connectors` with `keyword: "ocr"`.

Relevant connectors:

| Connector ID | What it covers |
|---|---|
| `connector.ocr.document_extract_v1` | Document OCR extraction |
| `connector.ocr.vision_llm_v1` | Vision LLM OCR (OpenRouter) |
| `connector.finance.duplicate_check_v1` | Duplicate invoice detection |
| `connector.tax.vat_validate_v1` | VAT number validation (VIES) |
| `connector.erp.invoice_post_v1` | ERP invoice posting / status update |

Call `mova_register_connector` with `connector_id`, `endpoint`, optional `auth_header` and `auth_value`.

## Rules

- NEVER make HTTP requests manually
- NEVER invent or simulate results — if a tool call fails, show the exact error
- Use MOVA plugin tools directly (mova_hitl_start, mova_hitl_decide, etc.) — do NOT use exec or shell
- CONTRACT_ID comes from the mova_hitl_start response, not from the invoice number
