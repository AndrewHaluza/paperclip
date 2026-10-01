import { useMemo, useState } from "react";
import { Network, Plus, Search } from "lucide-react";
import type { Agent } from "@paperclipai/shared";
import { useCompany } from "@/context/CompanyContext";
import { useAgentConversations, type AgentConversation } from "@/hooks/useAgentConversations";
import { Link, useLocation, useNavigate } from "@/lib/router";
import { timeAgo } from "@/lib/timeAgo";
import { agentRouteRef, cn } from "@/lib/utils";
import { AgentChatPicker } from "./AgentChatPicker";
import { AgentAvatar } from "./AgentAvatar";
import { ContextualSidebarFrame } from "./ContextualSidebarFrame";
import { contextualSidebarStyles } from "./contextual-sidebar-styles";
import { Button } from "./ui/button";
import { Input } from "./ui/input";

export function chatHref(agent: Pick<Agent, "id" | "name" | "urlKey">) {
  return `/chats/${encodeURIComponent(agentRouteRef(agent))}`;
}

/**
 * Secondary rail for the Chat surface (PAP-670). The primary nav keeps a single
 * `Chat` row; the agents you talk to live here, beside the open conversation,
 * the same way Skills and Apps keep their local navigation in a second rail.
 */
export function ChatContextualSidebar() {
  const { selectedCompanyId } = useCompany();
  const location = useLocation();
  const navigate = useNavigate();
  const [search, setSearch] = useState("");
  const [pickerOpen, setPickerOpen] = useState(false);
  const { agents, agentsQuery, eligibleAgents, conversations, loading } = useAgentConversations(selectedCompanyId, true);

  const activeRef = decodeURIComponent(location.pathname.match(/\/chats\/([^/]+)/)?.[1] ?? "");
  const activeId = agents.find((agent) => agent.id === activeRef || agentRouteRef(agent) === activeRef)?.id;

  const rows = useMemo(() => {
    // Every agent you can chat with has a row: the ones you have talked to
    // first, most recent first, then everyone else by name. The open
    // conversation always keeps its row, even before its first message.
    const listed = new Set(conversations.map(({ agent }) => agent.id));
    const rest = eligibleAgents
      .filter((agent) => !listed.has(agent.id))
      .sort((left, right) => left.name.localeCompare(right.name, undefined, { sensitivity: "base" }))
      .map((agent): AgentConversation => ({ agent, issue: null }));
    const open = activeId && !listed.has(activeId) && !rest.some(({ agent }) => agent.id === activeId)
      ? agents.find((agent) => agent.id === activeId)
      : undefined;
    const all: AgentConversation[] = [...(open ? [{ agent: open, issue: null }] : []), ...conversations, ...rest];
    const query = search.trim().toLowerCase();
    if (!query) return all;
    return all.filter(({ agent }) =>
      [agent.name, agent.title ?? "", agent.role].some((field) => field.toLowerCase().includes(query)));
  }, [activeId, agents, eligibleAgents, conversations, search]);

  return (
    <ContextualSidebarFrame
      surface="chat"
      title="Chat"
      showHeader={false}
      className="border-r border-border bg-background"
    >
      <div className="flex shrink-0 items-center justify-between gap-2 px-4 pb-2 pt-4">
        <h2 className="text-base font-semibold text-foreground">Chat</h2>
        <Button
          type="button"
          variant="outline"
          size="icon-sm"
          aria-label="New chat"
          onClick={() => setPickerOpen(true)}
        >
          <Plus className="h-4 w-4" />
        </Button>
      </div>
      <div className="relative shrink-0 px-4 pb-2">
        <Search
          aria-hidden="true"
          className="pointer-events-none absolute left-6 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-muted-foreground"
        />
        <Input
          type="search"
          aria-label="Find an agent"
          placeholder="Find an agent"
          value={search}
          onChange={(event) => setSearch(event.target.value)}
          className="h-8 w-full pl-8 text-xs"
        />
      </div>

      <nav aria-label="Conversations" data-slot="contextual-sidebar-nav" className={contextualSidebarStyles.nav}>
        <div data-slot="contextual-sidebar-section-label" className={contextualSidebarStyles.sectionLabel}>
          Teammates
        </div>
        {loading && rows.length === 0 ? (
          <p role="status" className="px-2 py-2 text-xs text-muted-foreground">Loading agents…</p>
        ) : rows.length === 0 ? (
          <div className="px-2 py-2 text-xs text-muted-foreground">
            {search.trim() ? <>No agents match “{search.trim()}”.</> : <>No agents to chat with yet.</>}
          </div>
        ) : (
          <div data-slot="contextual-sidebar-group" className="flex flex-col gap-1">
            {rows.map(({ agent, issue }) => {
              const active = agent.id === activeId;
              const stamp = issue?.updatedAt ?? issue?.createdAt;
              // An agent titled after itself (the CEO is "CEO") gets no echo line.
              const subtitle = [agent.title, agent.role].find(
                (value) => value && value.toLowerCase() !== agent.name.toLowerCase(),
              );
              return (
                <Link
                  key={agent.id}
                  to={chatHref(agent)}
                  aria-current={active ? "page" : undefined}
                  data-agent-id={agent.id}
                  className={cn(
                    "flex items-center gap-3 rounded-lg px-2 py-2 transition-colors",
                    active
                      ? "bg-sidebar-accent text-sidebar-accent-foreground"
                      : "text-foreground/80 hover:bg-sidebar-accent hover:text-sidebar-accent-foreground",
                  )}
                >
                  <AgentAvatar agent={agent} size={32} />
                  <span className="min-w-0 flex-1">
                    <span className="flex items-baseline gap-2">
                      <span className="min-w-0 flex-1 truncate text-(length:--text-compact) font-medium text-foreground">
                        {agent.name}
                      </span>
                      {stamp ? (
                        <span className="shrink-0 text-(length:--text-micro) text-muted-foreground">
                          {timeAgo(stamp)}
                        </span>
                      ) : null}
                    </span>
                    {subtitle ? (
                      <span className="block truncate text-xs text-muted-foreground">{subtitle}</span>
                    ) : null}
                  </span>
                </Link>
              );
            })}
          </div>
        )}
      </nav>

      <div className="shrink-0 border-t border-border px-3 py-2">
        <Link
          to="/agents"
          className="flex items-center gap-2.5 rounded-lg px-2 py-1.5 text-(length:--text-compact) text-muted-foreground transition-colors hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
        >
          <Network className="h-4 w-4 shrink-0" aria-hidden="true" />
          Browse all agents
        </Link>
      </div>

      <AgentChatPicker
        agents={agents}
        open={pickerOpen}
        onOpenChange={setPickerOpen}
        loading={agentsQuery.isPending}
        error={agentsQuery.error as Error | null}
        onRetry={() => { void agentsQuery.refetch(); }}
        onSelect={(agent) => navigate(chatHref(agent))}
      />
    </ContextualSidebarFrame>
  );
}
