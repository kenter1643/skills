---
name: article-to-x-articles
description: 接收文章链接 → 提取文字与图片 → 去水印 → 改写为原创 → 用 X Articles 长文章发布到 X。全程 Chrome 自动化，无需 API 密钥。
version: 1.0.0
author: Hermes Agent
platforms: [macos]
prerequisites:
  commands: [osascript, python3, pbcopy]
  python_packages: [Pillow, readability-lxml, lxml]
metadata:
  hermes:
    tags: [x, twitter, article, publish, rewrite, web]
---

# Article to X Articles — 文章提取+改写+X长文发布

将网页文章转化为 X Articles（长文）的全流程工具。

## 核心流程

```
用户发链接 → 提取正文/图片 → 下载图片去水印 → AI改写原创 → X Articles发布
```

## Step 1: 提取文章内容

### 方案 A：浏览器注入（无需额外依赖）

使用 Chrome 加载文章URL，通过 JavaScript 提取正文和图片：

```python
import subprocess, json, time, re, os
from urllib.parse import urljoin

def chrome_js(js_code, timeout=15):
    script = f'''tell app "Google Chrome"
        execute active tab of window 1 javascript {json.dumps(js_code)}
    end tell'''
    r = subprocess.run(['osascript', '-e', script], capture_output=True, text=True, timeout=timeout)
    return r.stdout.strip()

def extract_article(url):
    """用 Chrome 提取文章内容"""
    # 1. 导航到文章
    script = f'''tell app "Google Chrome"
        set URL of active tab of window 1 to "{url}"
    end tell'''
    subprocess.run(['osascript', '-e', script], timeout=10)
    time.sleep(5)  # 等待页面加载
    
    # 2. 提取标题、正文、图片
    js = """
(function() {
  // 提取标题
  let title = document.title;
  
  // 尝试多种选择器找文章标题
  const titleEl = document.querySelector('h1') || 
                  document.querySelector('article h1') ||
                  document.querySelector('.article-title') ||
                  document.querySelector('.post-title');
  if (titleEl) title = titleEl.textContent.trim();
  
  // 提取正文（尝试多种选择器）
  let content = '';
  const article = document.querySelector('article') || 
                  document.querySelector('.article-content') ||
                  document.querySelector('.post-content') ||
                  document.querySelector('.entry-content') ||
                  document.querySelector('[role="main"]');
  
  if (article) {
    // 获取所有文本段落
    const paragraphs = article.querySelectorAll('p, h2, h3, h4, blockquote, li');
    let texts = [];
    paragraphs.forEach(p => {
      const t = p.textContent.trim();
      if (t.length > 10) texts.push(t);
    });
    content = texts.join('\\n\\n');
  } else {
    // fallback: 取 body 文本
    const body = document.body;
    if (body) content = body.innerText.substring(0, 10000);
  }
  
  // 提取所有图片
  const images = [];
  const imgs = document.querySelectorAll('article img, .article-content img, .post-content img, .entry-content img');
  imgs.forEach(img => {
    const src = img.getAttribute('src') || img.getAttribute('data-src') || '';
    if (src && !src.includes('icon') && !src.includes('emoji') && !src.includes('avatar')) {
      // 优先用大图
      const dataSrc = img.getAttribute('data-original') || img.getAttribute('data-src-large') || '';
      images.push(dataSrc || src);
    }
  });
  
  return JSON.stringify({title: title, content: content, images: images.slice(0, 10)});
})();
"""
    raw = chrome_js(js)
    return json.loads(raw)
```

### 方案 B：Python 库提取（推荐，更干净）

需要先安装：`pip install readability-lxml lxml Pillow`

```python
import requests
from readability import Document
from bs4 import BeautifulSoup
import re

def extract_article_python(url):
    """用 readability-lxml 提取文章，更可靠"""
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}
    resp = requests.get(url, headers=headers, timeout=30)
    resp.encoding = resp.apparent_encoding
    
    doc = Document(resp.text)
    title = doc.title()
    
    # 提取正文 HTML
    content_html = doc.summary()
    
    # 用 BeautifulSoup 提取纯文本和图片
    soup = BeautifulSoup(content_html, 'lxml')
    
    # 段落文本
    paragraphs = []
    for p in soup.find_all(['p', 'h2', 'h3', 'h4', 'blockquote', 'li']):
        t = p.get_text(strip=True)
        if len(t) > 10:
            paragraphs.append(t)
    content = '\n\n'.join(paragraphs)
    
    # 图片
    images = []
    base_url = url[:url.rfind('/')+1] if '/' in url else url
    for img in soup.find_all('img'):
        src = img.get('src') or img.get('data-src') or ''
        if src and not src.startswith('data:'):
            if not src.startswith('http'):
                src = urljoin(url, src)
            if not any(kw in src.lower() for kw in ['icon', 'avatar', 'emoji', 'logo', 'favicon']):
                images.append(src)
    
    return {'title': title, 'content': content, 'html': content_html, 'images': images}

from urllib.parse import urljoin
```

