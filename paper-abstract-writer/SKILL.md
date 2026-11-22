---
name: "paper-abstract-writer"
description: "为 Yikun 的英文论文（综述或研究论文，CSR/RSC、IEEE TVT、Elsevier 等）撰写、改写或审查 Abstract，要求有学术张力。用户提到写摘要、改摘要、审摘要、abstract、学术张力时使用。"
---

# 论文摘要写作（Abstract Writer）

本 skill 只负责一件事：写好论文的 Abstract。它来自 ASSB AI4Science 综述（V40）摘要的修改过程，前后经过三轮：

1. 导师否定了第一版：风格不对，用词不像科研写作（设问句、口语化动词、比喻）。
2. 导师给了蓝本综述的摘要作参考，要求语气更强。
3. 导师通过了“有学术张力”的版本（见第五节范例）。

与用户沟通用中文，摘要正文用英文。

## 一、核心原则：学术张力

学术张力来自先把一对矛盾讲清楚，再说明本文如何回答它。不要靠形容词堆砌语气。

1. **先讲能力，再讲缺口，两边都带数字。** 例如：“加速超过五个数量级、筛选数千万候选材料”对“实测电导率模型误差仍约一个数量级、部分已报道的发现在复核后被修正”。
2. **把矛盾收束成一句明确的开放问题。** 例如：“Whether AI4Science can deliver better batteries, rather than faster calculations, therefore remains an open question.” 后面每一句都是在回答这个问题。
3. **不要先宣布答案。** 开头写 “offers a powerful means of overcoming these limitations”，后面又说优势受限，会前后矛盾，张力也被抵消。结论只在结果句里出现一次。
4. **结论句是全文落点。** 用对比式给出核心发现，例如 “the advantage … is clear for X but narrows markedly for Y, where …”，并说明原因。
5. **语气靠证据和动词，不靠自我评价。** 少用 comprehensive、powerful、clear、novel 这类形容词，多用 addresses、classifies、shows、proposes 这类有内容的动词，加上具体数字。

## 二、结构

### 综述（约 250–330 词，一段）

| 步骤 | 内容 | 范例对应句 |
|---|---|---|
| 1 | 宏观需求 | electrification … demand safer, more energy-dense batteries |
| 2 | 研究对象及其前景，用 yet 接主要障碍（3–4 个） | ASSBs … one of the most promising routes …, yet … hindered by … |
| 3 | 技术已经做到什么（带数字） | AI4Science has accelerated … by more than five orders of magnitude … |
| 4 | 但缺口在哪里（带数字或证据） | These gains, however, have been demonstrated mainly for computed quantities: … |
| 5 | 开放问题（一句） | Whether …, rather than …, therefore remains an open question. |
| 6 | 本文的视角或框架，以及它怎样回答问题 | This review addresses that question through a multiscale validation framework that … |
| 7 | 覆盖范围：方法轴和对象轴 | Within this framework, we critically assess … as applied to … |
| 8 | 核心发现（对比式） | A SWOT analysis … shows that … clear for … but narrows markedly for …, where … |
| 9 | 提出了什么，挑战有哪些 | To address this gap, we propose … and outline the remaining challenges in … |
| 10 | 价值定位（一句） | This review aims to provide both a reference and a practical guide for … |

第 1–2 步与导师蓝本一致（背景 → 对象 → 局限），第 3–5 步是导师认可的张力部分。

### 研究论文（IEEE 通常 150–250 词；Elsevier 通常不超过 250 词；以期刊作者指南为准）

1. 问题和场景（1 句）
2. 现有方法为什么不够，给出具体失效方式或代价（1–2 句），这是张力来源
3. 本文方法的核心思想，一句话说清楚“怎么做到的”（1–2 句）
4. 数据和实验设置：数据集规模、真实场景（1 句）
5. 定量结果：与最强基线对比，给出数字（1–2 句）
6. 意义或适用范围（1 句）

## 三、写法规则

### 用词

不用口语、拟人、比喻、商业用语和设问。导师已经否定过下面这些用法：

| 不用 | 改用 |
|---|---|
| promise safer cells | are expected to improve safety |
| conduct as fast as | exhibit conductivities comparable to |
| survive the transition | remain valid when … |
| at a fraction of the cost | at substantially lower computational cost |
| close this gap（口语套话） | address this gap / discrepancy |
| working cells | full cells |
| How much … is less clear.（设问） | … has not yet been systematically assessed. |
| no longer X but Y | not X but Y / rather than |
| map, path, thread 等比喻 | framework, relation, criterion |
| competitive assessment | comparative assessment |

### 语气

- 导师要求语气要强。可用的强表述：one of the most promising routes、a distinctive feature of this review is …、critically assess、establishes … as a roadmap、shows that …。
- 不用 “for the first time”、“the first review”、“sets a new benchmark”、“novel integration”，除非用户明确要求。如果用户要求，改写为 “To the best of our knowledge, …”，并提醒用户审稿人会去核查。
- 综述不能说 “demonstrates significant improvements”，因为综述本身不做实验。

### 句法

- 主语轮换：This review addresses … / we critically assess … / A SWOT analysis shows …。同一个主语开头的句子不超过两次。
- 不用悬垂分词。“…, evaluating the extent to which …” 的主语不清楚，应改为独立分句。
- 主题词（如 AI4Science）不超过 4–5 次，可以用 these gains、the approach 等指代。同一句里不重复同一个词（advantages … advantages）。
- 相邻句不重复同一个概念（enhanced safety / intrinsic safety）。

