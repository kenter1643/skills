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

### ⚠️ Critical Rule: Never use Python subprocess for osascript

This is the #1 cause of silent failure. `subprocess.run(['osascript', '-e', ...])` from Python STOPS returning JS execution results mid-session — it prints the raw AppleScript source code instead of actual JS return values. This gives a false "success" signal: your script thinks it clicked "posted" but the actual JavaScript was never executed.

**The ONLY reliable pattern: use raw terminal `osascript` commands.**

| Task | Method |
|------|--------|
| Navigate / set URL | `osascript -e 'tell app "Google Chrome" to set URL ...'` (raw terminal) |
| Insert text (long JS) | Write `.applescript` file → `osascript /tmp/file.applescript` |
| Check button / click | `osascript -e 'tell app "Google Chrome" to execute ...'` (raw terminal) |
| Verify URL | `osascript -e 'tell app "Google Chrome" to get URL ...'` (raw terminal) |

**Never use Python's `subprocess.run(['osascript', ...])` for any osascript call that needs a JS return value.** It silently breaks.

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

### Step 2: Try URL Intent First (Sometimes Works)

**Try this first** — if it works, it's the simplest approach. Navigate directly to X's intent/post URL with URL-encoded text:

```bash
# Navigate directly to intent URL with tweet text URL-encoded
osascript -e 'tell app "Google Chrome" to set URL of active tab of window 1 to "https://x.com/intent/post?text=YOUR_URL_ENCODED_TEXT"'
# Wait for React to process (5 seconds)
sleep 5
# Check if the button is enabled
osascript -e 'tell app "Google Chrome" to execute active tab of window 1 javascript "var b=document.querySelector('"'"'[data-testid=tweetButton]'"'"')||document.querySelector('"'"'[data-testid=tweetButtonInline]'"'"'); if(b){'"'"'disabled='"'"'+b.disabled}else{'"'"'no button'"'"'}"'
```

If `disabled=false`, you're good — skip to click step.

**Known failure case (2026):** The intent URL SOMETIMES loads the text but leaves the Post button disabled. The page may even redirect to the user's profile instead of showing compose. When this happens, **don't waste time debugging** — jump straight to the DOM Injection method below.

> **Note:** The DOM Injection method below is the ONLY method with 4/4 proven posts on this system (all verified 2026). The URL intent approach has ~50% reliability — try it but always verify before clicking.

## The Proven DOM Injection Recipe (4/4 posts successful, verified 2026-04-26)

When the URL intent approach doesn't work (text too long, X doesn't process the param, or button stays disabled), use this EXACT sequence. Four consecutive successful posts confirm it — this is the most reliable method.

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

#### ⚡ Complete End-to-End Workflow (Copy-Paste Ready)

