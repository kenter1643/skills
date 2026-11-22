---
name: yikun-figure-style
description: Yikun 的个人论文绘图风格：按投稿标准（RSC/CSR、IEEE TVT、Elsevier）用 matplotlib 绘制、重绘或检查论文图件和示意图，先从个人风格库（S0–S6）列出相近风格的缩略图供选择，再出 600 dpi TIFF/矢量 PDF，并同时撰写图注和正文引用句。
---

# Yikun 论文绘图风格（yikun-figure-style）

在 Chen Liu 的 figures4papers 技能（https://github.com/ChenLiu-1996/figures4papers ，CC BY-NC 4.0，仅限非商业用途）基础上改写：保留它的布局套路、语义配色思路和柱状图/趋势图/热图写法，按 Yikun 的投稿要求重定尺寸、字号、分辨率和导出格式，并加入 ASSB 综述 V37 改图时总结的数据来源规则和成图检查清单。用于论文、综述、学位论文和投稿用图，不用于交互式图表和商业宣传材料。

与 Yikun 沟通用中文；图中文字默认用英文，投中文期刊时用中文标注（见第六节）。

## 一、先定目标期刊和成图尺寸

**先问清楚投哪个期刊**。不知道时按 RSC 双栏处理，并在回复里说明。所有图都按最终印刷尺寸直接绘制，不靠缩放。

| 期刊 | 单栏 | 双栏 | 最大高度 | 分辨率 | 提交格式 |
|---|---|---|---|---|---|
| RSC（Chem. Soc. Rev. 等） | 83 mm | 171 mm | 233 mm | ≥600 dpi | TIFF |
| IEEE（TVT 等） | 88.9 mm（3.5 in） | 181.9 mm（7.16 in） | 220 mm | 彩色/灰度 >300、线条图 >600；统一按 600 | TIFF/EPS/PDF |
| Elsevier | 90 mm | 190 mm | 约 240 mm | 照片 300、图文混合 500、线条图 1000 | TIFF/EPS/PDF |

- 投稿前再对照目标期刊作者指南核对一次，以期刊页面为准。
- 放进 Word 时按版心宽度插入（Letter 页 1 英寸页边距为 165 mm），要算一下插入后的实际 dpi，不得低于 600。`save()` 会打印这个数字。
- RSC 综述要求转载图不超过全部图的约 20%，超出时投稿要附理由。能用原文数据重画的就重画。

## 二、风格规范

**字号（按成图尺寸）**：正文 6.5 pt，刻度 6 pt，图例 6 pt，小标题 7 pt 加粗，子图字母 8 pt 加粗小写（a, b, c）。任何文字不小于 5.5 pt。
**线宽**：坐标轴 0.5 pt，数据线 0.9 pt，示意图边框 0.6–0.7 pt，最细不小于 0.25 pt。
**字体**：Arial 类无衬线字体（服务器上用 Liberation Sans），PDF 嵌入字体（fonttype 42）。
**坐标轴**：去掉上、右边框；图例不加边框；网格只在需要读数时用浅灰细线。
**配色**（色盲友好，全文统一）：
- blue #2C5F9E：本文方法、关键结果、主数据系列
- teal #2A9D8F：改进、成功、第二系列
- orange #E9A23B：替代方案、不确定、生成式方法
- red #D1495B：对照、失败风险、第三系列
- purple #7B6FB0、grey #9AA3AD：补充类别和基线
- 浅色底：#E3EAF5、#DFF1EE、#FBEFD9、#F8E1E5、#EEF0F2
同一概念在全文所有图里用同一颜色。一张图里出现的每种颜色、每种标记都要在图例或图注里解释。

**保留 figures4papers 的做法**：
- 图例多时单独占一个子图（`legend_panel`），不压在数据上。
- 柱上直接标数值；方法多时可隐藏 x 刻度标签，靠图例和标题区分。
- 灰度打印要能区分：同色柱用白边加不同填充纹（hatch）区分。
- 消融实验用同一颜色、不同深浅表示完整程度。
- 每个坐标系最多 2–4 条主曲线，不确定性用 `fill_between` 色带。
- 多子图之间字号、线宽和配色保持一致，不给单个子图额外装饰。

**改掉 figures4papers 的做法**：
- 柱状图纵轴必须从 0 开始。原技能建议收紧纵轴来放大差异，这会夸大很小的差别（ASSB 综述图 3b 就出过这个问题）。只有点图和折线图可以截断纵轴，而且要在图注里说明。
- 不用 15–24 pt 大字配大画布再缩小的做法，字号按成图尺寸定。
- 不用默认 300 dpi，按第一节的表导出。

## 三、数据来源规则

1. **数值只用正式发表版。** 不用 arXiv 预印本的数值（Kim 等人 JCP 2026 的 MAE 就是教训：预印本是 0.611/0.543/0.657，正式版是 1.108/1.172/0.798）。拿不到正式版时，在回复里说明用了哪个版本。
2. **不编造数据。** 原文只给范围就画范围（`dot_range`），只给一组模型的总体范围就标“范围适用于这组模型”。原文没有的数值不能从图上估读后当精确值用；确实需要读图取值时，图注写 “values read from Fig. X of Ref. [n]”。
3. **按原文要素重新设计，不照描原图。** 可以用原文的数据、方程和标注重新计算或重排，例如密度–孔隙率图按原文密度和堆积模型重算，并把结果和原图标注值对一遍。
4. **图注写清来源类型**，并与正文引用编号一致：
   - 自绘综合图：`Original synthesis [n–m].`
   - 用原文数据重画：`Data from Ref. [n].` 或 `Values replotted from Ref. [n].`
   - 改编：`Adapted from Ref. [n], Figure k, under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/).`
   - 直接转载：`Reproduced from Ref. [n] (https://doi.org/...), Figure k, under CC BY 4.0 (...).`
   - 非 CC BY 的文献要通过 RightsLink 申请许可；CC BY-NC 和 CC BY-ND 的文献不要改编。
5. **图、图注、正文三处的数字必须一致。** 改了任何一处，另外两处一起改。

## 四、版式经验

- 示意图用 `box` 和 `arrow` 搭建；箭头起止点不要落在方框内部，回环箭头要从方框外侧绕过。
- 证据阶段、流程这类图，没有达到的阶段不要用连线穿过，否则读者会以为已经达到。
- 长注释放在坐标区外（`clip_on=False`），或放在条形内部用白字。
- 标签放不下时先换行、缩短措辞，最后才缩小字号（不小于 5.5 pt）。
- 对数坐标的次刻度标签太乱时，用 `FixedLocator` 和 `FixedFormatter` 手动指定刻度。
- 圆形标记在非等比例的 figure 坐标里会变成椭圆，要放在坐标系里用 `scatter` 画。

## 五、导出

`save()` 一次输出三个文件：
- PNG：RGB、去掉透明通道，插入 Word 用；
- TIFF：LZW 压缩，投稿用；
- PDF：矢量，便于编辑和期刊排版。
另外把绘图脚本一起保存，方便以后修改。转载图的分辨率不够时，从出版社 PDF 中按 600 dpi 提取原图，不要直接插值放大。

## 六、中文标注

`apply_style(cjk=True)` 会把中文字体放在字体列表最前面（Noto Sans CJK SC / 思源黑体 / 黑体 / 微软雅黑），英文和数字仍用 Arial 类字体。中文图里的单位和化学式写法与英文版保持一致。

## 七、成图检查清单（每张图交付前都要做）

1. 出图后实际打开看一遍：整图看一次，再把文字密集的区域裁出来放大看，确认没有文字重叠、被截断或压到边框上。
2. 尺寸和分辨率符合第一节的表；插入 Word 后的实际 dpi 不低于 600。
3. 每种颜色和标记都有解释；子图字母与图注一一对应。
4. 柱状图纵轴从 0 开始；截断的坐标轴在图注里有说明。
5. 图中数字与图注、正文、原文正式版一致。
6. 图注写明来源类型和许可；转载图占比按期刊要求控制。
7. 同一篇文章的所有图配色、字体族、子图编号写法和风格族一致。
8. 图注按第十节写好，子图描述与子图实际内容逐个对过；正文引用句已给出。

## 八、个人风格库与选型流程

风格库来自 Yikun 提供的 4 张样例（2026-11）：两张导师综述的示意图（S1、S2），两张 Chem. Soc. Rev. 综述的多面板图（S3–S6），加上 V37 现用的 Nature 线框风格（S0）。只学视觉规则（配色关系、版式、图标编码、标注习惯），不照搬原图的图形和内容。

### 8.1 风格条目

