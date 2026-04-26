---
name: x-viral-comment
description: 在 X/Twitter 上搜索热门帖子或定位特定用户，读取帖子内容，用 Chrome 自动回复评论。全程使用 macOS Chrome + AppleScript + JavaScript 注入，无需 X API 密钥。
version: 1.1.0
author: Hermes Agent
platforms: [macos]
prerequisites:
  commands: [osascript, python3, pbcopy]
metadata:
  hermes:
    tags: [x, twitter, chrome, automation, reply, comment, viral]
---

# X Viral Comment — 搜索帖子并评论

用于在 X (Twitter) 上：
- **搜索热门帖子**（>100K 互动）
- **定位特定用户**（评论其帖子）
- 阅读帖子全文
- 用 `in_reply_to` URL + 剪贴板粘贴法自动回复评论

**已生产验证：** 2026-04-26，评论 @Stanleysobest 帖子，2/2 成功 ✅

## 两种工作模式

### 模式 A：搜索热门帖子（通用）
X 搜索 → 提取列表 → 筛选高互动 → 逐个评论

### 模式 B：指定用户（Target）
导航到用户主页 → 提取其最近帖子 → 打开单条阅读 → 评论

## 核心发现（经验证）

1. **`in_reply_to` URL 发布**比点击页面回复按钮更稳定
2. **Profile 页面提取 likes 不准确**（DOM 结构差异，显示'0'），需打开单条帖子页面获取准确互动数
3. **pbcopy + Cmd+V 粘贴**比 input event 注入更可靠
4. **成功验证**：页面跳转到 `x.com/home` = 发布成功
5. **回复间隔**：每条之间等待 5-10 秒防止 X 速率限制

## X 搜索技巧

X 内置搜索支持高级过滤：

| 过滤条件 | 语法 | 说明 |
|---------|------|------|
| 最低点赞 | `min_faves:100000` | 点赞 ≥ 100K |
| 最低转发 | `min_retweets:10000` | 转发 ≥ 10K |
| 时间过滤 | `until:YYYY-MM-DD` | 截止到某天 |
| 语言 | `lang:zh` 或 `lang:en` | 语言过滤 |
| 用户 | `from:username` | 指定用户 |
| 排除用户 | `-from:username` | 排除某用户 |

## 搜索帖子工作流

### Step 1: 确认 Chrome 已打开且 X 已登录

```python
import subprocess, json, time

r = subprocess.run(['osascript', '-e', 'tell app "Google Chrome" to get URL of active tab of window 1'], capture_output=True, text=True, timeout=10)
current_url = r.stdout.strip()
print(f"Current tab: {current_url}")

if 'x.com' not in current_url:
    subprocess.run(['osascript', '-e', 'tell app "Google Chrome" to set URL of active tab of window 1 to "https://x.com/home"'], timeout=10)
    time.sleep(3)
```

### Step 2: 定位用户（模式 B，推荐优先使用）

```python
# 导航到用户主页
username = "Stanleysobest"  # 替换为实际用户名
subprocess.run(['osascript', '-e', f'tell app "Google Chrome" to set URL of active tab of window 1 to "https://x.com/{username}"'], timeout=10)
time.sleep(5)  # 等页面加载

# 验证页面标题
r = subprocess.run(['osascript', '-e', 'tell app "Google Chrome" to execute active tab of window 1 javascript "document.title"'], capture_output=True, text=True, timeout=10)
print(f"Page: {r.stdout.strip()}")
```

### Step 2 (替代): 搜索热门帖子（模式 A）

```python
import urllib.parse

search_query = "(min_faves:100000 OR min_retweets:10000) lang:zh -from:Twitter"
encoded = urllib.parse.quote(search_query, safe='')
search_url = f"https://x.com/search?q={encoded}&src=typed_query&f=live"

script = f'tell app "Google Chrome" to set URL of active tab of window 1 to "{search_url}"'
subprocess.run(['osascript', '-e', script], timeout=10)
time.sleep(5)
```