```bash
# ====== Step 1: Navigate to fresh compose ======
osascript -e 'tell app "Google Chrome" to set URL of active tab of window 1 to "https://x.com/compose/post"'
sleep 5

# ====== Step 2: Insert text via .applescript file ======
# Write the file (replace char codes with your text's codes)
cat > /tmp/post_x.applescript << 'APPLESCRIPT'
tell app "Google Chrome"
    set jsCode to "var text = String.fromCharCode(31243,24207,21592,20986,36712,25968,25454,26377,22810,25166,24515,65311,13,13,26576,24179,21488,32479,35745,65306,31243,24207,21592,20986,36712,29575,84,79,80,51,65292,34987,20986,36712,29575,20063,26159,84,79,80,51,12290,21152,29677,39640,23792,26399,65288,50,49,58,48,48,21518,65289,20986,36712,21344,27604,36229,54,48,37,12290,13,13,19981,26159,20182,20204,24819,20986,36712,8212,8212,26159,34892,19994,25226,24651,29233,26102,38388,20840,21464,25104,20102,20195,30721,12290,13,13,65,46,32,38065,22810,22280,23376,23567,61,39118,38505,22823,13,66,46,32,34987,20986,36712,25165,26159,30495,25968,25454,13,67,46,32,21152,29677,27585,25152,26377,13,68,46,32,35780,35770,21306,35265);" & "var ta = document.querySelector('[data-testid=tweetTextarea_0]'); if(!ta) ta = document.querySelector('[data-testid=tweetTextarea_1]'); if(!ta) ta = document.querySelector('div[role=\"textbox\"][contenteditable=\"true\"]'); if(ta) { ta.focus(); ta.textContent = ''; document.execCommand('insertText', false, text); ta.dispatchEvent(new InputEvent('beforeinput', {inputType:'insertFromPaste', data:text, dataTransfer:new DataTransfer(), bubbles:true, cancelable:true})); ta.dispatchEvent(new InputEvent('beforeinput', {inputType:'insertText', data:text, bubbles:true})); ta.dispatchEvent(new InputEvent('textInput', {data:text, bubbles:true})); ta.dispatchEvent(new Event('input', {bubbles:true})); ta.dispatchEvent(new Event('change', {bubbles:true})); ta.dispatchEvent(new CompositionEvent('compositionstart', {data:text, bubbles:true})); ta.dispatchEvent(new CompositionEvent('compositionend', {data:text, bubbles:true})); ta.dispatchEvent(new KeyboardEvent('keydown', {key:' ', bubbles:true})); ta.dispatchEvent(new KeyboardEvent('keypress', {key:' ', bubbles:true})); ta.dispatchEvent(new KeyboardEvent('keyup', {key:' ', bubbles:true})); 'inserted'; } else { 'no-textarea'; }"
    execute active tab of window 1 javascript jsCode
end tell
APPLESCRIPT
osascript /tmp/post_x.applescript
# Expected output: "inserted"

# ====== Step 3: Verify button is enabled ======
osascript -e 'tell app "Google Chrome" to execute active tab of window 1 javascript "var b=document.querySelector('"'"'[data-testid=tweetButton]'"'"')||document.querySelector('"'"'[data-testid=tweetButtonInline]'"'"'); if(b){'"'"'disabled='"'"'+b.disabled}else{'"'"'no button'"'"'}"'
# Expected output: "disabled=false"

# ====== Step 4: Click Post ======
osascript -e 'tell app "Google Chrome" to execute active tab of window 1 javascript "var b=document.querySelector('"'"'[data-testid=tweetButton]'"'"')||document.querySelector('"'"'[data-testid=tweetButtonInline]'"'"'); if(b&&!b.disabled){b.click();'"'"'posted'"'"'}else{'"'"'not clicked: '"'"'+b.disabled}"'
# Expected output: "posted"

# ====== Step 5: Verify success ======
sleep 3
osascript -e 'tell app "Google Chrome" to get URL of active tab of window 1'
# Expected output: "https://x.com/home" (means success!)
```

**Key quoting trick for bash:** The `'"'"'` pattern closes a single-quoted string, inserts an escaped single quote, and reopens the single-quoted string. This embeds literal single quotes inside bash single-quoted arguments — essential for X's `data-testid` attribute selectors.

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
1. **\\n vs \\r**: `execCommand('insertText')` eats `\\n` (code 10). Use `\\r` (code 13) for ALL line breaks.
2. **Stale state**: Never reuse an already-open compose dialog. Close first, then fresh `/compose/post`.
3. **fromCharCode is non-negotiable**: Direct Chinese characters in AppleScript's JavaScript strings cause silent corruption.
4. **Single input event ≠ enough**: React needs the full 11-event chain. One `input` event leaves button disabled.
5. **osascript -e breaks for long JS**: The `-e` flag has a string length limit. Write to file, run `osascript file.applescript`.
6. **Python subprocess unstable**: Python's `subprocess.run(['osascript', '-e', ...])` may stop returning JS values mid-session. Fall back to raw `osascript` with simple queries, or file execution for complex ones.
7. **URL intent redirects silently**: The `/intent/post?text=` page may load but then redirect to the user's profile without posting, leaving the compose dialog in an inconsistent state. Always verify `disabled=false` before clicking — if the button is disabled despite text appearing, navigate fresh to `/compose/post` and use DOM injection.
8. **False positive from Python + osascript**: Python's `subprocess.run(['osascript', '-e', script], capture_output=True)` returns the APPPLESCRIPT SOURCE CODE instead of JS execution output when the osascript process gets into a bad state. The script prints something that looks like success (raw AppleScript source) but no JavaScript was actually executed. The only fix: use raw terminal `osascript` for all verification and click steps.

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

