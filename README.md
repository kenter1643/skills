# skills

Marvis 助手技能集合。

## 技能列表

| 技能 | 描述 | 版本 |
|------|------|:--:|
| [主理人](zhuliren-skill/) | 从人物或主题的公开资料中提炼思维框架，并生成可运行的人物 Skill | fork |
| [limit-up-1to2-prediction](limit-up-1to2-prediction/) | A股短线首板晋级二板预测，整合宏观情绪+板块拥挤度+主线过热+基本面过滤+技术面评分 | v3.4 |
| [api-doc-generator](api-doc-generator/) | API 文档生成器 | - |
| [generator-code-completer](generator-code-completer/) | 代码补全生成器 | - |
| [javaDevelop](javaDevelop/) | Java 开发辅助 | - |
| [social-media](social-media/) | 社交媒体辅助 | - |
| [finance](finance/) | 金融相关 | - |
| [social](social/) | 社交相关 | - |

## 目录结构

```
skills/
├── README.md
├── .claude/                        # Claude/Codex 配置
├── zhuliren-skill/                 # 主理人：人物思维框架蒸馏与 Skill 生成
│   ├── SKILL.md                    # 技能定义
│   ├── README.md                   # 使用说明与来源声明
│   ├── scripts/                    # 字幕、研究合并与质量检查工具
│   ├── references/                 # 提炼框架与生成模板
│   └── examples/                   # 人物 Skill 示例
├── limit-up-1to2-prediction/       # 涨停二板预测 v3.4
│   ├── SKILL.md                    # 技能定义
│   ├── meta.json                   # 元数据
│   └── README.md                   # 使用说明
├── api-doc-generator/
├── generator-code-completer/
├── javaDevelop/
├── social-media/
├── finance/
└── social/
```