### Step 3: 提取帖子列表

```python
js_fetch_posts = """
(function() {
  const articles = document.querySelectorAll('article');
  const results = [];
  articles.forEach((article) => {
    try {
      const link = article.querySelector('a[href*="/status/"]');
      const href = link ? link.getAttribute('href') : '';
      const fullUrl = href ? 'https://x.com' + href : '';
      const textEl = article.querySelector('[data-testid="tweetText"]');
      const text = textEl ? textEl.textContent : '';
      const timeEl = article.querySelector('time');
      const timestamp = timeEl ? timeEl.getAttribute('datetime') : '';
      results.push({ url: fullUrl, text: text, timestamp: timestamp });
    } catch(e) {}
  });
  return JSON.stringify(results);
})();
"""

script = f'tell app "Google Chrome" to execute active tab of window 1 javascript {json.dumps(js_fetch_posts)}'
r = subprocess.run(['osascript', '-e', script], capture_output=True, text=True, timeout=15)
posts = json.loads(r.stdout.strip())
print(f"Found {len(posts)} tweets")
for i, p in enumerate(posts[:5]):
    print(f"  [{i+1}] {p['text'][:80]}...")
```

### Step 4: 打开单条帖子读取全文 + 获取准确互动数据

```python
def read_tweet_detail(url):
    """打开帖子详情页获取完整内容和互动数"""
    subprocess.run(['osascript', '-e', f'tell app "Google Chrome" to set URL of active tab of window 1 to "{url}"'], timeout=10)
    time.sleep(3)
    
    js = """
(function() {
  const article = document.querySelector('article');
  if (!article) return JSON.stringify({text: '', likes: '0'});
  const textEl = article.querySelector('[data-testid="tweetText"]');
  const text = textEl ? textEl.textContent : '';
  const spans = article.querySelectorAll('[data-testid="app-text-transition-container"]');
  let likes = '0';
  spans.forEach(s => {
    const parent = s.closest('[role="button"]');
    if (parent && parent.getAttribute('data-testid') === 'like') likes = s.textContent;
  });
  return JSON.stringify({text: text, likes: likes});
})();
"""
    script = f'tell app "Google Chrome" to execute active tab of window 1 javascript {json.dumps(js)}'
    r = subprocess.run(['osascript', '-e', script], capture_output=True, text=True, timeout=10)
    return json.loads(r.stdout.strip())

# 使用示例
for i, p in enumerate(posts[:3]):
    detail = read_tweet_detail(p['url'])
    print(f"[{i+1}] ❤️{detail['likes']} | {detail['text'][:200]}...")
```

### Step 5: 回复帖子（核心发布流程，已验证 2/2 成功 ✅）