| 编号 | 名称 | 视觉特征 | 适合 | 实现（pub_schem.py） |
|---|---|---|---|---|
| S0 | Nature 线框流程 | 无图标；0.7 pt 彩色细边圆角框 + 同色浅底；无衬线 6.5–7 pt；灰色细箭头；虚线回路表示反馈 | 正文流程图、方法框架、算法步骤；最稳妥的默认 | `pub_fig.box/arrow` 或 `flow_arrow` |
| S1 | 虚线分栏工作流 | 3–5 个纵向分栏，绿色点线圆角边框（#70AD47）；Times 粗体栏标题在左上；扁平图标纵向串联，中间成对细蓝箭头；图标旁竖排粗体标签；属性用半透明粉彩椭圆云 | 方法总览（数据→特征→模型→部署）、综述 Fig. 1 | `dotted_column`、`icon`、`down_arrows`、`ellipse_cloud` |
| S2 | 水滴阶段流程 | 灰色粗圆环内放图标；下方粉彩水滴（黄/绿/橙/蓝）；水滴上方饱和色圆角标签写阶段名（Times 粗体）；深橄榄色 V 形箭头连接各阶段；水滴内放小图标 + 短语 | 综述首图、研究路线图、"发现→模拟→预测→实验"阶段图 | `ring`、`teardrop`、`pill`、`chevron`、`icon` |
| S3 | 时间轴 + 类别图标 | 横向年份轴，年份粗体在轴下；每个事件上方是类别图标，图标上写彩色类别词，再上是事件名；整幅浅色渐变底 | 发展历程、里程碑；可与发文量柱图（S5）组成一张图 | `timeline`、`tint_panel` |
| S4 | 分区色块多面板 | 每个子图一块极浅的底色（绿/粉/蓝/灰/淡紫），可做上下渐变；子图编号写 "(a)"（不加粗）；无边框 | 机理示意 + 数据图的组合图；CSR 类综述 | `tint_panel` + 普通 matplotlib 坐标轴 |
| S5 | 单色数值柱 | 单色柱（#3173CA），柱顶标数值；轴刻度、轴标题与柱同色，轴标题可全大写；图内左上写标题和括号说明；纵轴从 0 开始 | 发文趋势、单指标对比 | `bar` + 着色刻度（见 demos.s4） |
| S6 | 证据拼贴版式 | 多来源子图按主题分区着色拼排，宽窄子图混排；每个子图单独标来源和许可 | 综述里汇总多篇文献的证据；转载图多时用 | `tint_panel` 布局；内容尽量用重画图 |

配色速查：
- S1/S2 用 Office 主题色，成对使用（浅底配深色）：黄 #FFF2CC/#FFD966、绿 #E2F0D9/#A9D18E、橙 #F8CBAD/#C55A11、蓝 #BDD7EE/#4472C4，点线框 #70AD47，图标深蓝 #10314D、品红 #9A4590、青 #00ACDC，V 形箭头 #5D5036。
- S3–S5 是 CSR 配色：蓝 #3173CA、绿 #5AAE30、橙 #F28C28；分区底色 #F3F9F1、#FBF3F2、#ECF5FC、#F5F6F8、#F6F4FA。
- 数据图仍用第二节的 V37 调色板。

### 8.2 与第二节规范的取舍

- **字体：** 一篇论文所有图只用一种字体族。投导师体系的综述（样例 1、2 用 Times）时，全部图用 serif（Liberation Serif / Times New Roman），数据图也一样；投 RSC/IEEE/Elsevier 默认用无衬线。
- **子图编号：** RSC 综述用 "(a)"（与 CSR 样例一致）；Nature 系用加粗小写 "a"。同一篇只用一种，与图注写法一致。
- **饱和色标签：** 深色底（#C55A11、#4472C4）上的文字用白色。样例 2 用黑字，对比度不够，不学。
- **字号：** 样例在成图尺寸下文字约 7–9 pt；我们仍按第二节的下限（≥5.5 pt）和 6.5–8 pt 的常用字号。
- **图标：** 一律用 `pub_schem` 里自己画的简单几何图标，或 Yikun 有授权的图标。不从网上图标库或别人的图里截图标。
- **贴图：** 样例 1、4 里粘贴的位图分辨率低、风格不一。示意内容重画，确需转载的按第三节处理并控制占比。

### 8.3 选型流程（每次画新图都按这个来）

1. **判断图的用途**，从下表取 2–4 个相近风格：

   | 用途 | 候选风格（首选在前） |
   |---|---|
   | 方法流程、框架 | S0、S1、S2 |
   | 综述首图、路线图 | S2、S1、S0 |
   | 发展历程 | S3（+ S5 发文量）、S0 |
   | 机理 + 数据组合 | S4、S0 |
   | 多文献证据汇总 | S4（重画）、S6（拼贴） |
   | 纯数据对比 | V37 数据图（第二节）、S5 |

2. **用 Yikun 的真实内容**把每个候选风格各画一版缩略图（150 dpi 即可），拼成一张对比图发给他。每版标上风格编号和一句话特点，再用选择题请他选。他不在时，按期刊选默认风格（CSR → S4/S0；导师体系综述 → S1/S2），并在回复开头说明选了哪个。
3. **选定后**按 600 dpi 出成图，附上第十节的图注和正文引用句。同一篇论文后续的图沿用同一风格族，不再重复询问。
4. **以后风格库要扩充时：** Yikun 再发新样例，就按 8.1 的格式加 S7、S8……，写清视觉特征、适合场景和实现函数。

## 九、绘图模块 pub_fig.py

使用时把下面的代码写成 `pub_fig.py`，与绘图脚本放在同一目录，然后 `from pub_fig import *`。

