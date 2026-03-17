# hiAgentChat API Reference

## Endpoint

```
POST https://aigctest.gf.com.cn/api/aigc/api/base/hiAgentChat?robotId=cjzj&agentId=ths_dhstw
```

## Request

- **Headers**: `Content-Type: application/json`, `accept: text/event-stream`, `Cookie: <GF_AGENT_COOKIE>`
- **Body** (only API-related fields; do not inject user/session metadata):

```json
{
  "question": "<用户问题>",
  "conversationId": "",
  "mindSet": "auto",
  "agentId": "ths_dhstw",
  "robotId": "cjzj",
  "currentRobotId": "cjzj",
  "extendParams": { "webSearchMode": "auto" }
}
```

- **conversationId**: Empty for new conversation; can be set for multi-turn if the API returns and requires it.

## Authentication

- **GF_AGENT_COOKIE**: Full Cookie string (e.g. `LtpaToken2=...; oauth_token=...`). Set via environment; do not hardcode or commit.

## Response format and parsing

- **Content type**: SSE (`text/event-stream`).
- **Events**: Each event line is `data: <JSON>` (no space after `data:`).
- **Fields to extract**: From each parsed `data` object, take **`extendData.section.rich_text`** as the reply content. Multiple events may be sent (streaming); `extendData.section.is_last` indicates the last chunk. The script concatenates all `rich_text` in order and outputs once.
- **rich_text**: In practice a string (e.g. `"一交易"`). If the API sends an array of segments, the script concatenates them.
- **stdout**: Script outputs only the concatenated content from `extendData.section.rich_text`; no other fields (sources, conversationId, etc.) are appended.
- **Errors**: If the payload has `code` (non-zero) and `message`, the script logs the message to stderr and exits with non-zero code.

### Sample data line (structure)

One SSE line looks like (IDs shortened for readability):

```
data:{"event":null,"answer":null,"messageId":"msg-...","conversationId":"conv-...","moduleType":"AIChatThsFinance","agentId":"ths_dhstw","realQuestion":"今日大盘","sources":null,"extendData":{"extra":{},"section":{"show_type":"rich_text","text_answer":"一交易","is_last":false,"tag_info_list":[],"info_texts":[],"voice_txt":"一交易","rich_text":"一交易","id":2001,"result_page":{},"choice":[]},"answer_path":"other/openAnswer","logs":[]},"relateQuestions":null,"relativeAgents":null,"suffixCard":null}
```

- **Parse**: `extendData.section.rich_text` → `"一交易"` (this segment). When `is_last` is true, the stream for this reply is complete.
- Other fields (`text_answer`, `voice_txt`, `realQuestion`, `conversationId`, etc.) are not used for stdout.

## Security

Do not commit `GF_AGENT_COOKIE` or any token to the repository. Use environment variables or a secure secret store.
