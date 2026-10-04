export type CapabilityStatus = {
  name: string;
  status: "ready" | "planned";
  vertex_task: string;
};

export type SystemStatus = {
  application: string;
  environment: string;
  release: string;
  status: "foundation_ready";
  capabilities: CapabilityStatus[];
};

