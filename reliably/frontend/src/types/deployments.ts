export interface Deployment {
  name: string;
  definition:
    | GitHubDeploymentDefinition
    | ReliablyDeploymentDefinition
    | ContainerDeploymentDefinition
    | KubernetesDeploymentDefinition;
  id?: string;
  org_id?: string;
  created_date?: Date | string;
}

export interface NewDeploymentName {
  name: string;
}

export interface NewDeploymentName {
  name: string;
}

export interface DeploymentsApiJsonResponse {
  items: Deployment[];
  count: number;
}

export interface DeploymentsPage {
  page: number;
  deployments: Deployment[];
  total: number;
  isReady: boolean;
}

export interface DeploymentForPlanForm {
  name: string;
  id: string;
  type: string;
}

export interface GitHubDeploymentDefinition {
  type: string;
  repo: string;
  branch?: string;
  name?: string;
  username: string;
  token: string;
}

export interface ReliablyDeploymentDefinition {
  type: string;
  mode?: string;
  base_dir?: string | null;
  py_version?: string | null;
  py_dependencies?: string | null;
}

export interface ContainerDeploymentDefinition {
  type: string;
  image: string;
}

export interface KubernetesDeploymentDefinition {
  type: string;
  use_default_manifest: boolean;
  image?: string;
  namespace: string;
  manifest?: string;
  credentials?: string;
  use_in_cluster_credentials: boolean;
}
