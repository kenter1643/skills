---
name: "review-paper-blueprint"
description: "按导师审核通过的蓝本综述（GenAI × 电化学储能，纳/微尺度视角）的章节骨架、段落套路和论证思路来规划、撰写、改写或检查英文综述论文。用户提到写综述、review paper、综述大纲、章节安排、参考导师给的那篇综述、ASSB/SOH 综述、按蓝本改稿时使用。"
---

# 综述论文蓝本（Review Paper Blueprint）

蓝本来源：导师审核通过的综述 *GenAI for scientific discovery in electrochemical energy storage: State-of-the-art and perspectives from nano- and micro-scale*（R1 修订稿，正文约 28 页、115 篇文献、5 图 2 表）。

本 skill 提炼的是它的**结构、段落套路和论证思路**，用于写新的综述。只借骨架，不借句子：所有正文必须针对新主题重新写，不得照搬或近似改写蓝本原句（用户后续还要查重降重）。

## 一、核心思路：三轴矩阵

蓝本全篇由三个轴撑起来，动笔前先和用户把这三个轴定下来：

| 轴 | 蓝本中的取值 | 作用 |
|---|---|---|
| 方法轴（技术） | Autoencoders / GANs / Diffusion & Flow / Foundation models | 构成第 2 章“方法总览” |
| 对象轴（应用体系） | 燃料电池 / 锂离子电池 / 液流电池 | 每个对象一章（第 3–5 章） |
| 视角轴（贯穿主线） | 纳米尺度 + 微米尺度 | 写进标题，并在每一节反复回扣 |

要点：
- 视角轴是这篇综述区别于同类综述的“卖点”。它出现在标题、摘要、贡献点、每个方法小节、每个应用小节、每个挑战小节里。新综述也要选一个这样的视角并贯穿到底。
- 对象章内部的小节按“任务 × 尺度”划分：材料发现/合成（纳米）→ 结构设计（微米）→ 性能预测 → 相互作用优化或自动化实验。
- 标题公式：`[技术] for scientific discovery in [领域]: State-of-the-art and perspectives from [视角]`。

迁移示例（仅为建议，须与用户确认）：
- ASSB × AI4Science：方法轴可取 ML 势函数 / 生成模型 / 基础模型与 LLM / 自主实验；对象轴可取固态电解质 / 界面 / 电极与电芯；视角轴可取多尺度或“计算—实验闭环”。
- 电池 SOH 综述：方法轴取模型类别；对象轴取数据来源或应用场景（实验室、车端、储能电站）；视角轴取如“可迁移性/基础模型”。

## 二、章节骨架

```
Title / Authors / Abstract / Keywords（6 个左右）
1. Introduction
2. Overview of [技术] for [领域]
   2.1–2.4 每种方法一小节
   Table I 方法总表 + 一段表格解读
   2.5 Practical application（带量化结果的真实案例）
3. [技术] in [对象 A]      ← 引导段 + 框架图 + 3–4 小节
4. [技术] in [对象 B]      ← 同上；章末放“传统 vs AI”对比表
5. [技术] in [对象 C]      ← 同上，可较短
6. Challenges（6 个小节）
7. Concluding Remarks
Acknowledgments / CRediT / Competing Interest / Data availability / References
```

篇幅比例（正文约 9000 词）：引言约 20%，方法总览约 25%，三章应用合计约 30%，挑战约 20%，结论约 3–5%。引言和挑战都写得很足，这是蓝本的特点。

### 摘要（一段，约 200 词）六步
1. 宏观背景与需求
2. 研究对象及其重要性
3. 现存局限（成本、材料、效率等）
4. 本文做什么：引入哪些技术、覆盖哪些任务
5. 强调独特视角（视角轴）
6. 挑战与未来方向 + 一句价值定位

### 1. Introduction（约 10 段，漏斗式）
1. 大背景：能源转型 → 领域的重要性 → 现有局限 → 一句话点出技术的潜力
2. 对象 A：原理、优势、瓶颈；**段尾用一句话说明该技术能为它做什么**
3. 对象 B / C：同样写法，段尾同样回扣技术
4. 视角之一（纳米尺度）：研究什么、为什么关键
5. 视角之二（微米尺度）：同上
6. 技术在该领域的变革作用（总述，能做什么）
7. 技术的进一步贡献（如结构优化、数据处理）
8. 为什么现在需要这篇综述：`First… Second… Additionally…`，最后点出读者群（研究者、政策制定者、产业界）
9. 新颖性声明：与已有综述对比（`Unlike previous studies that…`），随后列 **3 条加粗小标题的贡献点**，分别对应方法轴、对象轴、视角轴
10. 全文路线图：`In the rest of the paper, Section 2… Section 3… Finally, Section 7…`