```python
"""pub_fig: journal-ready matplotlib figures for Yikun's papers.

Adapted from the figures4papers house style by Chen Liu (CC BY-NC 4.0,
https://github.com/ChenLiu-1996/figures4papers) and the ASSB review V37 figure set.
Draw at FINAL print size; never rely on downscaling.
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
from PIL import Image

MM = 1 / 25.4

# width in mm, min dpi for the delivered raster, max height in mm, preferred raster format
JOURNALS = {
    "rsc":      dict(single=83,  double=171, max_h=233, dpi=600, fmt="tif"),   # Chem. Soc. Rev. etc.
    "ieee":     dict(single=88.9, double=181.9, max_h=220, dpi=600, fmt="tif"),  # TVT etc. (>300 colour, >600 line art)
    "elsevier": dict(single=90,  double=190, max_h=240, dpi=1000, fmt="tif"),  # 300 photo / 500 combo / 1000 line art
}

C = dict(  # colour-blind-safe core palette (V37)
    blue="#2C5F9E", teal="#2A9D8F", orange="#E9A23B", red="#D1495B", purple="#7B6FB0",
    grey="#9AA3AD", dark="#1F2328", mid="#5B6570",
    lblue="#E3EAF5", lteal="#DFF1EE", lorange="#FBEFD9", lred="#F8E1E5", lgrey="#EEF0F2",
)
# semantic roles (figures4papers idea, V37 colours)
ROLE = dict(key=C["blue"], improved=C["teal"], alternative=C["orange"], contrast=C["red"],
            baseline=C["grey"], extra=C["purple"])
SERIES = [C["blue"], C["teal"], C["orange"], C["red"], C["purple"], C["grey"]]


def apply_style(cjk=False):
    sans = ["Liberation Sans", "Arial", "Helvetica", "DejaVu Sans"]
    if cjk:
        sans = ["Noto Sans CJK SC", "Source Han Sans SC", "SimHei", "Microsoft YaHei"] + sans
    plt.rcParams.update({
        "font.family": "sans-serif", "font.sans-serif": sans,
        "font.size": 6.5, "axes.titlesize": 7, "axes.labelsize": 6.5,
        "xtick.labelsize": 6, "ytick.labelsize": 6, "legend.fontsize": 6,
        "axes.linewidth": 0.5, "xtick.major.width": 0.5, "ytick.major.width": 0.5,
        "xtick.major.size": 2.5, "ytick.major.size": 2.5, "lines.linewidth": 0.9,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.edgecolor": C["dark"], "axes.labelcolor": C["dark"], "text.color": C["dark"],
        "xtick.color": C["dark"], "ytick.color": C["dark"],
        "legend.frameon": False, "pdf.fonttype": 42, "svg.fonttype": "none",
        "mathtext.default": "regular", "hatch.linewidth": 0.5, "axes.unicode_minus": False,
    })


def figure(journal="rsc", width="double", height_mm=70):
    j = JOURNALS[journal]
    w = j[width] if isinstance(width, str) else width
    assert height_mm <= j["max_h"], f"height {height_mm} mm exceeds {j['max_h']} mm"
    return plt.figure(figsize=(w * MM, height_mm * MM))


def panel(fig, x, y, letter):
    fig.text(x, y, letter, fontsize=8, fontweight="bold", va="top", ha="left")


def box(ax, x, y, w, h, text="", fc=None, ec=None, fs=6.5, bold=False, lw=0.7):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.015",
                                fc=fc or C["lblue"], ec=ec or C["blue"], lw=lw,
                                transform=ax.transAxes, zorder=2))
    if text:
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs,
                fontweight="bold" if bold else "normal", transform=ax.transAxes, zorder=3)


def arrow(ax, x0, y0, x1, y1, color=None, lw=0.8, ls="-"):
    ax.add_artist(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=6,
                                  color=color or C["mid"], lw=lw, ls=ls,
                                  transform=ax.transAxes, zorder=4, shrinkA=0, shrinkB=0))


def grouped_bar(ax, categories, series, labels, colors=None, annotate=True, fmt="{:.2f}",
                hatches=None, ylabel=None):
    """Bars always start at zero (do not truncate bar axes)."""
    colors = colors or SERIES
    n = len(series)
    width = 0.8 / n
    x = np.arange(len(categories))
    for i, (vals, lab) in enumerate(zip(series, labels)):
        vals = np.asarray(vals, float)
        assert len(vals) == len(categories)
        b = ax.bar(x + (i - (n - 1) / 2) * width, vals, width * 0.92, label=lab,
                   color=colors[i % len(colors)], edgecolor="white", lw=0.4,
                   hatch=hatches[i] if hatches else None)
        if annotate:
            for r, v in zip(b, vals):
                ax.text(r.get_x() + r.get_width() / 2, v, " " + fmt.format(v), ha="center",
                        va="bottom", fontsize=5.6, rotation=90 if n > 3 else 0)
    ax.set_xticks(x)
    ax.set_xticklabels(categories)
    top = max(np.max(np.asarray(v, float)) for v in series)
    ax.set_ylim(0, top * 1.18)   # headroom for value labels and a top legend
    if ylabel:
        ax.set_ylabel(ylabel)


def trend(ax, x, ys, labels, colors=None, bands=None, xlabel=None, ylabel=None):
    """2-4 lines per axis; bands = list of (lo, hi) arrays or None."""
    colors = colors or SERIES
    for i, (y, lab) in enumerate(zip(ys, labels)):
        ax.plot(x, y, color=colors[i % len(colors)], label=lab)
        if bands and bands[i] is not None:
            ax.fill_between(x, bands[i][0], bands[i][1], color=colors[i % len(colors)],
                            alpha=0.18, lw=0)
    if xlabel: ax.set_xlabel(xlabel)
    if ylabel: ax.set_ylabel(ylabel)


def dot_range(ax, labels, lo, hi, point=None, colors=None, fmt="{:.2f}", xlabel=None):
    """Horizontal ranges for values reported only as ranges; point marks a single value."""
    colors = colors or SERIES
    n = len(labels)
    for i in range(n):
        y = n - 1 - i
        c = colors[i % len(colors)]
        if hi[i] > lo[i]:
            ax.add_patch(Rectangle((lo[i], y - 0.12), hi[i] - lo[i], 0.24, fc=c, alpha=0.35, ec="none"))
        v = point[i] if point is not None else (lo[i] + hi[i]) / 2
        ax.scatter([v], [y], s=20, color=c, zorder=3)
        txt = fmt.format(lo[i]) if hi[i] == lo[i] else f"{fmt.format(lo[i])}–{fmt.format(hi[i])}"
        ax.text(hi[i] + 0.03 * max(hi), y, " " + txt, ha="left", va="center", fontsize=5.6, color=c)
    ax.set_yticks(range(n)); ax.set_yticklabels(labels[::-1])
    ax.tick_params(axis="y", length=0); ax.spines["left"].set_visible(False)
    ax.set_ylim(-0.6, n - 0.4)
    ax.set_xlim(0, max(hi) * 1.3)
    if xlabel: ax.set_xlabel(xlabel)


def heatmap(ax, M, xlabels, ylabels, cmap="viridis", cbar_label=None, annotate=False, fmt="{:.2f}"):
    im = ax.imshow(np.asarray(M), cmap=cmap, aspect="auto")
    ax.set_xticks(range(len(xlabels))); ax.set_xticklabels(xlabels, rotation=45, ha="right")
    ax.set_yticks(range(len(ylabels))); ax.set_yticklabels(ylabels)
    for s in ax.spines.values(): s.set_visible(False)
    cb = ax.figure.colorbar(im, ax=ax, fraction=0.046, pad=0.03)
    cb.outline.set_linewidth(0.4)
    if cbar_label: cb.set_label(cbar_label)
    if annotate:
        M = np.asarray(M); mid = (M.max() + M.min()) / 2
        for i in range(M.shape[0]):
            for j in range(M.shape[1]):
                ax.text(j, i, fmt.format(M[i, j]), ha="center", va="center", fontsize=5.5,
                        color="white" if M[i, j] < mid else C["dark"])
    return im


def legend_panel(ax, handles, labels, ncol=1):
    ax.set_axis_off()
    ax.legend(handles, labels, loc="center", ncol=ncol)


def save(fig, path, journal="rsc", text_width_mm=None):
    """Write PNG (for Word), TIFF (submission) and vector PDF; report size and dpi.
    text_width_mm: width the PNG will be placed at in Word (e.g. 165 for Letter with 1-in margins)."""
    dpi = JOURNALS[journal]["dpi"]
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    fig.savefig(path + ".png", dpi=dpi, facecolor="white")
    fig.savefig(path + ".pdf", facecolor="white")
    im = Image.open(path + ".png").convert("RGB")          # no alpha channel
    im.save(path + ".png", dpi=(dpi, dpi))
    im.save(path + ".tif", dpi=(dpi, dpi), compression="tiff_lzw")
    plt.close(fig)
    w, h = im.size
    msg = f"{os.path.basename(path)}: {w}x{h}px = {w / dpi * 25.4:.0f}x{h / dpi * 25.4:.0f} mm @ {dpi} dpi"
    if text_width_mm:
        msg += f"; in Word at {text_width_mm} mm -> {w / (text_width_mm / 25.4):.0f} dpi"
    print(msg)
    return w, h
```

### 用法示例

```python
from pub_fig import *
apply_style()                                   # 中文图用 apply_style(cjk=True)
fig = figure("rsc", "double", height_mm=60)     # 171 mm 宽
ax = fig.add_axes([0.08, 0.2, 0.4, 0.68])
grouped_bar(ax, ["Stoich.", "Stoich.+geom.", "LLM"], [[1.108, 1.172, 0.798]], ["Test MAE"],
            colors=[C["blue"]], fmt="{:.3f}", ylabel="MAE (log$_{10}$ S cm$^{-1}$)")
ax2 = fig.add_axes([0.6, 0.2, 0.36, 0.68])
dot_range(ax2, ["M3GNet", "MACE, SevenNet", "fine-tuned"], [0.32, 0.07, 0.10], [0.32, 0.08, 0.11],
          xlabel="Barrier MAE (eV)")
panel(fig, 0.0, 0.99, "a"); panel(fig, 0.52, 0.99, "b")
save(fig, "figures/fig18", journal="rsc", text_width_mm=165)
```

## 十、图注写作（每张图必须同时交付）

每张图的交付物包括：
- 图文件；
- 英文图注（中文稿另附中文图注）；
- 一句正文引用句；
- 来源与许可核对行，即"子图 → 来源 → 许可 → 是否已取得"。

### 10.1 期刊格式

| 期刊 | 写法 | 示例开头 |
|---|---|---|
| RSC（CSR 等） | "Fig. n" 加粗，后接空格，不加句点。综述常不写总标题，直接把子图串成一句："(a) …, (b) … and (c) …." | **Fig. 2** (a) Selected milestones of …, (b) … |
| IEEE | "Fig. n." 后接句点。先写一句总述，再逐个子图写 "(a) … (b) …"，用句首大写 | Fig. 3. Fault-detection pipeline. (a) … |
| Elsevier | 要有简短标题（不写在图上）加说明："Fig. n. 标题. (a) …" | Fig. 4. Ionic conductivity prediction. (a) … |

以上格式投稿前以期刊作者指南为准。

### 10.2 结构顺序

