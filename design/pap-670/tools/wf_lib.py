"""PAP-670 wireframe primitives.

House style (from the `wireframe` skill): monochrome, 8px grid,
type scale 12/14/20/28 only, #d33 dashed for the annotation layer only.
"""
import os, html

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, "..", "wireframes"))
os.makedirs(OUT, exist_ok=True)

INK, PH, MUT, ACC = "#000", "#e6e6e6", "#666", "#d33"
FONT = "-apple-system, system-ui, sans-serif"

def e(s): return html.escape(str(s))

def svg(w, h, body, note):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"\n'
            f'     font-family="{FONT}" fill="#fff" stroke="{INK}" stroke-width="1.5">\n'
            f'  <!-- {note} -->\n'
            f'  <rect x="0" y="0" width="{w}" height="{h}" />\n{body}</svg>\n')

def rect(x, y, w, h, rx=0, fill="#fff", stroke=INK, sw=1.5, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    s = f' stroke="{stroke}"' if stroke else ' stroke="none"'
    return f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}"{s} stroke-width="{sw}"{d} />\n'

def txt(x, y, s, size=14, anchor="start", fill=INK, weight=None, mono=False):
    w = f' font-weight="{weight}"' if weight else ""
    f = ' font-family="ui-monospace, SFMono-Regular, monospace"' if mono else ""
    return (f'  <text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" '
            f'stroke="none" fill="{fill}"{w}{f}>{e(s)}</text>\n')