规律：前面每个背景段的最后一句都把话题拉回“技术能解决什么”，这样引言读起来始终围绕主题，不像纯背景堆砌。

### 2. 方法总览
- 章首引导段：一句话定位 + 预告 Fig. 1（多面板 (a)(b)(c)(d)，每种方法一个示意图）。
- 每个方法小节 3–4 段，固定套路：
  1. **定义与机理**：是什么、由哪几部分组成、如何工作（引通用 AI 文献）
  2. **在本领域的用途**：解决哪些问题（数据稀缺、材料探索、退化机理等）
  3. **从视角轴看**：在该视角下的独特价值，配 `For example / For instance` 的具体场景
  4. **小结段**：以 `In summary / Overall` 开头，重申价值
- Table I 方法总表，列为：`Technique | Description | Applications | [视角]贡献 | References`；表后用一段逐行概括。
- 2.5 实践案例小节：逐条写真实文献的工作——谁用了什么模型、做了什么任务、得到什么**量化结果**（如建模时间缩短多少倍）。这一节是蓝本里证据最扎实的部分，新综述应加大这类内容的比重。

### 3–5. 对象应用章
- **章首引导段**：一句总述 → 预告本章框架图 → 用 `Firstly… Secondly… Thirdly… Lastly…` 各用一句话预告每个小节。
- 每章配一张框架/流程图（图题格式：`[技术] in [对象]: 任务1, 任务2, 任务3, 任务4`）。
- **小节五步法**（每小节 1–3 段）：
  1. 该任务为什么重要
  2. 传统方法及其局限（试错、耗时、昂贵、难以刻画复杂行为）
  3. 转折：`In contrast, …`，引出 AI 方法怎么做
  4. 具体技术与例子（哪类模型，与 DFT/MD/CFD 等如何结合）
  5. 带来的收益与意义
- 在应用章末尾放 Table II“传统方法 vs AI 方法”对比表，指标如 Accuracy / Time / Cost / Discovery speed / Exploration / Optimization，并配一段解读及“模型如何与实验数据结合验证”的说明。

### 6. Challenges
- 章首引导段 + 一张“挑战与展望”总图；引导段用 `Firstly… Finally…` 把每个挑战各用**一句问题 + 一句对策**预告一遍。
- 蓝本的六个挑战：数据质量与可得性 / 可解释性与透明度 / 与现有工作流的集成 / 可扩展性（实验室到产业）/ 伦理与环境 / 监管与安全。新综述按主题替换，但保留“技术—工程—社会”由内到外的顺序。
- 每个挑战小节的套路：
  1. 问题陈述：为什么这是障碍
  2. 具体例子（`For instance…`）
  3. 对策：合作共享、标准化、XAI、混合建模、培训等
  4. **回扣视角轴**：`When focusing on [视角]…`，说明该视角下的额外考虑
  5. 展望式收尾
- 挑战与对策成对出现，不写只提问题不给方向的段落。

### 7. Concluding Remarks（两段）
1. 综合：本文表明了什么，技术在各对象、各任务上的总体贡献
2. 未来工作：呼应第 6 章的挑战，强调跨界合作与后续方向

### 尾部
Acknowledgments、CRediT authorship contribution statement、Declaration of Competing Interest、Data availability，参考文献用 IEEE 数字编号格式。

## 三、行文特征
- 每章、每小节都以引导句开头（`This section explores…`），以小结句收尾。
- 段落内部常用骨架：`Traditional methods… However… In contrast, [技术]… For instance… This not only… but also…`。
- 图表都在正文中先预告再出现（`As shown in Fig. X` / `Table I provides…`），表格后必有一段文字解读。
- 术语首次出现给全称加缩写，之后统一用缩写。
- 引用密度：背景句和定义句每句 1–3 篇；一个小节约 4–8 篇；全文百篇以上，其中领域权威综述、通用 AI 方法文献、近两年新工作各占一部分。

## 四、不要继承的问题
蓝本通过了导师审核，但有几处在新稿里应当做得更好：
- 有的具体案例只写了机构名而没有给出文献引用。新稿里每个具体案例都要有可核实的出处。
- 个别参考文献与主题相关性弱。新稿每条引用都要与所在句子的论点直接对应。
- 对比表是定性描述（如 “High to Very High”）。能找到数据时用带出处的定量数字。
- 部分小节以概括性陈述为主。新稿多写“某文献—某模型—某数据集—某结果”式的具体内容，并加入对方法优劣的比较和批判性评述。
- 用词上少用 revolutionize / transformative / pivotal 这类重复出现的强调词，这也有助于降低“AI 味”。

## 四之二、英文行文规则（来自 ASSB 综述 V36 润色的经验）
导师认为初稿“不够像人写的”。对比润色稿后，下面这些改法有效，所有新稿都照此执行：

