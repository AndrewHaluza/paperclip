import { useEffect, useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { MessageSquare, Search, SquarePen } from "lucide-react";
import type { Agent } from "@paperclipai/shared";
import { agentsApi } from "@/api/agents";
import { authApi } from "@/api/auth";
import { AgentIcon } from "@/components/AgentIconPicker";
import { AgentChatPicker } from "@/components/AgentChatPicker";
import { EmptyState } from "@/components/EmptyState";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useBreadcrumbs } from "@/context/BreadcrumbContext";
import { useCompany } from "@/context/CompanyContext";
import { useAgentChatEnabled } from "@/hooks/useAgentChatEnabled";
import {
  starredResourceIds,
  useResourceMembershipMutation,
  useResourceMemberships,
} from "@/hooks/useResourceMemberships";
import { queryKeys } from "@/lib/queryKeys";
import { Navigate, useNavigate } from "@/lib/router";
import { useRecentAgentChats } from "@/lib/recent-agent-chats";
import { agentRouteRef, cn } from "@/lib/utils";
import { StarToggle } from "@/components/StarToggle";
import { chatHref } from "@/components/ChatContextualSidebar";
import { useSidebar } from "@/context/SidebarContext";
import { useAgentConversations } from "@/hooks/useAgentConversations";

/**
 * Landing surface for the `Chat` nav row added in PAP-670. `/chats/:agentRef`
 * already existed; `/chats` did not, so the nav item had nowhere to land.
 *
 * Desktop pairs this route with the Chat secondary rail (the list of agents
 * you talk to), so the landing opens your most recent conversation beside it.
 * Mobile has no rail, so the landing is the agent list itself.
 */
export function AgentChatIndex() {
  const { isMobile } = useSidebar();
  return isMobile ? <AgentChatList /> : <AgentChatDesktopLanding />;
}

function AgentChatDesktopLanding() {
  const { selectedCompanyId } = useCompany();
  const { setBreadcrumbs } = useBreadcrumbs();
  const { enabled, loaded } = useAgentChatEnabled();
  const { agents, agentsQuery, conversations, recentIds, loading } = useAgentConversations(selectedCompanyId, enabled);
  // Return to the chat you last had open in this browser without waiting for
  // every agent's lookup; fall back to the most recent conversation.
  const lastVisited = agents.find((agent) => agent.id === recentIds[0]);
  const [pickerOpen, setPickerOpen] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    setBreadcrumbs([{ label: "Chat" }]);
  }, [setBreadcrumbs]);

  if (enabled && lastVisited) return <Navigate to={chatHref(lastVisited)} replace />;
  if (!loaded || (enabled && loading)) {
    return <p className="text-sm text-muted-foreground">Loading chats…</p>;
  }
  if (!enabled) {
    return (
      <EmptyState
        icon={MessageSquare}
        title="Agent Chat is disabled"
        message="Enable Agent Chat in Experimental settings to start conversations with your agents."
        description="Existing history stays reachable through task links."
      />
    );
  }
  const latest = conversations[0];
  if (latest) return <Navigate to={chatHref(latest.agent)} replace />;
  return (
    <>
      <EmptyState
        icon={MessageSquare}
        message="No conversations yet."
        description="Pick an agent to start chatting."
        action="New chat"
        onAction={() => setPickerOpen(true)}
      />
      <AgentChatPicker
        agents={agents}
        open={pickerOpen}
        onOpenChange={setPickerOpen}
        loading={agentsQuery.isPending}
        error={agentsQuery.error as Error | null}
        onRetry={() => { void agentsQuery.refetch(); }}
        onSelect={(agent) => navigate(chatHref(agent))}
      />
    </>
  );
}

