"""Rebuild design/pap-670/index.html. Reuses the CSS/JS already in the file."""
import os, html, re, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.normpath(os.path.join(HERE, ".."))
prev = open(os.path.join(D, "index.html")).read()
css = prev[prev.index("<style>"):prev.index("</style>") + len("</style>")]
js  = prev[prev.index("<script>"):]

SCREENS = [
 dict(id="s1", n=1, slug="left-nav", lede="Step 1 · The nav itself",
   title="The left nav, after",
   desc="Eleven static rows instead of thirteen, and the one thing that had no entry point — chat — gets the first slot under Work. Search, Inbox and Workspaces keep their pages and their URLs; they just stop spending a permanent row. Dashboard stays exactly where it is.",
   notes=[
    "Organisation switcher — unchanged as a switcher. It picks up one new item: Workspaces (screen 6).",
    "The New Task row keeps its full width; a search icon button sits at its right edge. ⌘K still opens the command palette, and /search is unchanged. In the collapsed rail this becomes its own icon row directly under New Task.",
    "Dashboard — stays as its own row, directly below New Task, keeping its live-run count. This is the one thing that changed between revision 1 and revision 2 of this plan.",
    "Chat — new, first item under Work. Opens a /chats landing (screen 5). Hidden entirely while enableAgentChat is off, the same no-flash pattern the other flagged rows already use.",
    "Tasks — now the only task surface. It carries the badge that used to sit on Inbox: unread count, danger tone when a heartbeat run has failed.",
    "Projects and its starred children — unchanged.",
    "Org group — unchanged, and Audit stays in it. Confirmed by the board.",
    "Recent tasks — unchanged.",
    "Account bar — unchanged.",
    "The Views control in the content area is the single entry point to every list the old nav split across two separate rows.",
   ],
   mobile="On mobile the same rows render inside the drawer. Behind the scrim, the bottom tab bar swaps Inbox for Chat — Home · Tasks · + · Chat · Agents. Home keeps pointing at /dashboard; the board asked for it to stay.",
   why="The nav was carrying two rows that are a once-a-day destination at most (Search, Workspaces) and one that duplicates a list you already have (Inbox). Chat is the opposite: a thing you reach for constantly with no entry point at all. Dashboard did not fit that pattern, so it keeps its row.",
 ),
 dict(id="s2", n=2, slug="tasks-mine", lede="Step 2 · The merge",
   title="Tasks, opening on your last-used view",
   desc="Inbox stops being a page and becomes a view. Everything that made the inbox an inbox — unread dots, mark-all-read, swipe/hover archive, date grouping — comes across with it.",
   notes=[
    "The Views control replaces both the Inbox tab bar and the implicit “all tasks” default that /issues has today. Bare /issues opens whichever view you used last, defaulting to Mine on a fresh profile — confirmed by the board.",
    "The active view reads back as a chip with its live count, so you can see you are in a filtered view without opening the menu.",
    "Mark all read and Archive appear only while a My Work view is active; they are meaningless in “All tasks”.",
    "Unread dots, hover archive and mark-unread — all preserved. These are the behaviours that make it an inbox rather than a list.",
    "Date-group separators already exist on both surfaces today; after the merge there is one implementation.",
    "Row hover reveals the inbox actions, exactly as it does on /inbox/mine now.",
   ],
   mobile="The toolbar collapses to a pill row (Views · Filter · overflow) and Views opens as a bottom sheet rather than a dropdown. Rows go to two lines plus a meta line.",
   why="Two surfaces that both list tasks, with two toolbars, two filter states and two saved-view stores, is the actual cost of the current split — not the nav row. Merging is what makes removing the row honest.",
 ),
 dict(id="s3", n=3, slug="tasks-views", lede="Step 3 · Reaching the old views",
   title="Every current view, in one menu",
   desc="This is the answer to “how does a user get to all the views they have today”. Nothing is dropped; each one becomes a named view.",
   notes=[
    "The Views trigger, showing the active view.",
    "MY WORK — the five former /inbox tabs, unchanged in meaning: Mine, Unread, Blocked, Recent, Everything.",
    "ORGANISATION — the former /issues presets: All tasks, Active, Backlog, Done. These are already redirects to /issues today, so they cost nothing to reinstate as views.",
    "Saved views — new. Any filter set you build can be named and pinned here, which is what stops the menu from needing to grow again.",
   ],
   mobile="The menu becomes a bottom sheet with the same three groups and the same order.",
   why="A dropdown of 10 named views is cheaper to scan than 2 nav rows plus a 5-tab bar plus 4 redirect URLs, and it is the only structure that keeps growing gracefully.",
 ),
 dict(id="s4", n=4, slug="tasks-everything", lede="Step 4 · The hard part",
   title="“Everything” has to carry non-task rows",
   desc="The inbox is not only tasks. /inbox/all mixes in approvals, failed heartbeat runs, join requests and alerts, each with its own row component and its own actions. This is the part of the merge that is real work rather than routing.",
   notes=[
    "Everything is the former /inbox/all.",
    "The category chips are the existing allCategoryFilter values: everything · tasks · approvals · failed runs · join requests · alerts.",
    "Non-task rows keep their own components and actions. An approval is approved, a failed run is retried, a join request is admitted — none of those are task operations, and rendering them as task rows would be a regression.",
    "So the combined list needs a row renderer that switches on item kind. IssuesList is task-only today; this is the one place the plan adds a genuinely new capability rather than moving code.",
   ],
   mobile="Chips scroll horizontally; the kind tag moves under the title so the row stays two-thumb readable.",
   why="Calling this out up front is the difference between a two-day change and a two-week one. If it turns out to be too much, the fallback is to keep /inbox/all as its own page reachable from the Views menu — the nav row still goes away.",
 ),
 dict(id="s5", n=5, slug="chat", lede="Step 5 · The thing we are making room for",
   title="Chat gets a landing page",
   desc="Today the only way into a chat is a sidebar section that appears when a flag is on, and there is no /chats index at all — you have to already know an agent's route ref. The new nav item needs somewhere to go.",
   notes=[
    "The Chat nav item is active; the existing starred-agents sidebar section can nest under it exactly as starred projects nest under Projects.",
    "New chat opens the existing AgentChatPicker — no new picker.",
    "Starred and recent conversations reuse orderChatAgents and useRecentAgentChats, which already back the sidebar section.",
    "Selecting a conversation opens the existing /chats/:agentRef view; on desktop it previews in place.",
   ],
   mobile="The conversation list is a full screen; selecting a conversation pushes to the chat, with a back affordance in the app bar.",
   why="“Make space for chat” only pays off if the space leads somewhere. A nav row pointing at a route that does not exist would be worse than no row.",
 ),
 dict(id="s6", n=6, slug="org-menu", lede="Step 6 · Where Workspaces lands",
   title="The organisation menu takes Workspaces",
   desc="Workspaces is an “about this organisation” page rather than an “about my work” page, and the organisation switcher is already the organisation-scoped menu. It is the only thing moving here — Dashboard keeps its nav row.",
   notes=[
    "The existing organisation list, reorder and switch behaviour — unchanged.",
    "One new item: Workspaces, still flag-gated on enableIsolatedWorkspaces and still reachable at /projects/:id/workspaces. This is the only addition to this menu.",
    "Create organisation, Invite people, Settings and Sign out — unchanged.",
   ],
   mobile="The dropdown becomes a bottom sheet; the same item sits between the organisation list and the actions.",
   why="Workspaces is flag-gated, rarely visited, and organisation-scoped — three reasons it does not earn a permanent row, and one menu that already matches its scope.",
 ),
]

