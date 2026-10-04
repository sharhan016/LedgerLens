import { createContext, useContext, useMemo, useState, type ReactNode } from "react";

import { demoLogin } from "../services/api";
import type { DemoSession, Role } from "../types/api";

type AuthContextValue = {
  session: DemoSession | null;
  loading: boolean;
  error: string | null;
  login: (role: Role) => Promise<void>;
  logout: () => void;
};

const AuthContext = createContext<AuthContextValue | null>(null);
const STORAGE_KEY = "ledgerlens.demo-session";

function storedSession(): DemoSession | null {
  try {
    const value = localStorage.getItem(STORAGE_KEY);
    return value ? (JSON.parse(value) as DemoSession) : null;
  } catch {
    return null;
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<DemoSession | null>(storedSession);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const value = useMemo<AuthContextValue>(
    () => ({
      session,
      loading,
      error,
      login: async (role) => {
        setLoading(true);
        setError(null);
        try {
          const next = await demoLogin(role);
          localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
          setSession(next);
        } catch (reason) {
          setError(reason instanceof Error ? reason.message : "Unable to start demo session");
        } finally {
          setLoading(false);
        }
      },
      logout: () => {
        localStorage.removeItem(STORAGE_KEY);
        setSession(null);
      },
    }),
    [error, loading, session],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const value = useContext(AuthContext);
  if (!value) throw new Error("useAuth must be used inside AuthProvider");
  return value;
}

