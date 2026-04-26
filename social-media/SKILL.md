---
name: x-browser-relay-post
description: Post content to X/Twitter for free using the user's own Chrome browser via AppleScript (primary), or Browser Relay / CDP as fallbacks. Covers all three approaches since paid X API (xurl/xitter) requires API credits.
---

# Free X (Twitter) Post — Via User's Chrome

**Core principle:** xurl and xitter both require paid X API. For free posting, automate the user's own Chrome browser — specifically the user's already-logged-in Chrome session, since fresh Playwright/Camofox browsers always hit X's CAPTCHA/phone verification.

Only one reliable approach on macOS: **AppleScript** (after user enables one flag).

---

## Prerequisite: Enable Apple Events JS in Chrome

**Must be done once by the user in their Chrome browser:**

Chrome menu bar → **View** → **Developer** → check ✅ **"Allow JavaScript from Apple Events"**

Or navigate to: `chrome://flags/#allow-javascript-apple-events` → set **Enabled**

Without this flag, `osascript execute ... javascript` calls silently fail.

---

## Primary Approach: AppleScript (Recommended — Proven Working)

No Chrome extension, no port binding, no new browser launch needed. Uses the user's existing Chrome window directly.

### Step 0: Find the right Chrome profile with X login

**Critical:** The user likely has multiple Chrome profiles. Only the one where they logged into X has the `auth_token` cookie. AppleScript controls whatever Chrome window is active — but that window might be on the wrong profile.

Check if the current Chrome tab is already on X:

```bash
osascript -e 'tell app "Google Chrome" to get URL of active tab of window 1'
```

If it shows a login page (`/i/flow/login` or `/login`), the current Chrome profile is NOT logged into X. Find the profile that is:

```bash
ls ~/Library/Application\ Support/Google/Chrome/ | grep -i profile
```

For each profile, check if it has X auth cookies:

```bash
sqlite3 "$HOME/Library/Application Support/Google/Chrome/Profile 2/Cookies" \
  "SELECT host_key, name FROM cookies WHERE host_key LIKE '%.x.com%' AND name IN ('auth_token','ct0','twid','kdt') LIMIT 10"
```

Look for a profile that has **`auth_token`** — that's the one logged into X.

**What to do:** Ask the user to switch Chrome to that profile (click the profile avatar → switch), then open X.com. You cannot switch profiles programmatically via AppleScript.

### Step 1: Verify Chrome is running with X.com open and logged in

```bash
osascript -e 'tell app "Google Chrome" to get URL of active tab of window 1'
```

Check the URL — it should show `x.com/home` or `x.com/explore` or similar, NOT a login page.

If X is not open, either ask the user to open x.com or (if they're already on the correct profile) navigate there:

```bash
osascript -e 'tell app "Google Chrome" to set URL of active tab of window 1 to "https://x.com"'
```

Wait for the page to load before proceeding.

### Step 2: Post via URL Intent (Most Reliable Method — Proven Working 2026)

**This is the preferred approach.** Navigate directly to X's intent/post URL with URL-encoded text. This properly triggers X's React state management — the Post button becomes enabled immediately, unlike DOM injection which requires complex event dispatching.

**Key advantage:** The `x.com/intent/post?text=` URL is X's official share intent endpoint. React processes the text parameter natively, so the Post button lights up without any manual event dispatch. This avoids all the issues with `execCommand('insertText')` and React synthetic events.

**One-step approach (no text injection needed):**

```bash
# Navigate directly to intent URL with tweet text URL-encoded
osascript -e 'tell app "Google Chrome" to set URL of active tab of window 1 to "https://x.com/intent/post?text=YOUR_URL_ENCODED_TEXT"'
```

Wait for the page to load (3-5 seconds), then the Post button should be enabled.

#### Python helper with proper encoding:

```python
import subprocess
import json
import urllib.parse

tweet_text = "你的推文内容"  # Unicode text, any language

# URL-encode the text for the intent URL
encoded = urllib.parse.quote(tweet_text)
url = f"https://x.com/intent/post?text={encoded}"

# Navigate to the intent URL — React processes the text natively
script = json.dumps(f'tell app "Google Chrome" to set URL of active tab of window 1 to "{url}"')
subprocess.run(['osascript', '-e', script], capture_output=True, text=True, timeout=15)
# Wait for page to load
import time
time.sleep(4)

# Verify the button is enabled
js = """var btn = document.querySelector('[data-testid=tweetButton]') || document.querySelector('[data-testid=tweetButtonInline]');
if (btn) { 'disabled=' + btn.disabled; } else { 'no button'; }"""
script = json.dumps(f'tell app "Google Chrome"\n  execute active tab of window 1 javascript {json.dumps(js)}\nend tell')
result = subprocess.run(['launchctl', 'asuser', '501', 'osascript', '-e', script], capture_output=True, text=True, timeout=10)
print(result.stdout)  # Should show 'disabled=false'
```

**Why this is better than DOM injection:**
- No complex event dispatching needed — React processes the intent URL text natively
- No issues with `String.fromCharCode()` for Unicode text
- No character corruption or encoding problems
- No need to fire `beforeinput` / `InputEvent` — it Just Works
- The Post button is reliably enabled after the page loads

> **Note:** The `execCommand('insertText')` + event dispatch approach (described below in "Alternative: DOM Injection") was the primary method for 2024–2025, but as of 2026, X's React implementation may not respond to dispatched `InputEvent` — the Post button stays `disabled=true`. The URL intent approach is now the recommended primary method.

## The Proven DOM Injection Recipe (3/3 posts successful, 2026-04-26)

When the URL intent approach doesn't work (e.g., text too long or X doesn't process the param), use this EXACT sequence. Three successful posts confirm it.

