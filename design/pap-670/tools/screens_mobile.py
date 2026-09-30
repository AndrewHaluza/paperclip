import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wf_lib import *

MW_, MH_ = 375, 812
M0, M1 = 16, 359

def appbar(title, y=0, menu=True):
    s  = rect(0, y, MW_, 56, fill="#fff")
    if menu: s += glyph(16, y + 20)
    s += txt(56 if menu else 16, y + 36, title, 20, weight="bold")
    s += avatar(343, y + 28, 12)
    s += line(0, y + 56, MW_, y + 56, MUT, 1)
    return s

def tabbar(active="Tasks"):
    """Rev 3 order, set by the board: Home · Chat · + · Tasks · Agents.
    Home stays; Inbox is gone and Chat takes the second slot."""
    s  = rect(0, 744, MW_, 68, fill="#fff")
    s += line(0, 744, MW_, 744, INK, 1.5)
    for i, t in enumerate(["Home", "Chat", "New", "Tasks", "Agents"]):
        cx = 37 + i * 75
        if t == "New":
            s += circ(cx, 776, 16, fill=PH); s += txt(cx, 782, "+", 20, "middle"); continue
        if t == active:
            s += rect(cx - 28, 756, 56, 24, rx=12, fill=PH)
        s += glyph(cx - 8, 760)
        s += txt(cx, 798, t, 12, "middle", INK if t == active else MUT)
    return s

def m_task_row(y, title, meta, unread=False, kind="task"):
    s  = line(M0, y, M1, y, MUT, 1)
    if unread: s += circ(M0 + 6, y + 24, 4, fill=INK)
    s += circ(M0 + 28, y + 24, 7)
    s += txt(M0 + 48, y + 21, title[:30], 14)
    s += txt(M0 + 48, y + 40, meta, 12, fill=MUT)
    if kind != "task":
        tag = {"approval": "APPROVAL", "failed_run": "FAILED RUN", "join_request": "JOIN REQUEST"}[kind]
        tw = 7 * len(tag) + 16
        s += rect(M0 + 48, y + 48, tw, 18, rx=9, fill=PH)
        s += txt(M0 + 48 + tw / 2, y + 61, tag, 12, "middle")
    s += avatar(M1 - 16, y + 24, 9)
    s += txt(M1 - 16, y + 52, "2h", 12, "middle", MUT)
    return s

# ------------------------------------------------------- 1. left-nav-mobile
DW_ = 288
b  = rect(0, 0, MW_, MH_, fill=PH)
b += draw_nav(NEW_NAV, x0=0, w=DW_, h=MH_, account=True)
b += region(8, 192, DW_ - 16, 32)
b += region(DW_ + 8, 744, MW_ - DW_ - 16, 60)
for cy, n in [(28, "1"), (112, "2"), (144, "3"), (208, "4"), (240, "5"),
              (272, "6"), (464, "7"), (624, "8"), (760, "9")]:
    b += callout(DW_ + 40, cy, n)
b += txt(DW_ + 8, 700, "tab bar", 12, "start", ACC)
b += txt(DW_ + 8, 716, "behind", 12, "start", ACC)
write("left-nav-mobile.svg", MW_, MH_, b, "PAP-670 rev3 new left nav as the mobile drawer")

# ------------------------------------------------------- 2. tasks-mine-mobile
b  = appbar("Tasks")
b += rect(M0, 72, 168, 32, rx=16, fill=PH)
b += glyph(M0 + 12, 80)
b += txt(M0 + 40, 93, "Views: Mine", 14, weight="600")
b += chev(M0 + 148, 86)
b += rect(M0 + 184, 72, 72, 32, rx=16)
b += txt(M0 + 220, 93, "Filter", 12, "middle", MUT)
b += rect(M0 + 264, 72, 64, 32, rx=16)
b += glyph(M0 + 288, 80)
b += txt(M0, 136, "TODAY", 12, fill=MUT, weight="600", mono=True)
for i, (t, m, u) in enumerate([("PAP-670 clean up left nav", "assigned to me · in progress", True),
                               ("PAP-664 destructive token", "assigned to me · blocked", True),
                               ("PAP-659 connectors UX", "assigned to me · in review", True),
                               ("PAP-649 local Sentry setup", "assigned to me · blocked", False)]):
    b += m_task_row(152 + i * 72, t, m, unread=u)
b += txt(M0, 480, "EARLIER", 12, fill=MUT, weight="600", mono=True)
for i, t in enumerate(["PAP-640 icon animation", "PAP-628 Bucket A papercuts", "PAP-612 timestamps"]):
    b += m_task_row(496 + i * 72, t, "assigned to me · done")
b += line(M0, 712, M1, 712, MUT, 1)
b += tabbar("Tasks")
b += region(M0, 152, M1 - M0, 72)
b += callout(M0 + 84, 56, "1")
b += callout(M1 - 8, 136, "2")
b += callout(224, 728, "3")
write("tasks-mine-mobile.svg", MW_, MH_, b, "PAP-670 rev3 combined Tasks on mobile")

# ------------------------------------------------------- 3. tasks-views-mobile
b  = appbar("Tasks")
b += rect(M0, 72, 168, 32, rx=16, fill=PH)
b += txt(M0 + 40, 93, "Views: Mine", 14, weight="600")
for i in range(3):
    b += m_task_row(152 + i * 72, "PAP-6xx task title", "assigned to me")