def line(x1, y1, x2, y2, stroke=INK, sw=1.5, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'  <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-width="{sw}"{d} />\n'

def circ(cx, cy, r, fill="#fff", stroke=INK, sw=1.5):
    return f'  <circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" />\n'

def glyph(x, y, s=16):
    return rect(x, y, s, s, rx=3)

def avatar(cx, cy, r=10):
    return circ(cx, cy, r, fill=PH)

def callout(cx, cy, n):
    return circ(cx, cy, 11, fill="#fff", stroke=ACC) + txt(cx, cy + 4, n, 12, "middle", ACC, "bold")

def region(x, y, w, h):
    return rect(x, y, w, h, rx=4, fill="none", stroke=ACC, dash="5 4")

def arrow(x1, y1, x2, y2, stroke=ACC, dash="5 4"):
    import math
    a = math.atan2(y2 - y1, x2 - x1)
    l, sp = 9, 0.5
    p1 = (x2 - l * math.cos(a - sp), y2 - l * math.sin(a - sp))
    p2 = (x2 - l * math.cos(a + sp), y2 - l * math.sin(a + sp))
    return (line(x1, y1, x2, y2, stroke, 1.5, dash) +
            f'  <path d="M{x2:.1f},{y2:.1f} L{p1[0]:.1f},{p1[1]:.1f} L{p2[0]:.1f},{p2[1]:.1f} Z" '
            f'fill="{stroke}" stroke="none" />\n')

def chev(x, y, d="down"):
    return f'  <path d="M{x},{y} l4,4 l4,-4" fill="none" stroke="{MUT}" stroke-width="1.5" />\n'

# ---------------------------------------------------------------- nav builder
NAV_W = 240
PITCH = 32

def nav_row(y, label, x0=0, w=NAV_W, indent=0, active=False, badge=None,
            star=False, trailing=None, muted=False):
    s = ""
    if active:
        s += rect(x0 + 8, y, w - 16, PITCH, rx=6, fill=PH)
    ix = x0 + 24 + indent
    if star:
        s += circ(ix + 8, y + 16, 6)
    else:
        s += glyph(ix, y + 8)
    s += txt(ix + 28, y + 21, label, 14, fill=MUT if muted else INK,
             weight="600" if active else None)
    if badge is not None:
        bx = x0 + w - 24 - 26
        s += rect(bx, y + 9, 26, 14, rx=7, fill=PH)
        s += txt(bx + 13, y + 20, badge, 12, "middle", INK)
    if trailing:
        s += glyph(x0 + w - 24 - 16, y + 8)
    return s

def nav_label(y, label, x0=0, w=NAV_W):
    return txt(x0 + 24, y + 16, label, 12, fill=MUT, weight="600", mono=True)

def nav_header(y, x0=0, w=NAV_W, name="Paperclip"):
    s  = rect(x0 + 24, y + 18, 20, 20, rx=4, fill=PH)
    s += txt(x0 + 52, y + 33, name, 14, weight="bold")
    s += chev(x0 + w - 40, y + 25)
    return s

def account_bar(y, x0=0, w=NAV_W, h=56):
    s  = rect(x0, y, w, h, fill=PH)
    s += avatar(x0 + 32, y + h // 2)
    s += txt(x0 + 52, y + h // 2 + 5, "Scott", 14)
    return s

# ============================================================= nav definitions
# Revision 3 (board, 2026-09-30): Search returns to its own row, so the top group
# reads New Task / Search / Dashboard. Workspaces is removed outright — from the
# nav AND the organisation menu — with no new home. Only Inbox and Workspaces leave.
NEW_NAV = [
    ("row",   64, "New Task", {}),
    ("row",   96, "Search", {}),
    ("row",  128, "Dashboard", dict(badge="2")),
    ("label", 168, "WORK", {}),
    ("row",  192, "Chat", {}),
    ("row",  224, "Tasks", dict(active=True, badge="3")),
    ("row",  256, "Projects", {}),
    ("row",  288, "Design System", dict(indent=16, star=True, muted=True)),
    ("row",  320, "Marketing site", dict(indent=16, star=True, muted=True)),
    ("row",  352, "Routines", {}),
    ("row",  384, "Artifacts", {}),
    ("label", 416, "ORG", {}),
    ("row",  448, "Agents", {}),
    ("row",  480, "Skills", {}),
    ("row",  512, "Connectors", {}),
    ("row",  544, "Audit", {}),
    ("label", 576, "RECENT", {}),
    ("row",  608, "PAP-670 clean up left nav", dict(muted=True)),
    ("row",  640, "PAP-664 destructive token", dict(muted=True)),
    ("row",  672, "PAP-659 connectors UX", dict(muted=True)),
]

OLD_NAV = [
    ("row",   64, "New Task", {}),
    ("row",   96, "Search", {}),
    ("row",  128, "Dashboard", dict(badge="2")),
    ("row",  160, "Inbox", dict(badge="3")),
    ("label", 192, "WORK", {}),
    ("row",  216, "Tasks", {}),
    ("row",  248, "Projects", {}),
    ("row",  280, "Design System", dict(indent=16, star=True, muted=True)),
    ("row",  312, "Marketing site", dict(indent=16, star=True, muted=True)),
    ("row",  344, "Routines", {}),
    ("row",  376, "Artifacts", {}),
    ("row",  408, "Workspaces", {}),
    ("label", 440, "ORG", {}),
    ("row",  464, "Agents", {}),
    ("row",  496, "Skills", {}),
    ("row",  528, "Connectors", {}),
    ("row",  560, "Audit", {}),
    ("label", 592, "RECENT", {}),
    ("row",  616, "PAP-670 clean up left nav", dict(muted=True)),
    ("row",  648, "PAP-664 destructive token", dict(muted=True)),
    ("row",  680, "PAP-659 connectors UX", dict(muted=True)),
]

def draw_nav(spec, x0=0, w=NAV_W, h=800, account=True, active_label=None):
    s  = rect(x0, 0, w, h, fill="#fff")
    s += nav_header(0, x0, w)
    for kind, y, label, kw in spec:
        if kind == "label":
            s += nav_label(y, label, x0, w)
            continue
        kw = dict(kw)
        if active_label is not None:
            kw["active"] = (label == active_label)
        if kw.pop("trailing", None):
            s += nav_row(y, label, x0, w, **kw)
            s += rect(x0 + w - 24 - 28, y + 2, 28, 28, rx=6)
            s += glyph(x0 + w - 24 - 22, y + 8, 16)
        else:
            s += nav_row(y, label, x0, w, **kw)
    if account:
        s += account_bar(h - 56, x0, w)
    s += line(x0 + w, 0, x0 + w, h)
    return s

CX, CR = 288, 1256   # content left / right edge on the 1280 canvas

def toolbar(y, view="Mine", search_ph="Search tasks…", views_w=168):
    s  = rect(CX, y, views_w, 32, rx=6)
    s += glyph(CX + 12, y + 8)
    s += txt(CX + 40, y + 21, f"Views: {view}", 14, weight="600")
    s += chev(CX + views_w - 20, y + 14)
    nx = CX + views_w + 16
    s += rect(nx, y, 88, 32, rx=6)
    s += txt(nx + 44, y + 21, "+ New", 14, "middle")
    sx = nx + 112
    s += rect(sx, y, 280, 32, rx=6)
    s += glyph(sx + 12, y + 8)
    s += txt(sx + 40, y + 21, search_ph, 14, fill=MUT)
    for i, lbl in enumerate(["Filter", "Sort", "Group"]):
        bx = CR - 320 + i * 88
        s += rect(bx, y, 80, 32, rx=6)
        s += txt(bx + 40, y + 21, lbl, 12, "middle", MUT)
    s += rect(CR - 48, y, 48, 32, rx=6)
    s += glyph(CR - 36, y + 8)
    return s

def group_label(y, label):
    return txt(CX, y + 16, label, 12, fill=MUT, weight="600", mono=True)

def task_row(y, title, meta="in progress", unread=False, kind="task", w=None):
    w = w or (CR - CX)
    s  = line(CX, y, CX + w, y, MUT, 1)
    if unread:
        s += circ(CX + 8, y + 24, 4, fill=INK)
    s += circ(CX + 32, y + 24, 7)
    s += txt(CX + 56, y + 21, title, 14)
    s += txt(CX + 56, y + 38, meta, 12, fill=MUT)
    if kind != "task":
        tag = {"approval": "APPROVAL", "failed_run": "FAILED RUN", "join_request": "JOIN REQUEST"}[kind]
        tw = 8 * len(tag) + 16
        s += rect(CX + w - 320, y + 14, tw, 20, rx=10, fill=PH)
        s += txt(CX + w - 320 + tw / 2, y + 28, tag, 12, "middle", INK)
    s += avatar(CX + w - 152, y + 24, 9)
    s += txt(CX + w - 8, y + 28, "2h", 12, "end", MUT)
    return s

def write(name, w, h, body, note):
    path = os.path.join(OUT, name)
    open(path, "w").write(svg(w, h, body, note))
    print("wrote", os.path.basename(path))
