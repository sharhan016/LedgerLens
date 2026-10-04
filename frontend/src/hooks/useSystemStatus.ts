import { useEffect, useState } from "react";

import { getSystemStatus } from "../services/system";
import type { SystemStatus } from "../types/system";

type SystemStatusState = {
  data: SystemStatus | null;
  error: string | null;
  loading: boolean;
};

export function useSystemStatus(): SystemStatusState {
  const [state, setState] = useState<SystemStatusState>({
    data: null,
    error: null,
    loading: true,
  });

  useEffect(() => {
    const controller = new AbortController();
    getSystemStatus(controller.signal)
      .then((data) => setState({ data, error: null, loading: false }))
      .catch((error: unknown) => {
        if (error instanceof DOMException && error.name === "AbortError") return;
        const message = error instanceof Error ? error.message : "API unavailable";
        setState({ data: null, error: message, loading: false });
      });
    return () => controller.abort();
  }, []);

  return state;
}