## Step 2: 下载图片并裁剪水印

```python
from PIL import Image
import requests, io, os

def download_and_crop_image(img_url, output_path, watermark_crop_bottom=0):
    """下载图片并裁剪底部水印，返回文件路径"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        resp = requests.get(img_url, headers=headers, timeout=20)
        img = Image.open(io.BytesIO(resp.content))
        
        if watermark_crop_bottom > 0:
            # 从底部裁剪指定像素
            w, h = img.size
            img = img.crop((0, 0, w, h - watermark_crop_bottom))
        
        # 转为 RGB 保存为 JPEG
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        img.save(output_path, 'JPEG', quality=90)
        return output_path
    except Exception as e:
        print(f"  ⚠️ 下载失败 {img_url[:60]}: {e}")
        return None

def auto_crop_watermark(image_path):
    """自动检测并裁剪底部水印区域（启发式：底部固定高度区域）"""
    img = Image.open(image_path)
    w, h = img.size
    
    # 大多数文章水印在底部 30-60 像素区域
    # 检测底部 60px 是否为纯色/半透明
    bottom_strip = img.crop((0, h-60, w, h))
    pixels = list(bottom_strip.getdata())
    
    # 如果底部大部分是半透明或相似颜色，裁剪掉
    # 简化策略：默认裁剪底部 40px
    crop_h = 0
    # 检查底部是否有明显的logo区域
    for y in range(h-5, h-1):
        row_pixels = [img.getpixel((x, y))[:3] for x in range(0, w, 5)]
        # 如果某行像素几乎一样（纯色），可能是水印背景
        unique_colors = len(set(row_pixels))
        if unique_colors <= 3:
            crop_h = h - y + 5
            break
    
    if crop_h > 0 and crop_h < 100:  # 限制最大裁剪 100px
        img = img.crop((0, 0, w, h - crop_h))
        img.save(image_path, 'JPEG', quality=90)
    
    return image_path
```

## Step 3: AI 改写原创

文章改写原则：
1. 保留核心事实和数据，不瞎编
2. 结构调整：原文→时间顺序→问题展开→结论，可以改为 观点→论据→对比→升华
3. 语言风格：改为X口吻（短句、亮观点、带态度）
4. 增加「原创价值」：补充分析角度、个人观点、行业关联
5. 长度：适合 X Articles 的 500-2000 字长文

```python
def rewrite_article(title, content, style_prompt=""):
    """改写为原创（由AI在调用时根据内容生成）
    
    rewrite_prompt = f'''
    改写下面这篇文章为原创。要求：
    1. 保留核心事实和数据
    2. 改变叙述结构和逻辑顺序
    3. 增加个人分析视角和评论
    4. 使用口语化、有观点的X语言风格
    5. 段落短小精悍，每段2-4句
    6. 总字数：500-1200字
    
    原文标题：{title}
    原文内容：{content[:2000]}
    '''
    
    实际由 agent 根据文章内容自行调用 AI 生成改写
    """
    pass
```

## Step 4: 发布到 X Articles

X Articles 发布界面：`https://x.com/i/articles/new`

### 发布工作流

