import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wf_lib import *

# Nav-gutter callout anchors, keyed to NEW_NAV row centres (revision 2).
NAV_CALLOUTS = [(28, "1"), (80, "2"), (112, "3"), (176, "4"), (208, "5"),
                (240, "6"), (432, "7"), (592, "8"), (772, "9")]

# =========================================================== 1. left-nav
b  = draw_nav(NEW_NAV, active_label="Tasks")
b += txt(CX, 48, "Tasks", 20, weight="bold")
b += toolbar(80)
b += group_label(136, "TODAY")
for i, t in enumerate(["PAP-670 clean up left nav, make space for chat",
                       "PAP-664 destructive button token",
                       "PAP-659 simplify connectors UX",
                       "PAP-649 local Sentry setup"]):
    b += task_row(160 + i * 48, t, "assigned to me · in progress", unread=(i < 2))
b += group_label(376, "EARLIER")
for i, t in enumerate(["PAP-640 in-progress icon animation",
                       "PAP-628 Bucket A papercuts",
                       "PAP-612 relative timestamps",
                       "PAP-601 verify primary instance",
                       "PAP-584 first-task redesign"]):
    b += task_row(400 + i * 48, t, "assigned to me · in review")
b += line(CX, 640, CR, 640, MUT, 1)
b += region(0, 8, 240, 48)
b += region(8, 96, 224, 32)      # Dashboard stays put — board decision
b += region(8, 160, 224, 32)     # Chat — the new row
for cy, n in NAV_CALLOUTS:
    b += callout(260, cy, n)
b += callout(CX + 176, 56, "10")
write("left-nav.svg", 1280, 800, b, "PAP-670 rev2 new left nav in context (desktop 1280x800)")

# =========================================================== 2. tasks-mine
b  = draw_nav(NEW_NAV, active_label="Tasks")
b += txt(CX, 48, "Tasks", 20, weight="bold")
b += toolbar(80)
b += rect(CX, 128, 168, 24, rx=12, fill=PH)
b += txt(CX + 84, 145, "Mine · 3 unread", 12, "middle")
b += rect(CX + 184, 128, 136, 24, rx=12)
b += txt(CX + 252, 145, "Mark all read", 12, "middle", MUT)
b += rect(CX + 336, 128, 104, 24, rx=12)
b += txt(CX + 388, 145, "Archive", 12, "middle", MUT)
b += group_label(176, "TODAY")
for i, (t, m, u) in enumerate([
        ("PAP-670 clean up left nav, make space for chat", "assigned to me · in progress", True),
        ("PAP-664 destructive button token", "assigned to me · blocked", True),
        ("PAP-659 simplify connectors UX", "assigned to me · in review", True),
        ("PAP-649 local Sentry setup", "assigned to me · blocked", False)]):
    b += task_row(200 + i * 48, t, m, unread=u)
b += group_label(416, "EARLIER")
for i, t in enumerate(["PAP-640 in-progress icon animation",
                       "PAP-628 Bucket A papercuts",
                       "PAP-612 relative timestamps",
                       "PAP-601 verify primary instance"]):
    b += task_row(440 + i * 48, t, "assigned to me · done")
b += line(CX, 632, CR, 632, MUT, 1)
b += rect(CR - 256, 672, 256, 64, rx=6, fill="none", stroke=MUT)
b += txt(CR - 240, 696, "row hover reveals archive /", 12, fill=MUT)
b += txt(CR - 240, 716, "mark unread (inbox behaviour)", 12, fill=MUT)
b += callout(CX + 176, 56, "1")
b += callout(CX + 84, 112, "2")
b += callout(CX + 320, 112, "3")
b += callout(268, 224, "4")
b += callout(268, 424, "5")
b += callout(CR - 128, 660, "6")
write("tasks-mine.svg", 1280, 800, b, "PAP-670 rev2 combined Tasks, default view = last used (desktop)")

# =========================================================== 3. tasks-views
b  = draw_nav(NEW_NAV, active_label="Tasks")
b += txt(CX, 48, "Tasks", 20, weight="bold")
b += toolbar(80)
for i in range(6):
    b += task_row(152 + i * 48, "PAP-6xx task title", "assigned to me · in progress")
