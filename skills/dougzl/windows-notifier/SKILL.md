# Windows Notifier

Use local Windows desktop notifications via `node-notifier`.

Activate when the user asks to:
- send a Windows notification
- show a desktop toast / local popup
- test whether native Windows notifications work
- send a local reminder through `node-notifier`

Do **not** use this skill for:
- replying in chat only
- browser/web notifications inside Control UI
- cross-device messaging

## What this skill does

This skill sends a **local Windows notification** on the current machine by calling the existing notifier script:

- Script: `C:\Users\dongz\.openclaw\workspace\tools\study-notifier\notify.js`
- Runtime: Node.js
- Library: `node-notifier`

## Before sending

1. Confirm the request is for a **local Windows notification**.
2. If the user gave text, use it directly.
3. If they did not give a title, pick a short practical title.
4. Keep the message concise. Windows toast text should be short.

## Command template

Run this from PowerShell with `exec`:

```powershell
node "C:\Users\dongz\.openclaw\workspace\tools\study-notifier\notify.js" --title "<TITLE>" --message "<MESSAGE>" --timeout 10
```

Optional flags supported by the script:

- `--wait true|false`
- `--timeout <seconds>`

## Expected output

Success usually prints:

```text
NOTIFY_SENT
```

It may also print fields like:

- `RESPONSE:timeout`
- `METADATA:{...}`

That does **not** necessarily mean failure. It often just means the notification timed out naturally.

## Troubleshooting

If the user does not see a popup:

1. Check whether it appeared in Windows Notification Center.
2. If yes, the notifier likely worked and Windows suppressed the toast banner.
3. Likely causes:
   - Focus Assist / Do Not Disturb
   - app notification permissions
   - Windows banner style settings
   - another app or shell state affecting display

## Examples

### Send a quick test

```powershell
node "C:\Users\dongz\.openclaw\workspace\tools\study-notifier\notify.js" --title "OpenClaw Test" --message "This is a Windows notification test." --timeout 10
```

### Study reminder

```powershell
node "C:\Users\dongz\.openclaw\workspace\tools\study-notifier\notify.js" --title "软考学习提醒" --message "现在开始今天的学习时段。" --timeout 10
```

## Notes

- This skill relies on the existing `tools/study-notifier` folder already being installed.
- If dependencies are missing, install them in that folder with `npm install`.
- This skill is for **local machine notifications only**.
