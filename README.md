# skills

Marvis 助手技能集合。

## 技能列表

| 技能 | 描述 | 版本 |
|------|------|:--:|
| [主理人](zhuliren-skill/) | 从公开资料生成可运行的人物 Skill，内置投资人 V2 证据化蒸馏、迁移审计与专项质检 | V2 |
| [沃伦·巴菲特](buffett-perspective/) | 企业所有者型价值投资、估值、资本配置与永久损失框架 | V2-A |
| [李录](li-lu-perspective/) | 知识诚实、深度企业研究、长期复利与全球价值投资框架 | V2-A |
| [杰西·利弗莫尔](jesse-livermore-perspective/) | 趋势确认、试探仓、顺势加仓与永久资本保护框架 | V2-B |
| [林广茂](lin-guangmao-perspective/) | 商品供需、交割验证、趋势持有与方法适配框架 | V2-B |
| [缠中说禅](chzhshch-perspective/) | 《教你炒股票》108课的走势结构、完全分类与操作框架 | V2-B |
| [段永平](duan-yongping-perspective/) | 经营、投资与人生决策框架，强调本分、能力圈和长期主义 | 1.0 |
| [徐翔](xu-xiang-perspective/) | 投资人 V2 兼容迁移样例，基于可核验公开行为提炼的合法短线交易框架 | V2-B |
| [review-paper-blueprint](review-paper-blueprint/) | 综述论文写作蓝本：按导师审核通过的综述骨架与 Chem. Soc. Rev. 高质量综述写法规划、撰写、改写和检查英文综述，含英文行文规则与终检清单 | 1.0 |
| [yikun-figure-style](yikun-figure-style/) | 论文绘图：按 RSC/IEEE/Elsevier 投稿标准用 matplotlib 出 600 dpi 图，含个人风格库 S0–S6（选型缩略图）、示意图图标、数据来源规则与图注写作规范 | 1.0 |
| [limit-up-1to2-prediction](limit-up-1to2-prediction/) | A股短线首板晋级二板预测，整合宏观情绪+板块拥挤度+主线过热+基本面过滤+技术面评分 | v3.4 |
| [api-doc-generator](api-doc-generator/) | API 文档生成器 | - |
| [generator-code-completer](generator-code-completer/) | 代码补全生成器 | - |
| [javaDevelop](javaDevelop/) | Java 开发辅助 | - |
| [x-viral-writer](x-viral-writer/) | 中文 X 爆款文案：科技爆料、吐槽、短帖、反讽与事实核验规则 | 1.0.0 |
| [x-insight-commentator](x-insight-commentator/) | 中文 X 深度评论：检索案例、数据佐证、独立思考与可复制文案 | 1.0.0 |
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
│   ├── docs/                       # 投资人 V2 详细说明
│   ├── scripts/                    # 字幕、研究合并与质量检查工具
│   ├── references/                 # 提炼框架与生成模板
│   └── examples/                   # 人物 Skill 示例
├── chzhshch-perspective/           # 缠中说禅走势结构框架
├── buffett-perspective/            # 巴菲特企业所有者型价值投资
├── li-lu-perspective/              # 李录深度企业研究与长期复利
├── jesse-livermore-perspective/    # 利弗莫尔趋势与交易纪律
├── lin-guangmao-perspective/       # 林广茂商品趋势与交割
├── duan-yongping-perspective/      # 段永平经营与投资框架
├── xu-xiang-perspective/           # 徐翔公开行为交易框架
├── review-paper-blueprint/         # 综述论文写作蓝本
│   └── SKILL.md                    # 技能定义
├── yikun-figure-style/             # 论文绘图风格与图注写作
│   ├── SKILL.md                    # 技能定义（含完整代码）
│   ├── README.md                   # 使用说明与来源许可
│   ├── scripts/                    # pub_fig / pub_schem / demos
│   └── examples/                   # 风格库示例图
├── limit-up-1to2-prediction/       # 涨停二板预测 v3.4
│   ├── SKILL.md                    # 技能定义
│   ├── meta.json                   # 元数据
│   └── README.md                   # 使用说明
├── api-doc-generator/
├── generator-code-completer/
├── javaDevelop/
├── x-viral-writer/                # 中文 X 爆款文案
│   └── SKILL.md
├── x-insight-commentator/         # 中文 X 深度评论
│   └── SKILL.md
├── social-media/
├── finance/
└── social/
```