### Prerequisite: File-based execution (CRITICAL)

**Do NOT use `osascript -e` with inline JS.** Long JavaScript (>500 chars) causes AppleScript parser failures and silent returns. Instead:

```bash
# ALWAYS write AppleScript to a temp file, then execute
osascript /tmp/post.applescript
```

The AppleScript file embeds the JS as a single string variable, then executes it:

```applescript
tell app "Google Chrome"
    set jsCode to "var t=document.querySelector('[data-testid=tweetTextarea_0]'); ... ALL JS HERE ..."
    execute active tab of window 1 javascript jsCode
end tell
```

### Recipe (3 steps + verify)

**Step 1: Get fresh compose**
```bash
# Close any open compose, then navigate fresh
osascript -e 'tell app "Google Chrome" to set URL of active tab of window 1 to "https://x.com/compose/post"'
sleep 5  # Full React render
```

**Step 2: Insert with 11-event chain** — Write this as a `.applescript` file:
```javascript
// Build text via fromCharCode (never embed Chinese directly)
var text = String.fromCharCode(code1, code2, ...);
// LINE BREAKS: use \r (Unicode 13), NOT \n (Unicode 10). \n gets eaten.

ta.focus();
ta.textContent = '';
document.execCommand('insertText', false, text);

// Fire the 11-event chain:
ta.dispatchEvent(new InputEvent('beforeinput', {inputType:'insertFromPaste', data:text, dataTransfer:new DataTransfer(), bubbles:true, cancelable:true}));
ta.dispatchEvent(new InputEvent('beforeinput', {inputType:'insertText', data:text, bubbles:true}));
ta.dispatchEvent(new InputEvent('textInput', {data:text, bubbles:true}));
ta.dispatchEvent(new Event('input', {bubbles:true}));
ta.dispatchEvent(new Event('change', {bubbles:true}));
ta.dispatchEvent(new CompositionEvent('compositionstart', {data:text, bubbles:true}));
ta.dispatchEvent(new CompositionEvent('compositionend', {data:text, bubbles:true}));
ta.dispatchEvent(new KeyboardEvent('keydown', {key:' ', bubbles:true}));
ta.dispatchEvent(new KeyboardEvent('keypress', {key:' ', bubbles:true}));
ta.dispatchEvent(new KeyboardEvent('keyup', {key:' ', bubbles:true}));
```

**Step 3: Click Post**
```bash
osascript -e 'tell app "Google Chrome" to execute active tab of window 1 javascript "var b=document.querySelector(\"[data-testid=tweetButton]\")||document.querySelector(\"[data-testid=tweetButtonInline]\"); if(b&&!b.disabled){b.click();\"posted\"}else{\"\"+b.disabled}"'
sleep 4
osascript -e 'tell app "Google Chrome" to get URL of active tab of window 1'
# Returns "https://x.com/home" = success
```

### Pitfalls (all verified by failure)
1. **\n vs \r**: `execCommand('insertText')` eats `\n` (code 10). Use `\r` (code 13) for ALL line breaks.
2. **Stale state**: Never reuse an already-open compose dialog. Close first, then fresh `/compose/post`.
3. **fromCharCode is non-negotiable**: Direct Chinese characters in AppleScript's JavaScript strings cause silent corruption.
4. **Single input event ≠ enough**: React needs the full 11-event chain. One `input` event leaves button disabled.
5. **osascript -e breaks for long JS**: The `-e` flag has a string length limit. Write to file, run `osascript file.applescript`.
6. **Python subprocess unstable**: Python's `subprocess.run(['osascript', '-e', ...])` may stop returning JS values mid-session. Fall back to raw `osascript` with simple queries, or file execution for complex ones.

