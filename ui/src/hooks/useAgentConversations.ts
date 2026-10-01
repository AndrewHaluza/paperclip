import { useMemo } from "react";
import { useQueries, useQuery } from "@tanstack/react-query";
import type { Agent, Issue } from "@paperclipai/shared";
import { agentChatsApi } from "@/api/agentChats";
import { agentsApi } from "@/api/agents";
import { authApi } from "@/api/auth";
import { useRecentAgentChats } from "@/lib/recent-agent-chats";
import { resourceMembershipState, useResourceMemberships } from "@/hooks/useResourceMemberships";
import { queryKeys } from "@/lib/queryKeys";

export interface AgentConversation {
  agent: Agent;
  issue: Issue | null;
}

function lastActivity(conversation: AgentConversation) {
  const stamp = conversation.issue?.updatedAt ?? conversation.issue?.createdAt;
  return stamp ? new Date(stamp).getTime() : 0;
}

/**
 * The agents the signed-in user has a conversation with, most recent first.
 *
 * TODO(PAP-670): replace the fan-out with a list endpoint before this ships.
 * There is no list endpoint for agent chats yet — only the per-agent
 * `GET /companies/:id/chats/:agentRef` that `AgentChat` already calls — so this
 * resolves one lookup per agent under the same query key `AgentChat` uses. The
 * open conversation is therefore served from cache, and a first message sent
 * from the chat pane shows up here without a refetch.
 *
 * Agents visited in this browser (the recent-chats list) are included even
 * before their first message, so a chat you just opened keeps its row.
 */
export function useAgentConversations(companyId: string | null, enabled: boolean) {
  const session = useQuery({
    queryKey: queryKeys.auth.session,
    queryFn: () => authApi.getSession(),
  });
  const userId = session.data?.user?.id ?? session.data?.session?.userId ?? null;
  const agentsQuery = useQuery({
    queryKey: queryKeys.agents.list(companyId!),
    queryFn: () => agentsApi.list(companyId!),
    enabled: !!companyId,
  });
  const agents = useMemo(() => agentsQuery.data ?? [], [agentsQuery.data]);
  const membershipsQuery = useResourceMemberships(companyId);
  // Same rule the Agents section of the sidebar uses: terminated agents and
  // agents you have left are not people you can chat with.
  const eligibleAgents = useMemo(() => agents.filter((agent) =>
    agent.status !== "terminated"
    && (!membershipsQuery.isSuccess || resourceMembershipState(membershipsQuery.data, "agent", agent.id) !== "left")),
  [agents, membershipsQuery.data, membershipsQuery.isSuccess]);
  const recentIds = useRecentAgentChats(companyId ?? "", userId);

  const chats = useQueries({
    queries: agents.map((agent) => ({
      queryKey: queryKeys.agentChats.detail(companyId, userId, agent.id),
      queryFn: () => agentChatsApi.get(companyId!, agent.id),
      enabled: enabled && !!companyId && session.isFetched,
      // One lookup per agent is the expensive part of this hook; keep results
      // for the session rather than refetching on every visit to Chat.
      staleTime: 5 * 60_000,
    })),
  });

  const chatData = chats.map((chat) => chat.data);
  // chatData is a fresh array every render; this key changes only when a
  // conversation appears or moves.
  const chatKey = chatData.map((issue) => (issue ? `${issue.id}@${issue.updatedAt}` : "-")).join("|");
  const conversations = useMemo(() => {
    const recentRank = new Map(recentIds.map((id, index) => [id, index]));
    return agents
      .map((agent, index): AgentConversation => ({ agent, issue: chatData[index] ?? null }))
      .filter(({ agent, issue }) => issue != null || recentRank.has(agent.id))
      .sort((left, right) =>
        lastActivity(right) - lastActivity(left)
        || (recentRank.get(left.agent.id) ?? Infinity) - (recentRank.get(right.agent.id) ?? Infinity)
        || left.agent.name.localeCompare(right.agent.name, undefined, { sensitivity: "base" }));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [agents, recentIds, chatKey]);

  return {
    agents,
    agentsQuery,
    eligibleAgents,
    conversations,
    recentIds,
    loading: agentsQuery.isPending || session.isPending || (enabled && chats.some((chat) => chat.isPending && chat.fetchStatus !== "idle")),
  };
}
