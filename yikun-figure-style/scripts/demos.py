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