def sec(s):
    notes = "\n".join(f'              <li><strong>{i+1}</strong> — {html.escape(n)}</li>'
                      for i, n in enumerate(s["notes"]))
    return f'''
      <section id="{s['id']}">
        <div class="lede">{html.escape(s['lede'])}</div>
        <h2><span class="step-num">{s['n']}.</span>{html.escape(s['title'])}</h2>
        <p class="desc">{html.escape(s['desc'])}</p>
        <div class="grid">
          <div class="wire" data-zoom data-caption="{s['n']:02d} · {html.escape(s['title'])} (desktop)">
            <div class="label"><span>{s['slug']}.svg</span><span>1280×800 · desktop</span></div>
            <img src="wireframes/{s['slug']}.svg" alt="{html.escape(s['title'])} desktop wireframe" />
          </div>
          <div class="wire mobile-wire mobile-col" data-zoom data-caption="{s['n']:02d} · {html.escape(s['title'])} (mobile)">
            <div class="label"><span>{s['slug']}-mobile.svg</span><span>375×812</span></div>
            <img src="wireframes/{s['slug']}-mobile.svg" alt="{html.escape(s['title'])} mobile wireframe" />
          </div>
          <div class="notes notes-col">
            <h3>Annotations</h3>
            <ul>
{notes}
            </ul>
            <h3>On mobile</h3>
            <p style="color: var(--muted); font-size: 14px; margin: 4px 0 0;">{html.escape(s['mobile'])}</p>
            <div class="why"><strong>Why this changes.</strong> {html.escape(s['why'])}</div>
          </div>
        </div>
      </section>
'''

