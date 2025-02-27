import type { Environment } from "./environments";

export interface Integration {
  name: string;
  provider: string;
  environment?: Environment;
  id?: string;
  org_id?: string;
  created_date?: string;
  environment_id?: string;
  vendor?: string | null;
}

export interface IntegrationForPlanForm {
  name: string;
  provider: string;
  vendor: string;
  id: string;
}

export interface IntegrationsApiJsonResponse {
  items: Integration[];
  count: number;
}

export interface IntegrationsPage {
  page: number;
  integrations: Integration[];
  total: number;
  isReady: boolean;
}

export interface IntegrationControl {
  name: string;
  provider: IntegrationControlProvider;
}

interface IntegrationControlProvider {
  type: string;
  module: string;
  secrets: string[];
}
