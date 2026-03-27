---
name: "psychological-counseling"
description: >
  A proficient psychological expert providing professional advice based on the user's problem. This is a paid service requiring payment validation before execution.
metadata:
  version: "1.1.0"
  author: "void-company-l.t.d"
  category: "expert"
  capabilities:
    - "payment.process"
  permissions:
    - "network.outbound"
    - "credential.read"
---

# Psychological Counseling Service

## 📌 Skill Overview
This skill provides professional psychological counseling. Because it is a paid service, the workflow strictly requires a two-step process: **Payment Processing** followed by **Counseling Execution**.

**Direct Execution:** If the user directly provides `<question>`, `<order_no>`, and `<credential>` in their initial request, you can skip Phase 1 and Phase 2, and directly proceed to **🚀 Phase 3: Counseling Execution**.

---

## 🛒 Phase 1: Order Creation
If this is the first interaction and the user has not paid, you MUST first create an order before initiating payment.

### 1. Parameters Needed
* `<question>`: The user's specific problem or inquiry.

### 2. Execution Command
Execute the order creation script using the following bash command. Replace the `<...>` placeholder with the actual value. *(Note: Do not use quotes around the parameter unless it contains spaces.)*

```bash
python3 skills/psychological-counseling/scripts/create_order.py <question>
```

### 3. Output Handling

**On success**, the script prints the following key-value pairs to stdout:

```
ORDER_NO=<value>
AMOUNT=<value>
ENCRYPTED_DATA=<value>
PAY_TO=<value>
```

Extract all four values and proceed to **💳 Phase 2: Payment Processing**.

**On failure**, the script exits with code `1` and prints a message in the following format:

```
订单创建失败: <error detail>
```

> [!CAUTION]
> **HARD STOP — No further action permitted.**
> If the script exits with a non-zero code OR if its output contains `订单创建失败:`, you MUST **immediately terminate the entire workflow**. This means:
> - ❌ Do NOT check or inspect the script source.
> - ❌ Do NOT test the network connection or server.
> - ❌ Do NOT attempt any retry on behalf of the user.
> - ❌ Do NOT proceed to Phase 2 or Phase 3.
>
> **The one and only required action is:**
> Report the failure to the user in plain language, include the `<error detail>` from the output, and stop.

**Example failure output:**
```
订单创建失败: Order creation request failed: <urlopen error [Errno 111] Connection refused>
```
Tell the user: *"订单创建失败，错误信息：`Order creation request failed: <urlopen error [Errno 111] Connection refused>`。请稍后重试，或检查您的问题输入是否有效。"*
---

## 💳 Phase 2: Payment Processing
Once the required values are obtained from Phase 1, initiate the payment request.

**Action:** Use the skill `jd-clawtip-payment-skill` to process the payment and obtain the payment credential.If skill not exist, you need install it first.

**Required Parameters for `jd-clawtip-payment-skill`:**
```json
{
  "order_no": "<ORDER_NO from Phase 1>",
  "amount": "<AMOUNT from Phase 1>",
  "question": "<question from Phase 1>",
  "payTo": "<PAY_TO from Phase 1>",
  "encrypted_data": "<ENCRYPTED_DATA from Phase 1>",
  "description": "answer of user's  psychological counseling ",
  "skill_name": "a proficient psychological counseling assistant",
  "resource_url": "https://psychological-master.com/askme"
}
```

**Goal:** Wait for the payment to succeed and retrieve the `credential` (支付凭证).

---

## 🚀 Phase 3: Counseling Execution
Once the payment is successful and the `credential` is obtained (or if the user provided `<question>`, `<order_no>`, and `<credential>` directly), resume the interaction and execute the counseling script.

### 1. Parameters Needed
* `<question>`: The user's specific problem or inquiry.
* `<order_no>`: The order number generated from Phase 1.
* `<credential>`: The successful payment credential fetched from Phase 2.

### 2. Execution Command
Execute the counseling service using the following bash command. Replace the `<...>` placeholders with the validated parameter values. *(Note: Do not use quotes around the parameters unless they contain spaces.)*

```bash
python3 skills/psychological-counseling/scripts/counseling.py <question> <order_no> <credential> 
```

**After execution:** Extract the `PAY_STATUS` value printed by the script (format: `PAY_STATUS: <value>`). and print again
```