1. **总述句**：用一句话说明整图展示什么（RSC 综述可省）。
2. **逐个子图**：(a) 内容 + 关键条件（材料、倍率/电流密度、温度、数据集、测试划分）。子图描述必须与子图实际内容一一对应。写完逐个对照一遍。
3. **图形编码**：颜色、符号、线型、色带、误差棒各代表什么；误差棒写明是标准差还是标准误，以及 n 是多少。
4. **数据来源与方法**：例如 "Data from Web of Science using 'solid-state electrolyte' AND 'machine learning' as keywords (retrieved 2026-11-20); 2026 is a partial year."。部分年份数据不完整时必须说明。
5. **来源与许可**：逐个子图写，用第三节的措辞。RSC 样例的写法是 "Reproduced with permission from ref. 129. Copyright 2023, Elsevier."；CC BY 的写法是 "Reproduced from ref. 41 under CC BY 4.0."。出版社写全称（Springer Nature、American Chemical Society），不能写期刊名。
6. **缩写**：首次出现给全称，图注要能脱离正文读懂。

### 10.3 写法规则

- 描述图上有什么，用一般现在时。不写结论性评价（"remarkable"、"superior"），解读留给正文。
- 图注里的术语、符号、单位要与图上标签完全一致（不能图上写 "Vehicle mechanism"、图注写 "vehicular"），单位统一用 SI 写法（mAh g$^{-1}$）。
- 图注中的数字与图、正文、原文正式版一致（第三节第 5 条）。
- 长度：子图多时英文图注尽量控制在 100 词左右。实验细节放正文或 SI。
- 中文图注与英文逐句对应，术语用中文稿里的统一译法，化学式和单位不翻译。
- **正文引用句**：
  - 每张图在正文里先被引用，再出现，按编号顺序；
  - 写到子图级别（"as shown in Fig. 3b"，RSC 用 "Fig. 3b" 或 "Fig. 3(b)"，与期刊一致）；
  - 引用句说明读者该从图里看什么，不只写 "see Fig. 3"。

### 10.4 样例里不要学的地方（检查自己的图注时对照）

- **子图与图注对不上：** CSR 样例 Fig. 11 图注写 "(b) and (c) rate performance and cyclability"，但 (b) 实际是 TEM 形貌图。
- **出版社写错：** 同一图注 "Copyright 2016, Nature" 写的是期刊名，出版社应为 Springer Nature。
- **时间跨度不一致：** CSR 样例 Fig. 2 图注写 "two decades"，子图标题写 "a quarter century"，数据是 2000–2025 年。另外 2025 年可能是不完整年份，图注没有说明。
- **术语不统一：** 图注写 "vehicular"，图上写 "Vehicle Mechanism"。
- **贴图风格不统一：** 拼贴子图字体、单位写法（mAh/g 与 mAh g$^{-1}$）、大小写不统一，还有拼写错误（"ployhedron"）。

### 10.5 模板

**RSC 综述，自绘示意图 + 重画数据（S4）**
> **Fig. 5** (a) Schematic of vacancy hopping and concerted migration of Li$^+$ in a crystalline solid electrolyte; green circles are Li$^+$ and grey circles are vacant sites. (b) Test MAE of log$_{10}$ ionic conductivity for models using stoichiometric features, stoichiometric and geometric features, and an LLM-based representation. Data from ref. [n].

> 图 5 （a）晶态固态电解质中 Li$^+$ 空位跳跃与协同迁移示意图，绿色圆为 Li$^+$，灰色圆为空位。（b）分别采用化学计量特征、化学计量 + 几何特征和基于大语言模型的表示时，log$_{10}$ 离子电导率的测试集 MAE。数据取自文献 [n]。

> 正文：Fig. 5b shows that the LLM-based representation gave the lowest test MAE in ref. [n], whereas adding geometric descriptors did not reduce the error.

**时间轴（S3）**
> **Fig. 2** (a) Selected milestones in solid electrolytes, materials data infrastructure and AI models relevant to ASSBs [n–m]. Icons and colours indicate the category of each milestone (orange, materials; blue, data and tools; green, AI models).

**流程/路线图（S0–S2）**
> **Fig. 1** AI4Science workflow for ASSBs, from material discovery and atomistic simulation to property prediction and autonomous experimentation; the dashed arrow denotes experimental feedback. Original synthesis based on refs [n–m].

**拼贴（S6）**：每个子图一句内容 + 一句来源；全部写完后统计转载子图占比，在回复里报告。

## 十一、示意图模块 pub_schem.py

与 pub_fig.py 放在同一目录。`mm_canvas(fig)` 建一个以毫米为单位、等比例的整图坐标系，所有示意图元素直接按毫米摆放。