1. **不写套话式结尾句。** 去掉 “In summary…”“Overall…”“…which makes X a central tool” 这类收尾。它们只是把本段重说一遍，是 AI 味的主要来源。段落停在最后一个实质论点上。
   - 例：删去 “In summary, MLIPs combine near first-principles accuracy with long trajectories, which makes them a central tool…”，段落以 “Applying them … still requires representative configurations and tests against the intended observable.” 收尾。
2. **合并碎句，并写出逻辑连接。** 连续的短陈述句读起来像在罗列。合成一句，用 but / whereas / so / because 写出因果或转折。
   - 例：“Speed of this kind changes what can be screened. It does not, by itself, tell us…” → “Speed of this kind changes what can be screened, but it does not by itself tell us…”
3. **论断只说到证据支持的程度。** 用 “a common first step”，不用 “the most widely used”；不写 “for the first time”；收益要限定在所引文献范围内并用过去时，如 “In the studies collected in Table 3, AI4Science shortened…”。审稿人最先攻击的就是过度表述。
4. **补“为什么不同”的分析句。** 列完案例后，说明每个结果属于哪类证据、为什么不能直接比较。例如：
   - 计算加速、实测电导率、循环寿命是不同性质的结果，按证据类型而不是提升幅度排序；
   - 指出几个模型的验证终点都不是实测电导率；
   - 比较两项研究分别在变化哪类因素。
   这类句子体现批判性，导师最看重。
5. **结构保留，说法要换。** 蓝本的章首引导段（含逐节预告）、摘要中的视角句、引言里“为何此时需要本综述”的三点结构都必须保留，不能删。但不要每章都用 “This section explores…” 和 “Firstly… Secondly… Lastly…”，“In contrast,” 也不要每节重复。每处换一种句式，如 “We first consider…, then turn to…”“Transport prediction comes first…”。
6. **重点放在句首。** 当一段的核心论点是结论时，开门见山写出来，再给依据。
   - 例：“In a physical closed loop, experimental observations choose the next action, which turns AI4Science from a tool for prediction into a tool for decision-making.”
7. **拼写统一用美式**（modeling、behavior）。
8. **数字以正式发表版为准。** 不用 arXiv 预印本的数值。预印本和期刊版数字可能不同；Kim 等人 JCP 2026 就是一例。

交稿前自查：全文搜索 “In summary”“Overall”“In contrast”“Firstly”“This section”，看每个是否必要、是否重复；检查是否每组案例后都有一句对比分析。

## 五、使用流程
1. **定三轴**：和用户确认主题、方法轴、对象轴、视角轴、目标期刊及其格式要求。用户已有稿件时先读稿件，再对照蓝本找差距。
2. **出大纲**：按第二部分的骨架给出到二级标题的大纲，每节附 1–2 句写作要点、计划的图表（Fig. 1 方法总图、每章框架图、挑战图；Table I 方法总表、Table II 对比表）和预估篇幅。大纲经用户确认后再写正文。
3. **搜集文献**：先检索并核实文献，再动笔。不编造文献、作者、数据或机构合作；暂时没有出处的地方标 `[REF needed]` 留给用户补，不要凭印象填。
4. **分节撰写**：一次写一章，按对应的段落套路写，写完自查是否回扣了视角轴。
5. **终检清单**：
   - 标题、摘要、贡献点、各章是否都体现视角轴
   - 引言是否有“为何此时需要本综述”段、3 条贡献点、路线图段
   - 每个方法小节是否“定义—用途—视角”齐全（小结不靠套话句，见四之二）
   - 是否符合四之二的英文行文规则
   - 每个应用小节是否有“传统局限 → AI 方案”的对比
   - 每个挑战是否配了对策
   - 图表是否都在正文预告并解读
   - 每个具体论断是否有引用，引用是否真实相关
   - 是否存在与蓝本或其他文献雷同的句子
   - 引言是否有范围定义句和主线句；优势是否编号并定量
   - 每个对象/材料小节是否以“未解决问题”收尾，是否配了对比表
   - 结论是否写了理论与实际的差距、哪些结论不能说

## 五之二、第二蓝本：Chem. Soc. Rev. 高质量综述的可借鉴写法
来源：Ghani et al., *Understanding the chemistry of re-emerging proton batteries*, Chem. Soc. Rev. 2026（DOI 10.1039/D5CS00746A，40 页、约 220 篇文献、24 图 9 表）。导师称其为高质量综述。第一蓝本定义了导师认可的**结构**，这一篇补的是**深度和批判性**。两者叠加使用：结构按第一蓝本，下列写法按本节。

