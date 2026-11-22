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