### 一致性与证据

- 摘要里的每个数字和判断都必须能在正文里找到，并与正文表述一致：数量级、误差、样本数、结论措辞。数字取自正式发表版本，不用 arXiv 预印本的数字。
- 摘要里的挑战清单要与“挑战”一章的小节标题一一对应。
- 摘要说 “quantitative” 时，正文对应的表格必须确实是定量的。
- 缩写首次出现给全称（如 SWOT），摘要中的缩写在正文首次出现时还要再定义一次。

### 体例

- RSC/CSR：不用牛津逗号（“oxide, halide and polymer”）；少用破折号，改用逗号；US 拼写须与全文一致。
- IEEE：一段，不引文献，不用公式和特殊符号，150–250 词。
- 投稿前按目标期刊的作者指南核对字数上限。不确定时，在交付时提醒用户核对，不要凭印象写具体限制。

## 四、工作流程

### 写新摘要

1. 读稿件的引言、各章结论、核心表格和结论章。没有稿件时先问用户要。
2. 提取四样东西：
   - 张力对：能力和数字，缺口和数字；
   - 开放问题；
   - 本文的框架或方法；
   - 核心发现。
   每一项都标明出处（正文哪一节、哪篇文献）。
3. 按第二节的结构起草，然后按第六节的清单自查。
4. 交付：英文摘要全文，加一段中文说明（张力骨架是什么、各个数字出自哪里、需要用户确认的点）。

### 审查或改写用户写的摘要

1. 先用中文按类别列问题：张力结构、形容词与证据、重复、语法、体例。每类给出具体原句。先肯定改得好的地方。
2. 给出完整的建议版本（英文）。
3. 说明改了什么、为什么改，以及数字的出处。
4. 问用户是否替换进全文。替换时，顺带检查引言中相关表述是否需要同步调整。

## 五、范例（导师已通过，ASSB AI4Science 综述 V40）

这段只用来学习结构和张力的写法。写其他论文时不要照搬句子，以免查重时与已发表版本重合。

> The electrification of transport and the growing share of intermittent renewable energy demand rechargeable batteries that are safer and more energy-dense than current lithium-ion batteries. All-solid-state batteries (ASSBs), which replace the flammable liquid electrolyte with a solid ion conductor, are widely regarded as one of the most promising routes to this goal, yet their development is hindered by insufficient ionic conductivity in many solid electrolytes, chemical and electrochemical instability at electrode–electrolyte interfaces, mechanical degradation under stack pressure and poor reproducibility across laboratories. Artificial intelligence for science (AI4Science) has accelerated some atomistic simulations by more than five orders of magnitude and enabled the screening of tens of millions of candidate materials. These gains, however, have been demonstrated mainly for computed quantities: models of measured ionic conductivity still err by about one order of magnitude, several reported discoveries have been revised on re-examination, and few predictions have been tested in full cells. Whether AI4Science can deliver better batteries, rather than faster calculations, therefore remains an open question. This review addresses that question through a multiscale validation framework that follows predictions from atomic-scale ion transport through interfacial and microstructural processes to cell-level performance, and classifies each study by the highest level of experimental evidence it reaches. Within this framework, we critically assess machine-learning interatomic potentials, property-prediction and generative models, large language models for literature mining and closed-loop autonomous experimentation, as applied to sulfide, oxide, halide and polymer electrolytes, interfaces and microstructure, and cell design and testing. A SWOT (strengths, weaknesses, opportunities and threats) analysis against conventional simulation and trial-and-error experimentation shows that the advantage of AI4Science is clear for computed targets but narrows markedly for measured properties and cell performance, where data are sparse and processing conditions, stack pressure and cell format are often unreported. To address this validation gap, we propose minimum evidence requirements, validation designs and prospective tests, and we outline the remaining challenges in data quality, model comparability and uncertainty, and scalability from the laboratory to the engineering scale. This review aims to provide both a reference and a practical guide for researchers seeking to turn data-driven predictions into safe, high-energy-density solid-state batteries.

**为什么这版能通过**

- 张力骨架清楚：能力（数字）→ however → 缺口（三条证据）→ 开放问题 → 本文的回答。
- 开头没有先宣布 AI 能解决问题，所以结论句的对比（clear for … but narrows markedly for …）成了全文落点。
- 语气强但站得住：one of the most promising、critically assess、validation gap 都有正文支撑。
- 主语在 AI4Science、These gains、This review、we、A SWOT analysis 之间轮换，没有悬垂分词。

## 六、交付前自查清单

- [ ] 前 5 句内出现了能力与缺口的对比，两边都有数字或具体证据
- [ ] 有一句明确的开放问题，后文都在回答它
- [ ] 开头没有提前宣布答案；结论句与开头判断一致
- [ ] 核心发现用对比式表述，并说明原因
- [ ] 每个数字和判断都能在正文找到，且来自正式发表版本
- [ ] 挑战清单与挑战章的小节一一对应
- [ ] 没有口语、拟人、比喻、设问、商业用语
- [ ] 没有 first、novel、new benchmark（除非用户明确要求）
- [ ] 同一主语开头不超过两次；没有悬垂分词；相邻句没有同词重复
- [ ] 体例符合目标期刊（RSC 不用牛津逗号；IEEE 不引文献），并提醒用户核对字数上限
- [ ] 没有照搬范例或导师蓝本的原句