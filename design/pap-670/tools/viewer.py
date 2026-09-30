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
   desc="Twelve static rows instead of thirteen. Only two things leave: Inbox becomes a view inside Tasks, and Workspaces comes out of the chrome entirely. The row they free up goes to Chat — the one surface people reach for constantly with no entry point at all today. New Task, Search and Dashboard all keep their rows, in that order.",
   notes=[
    "Organisation switcher — completely unchanged. Nothing moves into it. Revisions 1 and 2 both tried to park something here; revision 3 does not.",
    "Search — keeps its own row, second in the top group. Revisions 1 and 2 turned it into an icon button in the New Task row; the board put it back, so search is untouched by this plan.",
    "Dashboard — keeps its own row, third in the top group, with its live-run count.",
    "Chat — new, first item under Work. Opens a /chats landing (screen 5). Hidden entirely while enableAgentChat is off, the same no-flash pattern the other flagged rows already use.",
    "Tasks — now the only task surface. It carries the badge that used to sit on Inbox: unread count, danger tone when a heartbeat run has failed.",
    "Projects and its starred children — unchanged.",
    "Org group — unchanged, and Audit stays in it. Confirmed by the board.",
    "Recent tasks — unchanged.",
    "Account bar — unchanged.",
    "The Views control in the content area is the single entry point to every list the old nav split across two separate rows.",
   ],
   mobile="On mobile the same rows render inside the drawer. Behind the scrim, the bottom tab bar is now Home · Chat · + · Tasks · Agents — Inbox is gone and Chat takes the second slot, the order the board asked for. Home keeps pointing at /dashboard.",
   why="Only two rows were actually earning their removal: Inbox duplicates a list you already have, and Workspaces is a flag-gated page almost nobody opens. Chat is the opposite — constant use, no entry point. Search and Dashboard did not fit that pattern, so the board kept them, and this revision stops trying to relocate them.",
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
        <h2>What changed in revision 3</h2>
        <p class="desc">Revision 2 moved search into an icon and re-homed Workspaces in the organisation menu. The board rejected both. Revision 3 stops relocating things that were not asked to move.</p>
        <div class="notes">
          <ul>
            <li><strong>Search keeps its own row.</strong> Revisions 1 and 2 turned it into an icon button in the New Task row; the top group is now New Task · Search · Dashboard, exactly as it is today. Search is untouched by this plan.</li>
            <li><strong>Workspaces is removed outright</strong> — from the left nav <em>and</em> the organisation dropdown, with no new home. The organisation menu therefore gains nothing at all, so the screen that showed it has been deleted rather than redrawn.</li>
            <li><strong>The mobile tab bar order is Home · Chat · + · Tasks · Agents.</strong> Chat takes the second slot; Inbox is gone.</li>
            <li>Carried over from revision 2 and unchanged: Dashboard keeps its row · Tasks opens your last-used view, defaulting to Mine · Audit stays in the nav · the mobile Home tab stays.</li>
          </ul>
          <div class="why"><strong>Two things to know.</strong> First, with Workspaces out of both menus, <code>/workspaces</code> is no longer reachable from any chrome — the route still resolves, and the page is still reachable at <code>/projects/:id/workspaces</code>, but nothing links to the standalone list. That is what &ldquo;remove it altogether&rdquo; means, and it is worth saying out loud. Second, screen 4 is still the only part of this that is not routing and CSS; if the mixed-row renderer turns out to be expensive, the fallback is to leave <code>/inbox/all</code> as its own page reached from the Views menu.</div>
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
          <span class="crumb">PAP-670 · Left nav · rev 3</span><br>
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
        <a href="#settled"><span class="num">✓</span>What changed in rev 3</a>
      </nav>
    </details>

    <main>
      <header class="hero">
        <div class="crumb">PAP-670 · Wireframes · revision 3</div>
        <h1>Clean up the left nav, make space for chat</h1>
        <p>Thirteen static nav rows become twelve. Inbox becomes a view inside Tasks, Workspaces comes out of the chrome entirely, and the row they free up goes to Chat — the one surface people reach for constantly that has no entry point at all today. New Task, Search and Dashboard all keep their rows, in that order. No route is deleted and no URL breaks.</p>
        <div class="pills">
          <span class="pill">Revision 3</span>
          <span class="pill">5 screens · 11 wireframes</span>
          <span class="pill">Desktop + mobile</span>
          <span class="pill">Lo-fi · monochrome</span>
          <span class="pill">Click any wireframe to zoom</span>
        </div>
      </header>

      <section id="flow" class="flow-section">
        <div class="lede">Flow</div>
        <h2>Where every left-nav item goes</h2>
        <p class="desc">Before on the left, after on the right, destinations in the middle. The grey dotted path is Search and Dashboard staying put. The red ✘ is Workspaces having no destination, on purpose. Red dashed marks are annotation, not UI.</p>
        <div class="wire" data-zoom data-caption="Flow — where every left-nav item goes">
          <div class="label"><span>flow.svg</span><span>1280×880</span></div>
          <img src="wireframes/flow.svg" alt="Before and after left nav with destinations for each removed item" />
        </div>
      </section>
{''.join(sec(s) for s in SCREENS)}
{SETTLED}
      <div class="footer">
        PAP-670 · revision 3 · regenerate with <code>design/pap-670/tools/</code> · lo-fi, monochrome, 8px grid · SVG sources in <code>wireframes/</code>
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