b += rect(0, 288, MW_, MH_ - 288, rx=16, fill="#fff")
b += rect(163, 304, 48, 4, rx=2, fill=PH)
b += txt(M0, 340, "VIEWS", 12, fill=MUT, weight="600", mono=True)
sheet = [("h", "MY WORK  (was Inbox)"),
         ("i", "Mine", "3", True), ("i", "Unread", "7", False), ("i", "Blocked", "2", False),
         ("i", "Recent", None, False), ("i", "Everything", "4", False),
         ("h", "ORGANISATION  (was Tasks)"),
         ("i", "All tasks", None, False), ("i", "Active", None, False),
         ("i", "Backlog", None, False), ("i", "Done", None, False),
         ("h", "SAVED VIEWS"), ("i", "Shipping this week", None, False)]
y = 360
for it in sheet:
    if it[0] == "h":
        b += txt(M0, y + 16, it[1], 12, fill=MUT, weight="600", mono=True); y += 24
    else:
        _, label, badge, active = it
        if active: b += rect(M0 - 8, y, M1 - M0 + 16, 32, rx=6, fill=PH)
        b += glyph(M0 + 4, y + 8)
        b += txt(M0 + 32, y + 21, label, 14, weight="600" if active else None)
        if badge:
            b += rect(M1 - 72, y + 8, 32, 16, rx=8, fill=PH)
            b += txt(M1 - 56, y + 20, badge, 12, "middle")
        y += 32
b += region(M0 - 8, 384, M1 - M0 - 16, 160)
b += callout(M1 - 8, 312, "1")
b += callout(M1 - 8, 464, "2")
b += callout(M1 - 8, 640, "3")
write("tasks-views-mobile.svg", MW_, MH_, b, "PAP-670 rev3 views picker as a bottom sheet")

# ------------------------------------------------------- 4. tasks-everything-mobile
b  = appbar("Tasks")
b += rect(M0, 72, 208, 32, rx=16, fill=PH)
b += glyph(M0 + 12, 80)
b += txt(M0 + 40, 93, "Views: Everything", 14, weight="600")
b += chev(M0 + 188, 86)
cx = M0
for label, on in [("Everything", True), ("Tasks", False), ("Approvals", False), ("Failed", False)]:
    w = 7 * len(label) + 24
    b += rect(cx, 120, w, 24, rx=12, fill=PH if on else "#fff")
    b += txt(cx + w / 2, 137, label, 12, "middle")
    cx += w + 8
b += txt(M1 - 8, 137, "›", 14, "end", MUT)
b += txt(M0, 176, "TODAY", 12, fill=MUT, weight="600", mono=True)
for i, (t, m, u, k) in enumerate([
        ("PAP-670 clean up left nav", "assigned to me · in progress", True, "task"),
        ("Approve $40 Ramp charge", "requested by CFO agent", True, "approval"),
        ("Heartbeat run failed — CEO", "adapter stopped after 2 retries", True, "failed_run"),
        ("Dana wants to join Paperclip", "invited by Scott", False, "join_request")]):
    b += m_task_row(192 + i * 88, t, m, unread=u, kind=k)
b += line(M0, 544, M1, 544, MUT, 1)
b += txt(M0, 584, "EARLIER", 12, fill=MUT, weight="600", mono=True)
b += m_task_row(600, "PAP-664 destructive token", "assigned to me · blocked")
b += line(M0, 672, M1, 672, MUT, 1)
b += tabbar("Tasks")
b += region(M0, 192, M1 - M0, 352)
b += callout(M1 - 8, 112, "1")
b += callout(M1 - 8, 180, "2")
write("tasks-everything-mobile.svg", MW_, MH_, b, "PAP-670 rev3 Everything view on mobile")

# ------------------------------------------------------- 5. chat-mobile
b  = appbar("Chat")
b += rect(M0, 72, M1 - M0 - 80, 32, rx=6)
b += glyph(M0 + 12, 80)
b += txt(M0 + 40, 93, "Find an agent…", 14, fill=MUT)
b += rect(M1 - 72, 72, 72, 32, rx=6, fill=PH)
b += txt(M1 - 36, 93, "+ New", 14, "middle")
b += txt(M0, 136, "STARRED", 12, fill=MUT, weight="600", mono=True)
for i, (n, s2) in enumerate([("CEO", "product direction, planning"),
                             ("Design QA", "screenshots + visual review")]):
    y = 152 + i * 72
    b += rect(M0, y, M1 - M0, 64, rx=8)
    b += avatar(M0 + 32, y + 32, 14)
    b += txt(M0 + 60, y + 28, n, 14, weight="600")
    b += txt(M0 + 60, y + 48, s2, 12, fill=MUT)
    b += circ(M1 - 28, y + 32, 6)
b += txt(M0, 320, "RECENT CONVERSATIONS", 12, fill=MUT, weight="600", mono=True)
for i, (n, s2, t) in enumerate([("CEO", "“draft the PAP-670 plan”", "2h"),
                                ("CodexCoder", "“patch the toolbar slot”", "1d"),
                                ("Design QA", "“recheck the light theme”", "3d"),
                                ("CFO", "“Sentry seat approved”", "4d")]):
    y = 336 + i * 72
    b += rect(M0, y, M1 - M0, 64, rx=8)
    b += avatar(M0 + 32, y + 32, 14)
    b += txt(M0 + 60, y + 28, n, 14, weight="600")
    b += txt(M0 + 60, y + 48, s2, 12, fill=MUT)
    b += txt(M1 - 16, y + 32, t, 12, "end", MUT)
b += tabbar("Chat")
b += callout(M1 - 8, 128, "1")
b += callout(M1 - 8, 312, "2")
b += callout(262, 728, "3")
write("chat-mobile.svg", MW_, MH_, b, "PAP-670 rev3 Chat landing on mobile")

# Screen 6 removed in revision 3: Workspaces is gone from the organisation menu,
# so that menu is unchanged and has nothing to wireframe.