```python
import subprocess, json, time, re

def publish_x_article(title, body_text, cover_image_path=None):
    """通过 Chrome 自动化发布 X Articles"""
    
    # 1. 导航到 X Articles 创作页面
    script = '''tell app "Google Chrome"
        set URL of active tab of window 1 to "https://x.com/i/articles/new"
    end tell'''
    subprocess.run(['osascript', '-e', script], timeout=10)
    time.sleep(6)
    
    # 2. 填写标题
    # X Articles 标题框
    js_focus_title = """
var titleInput = document.querySelector('[data-testid="articleTitle"]') || 
                   document.querySelector('div[contenteditable="true"][aria-label*="Title"]') ||
                   document.querySelector('div[aria-label*="title" i]');
if (titleInput) titleInput.focus();
"""
    script = f'''tell app "Google Chrome"
        execute active tab of window 1 javascript {json.dumps(js_focus_title)}
    end tell'''
    subprocess.run(['osascript', '-e', script], timeout=10)
    time.sleep(1)
    
    # 粘贴标题
    p = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
    p.communicate(input=title.encode('utf-8'))
    p.wait()
    subprocess.run(['osascript', '-e', 'tell app "Google Chrome" to activate'], timeout=5)
    time.sleep(0.3)
    subprocess.run(['osascript', '-e', 'tell app "System Events" to keystroke "v" using command down'], timeout=5)
    time.sleep(2)
    
    # 3. 填写正文
    # 正文编辑区域
    js_focus_body = """
var bodyInput = document.querySelector('[data-testid="articleBody"]') ||
                document.querySelectorAll('div[contenteditable="true"]')[1] ||
                document.querySelector('div[contenteditable="true"][aria-label*="body" i]') ||
                document.querySelector('div[contenteditable="true"][aria-label*="text" i]');
if (bodyInput) bodyInput.focus();
"""
    script = f'''tell app "Google Chrome"
        execute active tab of window 1 javascript {json.dumps(js_focus_body)}
    end tell'''
    subprocess.run(['osascript', '-e', script], timeout=10)
    time.sleep(1)
    
    # 分段粘贴（X Articles 支持富文本，一段一段粘贴效果更好）
    paragraphs = body_text.split('\n\n')
    for i, para in enumerate(paragraphs):
        if not para.strip():
            continue
        p = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
        p.communicate(input=para.strip().encode('utf-8'))
        p.wait()
        subprocess.run(['osascript', '-e', 'tell app "System Events" to keystroke "v" using command down'], timeout=5)
        time.sleep(1.5)
        # 每段后加回车（除非是最后一段）
        if i < len(paragraphs) - 1:
            subprocess.run(['osascript', '-e', 'tell app "System Events" to key code 36'], timeout=5)
            time.sleep(0.5)
            subprocess.run(['osascript', '-e', 'tell app "System Events" to key code 36'], timeout=5)
            time.sleep(0.5)
    
    time.sleep(2)
    
    # 4. 如果提供了封面图，上传封面
    if cover_image_path and os.path.exists(cover_image_path):
        pass  # 上传封面逻辑（X Articles 上传按钮点击+文件选择）
    
    # 5. 点击发布
    js_publish = """
var pubBtn = document.querySelector('[data-testid="publishArticleButton"]') ||
              document.querySelector('[data-testid="publish"]') ||
              document.querySelector('button:has(span:text("Publish"))') ||
              document.querySelector('button:has(span:text("发布"))');
if (pubBtn && !pubBtn.disabled) { pubBtn.click(); 'clicked'; } else { 'no-btn'; }
"""
    script = f'''tell app "Google Chrome"
        execute active tab of window 1 javascript {json.dumps(js_publish)}
    end tell'''
    subprocess.run(['osascript', '-e', script], timeout=10)
    time.sleep(4)
    
    # 6. 确认发布（X 可能有二次确认弹窗）
    js_confirm = """
var confirmBtn = document.querySelector('[data-testid="confirmPublish"]');
if (confirmBtn && !confirmBtn.disabled) { confirmBtn.click(); 'confirmed'; } else { 'no-confirm'; }
"""
    script = f'''tell app "Google Chrome"
        execute active tab of window 1 javascript {json.dumps(js_confirm)}
    end tell'''
    subprocess.run(['osascript', '-e', script], timeout=10)
    time.sleep(3)
    
    # 获取发布后的 URL
    current_url = subprocess.run(
        ['osascript', '-e', 'tell app "Google Chrome" to get URL of active tab of window 1'],
        capture_output=True, text=True, timeout=10
    ).stdout.strip()
    
    return current_url
```

## 完整执行流程（Agent 使用）

```python
# 1. 用户发来文章链接 → 记录到待处理队列
# 2. 用 extract_article() 或 extract_article_python() 提取内容
# 3. 用 download_and_crop_image() 下载所有图片 → 保存到 tweet_images/{article_title}/
# 4. AI 改写为原创（Agent 根据文章内容生成）
# 5. 发布到 X Articles
# 6. 返回发布链接给用户
```

## X Articles 界面选择器（需要实测确认）

X 的 Articles 发布界面可能变化，以下选择器可能需要适配：

| 功能 | 可能的选择器 |
|------|------------|
| 标题输入 | `[data-testid="articleTitle"]` / `div[contenteditable="true"]` |
| 正文编辑 | `[data-testid="articleBody"]` / `div[contenteditable="true"]:nth-child(2)` |
| 发布按钮 | `[data-testid="publishArticleButton"]` |
| 确认发布 | `[data-testid="confirmPublish"]` |
| 上传封面 | 文件输入框 |

## 坑点

- ⚠️ X Articles 是分阶段上线的功能，`/i/articles/new` 可能不可用 → 需要先确认用户账号是否有此功能
- ⚠️ 如果不可用，fallback：分段发长推文（发帖+引用回复串）
- ⚠️ 文章图片的 URL 可能使用懒加载（`data-src` 而不是 `src`）—— 两种都要检查
- ⚠️ 部分网站（微信、知乎等）有反爬机制，可能需要在浏览器中人工登录后才能看到完整内容
- ⚠️ 水印通常在图片右下角 30-60px 区域，裁剪策略需要根据实际图片调整
- ⚠️ X Articles 正文是富文本编辑器，不是简单的 textarea —— 粘贴时格式保留情况需要实测
- ⚠️ 长文章分段粘贴后，每段间的换行可能需要手动调整