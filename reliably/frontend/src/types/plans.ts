export interface Plan {
  id: string;
  created_date: Date | string;
  definition: {
    title?: string;
    environment: PlanGitHubEnvironment | PlanReliablyEnvironment | null;
    deployment: {
      deployment_id: string;
      deployment_type: string | null;
    };
    schedule: {
      type: string;
      pattern?: string;
      timezone?: string;
      via_agent?: boolean;
    };
    integrations?: string[];
    experiments: string[];
  };
  ref: string;
  status: string;
  error?: null | string;
  executions_count: number;
  last_executions_info?: PlanExecutionsInfo | null;
}

export interface PlanCreate {
  title?: string;
  environment: PlanGitHubEnvironment | PlanReliablyEnvironment | null;
  deployment: {
    deployment_id: string;
    deployment_type: string | null;
  };
  schedule: {
    type: string;
    pattern?: string;
    timezone?: string;
    via_agent?: boolean;
  };
  experiments: string[];
  integrations: string[];
}

export interface PlanGitHubEnvironment {
  provider: "github";
  name?: string;
  id?: string;
}

export interface PlanReliablyEnvironment {
  provider: "reliably_cloud";
  id?: string;
}

export interface PlanExecutionsInfo {
  running: { id: string; timestamp: string } | null;
  terminated: { id: string; timestamp: string } | null;
}

export interface PlansApiJsonResponse {
  items: Plan[];
  count: number;
}

export interface PlansPage {
  page: number;
  plans: Plan[];
  total: number;
  isReady: boolean;
}
