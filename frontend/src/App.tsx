import { useState } from "react";

import { WorkspaceShell } from "./components/WorkspaceShell";
import { canAccessWorkspaceView, type WorkspaceView } from "./config/workspaceAccess";
import { useAuth } from "./hooks/useAuth";
import { AssistantPage } from "./pages/AssistantPage";
import { EvaluationPage } from "./pages/EvaluationPage";
import { KnowledgePage } from "./pages/KnowledgePage";
import { LoginPage } from "./pages/LoginPage3";
import { OperationsPage } from "./pages/OperationsPage";
import "./styles.css";

export default function App() {
  const { session } = useAuth();
  const [view, setView] = useState<WorkspaceView>("assistant");
  if (!session) return <LoginPage />;
  const activeView = canAccessWorkspaceView(session.user.role, view) ? view : "assistant";

  function navigate(nextView: WorkspaceView) {
    if (session && canAccessWorkspaceView(session.user.role, nextView)) setView(nextView);
  }

  return (
    <WorkspaceShell active={activeView} onNavigate={navigate}>
      {activeView === "assistant" && <AssistantPage />}
      {activeView === "knowledge" && <KnowledgePage />}
      {activeView === "evaluation" && <EvaluationPage />}
      {activeView === "operations" && <OperationsPage />}
    </WorkspaceShell>
  );
}