### Step 3: Click Post button

After the text is written and the button becomes enabled, click it:

```python
import subprocess, json

js = """var btn = document.querySelector('[data-testid=tweetButton]') || document.querySelector('[data-testid=tweetButtonInline]');
if (btn && !btn.disabled) { btn.click(); 'clicked'; } else { 'no-btn or disabled'; }
"""
script = f"""tell app "Google Chrome"
    execute active tab of window 1 javascript {json.dumps(js)}
end tell"""
result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True, timeout=10)
```

### Step 4: Verify

After clicking post, check URL. If it navigated away from `/compose/post`, the post was published:

```bash
sleep 2
osascript -e 'tell app "Google Chrome" to get URL of active tab of window 1'
# Expected: https://x.com/home — indicates success
```

Or check programmatically:
```python
import subprocess, json
js = """// Our current location proves whether the post went through
window.location.href;
"""
script = f"""tell app "Google Chrome"
    execute active tab of window 1 javascript {json.dumps(js)}
end tell"""
result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True, timeout=10)
print("Current URL:", result.stdout)
```

**Success signal:** URL changes from `x.com/compose/post` to `x.com/home` (or user's timeline). No error toast is visible.

### AppleScript Reference Commands

```bash
# Get current URL
osascript -e 'tell app "Google Chrome" to get URL of active tab of window 1'

# Execute JavaScript (returns result)
osascript -e 'tell app "Google Chrome" to execute active tab of window 1 javascript "document.title"'

# Open a new tab
osascript -e 'tell app "Google Chrome" to set URL of tab 1 of window 1 to "https://x.com"'

# Count tabs
osascript -e 'tell app "Google Chrome" to count tabs of window 1'
```

### Limitations

- Can't see the page visually (no screenshots)
- JS returns string results only — use `JSON.stringify()` for objects
- Timing depends on page load speed — use `sleep` between steps
- React input handling requires proper event dispatching (see Step 3)

---

## Fallback A: OpenClaw `browser` CLI

If OpenClaw is installed, its `browser` CLI can manage Chrome via CDP on port 18800:

```bash
# Start the managed Chrome
openclaw browser start

# Navigate
openclaw browser navigate https://x.com

# Get page snapshot
openclaw browser snapshot

# Type into an element by ref
openclaw browser type 42 "hello world"

# Click by ref
openclaw browser click 55

# Evaluate JS on the page
openclaw browser evaluate --fn "() => document.title"
```

**Caveats:**
- `openclaw browser` manages its own Chrome instance (not the user's logged-in session)
- The OpenClaw config must not have stale plugin entries (`plugins.allow` excluding `browser`) or it shows warnings
- User must log into X in this managed Chrome — may hit verification roadblocks
- Requires the `openclaw` CLI (which the user already has at `/usr/local/bin/autocli` as AutoCLI)

---

## Fallback B: Chrome Remote Debugging (Port 9222)

**Known issue on macOS:** `--remote-debugging-port=9222` frequently does NOT bind the port due to macOS sandbox (`seatbelt-client`). Only use if AppleScript fails AND the user has a specific reason to prefer CDP.

```bash
# Kill existing Chrome, then launch with CDP
killall "Google Chrome" 2>/dev/null
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --remote-debugging-port=9222 &
```

**If the port binds successfully,** configure Camofox to connect to it (`cdp_url: http://localhost:9222` in `~/.hermes/config.yaml`) and use browser tools normally.

---

## Running from cron / background processes

When running AppleScript from a **cron job, launchd, or any non-GUI process**, `osascript` commands will time out because they can't access the user's GUI session (Aqua). 

**Fix:** Use `launchctl asuser <UID>` to run AppleScript in the correct user context:

```bash
# Find the user's UID (usually 501 for the first user)
id -u <username>  # e.g., id -u chenyikun → 501

# Run osascript through launchctl asuser
launchctl asuser 501 osascript -e 'tell app "Google Chrome" to get URL of active tab of window 1'

# Or run an AppleScript file
launchctl asuser 501 osascript /path/to/script.applescript
```

**For Python scripts running in cron context:**
```python
import subprocess, json

# Wrap every osascript call with launchctl asuser
script = json.dumps('tell app "Google Chrome" to get URL of active tab of window 1')
result = subprocess.run(
    ['launchctl', 'asuser', '501', 'osascript', '-e', script], 
    capture_output=True, text=True, timeout=15
)
```

**Without `launchctl asuser`**, you'll see the osascript command time out (exit code 124) with no output.

## Troubleshooting

### "X didn't log in — blank page / skeleton"

- X login requires the user's own Chrome session with saved cookies. Camofox/Firefox/Playwright-Chromium will NOT render the login page correctly. Always use the user's existing Chrome.
- If the user needs to log in for a fresh session, have them do it manually in their Chrome — automated login will hit CAPTCHA/phone verification.

### "osascript returned nothing or empty"

- Verify "Allow JavaScript from Apple Events" is checked in Chrome
- Try a simple command first: `osascript -e 'tell app "Google Chrome" to get URL of active tab of window 1'`
- If Chrome.app isn't responding to Apple Events, restart Chrome

### "Tweet text didn't appear / Post button stayed disabled"

**First try:** the DOM injection recipe above (fresh compose + `/compose/post` + `\r` line breaks + 11-event chain).

**If button still disabled:**
- Text may have `\n` instead of `\r` — execCommand eats `\n`. Rebuild with `\r`.
- Compose dialog may be stale — close it (click app-bar-close or navigate away), then re-open `/compose/post`.
- Event chain may be incomplete — ensure ALL 11 events fire. Missing `compositionend` or `keyboard` events are the most common culprits.
- Check actual text content: `osascript -e 'tell app "Google Chrome" to execute active tab of window 1 javascript "\"\"+document.querySelector(\"[data-testid=tweetTextarea_0]\").textContent.length"'`. If length < expected, text was truncated — check `\n` vs `\r` issue.
- The `fromCharCode` approach is mandatory for Chinese. Direct Unicode in AppleScript's JS causes character corruption (e.g. "白宫" → "白宇").

### "osascript returned nothing or empty (via Python subprocess)"

- Python's `subprocess.run(['osascript', '-e', ...])` may silently stop returning JS execution results mid-session. This is an AppleScript/process interaction quirk — the command runs but output is lost.
- **Fix:** For simple queries (`document.title`), use raw terminal `osascript -e ...`. For complex JS insertion, write to `.applescript` file and run `osascript /tmp/file.applescript`.
- For `execute ... javascript` queries, always return a simple string: `""+ta.textContent.length` not `'len='+...` which may be swallowed.

### "Cron / scheduled posting doesn't work"

- Hermes cron infrastructure has a known `ModuleNotFoundError: No module named 'agent.smart_model_routing'` bug (v0.11.0). Cron jobs will fail to initialize.
- **Workaround:** Use macOS `launchd` instead of Hermes cron. Or run posting manually.
- The cron context also requires `launchctl asuser <UID>` to access the GUI session — see "Running from cron" section.

---

## Content Guidelines: Question Format (Engagement Rule)

**Every post MUST end with a multiple-choice question (A/B/C/D)** to drive comment engagement. No open-ended questions — give readers specific options to pick from.

### Structure

```
[文学风格正文——比喻/叙事/反差]

A. [选项一——简短，带态度]
B. [选项二——简短，带态度]
C. [选项三——简短，带态度]
D. [选项四——简短，带态度]
```

### Rules
- **4 options only** (A/B/C/D). Never fewer, never more.
- **Each option ≤ 15 Chinese characters** — concise enough to scan, punchy enough to vote.
- **Option D should invite nuance** — "评论区见" / "看人" / "分情况" to acknowledge complexity.
- **Literary body ≤ 200 chars** to leave room for the 4 options within X's 280-count limit.
- **Write the body first**, then calculate remaining budget for options.

### X count reminder
- Chinese characters count as 2 against X's 280 limit
- A/B/C/D markers + spaces ≈ 12-16 X-count
- Each option letter + punctuation ≈ 4 X-count overhead
- Plan body to leave ~120 X-count for the 4 options<｜end▁of▁thinking｜>

| Element | Selector |
|---------|----------|
| Tweet textarea | `[data-testid="tweetTextarea_0"]` or `[data-testid="tweetTextarea_1"]` |
| Post button | `[data-testid="tweetButton"]` or `[data-testid="tweetButtonInline"]` |
| Compose opener | `[data-testid="SideNav_NewTweet_Button"]` or `a[href="/compose/post"]` |
| Contenteditable div | `div[role="textbox"][contenteditable="true"]` |