toc = "\n".join(f'        <a href="#{s["id"]}"><span class="num">{s["n"]}</span>{html.escape(s["title"])}</a>'
                for s in SCREENS)

SETTLED = '''
      <section id="settled">
        <div class="lede">Settled</div>
        <h2>What changed in revision 2</h2>
        <p class="desc">Revision 1 moved Dashboard into the organisation menu. The board rejected that and answered the four open questions. Everything below is now decided, not proposed.</p>
        <div class="notes">
          <ul>
            <li><strong>Dashboard stays in the nav</strong>, as its own row directly below New Task, keeping its live-run count. Revision 1 had it moving into the organisation menu; it no longer does. The organisation menu now gains only Workspaces.</li>
            <li><strong>The truncated ticket bullet is dropped.</strong> “avatar/icon and get rid of it as a” is set aside at the board's instruction. The separate “find another place for search” bullet still stands, so search still leaves the nav and becomes the icon button in the New Task row.</li>
            <li><strong>Tasks opens your last-used view</strong>, defaulting to Mine on a fresh profile.</li>
            <li><strong>Audit stays in the nav.</strong></li>
            <li><strong>The mobile Home tab stays</strong>, pointing at /dashboard. Only the Inbox tab is replaced, by Chat.</li>
          </ul>
          <div class="why"><strong>One risk still worth naming.</strong> Screen 4 is the only part of this that is not routing and CSS. If the mixed-row renderer turns out to be expensive, the fallback is to leave <code>/inbox/all</code> as its own page reached from the Views menu — every nav row still disappears, and the other nine views still merge.</div>
        </div>
      </section>
'''

page = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>PAP-670 — Clean up the left nav, make space for chat</title>
{css}
</head>
<body>
  <div class="shell">
    <details class="toc">
      <summary class="toc-summary">
        <span>
          <span class="crumb">PAP-670 · Left nav · rev 2</span><br>
          <span class="title">Jump to a screen</span>
        </span>
        <span class="chevron" aria-hidden="true"></span>
      </summary>
      <nav class="toc-body" aria-label="Section navigation">
        <h1>PAP-670</h1>
        <div style="font-size: 13px; color: var(--muted); margin-bottom: 16px;">Clean up the left nav, make space for chat</div>

        <h2>Flow</h2>
        <a href="#flow"><span class="num">⤳</span>Where every item goes</a>

        <h2>Screens</h2>
{toc}

        <h2>Decisions</h2>
        <a href="#settled"><span class="num">✓</span>What changed in rev 2</a>
      </nav>
    </details>

    <main>
      <header class="hero">
        <div class="crumb">PAP-670 · Wireframes · revision 2</div>
        <h1>Clean up the left nav, make space for chat</h1>
        <p>Thirteen static nav rows become eleven. Search, Inbox and Workspaces each move somewhere that already suits them, and the row they free up goes to Chat — the one surface people reach for constantly that has no entry point at all today. Dashboard keeps its own row, directly below New Task. Nothing is deleted and no URL breaks.</p>
        <div class="pills">
          <span class="pill">Revision 2</span>
          <span class="pill">6 screens · 13 wireframes</span>
          <span class="pill">Desktop + mobile</span>
          <span class="pill">Lo-fi · monochrome</span>
          <span class="pill">Click any wireframe to zoom</span>
        </div>
      </header>

      <section id="flow" class="flow-section">
        <div class="lede">Flow</div>
        <h2>Where every left-nav item goes</h2>
        <p class="desc">Before on the left, after on the right, destinations in the middle. The grey dotted path is Dashboard staying put. Red dashed marks are annotation, not UI.</p>
        <div class="wire" data-zoom data-caption="Flow — where every left-nav item goes">
          <div class="label"><span>flow.svg</span><span>1280×880</span></div>
          <img src="wireframes/flow.svg" alt="Before and after left nav with destinations for each removed item" />
        </div>
      </section>
{''.join(sec(s) for s in SCREENS)}
{SETTLED}
      <div class="footer">
        PAP-670 · revision 2 · regenerate with <code>design/pap-670/tools/</code> · lo-fi, monochrome, 8px grid · SVG sources in <code>wireframes/</code>
      </div>
    </main>
  </div>

  <div class="lightbox" id="lb">
    <span class="close" id="lbClose">×</span>
    <img id="lbImg" alt="" />
    <div class="caption" id="lbCap"></div>
  </div>

{js}
'''
open(os.path.join(D, "index.html"), "w").write(page)
print("wrote index.html", len(page))
