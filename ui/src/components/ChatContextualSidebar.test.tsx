// @vitest-environment jsdom

import { act } from "react";
import { createRoot } from "react-dom/client";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { ChatContextualSidebar } from "./ChatContextualSidebar";

const mockLocation = vi.hoisted(() => ({ pathname: "/PAP/chats/cto", search: "" }));
const mockConversations = vi.hoisted(() => ({
  agents: [] as Array<Record<string, unknown>>,
  eligibleAgents: [] as Array<Record<string, unknown>>,
  conversations: [] as Array<{ agent: Record<string, unknown>; issue: Record<string, unknown> | null }>,
}));

vi.mock("@/lib/router", () => ({
  Link: ({ to, children, ...props }: { to: string; children: React.ReactNode }) => (
    <a href={to} {...props}>{children}</a>
  ),
  useLocation: () => mockLocation,
  useNavigate: () => vi.fn(),
}));
vi.mock("@/context/CompanyContext", () => ({
  useCompany: () => ({ selectedCompanyId: "company-1", selectedCompany: { name: "Paperclip", issuePrefix: "PAP" } }),
}));
vi.mock("@/context/SidebarContext", () => ({
  useSidebar: () => ({ isMobile: false, setSidebarOpen: vi.fn() }),
}));
vi.mock("@/hooks/useAgentConversations", () => ({
  useAgentConversations: () => ({
    agents: mockConversations.agents,
    eligibleAgents: mockConversations.eligibleAgents,
    agentsQuery: { isPending: false, error: null, refetch: vi.fn() },
    conversations: mockConversations.conversations,
    loading: false,
  }),
}));
vi.mock("./AgentChatPicker", () => ({ AgentChatPicker: () => null }));
vi.mock("./AgentAvatar", () => ({ AgentAvatar: () => <span data-slot="agent-avatar" /> }));

// eslint-disable-next-line @typescript-eslint/no-explicit-any
(globalThis as any).IS_REACT_ACT_ENVIRONMENT = true;

const agent = (id: string, name: string, title: string) => ({
  id, name, title, role: "general", urlKey: id, icon: null, createdAt: "2026-09-01T00:00:00.000Z",
});

describe("ChatContextualSidebar", () => {
  let container: HTMLDivElement;
  const ceo = agent("ceo", "CEO", "Chief executive");
  const cto = agent("cto", "CTO", "Chief technologist");
  const qa = agent("qa", "QA", "Quality");
  const designer = agent("designer", "Designer", "Design");
  const fired = agent("fired", "Fired", "Gone");

  beforeEach(() => {
    container = document.createElement("div");
    document.body.appendChild(container);
    mockLocation.pathname = "/PAP/chats/cto";
    mockConversations.agents = [ceo, cto, qa, designer, fired];
    // `fired` is ineligible (terminated or left) so the hook leaves it out.
    mockConversations.eligibleAgents = [ceo, cto, qa, designer];
    mockConversations.conversations = [
      { agent: cto, issue: { id: "i-2", updatedAt: new Date().toISOString() } },
      { agent: ceo, issue: { id: "i-1", updatedAt: new Date().toISOString() } },
    ];
  });

  afterEach(() => {
    container.remove();
  });

  function render() {
    const root = createRoot(container);
    act(() => root.render(<ChatContextualSidebar />));
    return root;
  }

  function rowNames() {
    return [...container.querySelectorAll("a[data-agent-id]")].map((row) => row.getAttribute("data-agent-id"));
  }

  it("lists every eligible agent: conversations first, then the rest by name", () => {
    const root = render();
    expect(container.textContent).toContain("Teammates");
    expect(rowNames()).toEqual(["cto", "ceo", "designer", "qa"]);
    expect(container.textContent).not.toContain("Fired");
    expect(container.querySelectorAll('[data-slot="agent-avatar"]')).toHaveLength(4);
    expect(container.querySelector('a[href="/agents"]')?.textContent).toContain("Browse all agents");
    act(() => root.unmount());
  });

  it("marks the open conversation as the current page", () => {
    const root = render();
    expect(container.querySelector('a[aria-current="page"]')?.getAttribute("data-agent-id")).toBe("cto");
    act(() => root.unmount());
  });

  it("marks an agent opened before its first message without moving it", () => {
    mockLocation.pathname = "/PAP/chats/qa";
    const root = render();
    expect(rowNames()).toEqual(["cto", "ceo", "designer", "qa"]);
    expect(container.querySelector('a[aria-current="page"]')?.getAttribute("data-agent-id")).toBe("qa");
    act(() => root.unmount());
  });

  it("still lists every agent when there are no conversations", () => {
    mockLocation.pathname = "/PAP/chats";
    mockConversations.conversations = [];
    const root = render();
    expect(rowNames()).toEqual(["ceo", "cto", "designer", "qa"]);
    act(() => root.unmount());
  });

  it("explains an empty rail when no agent is eligible", () => {
    mockLocation.pathname = "/PAP/chats";
    mockConversations.conversations = [];
    mockConversations.eligibleAgents = [];
    const root = render();
    expect(rowNames()).toEqual([]);
    expect(container.textContent).toContain("No agents to chat with yet.");
    act(() => root.unmount());
  });
});