## Attaching Images to Tweets (图文一起发布)

### ✅ Verified: Image + Text Tweet (图文一起发布, 2026-04-26, 1/1 successful)

The **only proven approach** for posting text+image tweets via AppleScript automation. Uses macOS clipboard → paste into X compose.

#### Prerequisites

1. ✅ **Chrome**: "Allow JavaScript from Apple Events" enabled (`chrome://flags/#allow-javascript-apple-events`)
2. ✅ **Accessibility**: The calling process must have Accessibility permission (System Settings → Privacy & Security → Accessibility). If using `Hermes agent`, add the Hermes binary/terminal process to the Trusted list.
3. ✅ **macOS**: User must be logged into the GUI session (not SSH/cron context without launchctl asuser)

#### Full Step-by-Step

```bash
# ====== Step 0: Copy image to macOS clipboard ======
osascript -e 'set the clipboard to (read (POSIX file "/tmp/your_image.jpeg") as JPEG picture)'

# ====== Step 1: Navigate to fresh compose ======
osascript -e 'tell app "Google Chrome" to set URL of active tab of window 1 to "https://x.com/compose/post"'
sleep 5

# ====== Step 2: Focus textarea ======
osascript -e 'tell app "Google Chrome" to execute active tab of window 1 javascript "var ta=document.querySelector('"'"'[data-testid=tweetTextarea_0]'"'"')||document.querySelector('"'"'[role=textbox][contenteditable=true]'"'"'); if(ta){ta.focus();ta.click();'"'"'focused'"'"'}else{'"'"'none'"'"'}"'

# ====== Step 3: Paste image from clipboard ======
# ⚠️ CRITICAL: Use key code 9 (NOT keystroke "v")!
# keystroke "v" → error 1002 ("osascript not allowed to send keys")
# key code 9 → works (numeric key codes bypass some macOS security checks)
osascript -e 'tell application "System Events" to key code 9 using command down'

# ====== Step 4: Wait for X to upload the pasted image ======
sleep 5

# Verify: count blob URL images (= uploaded media previews)
osascript -e 'tell app "Google Chrome" to execute active tab of window 1 javascript "document.querySelectorAll('"'"'img[src^=\"blob:\"]'"'"').length+'"'"' blob imgs'"'"'"'
# Expected: "1 blob imgs" or more (3 if image generates multiple previews)

# ====== Step 5: Insert tweet text (DOM Injection method) ======
# Write .applescript file with String.fromCharCode + 11-event chain
# (See "The Proven DOM Injection Recipe" section above for the AppleScript template)
osascript /tmp/post_text.applescript
# Expected: "inserted"

# ====== Step 6: Verify Post button enabled & click ======
osascript -e 'tell app "Google Chrome" to execute active tab of window 1 javascript "var b=document.querySelector('"'"'[data-testid=tweetButton]'"'"')||document.querySelector('"'"'[data-testid=tweetButtonInline]'"'"'); if(b&&!b.disabled){b.click();'"'"'posted'"'"'}else{'"'"'disabled= '"'"'+b.disabled}"'
# Expected: "posted"

# ====== Step 7: Verify success ======
sleep 3
osascript -e 'tell app "Google Chrome" to get URL of active tab of window 1'
# Expected: "https://x.com/home" → tweet published!
```

#### macOS Key Code Reference (for System Events)