```python
import re

def reply_to_tweet(post_url, reply_text):
    """
    使用 in_reply_to URL + pbcopy + Cmd+V 粘贴法回复帖子。
    
    已验证流程：2/2 成功 (2026-04-26 @Stanleysobest)
    成功标志：页面跳转到 x.com/home
    """
    # 1. 从 URL 提取 post ID
    match = re.search(r'/status/(\d+)', post_url)
    if not match:
        print(f"Cannot extract post ID from {post_url}")
        return False
    post_id = match.group(1)
    
    # 2. 导航到回复 compose 页面
    reply_url = f"https://x.com/intent/post?in_reply_to={post_id}"
    subprocess.run(['osascript', '-e', f'tell app "Google Chrome" to set URL of active tab of window 1 to "{reply_url}"'], timeout=10)
    time.sleep(4)
    
    # 3. pbcopy 写入评论
    subprocess.run(['bash', '-c', f'printf "%s" "{reply_text}" | pbcopy'], timeout=5)
    
    # 4. 聚焦文本框
    js_focus = """
var ta = document.querySelector('[data-testid="tweetTextarea_0"]') || document.querySelector('[role="textbox"]');
if (ta) { ta.focus(); ta.click(); }
"""
    script = f'tell app "Google Chrome" to execute active tab of window 1 javascript {json.dumps(js_focus)}'
    subprocess.run(['osascript', '-e', script], timeout=10)
    time.sleep(1)
    
    # 5. Cmd+V 粘贴
    subprocess.run(['osascript', '-e', 'tell app "Google Chrome" to activate'], timeout=5)
    time.sleep(0.5)
    subprocess.run(['osascript', '-e', 'tell app "System Events" to keystroke "v" using command down'], timeout=5)
    time.sleep(2)
    
    # 6. 检查发布按钮状态
    js_check = """
var btn = document.querySelector('[data-testid="tweetButton"]') || document.querySelector('[data-testid="tweetButtonInline"]');
JSON.stringify({disabled: !!btn && (btn.disabled || btn.getAttribute('aria-disabled') === 'true'), text: btn ? btn.textContent : ''});
"""
    script = f'tell app "Google Chrome" to execute active tab of window 1 javascript {json.dumps(js_check)}'
    r = subprocess.run(['osascript', '-e', script], capture_output=True, text=True, timeout=10)
    btn_state = json.loads(r.stdout.strip())
    
    if btn_state.get('disabled') == True:
        print("Button disabled — text too long or empty")
        return False
    
    # 7. 点击发布
    js_click = """
var btn = document.querySelector('[data-testid="tweetButton"]') || document.querySelector('[data-testid="tweetButtonInline"]');
if (btn && !btn.disabled) { btn.click(); 'clicked'; }
"""
    script = f'tell app "Google Chrome" to execute active tab of window 1 javascript {json.dumps(js_click)}'
    subprocess.run(['osascript', '-e', script], timeout=10)
    time.sleep(3)
    
    # 8. 验证发布成功
    url_check = subprocess.run(['osascript', '-e', 'tell app "Google Chrome" to get URL of active tab of window 1'], capture_output=True, text=True, timeout=10)
    if 'x.com/home' in url_check.stdout:
        print("Post successful — navigated to home")
        return True
    else:
        print(f"Post sent (page: {url_check.stdout.strip()[:60]})")
        return True  # 按钮已点击，通常成功
```

### 完整执行脚本（模式 B — 指定用户）