MX, MY, MW = CX, 120, 328
items = [
    ("h", "MY WORK  (was Inbox)"),
    ("i", "Mine", "assigned to me / needs me", "3", True),
    ("i", "Unread", "touched, not yet read", "7", False),
    ("i", "Blocked", "waiting on someone", "2", False),
    ("i", "Recent", "tasks I touched recently", None, False),
    ("i", "Everything", "+ approvals, failed runs, join requests", "4", False),
    ("h", "ORGANISATION  (was Tasks)"),
    ("i", "All tasks", "every task in the org", None, False),
    ("i", "Active", "todo / in progress / in review / blocked", None, False),
    ("i", "Backlog", "not started", None, False),
    ("i", "Done", "completed + cancelled", None, False),
    ("h", "SAVED VIEWS"),
    ("i", "Shipping this week", "saved filter", None, False),
    ("a", "Save current filters as a view…"),
]
h = 16 + sum(24 if it[0] == "h" else 40 for it in items) + 16
b += rect(MX, MY, MW, h, rx=8)
y = MY + 16
for it in items:
    if it[0] == "h":
        b += txt(MX + 16, y + 16, it[1], 12, fill=MUT, weight="600", mono=True); y += 24
    elif it[0] == "a":
        b += txt(MX + 16, y + 24, it[1], 14, fill=MUT); y += 40
    else:
        _, label, sub, badge, active = it
        if active:
            b += rect(MX + 8, y, MW - 16, 40, rx=6, fill=PH)
        b += glyph(MX + 20, y + 12)
        b += txt(MX + 48, y + 20, label, 14, weight="600" if active else None)
        b += txt(MX + 48, y + 34, sub, 12, fill=MUT)
        if badge:
            b += rect(MX + MW - 52, y + 12, 32, 16, rx=8, fill=PH)
            b += txt(MX + MW - 36, y + 24, badge, 12, "middle")
        y += 40
b += region(MX, MY + 16, MW, 224)
b += txt(MX + MW + 24, MY + 88, "every former /inbox tab", 12, fill=ACC)
b += txt(MX + MW + 24, MY + 108, "lands here as a view", 12, fill=ACC)
b += txt(MX + MW + 24, MY + 320, "every former /issues/* preset", 12, fill=ACC)
b += txt(MX + MW + 24, MY + 340, "lands here too", 12, fill=ACC)
b += callout(CX + 176, 56, "1")
b += callout(MX + MW + 4, MY + 40, "2")
b += callout(MX + MW + 4, MY + 272, "3")
b += callout(MX + MW + 4, h + MY - 32, "4")
write("tasks-views.svg", 1280, 800, b, "PAP-670 rev2 Tasks views menu (desktop)")

# =========================================================== 4. tasks-everything
b  = draw_nav(NEW_NAV, active_label="Tasks")
b += txt(CX, 48, "Tasks", 20, weight="bold")
b += toolbar(80, view="Everything")
cx = CX
for label, on in [("Everything", True), ("Tasks", False), ("Approvals", False),
                  ("Failed runs", False), ("Join requests", False), ("Alerts", False)]:
    w = 8 * len(label) + 32
    b += rect(cx, 128, w, 24, rx=12, fill=PH if on else "#fff")
    b += txt(cx + w / 2, 145, label, 12, "middle")
    cx += w + 8
b += group_label(176, "TODAY")
for i, (t, m, u, k) in enumerate([
        ("PAP-670 clean up left nav, make space for chat", "assigned to me · in progress", True, "task"),
        ("Approve $40 Ramp charge — Sentry seat", "requested by CFO agent", True, "approval"),
        ("Heartbeat run failed — CEO · PAP-659", "adapter stopped after 2 retries", True, "failed_run"),
        ("Dana wants to join Paperclip", "join request · invited by Scott", False, "join_request"),
        ("PAP-664 destructive button token", "assigned to me · blocked", False, "task")]):
    b += task_row(200 + i * 48, t, m, unread=u, kind=k)
b += group_label(456, "EARLIER")
for i, t in enumerate(["PAP-659 simplify connectors UX", "PAP-649 local Sentry setup",
                       "PAP-640 in-progress icon animation"]):
    b += task_row(480 + i * 48, t, "assigned to me · in review")
b += line(CX, 624, CR, 624, MUT, 1)
b += region(CX, 200, CR - CX, 192)
b += callout(CX + 176, 56, "1")
b += callout(CX + 64, 112, "2")
b += callout(268, 272, "3")
b += callout(CR - 288, 188, "4")
write("tasks-everything.svg", 1280, 800, b, "PAP-670 rev2 Everything view, mixed inbox rows (desktop)")

# =========================================================== 5. chat
b  = draw_nav(NEW_NAV, active_label="Chat")
b += txt(CX, 48, "Chat", 20, weight="bold")
b += rect(CX, 80, 328, 32, rx=6)
b += glyph(CX + 12, 88)
b += txt(CX + 40, 101, "Find an agent…", 14, fill=MUT)
b += rect(CX + 344, 80, 120, 32, rx=6, fill=PH)
b += txt(CX + 404, 101, "+ New chat", 14, "middle")
b += group_label(144, "STARRED")
for i, (n, s2) in enumerate([("CEO", "product direction, planning"),
                             ("Design QA", "screenshots + visual review")]):
    y = 168 + i * 64
    b += rect(CX, y, 464, 56, rx=8)
    b += avatar(CX + 32, y + 28, 14)
    b += txt(CX + 60, y + 26, n, 14, weight="600")
    b += txt(CX + 60, y + 44, s2, 12, fill=MUT)
    b += circ(CX + 440, y + 28, 6)
