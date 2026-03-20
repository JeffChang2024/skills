# Windows Notifier Skill

Sends local Windows desktop notifications through the existing `node-notifier` setup in `tools/study-notifier`.

## When to use

Use this skill when you want a real local Windows toast / desktop notification instead of an OpenClaw chat reply.

## Backing script

- `C:\Users\dongz\.openclaw\workspace\tools\study-notifier\notify.js`

## Example

```powershell
node "C:\Users\dongz\.openclaw\workspace\tools\study-notifier\notify.js" --title "OpenClaw Test" --message "This is a Windows notification test." --timeout 10
```