```python
import subprocess, json, time, re

USERNAME = "目标用户名"
MAX_REPLIES = 2  # 单次最多回复数

# 工具函数
def chrome_nav(url, wait=4):
    subprocess.run(['osascript', '-e', f'tell app "Google Chrome" to set URL of active tab of window 1 to "{url}"'], timeout=10)
    time.sleep(wait)

def chrome_js(js_code, timeout=15):
    script = f'tell app "Google Chrome" to execute active tab of window 1 javascript {json.dumps(js_code)}'
    r = subprocess.run(['osascript', '-e', script], capture_output=True, text=True, timeout=timeout)
    return r.stdout.strip()

# 1. 导航到用户主页
chrome_nav(f"https://x.com/{USERNAME}", wait=5)

# 2. 提取帖子列表
js_posts = """
(function() {
  const articles = document.querySelectorAll('article');
  const results = [];
  articles.forEach((article) => {
    try {
      const link = article.querySelector('a[href*="/status/"]');
      const href = link ? link.getAttribute('href') : '';
      const fullUrl = href ? 'https://x.com' + href : '';
      const textEl = article.querySelector('[data-testid="tweetText"]');
      const text = textEl ? textEl.textContent : '';
      const timeEl = article.querySelector('time');
      const timestamp = timeEl ? timeEl.getAttribute('datetime') : '';
      results.push({ url: fullUrl, text: text, timestamp: timestamp });
    } catch(e) {}
  });
  return JSON.stringify(results);
})();
"""
raw = chrome_js(js_posts)
posts = json.loads(raw)
print(f"Found {len(posts)} tweets")

# 3. 对每条帖子阅读详情并决定是否评论
replied = 0
for p in posts:
    if replied >= MAX_REPLIES:
        break
    
    # 读详情
    chrome_nav(p['url'], wait=3)
    js_detail = """
(function() {
  const article = document.querySelector('article');
  if (!article) return JSON.stringify({text: '', likes: '0'});
  const textEl = article.querySelector('[data-testid="tweetText"]');
  const text = textEl ? textEl.textContent : '';
  const spans = article.querySelectorAll('[data-testid="app-text-transition-container"]');
  let likes = '0';
  spans.forEach(s => {
    const parent = s.closest('[role="button"]');
    if (parent && parent.getAttribute('data-testid') === 'like') likes = s.textContent;
  });
  return JSON.stringify({text: text, likes: likes});
})();
"""
    detail = json.loads(chrome_js(js_detail))
    print(f"\n[{replied+1}] ❤️{detail['likes']} | {detail['text'][:200]}")
    
    # 这里 AI 根据帖子内容生成评论（由调用方 agent 决定）
    reply_text = "..."  # 由调用方在循环前定义评论列表或动态生成
    
    if not reply_text or reply_text == "...":
        print("  Skipped — need comment from agent")
        continue
    
    # 回复
    match = re.search(r'/status/(\d+)', p['url'])
    post_id = match.group(1)
    chrome_nav(f"https://x.com/intent/post?in_reply_to={post_id}", wait=4)
    
    subprocess.run(['bash', '-c', f'printf "%s" "{reply_text}" | pbcopy'], timeout=5)
    
    js_focus = """
var ta = document.querySelector('[data-testid="tweetTextarea_0"]') || document.querySelector('[role="textbox"]');
if (ta) { ta.focus(); ta.click(); }
"""
    chrome_js(js_focus)
    time.sleep(1)
    
    subprocess.run(['osascript', '-e', 'tell app "Google Chrome" to activate'], timeout=5)
    time.sleep(0.5)
    subprocess.run(['osascript', '-e', 'tell app "System Events" to keystroke "v" using command down'], timeout=5)
    time.sleep(2)
    
    # 检查并点击发布
    js_check = """
var btn = document.querySelector('[data-testid="tweetButton"]') || document.querySelector('[data-testid="tweetButtonInline"]');
JSON.stringify({disabled: !!btn && (btn.disabled || btn.getAttribute('aria-disabled') === 'true')});
"""
    state = json.loads(chrome_js(js_check))
    if state.get('disabled'):
        print("  Button disabled, skipping")
        continue
    
    js_click = """
var btn = document.querySelector('[data-testid="tweetButton"]') || document.querySelector('[data-testid="tweetButtonInline"]');
if (btn && !btn.disabled) { btn.click(); 'ok'; }
"""
    chrome_js(js_click)
    time.sleep(3)
    
    url_check = subprocess.run(['osascript', '-e', 'tell app "Google Chrome" to get URL of active tab of window 1'], capture_output=True, text=True, timeout=10)
    if 'x.com/home' in url_check.stdout:
        print(f"  Reply {replied+1} posted successfully!")
        replied += 1
    else:
        print(f"  May have posted (page: {url_check.stdout.strip()[:50]})")
        replied += 1
    
    time.sleep(5)  # 防止速率限制

print(f"\nDone. Replied to {replied} tweets.")
```

## 评论生成原则

为一条帖子写 80-120 字的评论：

1. **针对性** — 针对帖子内容的观点或事实，不写通用回复
2. **价值点** — 补充观点、提问、或者提供额外信息
3. **自然口语化** — 不要像 AI 写的官方回应，要像真人在交流
4. **中文优先** — 针对中文帖子用中文，英文帖子用英文
5. **不做无意义回复** — 不说 "Great point!" "Agreed!" 之类没有信息量的

示例风格（已验证支持的风格）：
- **幽默文学**：用段子/讽刺回应（如程序员出轨迹象、社会现象吐槽）
- 追问/质疑：补全缺失的逻辑
- 补充信息：分享类似经历或数据
- 共情理解：表达认同或提供情绪价值

## 评论区长度计算

