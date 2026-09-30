import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wf_lib import *

W, H = 1280, 880
b  = txt(48, 56, "PAP-670 — where every left-nav item goes", 28, weight="bold")
b += txt(48, 84, "13 static nav rows become 11 — Search, Inbox and Workspaces leave — and Chat gains a first-class entry point. "
                 "Dashboard keeps its own row.", 14, fill=MUT)

BX, BY, BW = 48, 112, 256
b += txt(BX, BY - 8, "BEFORE", 12, fill=MUT, weight="600", mono=True)
b += rect(BX, BY, BW, 688, rx=8)
b += nav_header(BY - 8, BX, BW)
removed = {"Search", "Inbox", "Workspaces"}
for kind, y, label, kw in OLD_NAV:
    yy = BY + y - 24
    if kind == "label":
        b += nav_label(yy, label, BX, BW)
    else:
        b += nav_row(yy, label, BX, BW, **kw)
        if label in removed:
            b += region(BX + 8, yy, BW - 16, 32)

AX, AY, AW = 976, 112, 256
b += txt(AX, AY - 8, "AFTER", 12, fill=MUT, weight="600", mono=True)
b += rect(AX, AY, AW, 688, rx=8)
b += nav_header(AY - 8, AX, AW)
for kind, y, label, kw in NEW_NAV:
    yy = AY + y - 24
    kw = dict(kw)
    if kind == "label":
        b += nav_label(yy, label, AX, AW); continue
    if kw.pop("trailing", None):
        b += nav_row(yy, label, AX, AW, **kw)
        b += rect(AX + AW - 24 - 28, yy + 2, 28, 28, rx=6)
        b += glyph(AX + AW - 24 - 22, yy + 8)
        b += region(AX + AW - 56, yy, 32, 32)
    else:
        b += nav_row(yy, label, AX, AW, **kw)
        if label == "Chat":
            b += region(AX + 8, yy, AW - 16, 32)

DX, DW2 = 400, 512
cards = [
    (176, "Search  →  icon button in the New Task row + ⌘K palette",
          "/search page stays; the command palette and the Tasks toolbar search cover the rest."),
    (312, "Inbox  →  a view inside Tasks",
          "/inbox/{mine,recent,unread,blocked,all} redirect to /issues?view=…"),
    (448, "Workspaces  →  organisation menu + project detail",
          "/workspaces unchanged; also reachable at /projects/:id/workspaces."),
    (600, "Chat  ←  NEW first item under Work",
          "New /chats landing: agent picker + recent conversations."),
]
for y, title, sub in cards:
    b += rect(DX, y, DW2, 88, rx=8)
    b += txt(DX + 20, y + 34, title, 14, weight="600")
    b += txt(DX + 20, y + 58, sub, 12, fill=MUT)

for i, ny in enumerate([96, 160, 408]):                      # Search, Inbox, Workspaces
    b += arrow(BX + BW + 8, BY + ny - 24 + 16, DX - 8, cards[i][0] + 44)
b += arrow(DX + DW2 + 8, cards[0][0] + 44, AX - 8, AY + 64 - 24 + 16)    # -> New Task row icon
b += arrow(DX + DW2 + 8, cards[1][0] + 44, AX - 8, AY + 192 - 24 + 16)   # -> Tasks
b += arrow(DX + DW2 + 8, cards[2][0] + 44, AX - 8, AY + 8)               # -> org menu header
b += arrow(DX + DW2 + 8, cards[3][0] + 44, AX - 8, AY + 160 - 24 + 16)   # -> Chat

# Dashboard stays put: routed below the destination cards so it never reads as a move.
DY_ = 744
b += line(BX + BW + 8, BY + 128 - 24 + 16, BX + BW + 24, BY + 128 - 24 + 16, MUT, 1.5, "2 4")
b += line(BX + BW + 24, BY + 128 - 24 + 16, BX + BW + 24, DY_, MUT, 1.5, "2 4")
b += line(BX + BW + 24, DY_, AX - 24, DY_, MUT, 1.5, "2 4")
b += line(AX - 24, DY_, AX - 24, AY + 96 - 24 + 16, MUT, 1.5, "2 4")
b += arrow(AX - 24, AY + 96 - 24 + 16, AX - 8, AY + 96 - 24 + 16, stroke=MUT, dash=None)
b += txt(DX + 20, DY_ - 12, "Dashboard stays where it is \u2014 its own row, directly below New Task.", 12, fill=MUT)

b += txt(48, 836, "Unchanged: New Task \u00b7 Dashboard \u00b7 Projects + starred \u00b7 Routines \u00b7 Artifacts \u00b7 Agents \u00b7 Skills \u00b7 Connectors \u00b7 Audit \u00b7 Recent tasks \u00b7 account bar.", 12, fill=MUT)
b += txt(48, 860, "Every current URL keeps working \u2014 nothing is deleted, only demoted out of the nav.", 12, fill=MUT)
write("flow.svg", W, H, b, "PAP-670 rev2 nav before/after with destinations")