**章节逻辑：为什么 → 从哪里来 → 怎么工作 → 怎么看清 → 用什么材料 → 用什么介质 → 竞争地位 → 客观展望**
引言 / 历史 / 构造与机理 / 表征与建模 / 电极材料（按家族）/ 传导介质（按物相）/ SWOT / 结论与展望。机理章放在材料章之前，先给读者词汇，后面各材料节都用同一套机理语言来分析。

1. **引言里的优势要编号并定量。** 写成 (1)–(5) 条，每条带数字和对照物，如“氢丰度 1400 ppm，高于锂的 20 ppm”“HCoO₂ 理论容量 291 mAh g⁻¹，高于 LiCoO₂ 的 273”。不写没有数字的“excellent”。
2. **写一句范围定义。** 如 “In this work, we describe X as …, distinguishing them from Y and Z”，并说明涵盖哪些构型。审稿人最常问“为什么没包括…”，范围先写清楚就不会被问。
3. **创新点编号，每条加括号解释，再用一句“主线句”收束。** 例：“Thus, the central article revolves around understanding the unified … across materials, interfaces, and media.”主线句就是全文的视角轴。
4. **机理按空间位置组织。** 分为电极内部 / 界面 / 电解质内部。这是把“多尺度”落到章节上的一种写法；用在 ASSB 上就是体相电解质 / 界面 / 复合电极 / 电芯。
5. **表征章写“怎么判断”，不只列仪器。** 给出可操作的判据，例如：
   - Eₐ < 0.4 eV 对应 Grotthuss 机理，> 0.4 eV 对应载体机理；
   - 电导率在冰点附近是否陡降可以区分两种机理；
   - 给出具体测试方法，如用 H 型电解池测选择性。
   并写出实验与计算怎么对照验证，如 PDF 精修数据与 DFT/CGMC 模型对齐，NEB 势垒与实测电导率关联。
6. **每个材料小节用“未解决问题”收尾，不用 In summary。** 先写 2–4 个代表工作（数据、方程式、图），最后一段点名具体的未知问题。例如：
   - 纯嵌入与转化反应、相重构尚无法区分；
   - 高倍率下 H⁺ 与 H₃O⁺ 的嵌入界限不清；
   - 各向异性应变对高载量电极的疲劳风险。
   这样的结尾比总结句更有信息量，也更显批判性。
7. **设计原则编号。** 如 “An ideal solid framework … should have (1)…(4)…”，让综述给出可以照着做的东西。
8. **几乎每节都配对比表。** 包括：粒子性质表、与其他电池的优劣/市场/环境表、机理表、各材料家族性能表、介质表、文末已报道器件总表。器件总表列出电池形式（纽扣/软包/烧杯）和载量，缺失的数据标 NR（not reported），不硬填。
9. **章节之间互相指引。** 如 “will be discussed in Section 6.3”“correlated with the measured conductivity in Section 4.1.3”，把章节织成一张网。
10. **用 SWOT 做竞争定位，而且每一项都定量对标。** 例如：能量密度 245 vs 260 Wh kg⁻¹、活化能 0.1–0.3 vs 0.5–1.2 eV、成本 $500–700 vs $100–150 per kWh、循环寿命 500–1000 vs 2000–3000 次。威胁一项写到竞品技术、缺乏标准与测试规范、制造基础设施。
11. **结论要克制，有分寸。**
    - 每类材料用一句话点出它的取舍（“X exemplify the opposite extreme, i.e., …”）。
    - 用数字写出理论与实际的差距。
    - 明确写哪些结论不能说（“one cannot say ‘X last longer than Y’ … because these features depend on chemistry and design”）。
    - 整体基调是 “realistic optimism”，结论是“不会在所有应用中取代 Y，但在某些场景…”。
12. **图的做法。**
    - Fig. 1 用多面板反映大背景（丰度、离子半径、Ragone 图）。
    - 历史时间线配 Web of Science 发文趋势图，用来证明“为何此时需要本综述”。
    - 机理示意图自己画。
    - 转载的图在图注每个子图后都注明 “Reproduced with permission from ref. X. Copyright 年份, 出版社”。

**这篇也有不要学的地方**
- SWOT 和结论里的关键数字大量只依赖一两个来源（其 ref. 210/212）。
- 引用了新闻稿和咨询公司报告。
- 个别史实有误：锂离子电池商业化是 1991 年，文中写成 1992 年。
- 仍有 “fascinating”“pivotal”“In summary” 等套话。
- 材料节的中段偏向逐篇罗列。
- 转载图占比很高，约 28 处。
新稿关键数字要多源交叉引用，只引同行评审文献，并核对史实。

## 六、输出约定
- 论文正文用英文；与用户的沟通、大纲说明、修改意见用中文（除非用户另有要求）。
- 改稿任务：先给“对照蓝本的差距清单”（结构、论证、引用三类），再给修改后的文本。