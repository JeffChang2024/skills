#!/usr/bin/env node

/**
 * Calls GF hiAgentChat SSE API and outputs extendData.section.rich_text to stdout.
 * Only accepts the user's question as argument; no user/session context.
 * Requires GF_AGENT_COOKIE in env.
 */

const API_URL = 'https://aigctest.gf.com.cn/api/aigc/api/base/hiAgentChat?robotId=cjzj&agentId=ths_dhstw'

function usage() {
  console.error('Usage: node chat.mjs "user question"')
  console.error('  Only pass the question text. Requires GF_AGENT_COOKIE in env.')
  process.exit(2)
}

const args = process.argv.slice(2)
if (args.length === 0 || args[0] === '-h' || args[0] === '--help') usage()

const question = args[0].trim()
if (!question) usage()

const cookie = (process.env.GF_AGENT_COOKIE ?? '').trim()
if (!cookie) {
  console.error('Missing GF_AGENT_COOKIE')
  console.log('Investment analysis unavailable: Missing GF_AGENT_COOKIE. Do not retry; suggest user to configure GF_AGENT_COOKIE.')
  process.exit(1)
}

const body = {
  question,
  conversationId: '',
  mindSet: '',
  agentId: 'ths_dhstw',
  robotId: 'cjzj',
  currentRobotId: 'cjzj',
  extendParams: { webSearchMode: 'auto' }
}

function richTextToStr(rt) {
  if (rt == null) return ''
  if (typeof rt === 'string') return rt
  if (Array.isArray(rt)) {
    return rt.map((x) => (typeof x === 'string' ? x : (x?.text ?? x?.content ?? ''))).join('')
  }
  return String(rt?.text ?? rt?.content ?? rt ?? '')
}

async function main() {
  const res = await fetch(API_URL, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      accept: 'text/event-stream',
      Cookie: cookie
    },
    body: JSON.stringify(body)
  })

  if (!res.ok) {
    const text = await res.text().catch(() => '')
    console.error(`hiAgentChat failed (${res.status}): ${text.slice(0, 500)}`)
    console.log(`Investment analysis unavailable: API error (${res.status}). Do not retry.`)
    process.exit(1)
  }

  const text = await res.text()
  const parts = []
  let currentData = ''

  for (const line of text.split('\n')) {
    if (line.startsWith('data:')) {
      currentData = line.slice(5).trim()
      if (currentData === '[DONE]' || currentData === '') continue
      try {
        const obj = JSON.parse(currentData)
        const ext = obj?.extendData
        const section = ext?.section
        const rt = section?.rich_text
        if (rt != null) parts.push(richTextToStr(rt))
        if (obj?.code != null && obj.code !== 0 && obj.message) {
          console.error(`API message: ${obj.message}`)
        }
      } catch (_) {
        // skip unparseable data lines
      }
    }
  }

  const out = parts.join('').trim()
  if (out) console.log(out)
}

main().catch((err) => {
  console.error(err.message || err)
  console.log(`Investment analysis unavailable: ${err.message || err}. Do not retry.`)
  process.exit(1)
})