b += group_label(312, "RECENT CONVERSATIONS")
for i, (n, s2, t) in enumerate([("CEO", "“draft the PAP-670 plan”", "2h"),
                                ("CodexCoder", "“patch the toolbar slot”", "1d"),
                                ("Design QA", "“recheck the light theme”", "3d")]):
    y = 336 + i * 64
    b += rect(CX, y, 464, 56, rx=8)
    b += avatar(CX + 32, y + 28, 14)
    b += txt(CX + 60, y + 26, n, 14, weight="600")
    b += txt(CX + 60, y + 44, s2, 12, fill=MUT)
    b += txt(CX + 440, y + 32, t, 12, "end", MUT)
PX = CX + 512
b += line(PX - 24, 80, PX - 24, 736, MUT, 1)
b += avatar(PX + 16, 96, 12)
b += txt(PX + 40, 101, "CEO", 14, weight="600")
b += rect(PX, 136, 300, 56, rx=8, fill=PH)
b += txt(PX + 16, 160, "draft the PAP-670 plan and", 12)
b += txt(PX + 16, 178, "wireframe the new left nav", 12)
b += rect(PX + 56, 208, 400, 88, rx=8)
b += txt(PX + 72, 232, "On it. Chat goes first under Work,", 12)
b += txt(PX + 72, 250, "Inbox folds into Tasks as a view,", 12)
b += txt(PX + 72, 268, "and Dashboard keeps its own row.", 12)
b += rect(PX, 664, 456, 72, rx=8)
b += txt(PX + 16, 696, "Message CEO…", 14, fill=MUT)
b += rect(PX + 376, 696, 64, 28, rx=6, fill=PH)
b += txt(PX + 408, 715, "Send", 12, "middle")
b += callout(260, 176, "1")
b += callout(CX + 404, 56, "2")
b += callout(268, 344, "3")
b += callout(PX + 8, 56, "4")
write("chat.svg", 1280, 800, b, "PAP-670 rev2 Chat landing (desktop)")

# =========================================================== 6. org-menu
b  = draw_nav(NEW_NAV, active_label="Tasks")
b += txt(CX, 48, "Tasks", 20, weight="bold")
b += toolbar(80)
for i in range(8):
    b += task_row(152 + i * 48, "PAP-6xx task title", "assigned to me · in progress")
DX, DY, DW = 16, 56, 320
ditems = [("h", "ORGANISATIONS", None, None),
          ("o", "Paperclip", True, None), ("o", "Acme Robotics", False, None),
          ("o", "Side project", False, None),
          ("s", "", None, None),
          ("i", "Workspaces", "isolated execution workspaces", None),
          ("s", "", None, None),
          ("i", "Create organisation", None, None),
          ("i", "Invite people to Paperclip", None, None),
          ("i", "Settings", None, None),
          ("i", "Sign out", None, None)]
dh = 16 + sum({"h": 24, "o": 40, "s": 16}.get(it[0], 48 if it[2] else 36) for it in ditems) + 16
b += rect(DX, DY, DW, dh, rx=10)
y = DY + 16
for it in ditems:
    if it[0] == "h":
        b += txt(DX + 16, y + 16, it[1], 12, fill=MUT, weight="600", mono=True); y += 24
    elif it[0] == "s":
        b += line(DX, y + 8, DX + DW, y + 8, MUT, 1); y += 16
    elif it[0] == "o":
        if it[2]:
            b += rect(DX + 8, y, DW - 16, 40, rx=6, fill=PH)
        b += rect(DX + 20, y + 10, 20, 20, rx=4, fill=PH)
        b += txt(DX + 52, y + 25, it[1], 14, weight="600" if it[2] else None)
        if it[2]:
            b += txt(DX + DW - 28, y + 25, "✓", 14)
        y += 40
    else:
        b += glyph(DX + 20, y + 10)
        b += txt(DX + 52, (y + 22) if it[2] else (y + 24), it[1], 14)
        if it[2]:
            b += txt(DX + 52, y + 38, it[2], 12, fill=MUT)
        y += 48 if it[2] else 36
b += region(DX + 8, DY + 168, DW - 16, 48)
b += callout(DX + DW + 4, DY + 32, "1")
b += callout(DX + DW + 4, DY + 192, "2")
b += callout(DX + DW + 4, DY + dh - 56, "3")
write("org-menu.svg", 1280, 800, b, "PAP-670 rev2 organisation menu takes Workspaces only (desktop)")
