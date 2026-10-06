import type { SystemStatus } from "../types/system";

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? "";

export async function getSystemStatus(signal?: AbortSignal): Promise<SystemStatus> {
  const response = await fetch(`${apiBaseUrl}/api/v1/system/status`, { signal });
  if (!response.ok) {
    throw new Error(`System status request failed with ${response.status}`);
  }
  return response.json() as Promise<SystemStatus>;
}