```python
"""pub_schem: schematic primitives and flat icons for Yikun's style library (S1-S6).

Everything is drawn on one full-figure axes in millimetres (mm_canvas), so circles stay round
and positions can be read straight off the journal size table. Icons are simple generic shapes
drawn from patches, not copies of any icon set.
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import (FancyBboxPatch, Rectangle, Circle, Ellipse, Polygon,
                                FancyArrowPatch, PathPatch, Wedge)
from matplotlib.path import Path
from matplotlib.colors import LinearSegmentedColormap, to_rgb

MM = 1 / 25.4

# ---- palettes learned from the samples (see SKILL.md section 8) -------------------------
OFFICE = dict(  # S1/S2: PowerPoint-theme pastel + saturated pairs (mentor's review figures)
    green="#70AD47", lgreen="#E2F0D9", mgreen="#A9D18E",
    yellow="#FFD966", lyellow="#FFF2CC",
    orange="#C55A11", lorange="#F8CBAD",
    blue="#4472C4", lblue="#BDD7EE", pblue="#B4C7E7", vlblue="#DEEBF7",
    grey="#E6E7EB", navy="#10314D", magenta="#9A4590", cyan="#00ACDC", lime="#DDE882",
    violet="#6751E8", chevron="#5D5036", ring="#B6AFAB",
)
CSR = dict(  # S3/S4/S5: Chem. Soc. Rev. timeline/bars + tinted panels
    blue="#3173CA", green="#5AAE30", orange="#F28C28", dark="#475178", grey="#91949E",
    tint_green="#F3F9F1", tint_pink="#FBF3F2", tint_blue="#ECF5FC", tint_grey="#F5F6F8",
    tint_lilac="#F6F4FA", magenta="#99008F",
)


def mm_canvas(fig):
    W, H = fig.get_size_inches() / MM
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W); ax.set_ylim(0, H); ax.set_aspect("equal"); ax.set_axis_off()
    return ax


def _poly(ax, pts, fc, ec="none", lw=0, z=3, **kw):
    p = Polygon(pts, closed=True, fc=fc, ec=ec, lw=lw, zorder=z, **kw)
    ax.add_patch(p); return p


def gradient_fill(ax, patch, c_top, c_bottom, z=1):
    """Fill a patch with a vertical gradient (clipped image)."""
    ax.add_patch(patch); patch.set_zorder(z)
    (x0, y0), (x1, y1) = patch.get_path().transformed(patch.get_patch_transform()).get_extents().get_points()
    cmap = LinearSegmentedColormap.from_list("g", [c_bottom, c_top])
    im = ax.imshow(np.linspace(0, 1, 256)[:, None], extent=(x0, x1, y0, y1), origin="lower",
                   cmap=cmap, aspect="auto", zorder=z, interpolation="bicubic")
    im.set_clip_path(patch)
    return im


# ---- containers ---------------------------------------------------------------------------
def dotted_column(ax, x, y, w, h, title=None, color=OFFICE["green"], fs=8, serif=True, lw=0.9):
    """S1: column framed by a green dotted border, bold title at top-left."""
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=1.2",
                                fc="white", ec=color, lw=lw, ls=(0, (1, 1.6)), zorder=1))
    if title:
        ax.text(x + 1.5, y + h - 1.4, title, ha="left", va="top", fontsize=fs, fontweight="bold",
                family="serif" if serif else "sans-serif", zorder=5, linespacing=1.1)


def tint_panel(ax, x, y, w, h, color, color2=None, label=None, label_style="paren", fs=8):
    """S4: panel on a soft tinted (optionally gradient) background, label '(a)' or bold 'a'."""
    r = Rectangle((x, y), w, h, lw=0)
    if color2:
        gradient_fill(ax, r, color, color2, z=0.5)
    else:
        r.set_facecolor(color); r.set_zorder(0.5); ax.add_patch(r)
    if label:
        t = f"({label})" if label_style == "paren" else label
        ax.text(x + 1.2, y + h - 1.0, t, ha="left", va="top", fontsize=fs,
                fontweight="normal" if label_style == "paren" else "bold", zorder=6)


def ellipse_cloud(ax, items, x, y, w, h, colors, fs=6.5, serif=True, seed=0):
    """S1: overlapping pastel ellipses carrying property names. items laid out in rows
    (list of lists); ellipse width follows text length."""
    rng = np.random.default_rng(seed)
    nrow = len(items); rh = h / nrow; k = 0
    for i, row in enumerate(items):
        cy = y + h - rh * (i + 0.5)
        lens = np.array([max(len(s.split("\n")[0]), len(s.split("\n")[-1])) for s in row], float)
        widths = w * lens / lens.sum()
        cx = x
        for s, ww in zip(row, widths):
            ew = min(ww * 1.12, w); eh = rh * (1.25 if "\n" in s else 0.95)
            jx = rng.uniform(-0.6, 0.6); jy = rng.uniform(-0.8, 0.8)
            ax.add_patch(Ellipse((cx + ww / 2 + jx, cy + jy), ew, eh, fc=colors[k % len(colors)],
                                 ec="none", alpha=0.85, zorder=2))
            ax.text(cx + ww / 2 + jx, cy + jy, s, ha="center", va="center", fontsize=fs,
                    family="serif" if serif else "sans-serif", zorder=3, linespacing=0.95)
            cx += ww; k += 1


def teardrop(ax, cx, cy, r, tip_h, c_light, c_dark=None, z=1):
    """S2: water-drop body (round bottom centred at cx,cy, tip pointing up by tip_h)."""
    d = r + tip_h; phi = np.arccos(r / d)
    a = np.linspace(np.pi / 2 - phi, np.pi / 2 + phi - 2 * np.pi, 120)
    pts = [(cx, cy + d)] + [(cx + r * np.cos(t), cy + r * np.sin(t)) for t in a]
    p = Polygon(pts, closed=True, lw=0)
    if c_dark:
        gradient_fill(ax, p, c_dark, c_light, z=z)   # darker towards the tip, as in the sample
    else:
        p.set_facecolor(c_light); p.set_zorder(z); ax.add_patch(p)
    return p


def ring(ax, cx, cy, r, ec=OFFICE["ring"], lw=2.2, fc="white", z=4):
    """S2: white disc with a thick grey ring that holds an icon."""
    ax.add_patch(Circle((cx, cy), r, fc=fc, ec=ec, lw=lw, zorder=z))


def pill(ax, cx, cy, text, color, w=None, h=4.2, fs=7, tc="black", serif=True, bold=True, z=6):
    """S2: rounded label in the stage's saturated colour."""
    w = w or (len(text) * fs * 0.21 + 4)
    ax.add_patch(FancyBboxPatch((cx - w / 2, cy - h / 2), w, h, boxstyle=f"round,pad=0,rounding_size={h/2}",
                                fc=color, ec="none", zorder=z))
    ax.text(cx, cy, text, ha="center", va="center", fontsize=fs, color=tc, zorder=z + 1,
            fontweight="bold" if bold else "normal", family="serif" if serif else "sans-serif")


def chevron(ax, x, y, w, h, color=OFFICE["chevron"], notch=0.45, z=3):
    """S2: bold chevron between stages (x, y = left-centre)."""
    n = w * notch
    _poly(ax, [(x, y + h / 2), (x + w - n, y + h / 2), (x + w, y), (x + w - n, y - h / 2),
               (x, y - h / 2), (x + n, y)], color, z=z)


def down_arrows(ax, x, y0, y1, color=OFFICE["cyan"], n=2, gap=2.2, lw=0.8):
    """S1: thin paired arrows linking stacked icons."""
    for i in range(n):
        xx = x + (i - (n - 1) / 2) * gap
        ax.add_artist(FancyArrowPatch((xx, y0), (xx, y1), arrowstyle="-|>", mutation_scale=5,
                                      color=color, lw=lw, zorder=4, shrinkA=0, shrinkB=0))


def flow_arrow(ax, x0, y0, x1, y1, color="#5B6570", lw=0.8, ms=6, z=4, ls="-", rad=0.0):
    ax.add_artist(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=ms, color=color,
                                  lw=lw, ls=ls, zorder=z, shrinkA=0, shrinkB=0,
                                  connectionstyle=f"arc3,rad={rad}"))


def timeline(ax, x0, x1, y, events, cat_style, fs=6, label_h=14, icon_s=7):
    """S3: horizontal time axis; each event = (tick_label, category, text).
    cat_style = {category: (icon_kind, colour)}; the category word is printed in its colour
    above the icon, the event text above that."""
    n = len(events); xs = np.linspace(x0 + (x1 - x0) / (2 * n), x1 - (x1 - x0) / (2 * n), n)
    ax.plot([x0, x1], [y, y], color="#333333", lw=0.9, zorder=3, solid_capstyle="butt")
    step = xs[1] - xs[0] if n > 1 else 10
    for k in np.arange(x0 + step / 2, x1, step / 2):
        ax.plot([k, k], [y, y + 1.0], color="#333333", lw=0.6, zorder=3)
    for xx, (tick, cat, txt) in zip(xs, events):
        kind, col = cat_style[cat]
        ax.plot([xx, xx], [y, y + 1.8], color="#333333", lw=0.9, zorder=3)
        ax.text(xx, y - 1.6, tick, ha="center", va="top", fontsize=fs, fontweight="bold")
        icon(ax, kind, xx, y + 3.5 + icon_s / 2, icon_s, col)
        ax.text(xx, y + 5 + icon_s, cat, ha="center", va="bottom", fontsize=fs - 0.3, color=col)
        ax.text(xx, y + 8.5 + icon_s, txt, ha="center", va="bottom", fontsize=fs, linespacing=1.0)
    return xs


# ---- icons (all centred on x, y; s = overall size in mm) ---------------------------------
def icon(ax, kind, x, y, s, color="#2C5F9E", accent=None, z=5):
    a = accent or color
    f = ICONS[kind]
    f(ax, x, y, s, color, a, z)


def _database(ax, x, y, s, c, a, z):
    w = s * 0.8; hh = s * 0.26; e = s * 0.16
    for i in range(3):
        yc = y - s / 2 + e / 2 + i * hh * 1.08
        ax.add_patch(Rectangle((x - w / 2, yc), w, hh, fc=c, ec="none", zorder=z + i * 0.1))
        ax.add_patch(Ellipse((x, yc), w, e, fc=c, ec="none", zorder=z + i * 0.1))
        ax.add_patch(Ellipse((x, yc + hh), w, e, fc=c, ec="white", lw=0.6, zorder=z + i * 0.1 + 0.05))
    ax.add_patch(Ellipse((x, y - s / 2 + e / 2 + 2 * hh * 1.08 + hh), w, e, fc=a if a != c else "#E0F5FB",
                         ec="white", lw=0.6, zorder=z + 0.4))


def _gear_pts(x, y, r, n=8, depth=0.28, rot=0):
    pts = []
    for i in range(n):
        t0 = rot + 2 * np.pi * i / n
        for dt, rr in [(-0.32, r * (1 - depth)), (-0.18, r), (0.18, r), (0.32, r * (1 - depth))]:
            t = t0 + dt * 2 * np.pi / n
            pts.append((x + rr * np.cos(t), y + rr * np.sin(t)))
    return pts


def _gear(ax, x, y, s, c, a, z):
    r = s / 2
    _poly(ax, _gear_pts(x, y, r), c, z=z)
    ax.add_patch(Circle((x, y), r * 0.42, fc=a if a != c else "white", ec="none", zorder=z + 0.1))
    ax.add_patch(Circle((x, y), r * 0.22, fc="white", ec="none", zorder=z + 0.2))


def _gears(ax, x, y, s, c, a, z):
    _gear(ax, x - s * 0.17, y + s * 0.17, s * 0.62, c, "white", z)
    _gear(ax, x + s * 0.22, y - s * 0.22, s * 0.5, a, "white", z + 0.3)


def _atom(ax, x, y, s, c, a, z):
    for ang in (0, 60, 120):
        ax.add_patch(Ellipse((x, y), s, s * 0.36, angle=ang, fc="none", ec=c, lw=0.9, zorder=z))
    ax.add_patch(Circle((x, y), s * 0.08, fc=a, ec="none", zorder=z + 0.1))


def _battery(ax, x, y, s, c, a, z):
    w, h = s * 0.5, s * 0.9
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle=f"round,pad=0,rounding_size={s*0.05}",
                                fc=c, ec="none", zorder=z))
    ax.add_patch(Rectangle((x - w * 0.22, y + h / 2), w * 0.44, s * 0.06, fc=c, ec="none", zorder=z))
    ax.add_patch(Rectangle((x - w * 0.36, y - h * 0.42), w * 0.72, h * 0.84, fc="white", ec="none", zorder=z + 0.1))
    for i in range(4):
        ax.add_patch(Rectangle((x - w * 0.3, y - h * 0.38 + i * h * 0.2), w * 0.6, h * 0.15, fc=c,
                               ec="none", alpha=0.25, zorder=z + 0.15))
    _poly(ax, [(x + s * 0.05, y + h * 0.36), (x - s * 0.1, y - s * 0.02), (x + s * 0.0, y - s * 0.02),
               (x - s * 0.06, y - h * 0.36), (x + s * 0.11, y + s * 0.05), (x + s * 0.01, y + s * 0.05)],
          a if a != c else c, z=z + 0.2)


def _chart(ax, x, y, s, c, a, z):
    b = s * 0.15; base = y - s * 0.42
    for i, hh in enumerate([0.3, 0.5, 0.42, 0.7]):
        ax.add_patch(Rectangle((x - s * 0.4 + i * s * 0.22, base), b, s * hh, fc=c if i != 3 else a,
                               ec="none", zorder=z))
    ax.plot([x - s * 0.45, x + s * 0.45], [base, base], color="#333333", lw=0.7, zorder=z)
    xs = np.array([-0.38, -0.12, 0.1, 0.38]) * s + x; ys = np.array([0.0, 0.18, 0.12, 0.4]) * s + y
    ax.plot(xs, ys, color=a, lw=1.0, zorder=z + 0.2)
    flow_arrow(ax, xs[-2], ys[-2], xs[-1] + s * 0.05, ys[-1] + s * 0.05, color=a, lw=1.0, ms=5, z=z + 0.2)


def _flask(ax, x, y, s, c, a, z):
    nw, bw, h = s * 0.18, s * 0.75, s * 0.9
    top, bot = y + h / 2, y - h / 2
    pts = [(x - nw / 2, top), (x + nw / 2, top), (x + nw / 2, y + h * 0.1), (x + bw / 2, bot),
           (x - bw / 2, bot), (x - nw / 2, y + h * 0.1)]
    _poly(ax, pts, "white", ec=c, lw=0.9, z=z)
    lv = bot + h * 0.38; fr = (lv - bot) / (y + h * 0.1 - bot)
    lw_ = bw - (bw - nw) * fr
    _poly(ax, [(x - lw_ / 2, lv), (x + lw_ / 2, lv), (x + bw / 2, bot), (x - bw / 2, bot)], a, z=z + 0.1)


def _tree(ax, x, y, s, c, a, z):
    bw, bh = s * 0.3, s * 0.18
    ax.add_patch(Rectangle((x - bw / 2, y + s * 0.3), bw, bh, fc=a, ec="none", zorder=z))
    for dx in (-0.3, 0.3):
        ax.plot([x, x, x + dx * s, x + dx * s], [y + s * 0.3, y + s * 0.12, y + s * 0.12, y - s * 0.05],
                color=c, lw=0.9, zorder=z - 0.1)
        ax.add_patch(Rectangle((x + dx * s - bw / 2, y - s * 0.05 - bh), bw, bh, fc="white", ec=c, lw=0.9, zorder=z))
        ax.add_patch(Rectangle((x + dx * s - bw / 2, y - s * 0.42), bw, bh, fc="white", ec=c, lw=0.9, zorder=z))
        ax.plot([x + dx * s] * 2, [y - s * 0.05 - bh, y - s * 0.42 + bh], color=c, lw=0.9, zorder=z - 0.1)


def _classify(ax, x, y, s, c, a, z):
    rng = np.random.default_rng(3)
    h = s / 2
    ax.plot([x - h, x - h, x + h], [y + h, y - h, y - h], color="#333333", lw=0.7, zorder=z)
    t = np.linspace(-1, 1, 50)
    ax.plot(x + t * h * 0.9, y + np.tanh(t * 3) * h * 0.7, color=OFFICE["violet"], lw=1.2, zorder=z)
    for _ in range(14):
        px, py = rng.uniform(-0.85, 0.9, 2)
        side = py > np.tanh(px * 3) * 0.7
        ax.scatter([x + px * h], [y + py * h * 0.9], s=2.2, color=c if side else a, zorder=z + 0.1, lw=0)


def _network(ax, x, y, s, c, a, z):
    r = s / 2
    ang = np.linspace(0, 2 * np.pi, 7)[:-1] + np.pi / 6
    pts = [(x + r * 0.9 * np.cos(t), y + r * 0.9 * np.sin(t)) for t in ang] + [(x, y)]
    for i in range(6):
        for j in (i + 1, 6):
            j = j % 7 if j != 6 else 6
            ax.plot([pts[i][0], pts[j][0]], [pts[i][1], pts[j][1]], color=c, lw=0.7, zorder=z)
    for p in pts:
        ax.add_patch(Circle(p, s * 0.07, fc="white", ec=c, lw=0.8, zorder=z + 0.1))


def _molecule(ax, x, y, s, c, a, z):
    pts = [(-0.3, -0.1), (0.0, 0.1), (0.3, -0.05), (0.05, 0.42), (-0.25, -0.42), (0.42, 0.3)]
    pts = [(x + px * s, y + py * s) for px, py in pts]
    for i, j in [(0, 1), (1, 2), (1, 3), (0, 4), (2, 5)]:
        ax.plot([pts[i][0], pts[j][0]], [pts[i][1], pts[j][1]], color="#555555", lw=1.0, zorder=z)
    cols = [c, a, c, "#D1495B", "#9AA3AD", a]
    for p, cc, rr in zip(pts, cols, [0.12, 0.14, 0.12, 0.09, 0.09, 0.09]):
        ax.add_patch(Circle(p, s * rr, fc=cc, ec="none", zorder=z + 0.1))


def _lattice(ax, x, y, s, c, a, z):
    n = 4; g = s / (n - 1) * 0.85
    for i in range(n):
        for j in range(n):
            px, py = x - s * 0.425 + i * g, y - s * 0.425 + j * g
            ax.add_patch(Circle((px, py), s * 0.075, fc=c, ec="none", zorder=z))
    for i in range(n - 1):
        for j in range(n - 1):
            ax.add_patch(Circle((x - s * 0.425 + (i + 0.5) * g, y - s * 0.425 + (j + 0.5) * g), s * 0.05,
                                fc=a, ec="none", zorder=z))


def _cube(ax, x, y, s, c, a, z):
    h = s * 0.32
    top = [(x, y + 2 * h * 0.6), (x + h * 1.1, y + h * 0.6), (x, y), (x - h * 1.1, y + h * 0.6)]
    left = [(x - h * 1.1, y + h * 0.6), (x, y), (x, y - h * 1.3), (x - h * 1.1, y - h * 0.7)]
    right = [(x, y), (x + h * 1.1, y + h * 0.6), (x + h * 1.1, y - h * 0.7), (x, y - h * 1.3)]
    _poly(ax, top, a, ec="#2A2A2A", lw=0.7, z=z); _poly(ax, left, c, ec="#2A2A2A", lw=0.7, z=z)
    _poly(ax, right, to_rgb(c), ec="#2A2A2A", lw=0.7, z=z, alpha=0.75)
    for (px, py) in [top[0], (x + h * 1.1, y - h * 0.7), (x - h * 1.1, y - h * 0.7)]:
        ax.add_patch(Circle((px, py), s * 0.05, fc="white", ec="#2A2A2A", lw=0.6, zorder=z + 0.1))


def _monitor(ax, x, y, s, c, a, z):
    w, h = s * 0.9, s * 0.6
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2 + s * 0.1), w, h, boxstyle=f"round,pad=0,rounding_size={s*0.04}",
                                fc="white", ec=c, lw=1.0, zorder=z))
    ax.add_patch(Rectangle((x - s * 0.06, y - s * 0.38), s * 0.12, s * 0.18, fc=c, ec="none", zorder=z))
    ax.add_patch(Rectangle((x - s * 0.22, y - s * 0.42), s * 0.44, s * 0.05, fc=c, ec="none", zorder=z))
    _cube(ax, x, y + s * 0.1, s * 0.45, a, "#F9B418", z + 0.2)


def _particles(ax, x, y, s, c, a, z):
    cols = [c, a, "#D1495B", "#E9A23B", a, c]
    pos = [(-0.32, 0.3), (0.05, 0.36), (0.36, 0.12), (-0.3, -0.18), (0.08, -0.05), (0.25, -0.36)]
    dirs = [200, 60, 20, 250, 300, 320]
    r = s * 0.09
    for (px, py), cc, t in zip(pos, cols, np.radians(dirs)):
        cx, cy = x + px * s, y + py * s
        ax.add_patch(Circle((cx, cy), r, fc=cc, ec="#333333", lw=0.4, zorder=z))
        flow_arrow(ax, cx + r * np.cos(t), cy + r * np.sin(t), cx + 2.4 * r * np.cos(t),
                   cy + 2.4 * r * np.sin(t), color="#333333", lw=0.5, ms=3.5, z=z)


def _splash(ax, x, y, s, c, a, z):
    rng = np.random.default_rng(11)
    t = np.linspace(0, 2 * np.pi, 13)[:-1]
    rr = np.where(np.arange(12) % 2 == 0, 0.5, 0.25) * s * rng.uniform(0.8, 1.1, 12)
    _poly(ax, list(zip(x + rr * np.cos(t), y + rr * np.sin(t))), c, z=z)
    ax.add_patch(Circle((x, y), s * 0.22, fc=c, ec="none", zorder=z))
    for _ in range(4):
        tt = rng.uniform(0, 2 * np.pi)
        ax.add_patch(Circle((x + 0.58 * s * np.cos(tt), y + 0.58 * s * np.sin(tt)), s * 0.04, fc=c, ec="none", zorder=z))


def _pulse(ax, x, y, s, c, a, z):
    t = np.array([-0.5, -0.2, -0.1, 0.0, 0.08, 0.16, 0.5]) * s
    v = np.array([0, 0, 0.25, -0.3, 0.35, 0, 0]) * s
    ax.plot(x + t, y + v, color=c, lw=1.1, zorder=z, solid_joinstyle="round")


ICONS = dict(database=_database, gear=_gear, gears=_gears, atom=_atom, battery=_battery, chart=_chart,
             flask=_flask, tree=_tree, classify=_classify, network=_network, molecule=_molecule,
             lattice=_lattice, cube=_cube, monitor=_monitor, particles=_particles, splash=_splash,
             pulse=_pulse)
```