function AgentChatList() {
  const { selectedCompanyId } = useCompany();
  const { setBreadcrumbs } = useBreadcrumbs();
  const { enabled, loaded } = useAgentChatEnabled();
  const navigate = useNavigate();
  const [search, setSearch] = useState("");
  const [pickerOpen, setPickerOpen] = useState(false);

  useEffect(() => {
    setBreadcrumbs([{ label: "Chat" }]);
  }, [setBreadcrumbs]);

  const { data: session } = useQuery({
    queryKey: queryKeys.auth.session,
    queryFn: () => authApi.getSession(),
  });
  const userId = session?.user?.id ?? session?.session?.userId;

  const agentsQuery = useQuery({
    queryKey: queryKeys.agents.list(selectedCompanyId!),
    queryFn: () => agentsApi.list(selectedCompanyId!),
    enabled: !!selectedCompanyId,
  });
  const agents = agentsQuery.data ?? [];

  const memberships = useResourceMemberships(selectedCompanyId);
  const membershipMutation = useResourceMembershipMutation(selectedCompanyId);
  const starredIds = useMemo(
    () => new Set(starredResourceIds(memberships.data, "agent")),
    [memberships.data],
  );
  const recentIds = useRecentAgentChats(selectedCompanyId ?? "", userId);

  const normalizedSearch = search.trim().toLowerCase();
  const matches = useMemo(() => {
    if (!normalizedSearch) return agents;
    return agents.filter((agent) =>
      [agent.name, agent.title ?? "", agent.role]
        .some((field) => field.toLowerCase().includes(normalizedSearch)),
    );
  }, [agents, normalizedSearch]);

  const starred = useMemo(
    () => matches.filter((agent) => starredIds.has(agent.id)),
    [matches, starredIds],
  );
  const recent = useMemo(() => {
    const byId = new Map(matches.map((agent) => [agent.id, agent]));
    return recentIds
      .filter((id) => !starredIds.has(id))
      .flatMap((id) => (byId.has(id) ? [byId.get(id)!] : []));
  }, [matches, recentIds, starredIds]);
  const everyoneElse = useMemo(() => {
    const seen = new Set([...starred, ...recent].map((agent) => agent.id));
    return matches
      .filter((agent) => !seen.has(agent.id))
      .sort((left, right) => left.name.localeCompare(right.name, undefined, { sensitivity: "base" }));
  }, [matches, starred, recent]);

  const openChat = (agent: Agent) =>
    navigate(`/chats/${encodeURIComponent(agentRouteRef(agent))}`);

  if (!selectedCompanyId) {
    return <EmptyState icon={MessageSquare} message="Select an organization to start a chat." />;
  }
  if (!loaded) {
    return <p className="text-sm text-muted-foreground">Loading chats…</p>;
  }
  if (!enabled) {
    return (
      <EmptyState
        icon={MessageSquare}
        title="Agent Chat is disabled"
        message="Enable Agent Chat in Experimental settings to start conversations with your agents."
        description="Existing history stays reachable through task links."
      />
    );
  }
  if (agentsQuery.error) {
    return <p className="text-sm text-destructive">{(agentsQuery.error as Error).message}</p>;
  }

  const card = (agent: Agent) => {
    const isStarred = starredIds.has(agent.id);
    const pending =
      membershipMutation.isPending
      && membershipMutation.variables?.resourceType === "agent"
      && membershipMutation.variables.resourceId === agent.id;
    return (
      <div
        key={agent.id}
        className="group/chat-card relative flex items-center gap-3 rounded-lg border border-border bg-card p-3 transition-colors hover:border-foreground/20 hover:bg-accent/40"
      >
        <button
          type="button"
          onClick={() => openChat(agent)}
          className="flex min-w-0 flex-1 items-center gap-3 text-left"
        >
          <AgentIcon icon={agent.icon} className="h-8 w-8 shrink-0" />
          <span className="min-w-0 flex-1">
            <span className="block truncate text-sm font-medium text-foreground">{agent.name}</span>
            <span className="block truncate text-xs text-muted-foreground">
              {agent.title ?? agent.role}
            </span>
          </span>
        </button>
        <span className="shrink-0">
          <StarToggle
            size="row"
            quiet
            starred={isStarred}
            pending={pending}
            resourceName={agent.name}
            onToggle={() =>
              membershipMutation.mutate({
                resourceType: "agent",
                resourceId: agent.id,
                resourceName: agent.name,
                starred: !isStarred,
              })
            }
            revealClassName={cn(
              "opacity-0 transition-opacity group-hover/chat-card:opacity-100 group-focus-within/chat-card:opacity-100",
              isStarred && "opacity-100",
            )}
          />
        </span>
      </div>
    );
  };

  const group = (label: string, items: Agent[]) =>
    items.length === 0 ? null : (
      <section aria-label={label} className="space-y-2">
        <h2 className="font-mono text-(length:--text-nano) font-medium uppercase tracking-widest text-muted-foreground/70">
          {label}
        </h2>
        <div className="grid gap-2 sm:grid-cols-2 xl:grid-cols-3">{items.map(card)}</div>
      </section>
    );

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center gap-2">
        <div className="relative min-w-0 flex-1 sm:max-w-(--sz-320px)">
          <Search
            aria-hidden="true"
            className="pointer-events-none absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-muted-foreground"
          />
          <Input
            type="search"
            aria-label="Search agents by name or role"
            placeholder="Search agents…"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            className="h-8 w-full pl-8 text-xs"
            data-page-search-target="true"
          />
        </div>
        <Button size="sm" variant="outline" className="ml-auto" onClick={() => setPickerOpen(true)}>
          <SquarePen className="h-4 w-4 sm:mr-1" />
          <span className="hidden sm:inline">New chat</span>
        </Button>
      </div>

      <AgentChatPicker
        agents={agents}
        open={pickerOpen}
        onOpenChange={setPickerOpen}
        loading={agentsQuery.isPending}
        error={agentsQuery.error as Error | null}
        onRetry={() => { void agentsQuery.refetch(); }}
        onSelect={openChat}
      />

      {agentsQuery.isPending ? (
        <p role="status" className="text-sm text-muted-foreground">Loading agents…</p>
      ) : matches.length === 0 ? (
        <EmptyState
          icon={MessageSquare}
          message={agents.length === 0 ? "No agents yet." : `No agents match “${search}”.`}
          description={
            agents.length === 0
              ? "Hire an agent from the Agents page to start chatting."
              : "Try another name or role."
          }
        />
      ) : (
        <>
          {group("Starred", starred)}
          {group("Recent", recent)}
          {group(starred.length + recent.length > 0 ? "All agents" : "Agents", everyoneElse)}
        </>
      )}
    </div>
  );
}