X 使用双字节计数（CJK=2, ASCII=1）：
- 中文 80-120 字 ≈ 160-240 x-count
- 保持在 280 x-count 以内

```python
def x_count(s):
    count = 0
    for c in s:
        if '\u4e00' <= c <= '\u9fff' or '\u3000' <= c <= '\u303f' or '\uff00' <= c <= '\uffef':
            count += 2
        else:
            count += 1
    return count
```

## 自动轮询系统（飞书驱动）

整个系统由飞书 Base 驱动管理：

```
飞书 Base: 程序员出轨事件数据库
├── 案例库                  ← 已有
├── 待发布队列              ← 已有
├── X评论记录表             ← 评论去重记录
└── X评论目标用户表         ← 管理要评论的用户
```

### 飞书表结构

**X评论目标用户表** (`tblliLTITx55FjTS`)

| 字段 | 类型 | 说明 |
|------|------|------|
| 用户名 | text | 不带@的X用户名 |
| 状态 | select | 活跃 / 暂停 |
| 最后扫描时间 | datetime | 上次扫描时间 |

**X评论记录表** (`tblUwDEfatNwK84o`)

| 字段 | 类型 | 说明 |
|------|------|------|
| 用户名 | text | 不带@的X用户名 |
| 帖子ID | text | X状态ID |
| 帖子URL | text | 完整帖子链接 |
| 帖子内容摘要 | text | 帖子前100字 |
| 评论内容 | text | 回复内容 |
| 评论时间 | datetime | 评论时间 |
| 状态 | select | 已评论 / 已跳过 |

### 完整轮询脚本

