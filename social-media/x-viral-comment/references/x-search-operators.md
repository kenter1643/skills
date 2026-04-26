# X 搜索操作符参考

## 基础操作符

| 操作符 | 示例 | 说明 |
|--------|------|------|
| 关键词 | `AI` | 包含该关键词 |
| OR | `AI OR 人工智能` | 包含任一关键词 |
| -排除 | `AI -机器人` | 包含 AI 但不包含 机器人 |
| 短语 | `"机器学习"` | 精确匹配 |
| () 分组 | `(AI OR 人工智能) 创业` | 分组逻辑 |

## 高级过滤

| 操作符 | 示例 | 说明 |
|--------|------|------|
| `from:` | `from:elonmusk` | 指定用户的帖子 |
| `to:` | `to:elonmusk` | 回复该用户的帖子 |
| `@` | `@elonmusk` | 提到该用户 |
| `url:` | `url:youtube.com` | 包含该 URL |
| `lang:` | `lang:zh` | 语言 (zh/en/ja 等) |
| `has:links` | `AI has:links` | 包含链接 |
| `has:images` | `AI has:images` | 包含图片 |
| `has:videos` | `AI has:videos` | 包含视频 |
| `has:media` | `AI has:media` | 包含媒体 |
| `has:mentions` | `has:mentions` | 包含 @ 提及 |
| `is:reply` | `is:reply` | 仅回复 |
| `is:quote` | `is:quote` | 仅引用转发 |
| `is:verified` | `is:verified` | 仅认证用户 |
| `-is:retweet` | `-is:retweet` | 排除转发 |

## 时间过滤

| 操作符 | 示例 | 说明 |
|--------|------|------|
| `since:` | `since:2026-04-20` | 从该日期之后 |
| `until:` | `until:2026-04-26` | 到该日期之前 |

## 互动过滤

| 操作符 | 示例 | 说明 |
|--------|------|------|
| `min_faves:` | `min_faves:100000` | 最低点赞数 |
| `min_retweets:` | `min_retweets:10000` | 最低转发数 |
| `min_replies:` | `min_replies:5000` | 最低回复数 |

## 实用查询组合

```
# 中文高热度帖子（>10万赞或>1万转发，过去24小时）
(min_faves:100000 OR min_retweets:10000) lang:zh since:2026-04-25

# 英文 AI 相关热门
(AI OR "artificial intelligence") min_faves:100000 lang:en since:2026-04-25

# 编程/技术类热门
(code OR programming OR engineer) min_faves:50000 lang:en since:2026-04-25

# 中文幽默段子（带图片的）
(段子 OR 搞笑 OR 哈哈哈) has:images min_faves:50000 lang:zh

# 重磅爆料/爆料帖
(爆料 OR 曝光 OR 实锤) min_faves:100000 lang:zh

# 行业热点讨论
(程序员 OR 大厂 OR 互联网) min_faves:50000 lang:zh

# 职场话题
(离职 OR 裁员 OR 工资) min_faves:30000 lang:zh
```

## 获取 >10 小时前的帖子

由于 X 搜索结果默认按热度排序且偏向近期内容，要找到 >10 小时前的帖子：

```python
from datetime import datetime, timedelta

# 设置时间窗口：10小时前到20小时前
today = datetime.now()
ten_hours_ago = today - timedelta(hours=10)
twenty_hours_ago = today - timedelta(hours=20)

# 生成搜索查询
query = f"(min_faves:100000 OR min_retweets:10000) lang:zh since:{twenty_hours_ago.strftime('%Y-%m-%d')}"
```

注意：X 的 `since:` 操作符只能指定到天，无法到小时。