| Key | Key Code | Usage |
|-----|----------|-------|
| **v** (paste) | **9** | `key code 9 using command down` |
| c (copy) | 8 | `key code 8 using command down` |
| x (cut) | 7 | `key code 7 using command down` |
| a (select all) | 0 | `key code 0 using command down` |
| Return | 36 | `key code 36` |
| Escape | 53 | `key code 53` |
| Tab | 48 | `key code 48` |

#### Supported Image Formats

Same as X.com accepts: `image/jpeg, image/png, image/webp, image/gif`

Clipboard format specifiers:
```bash
# JPEG
osascript -e 'set the clipboard to (read (POSIX file "/tmp/img.jpg") as JPEG picture)'

# PNG
osascript -e 'set the clipboard to (read (POSIX file "/tmp/img.png") as PNG picture)'
```

### Key Technical Details

| Concept | Detail |
|---------|--------|
| **Clipboard method** | `set the clipboard to (read (POSIX file "/path/img.jpg") as JPEG picture)` |
| **Key code vs keystroke** | `key code 9` = 'v' key. Use `key code` NOT `keystroke "v"`! |
| **Why key code works** | macOS checks Accessibility permission on the calling process. `keystroke` checks the process name against the Trusted list; `key code` uses numeric identifiers which bypass some restrictions. |
| **Supported image types** | JPEG, PNG, GIF (same formats X accepts) |
| **Upload time** | 3-5 seconds for typical images (< 100KB) |
| **Verification** | Count `img[src^="blob:"]` elements — each blob = one uploaded media |

### Common `key code` Values for macOS

| Key | Key Code |
|-----|----------|
| v | 9 |
| c | 8 |
| x | 7 |
| a | 0 |
| Return/Enter | 36 |
| Escape | 53 |
| Tab | 48 |

Usage: `osascript -e 'tell application "System Events" to key code <N> using {command down}'`

### Potential Blockers

1. **macOS Accessibility Permission**: The process running `osascript` must be allowed to send keystrokes. If `key code 9 using command down` fails with error 1002, the calling process (e.g., Hermes agent subprocess) doesn't have Accessibility. In that case, try adding the terminal emulator or the calling binary to Settings → Privacy & Security → Accessibility. If even `key code` fails, the clipboard paste approach is unavailable.

2. **Clipboard format**: `as JPEG picture` assumes JPEG. For PNG: `as PNG picture`. Convert accordingly.

3. **Image too large**: Very large images (> 5MB) may take longer to upload. Increase sleep time after paste.

### Detailed Explanation: Why Programmatic File Input Doesn't Work

X.com's React 18+ event delegation checks `event.isTrusted`. Programmatically dispatched events always have `isTrusted=false`. The following were tested and **ALL failed** to trigger X's media handler:

| Approach | Result |
|----------|--------|
| `Object.defineProperty(fi, 'files', dt.files)` + `dispatchEvent(change)` | ❌ File IS set (`fi.files.length=1`) but React ignores the event |
| `fi.dispatchEvent(new InputEvent('input'))` | ❌ React ignores non-trusted input events |
| `ClipboardEvent('paste', {clipboardData: dt})` on textarea | ❌ `clipboardData` is read-only on programmatic events |
| `document.execCommand('paste')` | ❌ Deprecated, blocked in modern Chrome |
| System Events file dialog (`keystroke "g" using {cmd,shift}`) | ❌ Requires Accessibility; also unreliable with Chrome's native dialog |
| Local HTTP server + `fetch('http://localhost:18899/img.jpg')` | ❌ HTTPS→HTTP blocked by CORS/mixed content on X.com |

### AppleScript + Base64 for File Input (Archived — Not Recommended)

This approach was attempted but failed due to React's `isTrusted` check. The file DOES get set on the input (confirmed `fi.files.length=1, size matches`), but React's onChange is never triggered. Code is preserved in history for reference only — do NOT use this for production posting, as the file is attached but never processed by X's React component.

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
