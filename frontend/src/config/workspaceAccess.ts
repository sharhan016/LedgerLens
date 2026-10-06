import type { Role } from "../types/api";

export type WorkspaceView = "assistant" | "knowledge" | "evaluation" | "operations";

export type WorkspaceNavigationItem = {
  id: WorkspaceView;
  label: string;
  index: string;
  descriptor: string;
};

const navigation: WorkspaceNavigationItem[] = [
  { id: "assistant", label: "Ask LedgerLens", index: "01", descriptor: "Ask · retrieve · verify" },
  { id: "knowledge", label: "Knowledge base", index: "02", descriptor: "Ingest · classify · govern" },
  { id: "evaluation", label: "Evaluation", index: "03", descriptor: "Measure · compare · review" },
  { id: "operations", label: "Operations", index: "04", descriptor: "Observe · protect · account" },
];

const visibleViews: Record<Role, readonly WorkspaceView[]> = {
  viewer: ["assistant", "knowledge"],
  analyst: ["assistant", "knowledge"],
  compliance: ["assistant", "knowledge", "evaluation"],
  admin: ["assistant", "knowledge", "evaluation", "operations"],
};

export function workspaceNavigationFor(role: Role): WorkspaceNavigationItem[] {
  const allowed = visibleViews[role];
  return navigation.filter((item) => allowed.includes(item.id));
}

export function canAccessWorkspaceView(role: Role, view: WorkspaceView): boolean {
  return visibleViews[role].includes(view);
}
