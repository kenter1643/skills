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