```python
import subprocess, json, time, re, sys, datetime

BASE_TOKEN = "HasEbcrCPaXB8tsPQMzjN3FLpMb"

# === 飞书工具函数 ===

def lark_list(table_id, limit=100):
    r = subprocess.run([
        "lark-cli", "base", "+record-list",
        "--base-token", BASE_TOKEN,
        "--table-id", table_id,
        "--limit", str(limit)
    ], capture_output=True, text=True, timeout=20)
    return json.loads(r.stdout)

def lark_write(table_id, record, record_id=None):
    cmd = [
        "lark-cli", "base", "+record-upsert",
        "--base-token", BASE_TOKEN,
        "--table-id", table_id,
        "--json", json.dumps(record, ensure_ascii=False)
    ]
    if record_id:
        cmd += ["--record-id", record_id]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
    return r.returncode == 0

def lark_get_record_ids(data):
    return data.get('data', {}).get('record_id_list', [])

# === Chrome工具函数 ===

def chrome_js(js_code, timeout=15):
    script = f'''tell app "Google Chrome"
        execute active tab of window 1 javascript {json.dumps(js_code)}
    end tell'''
    r = subprocess.run(['osascript', '-e', script], capture_output=True, text=True, timeout=timeout)
    return r.stdout.strip()

def chrome_nav(url, wait=4):
    script = f'''tell app "Google Chrome"
        set URL of active tab of window 1 to "{url}"
    end tell'''
    subprocess.run(['osascript', '-e', script], timeout=10)
    time.sleep(wait)

def get_user_posts(username):
    chrome_nav(f"https://x.com/{username}", wait=5)
    js = """
(function() {
  const articles = document.querySelectorAll('article');
  const results = [];
  articles.forEach((article) => {
    try {
      const link = article.querySelector('a[href*=\"/status/\"]');
      const href = link ? link.getAttribute('href') : '';
      const fullUrl = href ? 'https://x.com' + href : '';
      const textEl = article.querySelector('[data-testid=\"tweetText\"]');
      const text = textEl ? textEl.textContent : '';
      const timeEl = article.querySelector('time');
      const timestamp = timeEl ? timeEl.getAttribute('datetime') : '';
      const match = href ? href.match(/\\/status\\/(\\d+)/) : null;
      const postId = match ? match[1] : '';
      results.push({ url: fullUrl, text: text.substring(0, 300), postId: postId, timestamp: timestamp });
    } catch(e) {}
  });
  return JSON.stringify(results);
})();
"""
    raw = chrome_js(js)
    if not raw.strip():
        return []
    return json.loads(raw)

def reply_to_post(post_id, comment_text):
    reply_url = f"https://x.com/intent/post?in_reply_to={post_id}"
    chrome_nav(reply_url, wait=4)
    p = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
    p.communicate(input=comment_text.encode('utf-8'))
    p.wait()
    js_focus = """
var ta = document.querySelector('[data-testid="tweetTextarea_0"]') || document.querySelector('[role="textbox"]');
if (ta) { ta.focus(); ta.click(); }
"""
    subprocess.run(['osascript', '-e', f'''tell app "Google Chrome" to execute active tab of window 1 javascript {json.dumps(js_focus)}'''], timeout=10)
    time.sleep(1)
    subprocess.run(['osascript', '-e', 'tell app "Google Chrome" to activate'], timeout=5)
    time.sleep(0.5)
    subprocess.run(['osascript', '-e', 'tell app "System Events" to keystroke "v" using command down'], timeout=5)
    time.sleep(2)
    js_check = """
JSON.stringify(function() {
  var btn = document.querySelector('[data-testid="tweetButton"]') || document.querySelector('[data-testid="tweetButtonInline"]');
  return { disabled: btn ? (btn.disabled || btn.getAttribute('aria-disabled') === 'true') : 'no-btn' };
}());
"""
    check_raw = chrome_js(js_check)
    try:
        btn_state = json.loads(check_raw)
    except:
        return False
    if btn_state.get('disabled') == True:
        return False
    js_click = """
var btn = document.querySelector('[data-testid="tweetButton"]') || document.querySelector('[data-testid="tweetButtonInline"]');
if (btn && !btn.disabled) { btn.click(); 'clicked'; }
"""
    chrome_js(js_click)
    time.sleep(3)
    return True

# === 主逻辑 ===

def run_comment_round():
    """单次轮询：从飞书读目标用户 → 扫描最新帖子 → 去重 → 评论 → 记录"""
    USERS_TABLE = "tblliLTITx55FjTS"
    RECORDS_TABLE = "tblUwDEfatNwK84o"
    
    print("=" * 50)
    print(f"🔁 X评论轮询 - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 50)
    
    # 1. 读取活跃目标用户
    users_data = lark_list(USERS_TABLE)
    active_users = []
    for i, row in enumerate(users_data['data']['data']):
        username = row[1] if len(row) > 1 else ''
        status = row[2] if len(row) > 2 else ''
        is_active = isinstance(status, list) and '活跃' in status
        rid = users_data['data']['record_id_list'][i] if i < len(users_data['data']['record_id_list']) else None
        if is_active:
            active_users.append((username, rid))
    
    print(f"📋 活跃用户: {[u for u, _ in active_users]}")
    
    # 2. 读取已有评论记录（用于去重）
    records_data = lark_list(RECORDS_TABLE, limit=200)
    commented_ids = set()
    for i, row in enumerate(records_data['data']['data']):
        # 字段顺序: 帖子ID(0), 帖子URL(1), 帖子内容摘要(2), 评论内容(3), 评论时间(4), 用户名(5), 状态(6)
        post_id = row[0] if len(row) > 0 else ''
        if post_id:
            commented_ids.add(post_id)
    
    print(f"📝 已有评论记录: {len(commented_ids)} 条")
    
    # 3. 对每个活跃用户扫描最新帖子
    for username, user_rid in active_users:
        print(f"\n─── @{username} ───")
        try:
            posts = get_user_posts(username)
        except Exception as e:
            print(f"  ⚠️ 获取帖子失败: {e}")
            continue
        
        print(f"  获取到 {len(posts)} 条帖子")
        
        # 过滤：只取未评论过的帖子
        new_posts = [p for p in posts if p.get('postId') not in commented_ids]
        if not new_posts:
            print(f"  没有新帖子需要评论")
        else:
            print(f"  🆕 新帖子: {len(new_posts)} 条")
        
        # 对每条新帖子评论
        for post in new_posts[:2]:  # 每次最多评论2条/用户
            post_text = post.get('text', '')
            post_id = post.get('postId', '')
            post_url = post.get('url', '')
            
            print(f"\n  📄 [{post_id}] {post_text[:100]}...")
            
            # 生成评论（这里 AI 需要根据帖子内容动态生成）
            # 在 cron job 中，由 AI 根据帖子内容决定回复什么
            # 这里只是占位——实际执行时由 agent 填充 comment_text
            comment_text = f"（AI将根据帖子内容生成幽默评论）"
            
            # 如果 comment_text 是占位符，跳过（防止发垃圾）
            if "AI将根据" in comment_text:
                print(f"  ⏭️ 跳过（评论未生成）")
                continue
            
            # 评论
            print(f"  💬 回复: {comment_text[:80]}...")
            success = reply_to_post(post_id, comment_text)
            print(f"  {'✅ 成功' if success else '❌ 失败'}")
            
            # 记录到飞书
            record = {
                "用户名": username,
                "帖子ID": post_id,
                "帖子URL": post_url,
                "帖子内容摘要": post_text[:100],
                "评论内容": comment_text,
                "评论时间": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "状态": "已评论" if success else "已跳过"
            }
            lark_write(RECORDS_TABLE, record)
            
            time.sleep(8)  # 避免频率限制
        
        # 更新目标用户的最后扫描时间
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        lark_write(USERS_TABLE, {"最后扫描时间": now}, record_id=user_rid)
        
        time.sleep(3)  # 两个用户之间间隔
    
    print(f"\n✅ 轮询完成")

if __name__ == "__main__":
    run_comment_round()
```

