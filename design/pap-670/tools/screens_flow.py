import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wf_lib import *

W, H = 1280, 880
b  = txt(48, 56, "PAP-670 \u2014 where every left-nav item goes", 28, weight="bold")
b += txt(48, 84, "13 static nav rows become 12. Only Inbox and Workspaces leave; Chat gains a first-class entry point. "
                 "New Task, Search and Dashboard all keep their rows.", 14, fill=MUT)

BX, BY, BW = 48, 112, 256
b += txt(BX, BY - 8, "BEFORE", 12, fill=MUT, weight="600", mono=True)
b += rect(BX, BY, BW, 688, rx=8)
b += nav_header(BY - 8, BX, BW)
removed = {"Inbox", "Workspaces"}
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
    if kind == "label":
        b += nav_label(yy, label, AX, AW); continue
    b += nav_row(yy, label, AX, AW, **dict(kw))
    if label == "Chat":
        b += region(AX + 8, yy, AW - 16, 32)

DX, DW2 = 400, 512
cards = [
    (200, "Inbox  \u2192  a view inside Tasks",
          "/inbox/{mine,recent,unread,blocked,all} redirect to /issues?view=\u2026"),
    (376, "Workspaces  \u2192  removed outright",
          "Out of the nav AND the organisation menu. No new home, by board decision."),
    (552, "Chat  \u2190  NEW first item under Work",
          "New /chats landing: agent picker + recent conversations."),
]
for y, title, sub in cards:
    b += rect(DX, y, DW2, 88, rx=8)
    b += txt(DX + 20, y + 34, title, 14, weight="600")
    b += txt(DX + 20, y + 58, sub, 12, fill=MUT)

b += arrow(BX + BW + 8, BY + 160 - 24 + 16, DX - 8, cards[0][0] + 44)   # Inbox
b += arrow(BX + BW + 8, BY + 408 - 24 + 16, DX - 8, cards[1][0] + 44)   # Workspaces
b += arrow(DX + DW2 + 8, cards[0][0] + 44, AX - 8, AY + 224 - 24 + 16)  # -> Tasks
b += arrow(DX + DW2 + 8, cards[2][0] + 44, AX - 8, AY + 192 - 24 + 16)  # -> Chat
# Workspaces has no destination: a stub that stops, deliberately.
b += line(DX + DW2 + 8, cards[1][0] + 44, DX + DW2 + 32, cards[1][0] + 44, ACC, 1.5, "5 4")
b += txt(DX + DW2 + 40, cards[1][0] + 50, "\u2718", 20, "start", ACC)

# Search and Dashboard stay exactly where they are: one grey path, two sources.
DY_ = 760
JX = BX + BW + 24
for ny in (96, 128):
    b += line(BX + BW + 8, BY + ny - 24 + 16, JX, BY + ny - 24 + 16, MUT, 1.5, "2 4")
b += line(JX, BY + 96 - 24 + 16, JX, DY_, MUT, 1.5, "2 4")
b += line(JX, DY_, AX - 24, DY_, MUT, 1.5, "2 4")
b += line(AX - 24, DY_, AX - 24, AY + 96 - 24 + 16, MUT, 1.5, "2 4")
b += arrow(AX - 24, AY + 96 - 24 + 16, AX - 8, AY + 96 - 24 + 16, stroke=MUT, dash=None)
b += txt(DX + 20, DY_ - 12, "Search and Dashboard stay exactly where they are \u2014 their own rows, in order.", 12, fill=MUT)

b += txt(48, 836, "Unchanged: New Task \u00b7 Search \u00b7 Dashboard \u00b7 Projects + starred \u00b7 Routines \u00b7 Artifacts \u00b7 Agents \u00b7 Skills \u00b7 Connectors \u00b7 Audit \u00b7 Recent tasks \u00b7 account bar.", 12, fill=MUT)
b += txt(48, 860, "/workspaces and /inbox/* still resolve \u2014 nothing is deleted, only removed from the chrome.", 12, fill=MUT)
write("flow.svg", W, H, b, "PAP-670 rev3 nav before/after with destinations")