## 十二、风格示例脚本 demos.py

用 ASSB AI4Science 内容画出 S0–S6 的示例（`python demos.py s1 s2` 只画指定风格）。做选型缩略图时，复制对应函数，换成 Yikun 的内容，并改用 `fig.savefig(path, dpi=150)` 出图。S3 的里程碑和 S4(b) 的 MAE 是真实文献内容（Kim et al., JCP 2026 正式版数值），用在论文里时要补上引用。

```python
"""Render one demo per style (S0-S6) with ASSB AI4Science content, 171 mm wide, 600 dpi."""
import sys
from pub_fig import *
from pub_schem import *

apply_style()
plt.rcParams["font.serif"] = ["Liberation Serif", "Times New Roman", "DejaVu Serif"]
OUT = "out/"
SER = dict(family="serif")


def fig_mm(h):
    fig = plt.figure(figsize=(171 * MM, h * MM)); return fig, mm_canvas(fig)


# ---------------- S0: V37 Nature line style ----------------------------------------------
def s0():
    fig, ax = fig_mm(32)
    names = ["Material\ndiscovery", "Atomistic\nsimulation", "Property\nprediction", "Autonomous\nexperiment"]
    subs = ["generative models,\nscreening", "MLIP-MD,\nLi$^+$ diffusion", "conductivity,\ninterface stability",
            "closed-loop\nsynthesis"]
    fills = [(C["lblue"], C["blue"]), (C["lteal"], C["teal"]), (C["lorange"], C["orange"]), (C["lred"], C["red"])]
    w, g = 35.5, 8
    for i, (n, s, (fc, ec)) in enumerate(zip(names, subs, fills)):
        x = 3 + i * (w + g)
        tcol = "#B26B12" if ec == C["orange"] else ec
        ax.add_patch(FancyBboxPatch((x, 9), w, 20, boxstyle="round,pad=0,rounding_size=1.2", fc=fc, ec=ec, lw=0.7))
        ax.text(x + w / 2, 24, n, ha="center", va="center", fontsize=7, fontweight="bold", color=tcol, linespacing=1.05)
        ax.text(x + w / 2, 14.5, s, ha="center", va="center", fontsize=6.2, linespacing=1.05)
        if i < 3:
            flow_arrow(ax, x + w + 1, 19, x + w + g - 1, 19)
    xl, xr = 3 + w / 2, 3 + 3 * (w + g) + w / 2
    ax.plot([xr, xr, xl], [9, 4, 4], color=C["mid"], lw=0.8, ls=(0, (2, 1.5)))
    flow_arrow(ax, xl, 4, xl, 8.8, color=C["mid"])
    ax.text(85.5, 4.8, "experimental feedback", ha="center", va="bottom", fontsize=6, color=C["mid"], style="italic")
    save(fig, OUT + "S0_nature_line", text_width_mm=165)


# ---------------- S1: dotted-column workflow ---------------------------------------------
def s1():
    fig, ax = fig_mm(80)
    widths = [50, 35, 36, 42]; gap = 2.6; H = 78; y0 = 1
    xs = [0.6]
    for w in widths[:-1]:
        xs.append(xs[-1] + w + gap)
    titles = ["Data and properties", "Feature\nengineering", "Model building", "Deployment"]
    for x, w, t in zip(xs, widths, titles):
        dotted_column(ax, x, y0, w, H, t, fs=8)
    
    # col 1: cell sketch + property cloud
    x = xs[0]
    cy = 57
    ax.add_patch(Rectangle((x + 4, cy - 7), 13, 14, fc="#E3EAF5", ec=OFFICE["navy"], lw=0.6))
    for (px, py) in [(6.5, 3), (10, 4.5), (14, 2.5), (7.5, -1.5), (12, -0.5), (6.5, -5), (10.5, -4.5), (14.5, -3)]:
        ax.add_patch(Circle((x + px + 1, cy + py), 1.25, fc=OFFICE["magenta"], ec="none", alpha=0.85))
    ax.add_patch(Rectangle((x + 17, cy - 7), 12, 14, fc="#FFF2CC", ec=OFFICE["navy"], lw=0.6))
    for i in range(4):
        for j in range(5):
            ax.add_patch(Circle((x + 18.6 + i * 2.9, cy - 5.6 + j * 2.8), 0.55, fc=OFFICE["orange"], ec="none"))
    ax.add_patch(Rectangle((x + 29, cy - 7), 9, 14, fc="#D9D9D9", ec=OFFICE["navy"], lw=0.6))
    for lab, xx in [("Cathode", 10.5), ("SSE", 23), ("Li", 33.5)]:
        ax.text(x + xx, cy + 8.2, lab, ha="center", va="bottom", fontsize=6, **SER)
    ax.add_patch(Rectangle((x + 2.5, cy - 7.9), 1.4, 15.8, fc="#7F7F7F", ec="none"))
    ax.add_patch(Rectangle((x + 38, cy - 7.9), 1.4, 15.8, fc=OFFICE["orange"], ec="none"))
    ax.text(x + 2, 44.5, "Target properties", ha="left", va="top", fontsize=8, fontweight="bold", **SER)
    ellipse_cloud(ax, [["Ionic\nconductivity", "Activation\nenergy"], ["Stability\nwindow", "Interface\nresistance"],
                       ["Elastic modulus", "Cost"], ["Electronic conductivity"]],
                  x + 2.5, 3, widths[0] - 5, 36,
                  [OFFICE["lyellow"], OFFICE["grey"], OFFICE["lgreen"], OFFICE["pblue"], "#FFE699",
                   OFFICE["vlblue"], "#C5E0B4"], fs=6.5)
    # col 2: data -> features -> model
    x = xs[1] + widths[1] / 2 - 3
    for (kind, yy, lab) in [("database", 55, "Data"), ("gears", 35, "Features"), ("cube", 14, "Model")]:
        icon(ax, kind, x, yy, 13, OFFICE["navy"], OFFICE["magenta"] if kind == "gears" else "#00ACDC")
        ax.text(x + 11, yy, lab, rotation=270, ha="center", va="center", fontsize=7.5, fontweight="bold", **SER)
    down_arrows(ax, x, 47, 43); down_arrows(ax, x, 27, 23)
    # col 3: regression / classification
    x = xs[2] + widths[2] / 2
    ax.text(x, 63, "Regression", ha="center", fontsize=7.5, fontweight="bold", **SER)
    icon(ax, "tree", x, 51, 20, OFFICE["violet"], OFFICE["violet"])
    ax.text(x, 33, "Classification", ha="center", fontsize=7.5, fontweight="bold", **SER)
    icon(ax, "classify", x, 18, 22, OFFICE["orange"], OFFICE["cyan"])
    # col 4: deployment targets
    x = xs[3] + widths[3] / 2
    for (kind, yy, lab, c, a) in [("network", 55, "SSE screening", OFFICE["navy"], OFFICE["navy"]),
                                  ("molecule", 32, "Interface design", OFFICE["navy"], OFFICE["cyan"]),
                                  ("flask", 10, "Closed-loop synthesis", OFFICE["blue"], OFFICE["lblue"])]:
        icon(ax, kind, x, yy, 12, c, a)
        ax.text(x, yy + 7.5, lab, ha="center", va="bottom", fontsize=7.5, fontweight="bold", **SER)
    save(fig, OUT + "S1_dotted_columns", text_width_mm=165)


# ---------------- S2: teardrop stage pipeline --------------------------------------------
def s2():
    fig, ax = fig_mm(74)
    stages = [("Material discovery", "atom", OFFICE["lyellow"], OFFICE["yellow"], "black",
               [("lattice", "Solid electrolytes"), ("splash", "Coatings")]),
              ("Atomistic simulation", "particles", OFFICE["lgreen"], OFFICE["mgreen"], "black",
               [("molecule", "MLIP-MD"), ("pulse", "Li$^+$ diffusion")]),
              ("Property prediction", "chart", OFFICE["lorange"], OFFICE["orange"], "white",
               [("battery", "Conductivity"), ("pulse", "Interface stability")]),
              ("Autonomous experiment", "flask", OFFICE["lblue"], OFFICE["blue"], "white",
               [("monitor", "Closed-loop design"), ("flask", "Robotic synthesis")])]
    xs = np.linspace(21.5, 149.5, 4); ry = 58; R = 9.5
    for i, (name, ic, light, dark, tc, inner) in enumerate(stages):
        x = xs[i]
        teardrop(ax, x, 22, 19.5, 26, light, None, z=1)
        ring(ax, x, ry, R)
        col = {"atom": "#2A2A2A", "particles": OFFICE["blue"], "chart": OFFICE["magenta"], "flask": OFFICE["blue"]}[ic]
        icon(ax, ic, x, ry, 12, col, {"atom": "#2A2A2A", "particles": "#3FB1A4", "chart": OFFICE["orange"],
                                      "flask": OFFICE["yellow"]}[ic])
        pill(ax, x, 44.5, name, dark, w=30, h=4.6, fs=7, tc=tc)
        for j, (k, lab) in enumerate(inner):
            yy = 28 - j * 13
            icon(ax, k, x - 9, yy, 8, {"pulse": "#2A2A2A"}.get(k, OFFICE["navy"]),
                 {"splash": OFFICE["orange"]}.get(k, OFFICE["cyan"]))
            if k == "splash":
                icon(ax, k, x - 9, yy, 8, OFFICE["orange"], OFFICE["orange"])
            ax.text(x - 3.5, yy, lab, ha="left", va="center", fontsize=6.5, **SER)
        if i < 3:
            chevron(ax, x + R + 6, ry, 11, 7.5)
    save(fig, OUT + "S2_teardrop_pipeline", text_width_mm=165)


# ---------------- S3: timeline with category icons ---------------------------------------
def s3():
    fig, ax = fig_mm(40)
    tint_panel(ax, 0, 0, 171, 40, "#FFFFFF", CSR["tint_green"], label=None)
    cats = {"Materials": ("splash", CSR["orange"]), "Data & tools": ("database", CSR["blue"]),
            "AI models": ("gears", CSR["green"])}
    ev = [("2011", "Materials", "Li$_{10}$GeP$_2$S$_{12}$\nsuperionic"),
          ("2013", "Data & tools", "Materials\nProject"),
          ("2016", "Materials", "Li$_{9.54}$Si$_{1.74}$P$_{1.44}$-\nS$_{11.7}$Cl$_{0.3}$"),
          ("2018", "AI models", "Deep potential\nMD"),
          ("2022", "AI models", "M3GNet\nuniversal IP"),
          ("2023", "Data & tools", "GNoME,\nA-Lab"),
          ("2025", "AI models", "MatterGen\ngenerative")]
    timeline(ax, 4, 167, 7, ev, cats, fs=6.5, icon_s=9)
    ax.text(1.5, 38.8, "(a)", ha="left", va="top", fontsize=8)
    save(fig, OUT + "S3_timeline_icons", text_width_mm=165)


# ---------------- S4 + S5: tinted multi-panel with CSR-style value bars -------------------
def s4():
    fig, ax = fig_mm(64)
    tint_panel(ax, 0, 0, 92, 64, CSR["tint_green"], "#FFFFFF", label="a")
    tint_panel(ax, 93, 0, 78, 64, CSR["tint_blue"], "#FFFFFF", label="b")
    # (a) mechanism sketch: vacancy hopping vs concerted migration
    for row, (yy, title, concerted) in enumerate([(44, "Vacancy hopping", False), (16, "Concerted migration", True)]):
        ax.text(46, yy + 12.5, title, ha="center", fontsize=7.5)
        for i in range(8):
            px = 12 + i * 9.5
            ax.add_patch(Circle((px, yy), 2.6, fc="#EEF0F2", ec="#9AA3AD", lw=0.5, zorder=2))   # sites
        occ = [0, 1, 2, 4, 5, 6] if not concerted else [0, 1, 2, 3, 5, 6]
        for i in occ:
            ax.add_patch(Circle((12 + i * 9.5, yy), 1.9, fc=CSR["green"], ec="none", zorder=3))
        movers = [(4, 3)] if not concerted else [(3, 4), (2, 3), (1, 2)]
        for a_, b_ in movers:
            flow_arrow(ax, 12 + a_ * 9.5, yy + 2.8, 12 + b_ * 9.5, yy + 2.8, color=CSR["dark"], rad=-0.6, lw=0.8)
    ax.add_patch(Circle((8, 3.5), 1.6, fc=CSR["green"], ec="none")); ax.text(10.5, 3.5, "Li$^+$", va="center", fontsize=6)
    ax.add_patch(Circle((22, 3.5), 1.9, fc="#EEF0F2", ec="#9AA3AD", lw=0.5)); ax.text(24.5, 3.5, "vacancy", va="center", fontsize=6)
    # (b) bar chart, CSR style
    bx = fig.add_axes([(93 + 15) / 171, 10 / 64, 58 / 171, 42 / 64]); bx.patch.set_alpha(0)
    vals = [1.108, 1.172, 0.798]; labs = ["Stoich.", "Stoich.+geom.", "LLM"]
    b = bx.bar(range(3), vals, 0.55, color=CSR["blue"])
    for r, v in zip(b, vals):
        bx.text(r.get_x() + r.get_width() / 2, v + 0.02, f"{v:.3f}", ha="center", va="bottom", fontsize=6,
                color=CSR["dark"])
    bx.set_ylim(0, 1.6); bx.set_xticks(range(3)); bx.set_xticklabels(labs)
    bx.set_ylabel("TEST MAE (log$_{10}$ S cm$^{-1}$)", color=CSR["blue"])
    for t in bx.get_yticklabels() + bx.get_xticklabels():
        t.set_color(CSR["blue"])
    bx.text(-0.25, 1.6, "Conductivity regression", color=CSR["blue"], fontsize=7, va="top")
    bx.text(-0.25, 1.49, "(same test split, three feature sets)", color=CSR["blue"], fontsize=6, va="top")
    save(fig, OUT + "S4_tinted_panels_bars", text_width_mm=165)


# ---------------- S6: evidence collage layout template -----------------------------------
def s6():
    fig, ax = fig_mm(96)
    def ph(x, y, w, h, txt):
        ax.add_patch(Rectangle((x, y), w, h, fc="#FFFFFF", ec="#C9CED6", lw=0.5, hatch="////", zorder=2))
        ax.text(x + w / 2, y + h / 2, txt, ha="center", va="center", fontsize=6, color="#5B6570", zorder=3,
                bbox=dict(fc="white", ec="none", pad=0.6))
    tint_panel(ax, 0, 70, 171, 26, CSR["tint_lilac"], label="a")
    for i in range(5):
        ph(8 + i * 32.5, 73, 28, 17, f"structure {i+1}\n(original drawing)")
    tint_panel(ax, 0, 38, 56, 31, CSR["tint_grey"], label="b")
    ph(7, 40, 47, 26, "Ref. [n], Fig. k\nmicroscopy")
    tint_panel(ax, 57, 38, 56, 31, CSR["tint_grey"], label="c")
    ph(64, 40, 47, 26, "replotted data\nfrom Ref. [n]")
    tint_panel(ax, 114, 0, 57, 69, CSR["tint_pink"], label="f")
    ph(121, 3, 48, 62, "mechanism schematic\n(redrawn)")
    tint_panel(ax, 0, 0, 56, 37, CSR["tint_blue"], label="d")
    ph(7, 2, 47, 31, "replotted curves\nfrom Ref. [m]")
    tint_panel(ax, 57, 0, 56, 37, CSR["tint_blue"], label="e")
    ph(64, 2, 47, 31, "Ref. [m], Fig. j\n(reproduced, CC BY)")
    save(fig, OUT + "S6_evidence_collage", text_width_mm=165)


if __name__ == "__main__":
    import os; os.makedirs(OUT, exist_ok=True)
    for f in (sys.argv[1:] or ["s0", "s1", "s2", "s3", "s4", "s6"]):
        globals()[f]()
```