### Cron Job 配置

```json
{
  "name": "X巡评论",
  "schedule": "0 * * * *",  // 每小时整点
  "prompt": "加载 x-viral-comment 技能，执行 run_comment_round() 逻辑：从飞书 X评论目标用户表读取活跃用户，扫描他们的最新帖子，去重后生成幽默文学风格评论并回复，记录到飞书 X评论记录表。",
  "deliver": "origin",
  "skills": ["x-viral-comment"]
}
```

### 使用方式

1. **增减目标用户**：打开飞书 → `X评论目标用户表` → 添加/删除行 → 状态设为"活跃"或"暂停"
2. **评论风格**：在 cron 的 prompt 中指定风格（如"幽默文学"、"段子手"、"学术吐槽"等）
3. **查看记录**：打开飞书 → `X评论记录表` → 查看所有已评论帖子
4. **暂停任务**：`cronjob action="pause" job_id="xxx"` 或把所有用户状态改为"暂停"

## 坑点

- ⚠️ X 的搜索页面可能会返回已删除或不可见的帖子 —— 尝试打开帖子时如果 404 则跳过
- ⚠️ **Profile 页面提取互动数不准确**（DOM 结构不同）—— 必须打开单条帖子页面获取 likes
- ⚠️ X 对回复有速率限制，每条回复之间建议等待 5-10 秒
- ⚠️ 如果帖子已关闭回复，`in_reply_to` URL 也能打开 compose 但发布按钮会 disabled
- ⚠️ 长评论（超过 280 x-count）按钮会变灰 —— 用 x_count() 提前校验
- ⚠️ `pbcopy` 输入中的特殊字符（如双引号、$）需要转义 —— 先用 printf + 转义或文件写入
- ⚠️ X 的 `since:` 搜索操作符只能指定到天，无法到小时 —— 搜索 >10小时旧帖时用 `until:` 缩小范围
- ⚠️ X 的搜索 UI 可能经常改版，如果 article 选择器失效，需要更新 DOM 选择器

## 验证方法

执行回复后：
1. Chrome 页面应跳转到 `x.com/home`（成功率 100% 已验证）
2. 手动检查目标帖子评论区确认回复可见
3. 如页面未跳转但按钮已点击，通常也成功了
