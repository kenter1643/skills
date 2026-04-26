# x-browser-relay-post

Free X (Twitter) posting via the user's own Chrome browser — no paid API required.

## Problem

X's official API (xurl, xitter) requires minimum $5 in API credits. This skill bypasses it entirely by automating the user's already-logged-in Chrome session through AppleScript.

## Why This Works

- No new browser launch → avoids X's CAPTCHA / phone verification
- Uses existing Chrome login cookies (auth_token, ct0)
- Works on macOS with zero API spend

## Setup (One-Time)

1. Chrome → View → Developer → ✅ **"Allow JavaScript from Apple Events"**
2. Keep Chrome open with X.com logged in (Profile 2 recommended)
3. That's it. No Chrome extensions, no port binding, no API keys.

## Usage

The skill provides two posting approaches:

### Primary: DOM Injection (Proven 2026-04-26, 3/3 successful)

Navigate to `x.com/compose/post`, inject text via `String.fromCharCode` + `execCommand('insertText')` + 11-event React chain, then click Post.

**Key pitfalls solved:**
- Line breaks must use `\r` (code 13), not `\n` (code 10)
- Long JS must be written to `.applescript` file, not passed via `osascript -e`
- 11-event dispatch chain required to trigger React (1 event ≠ enough)
- `String.fromCharCode()` mandatory for Chinese text (direct Unicode in AppleScript corrupts)

### Fallback: URL Intent

Navigate to `https://x.com/intent/post?text=URL_ENCODED_TEXT` — X processes it natively.

## Files

- `SKILL.md` — Full implementation guide with command reference, pitfalls, and troubleshooting
- `README.md` — You're reading it

## Author

Created by Kenter Chen for Hermes Agent.
