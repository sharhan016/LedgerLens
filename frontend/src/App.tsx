import { useState } from "react";

import { WorkspaceShell, type WorkspaceView } from "./components/WorkspaceShell";
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
  return (
    <WorkspaceShell active={view} onNavigate={setView}>
      {view === "assistant" && <AssistantPage />}
      {view === "knowledge" && <KnowledgePage />}
      {view === "evaluation" && <EvaluationPage />}
      {view === "operations" && <OperationsPage />}
    </WorkspaceShell>
  );
}
