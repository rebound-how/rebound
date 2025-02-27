export interface ExperimentsApiJsonResponse {
  items: Experiment[];
  count: number;
}

export interface SimpleExperimentsApiJsonResponse {
  items: SimpleExperiment[];
  count: number;
}

export interface Experiment {
  created_date: string;
  created_by?: string;
  id: string;
  org_id: string;
  definition: ExperimentDefinition;
  score?: ExperimentScore | null;
}

export interface ExperimentScore {
  score: number | null;
  trend: [string, string, number][] | null;
  // Execution ID, Date, score
}

export interface SimpleExperiment {
  created_date: Date | string;
  created_by?: string;
  id: string;
  org_id: string;
  title: string;
  last_statuses?: ("deviated" | "completed" | "interrupted" | "aborted" | "")[];
  last_execution?: Date | string;
  score?: number | null;
  trend?: [string, string, number][] | null;
}

export interface HypothesisRuntime {
  strategy:
    | "default"
    | "before-method-only"
    | "after-method-only"
    | "during-method-only"
    | "continuously";
  frequency?: number;
  fail_fast?: boolean;
}

export interface RollbacksRuntime {
  strategy: "default" | "always" | "never" | "deviated";
}

export interface Runtime {
  hypothesis?: HypothesisRuntime;
  rollbacks?: RollbacksRuntime;
}

export interface ExperimentDefinition {
  version?: string;
  id?: string;
  title: string;
  description: string;
  runtime?: Runtime;
  contributions?: Contributions;
  tags?: string[];
  uuid?: string;
  configuration?: Configuration;
  secrets?: { [key: string]: Secret };
  extensions?: Extension[];
  controls?: Control[];
  "steady-state-hypothesis"?: {
    title: string;
    probes?: Probe[];
  };
  method?: (Action | Probe)[];
  rollbacks?: Action[];
}

export interface ExperimentImportPayload {
  experiment: string;
}

export interface ExperimentStatus {
  // this is fetched from the executions store,
  // as it's built from executions data
  experimentId: string | null;
  lastExecution: Date | string | null;
  lastStatuses: ("deviated" | "completed" | "interrupted" | "aborted" | "")[];
}

export interface ExperimentShortForm {
  id: string;
  title: string;
}

export interface AllExperimentsApiResponse {
  items: ExperimentShortForm[];
  count: number;
}

export interface ExperimentReliablyExtension {
  name: string;
  objective_id: string;
  createdAt: string | Date;
  createdBy: string;
  lastExecution: string | Date;
  lastStatuses: ("deviated" | "completed" | "interrupted" | "aborted" | "")[];
}

export interface ExperimentsPage {
  page: number;
  experiments: SimpleExperiment[];
  total: number;
  isReady: boolean;
}

// export enum ContributionTypes {
//   Low = "low",
//   Medium = "medium",
//   High = "high",
//   None = "none",
// }
export type ContributionTypes = "none" | "low" | "medium" | "high";

export interface Contributions {
  [key: string]: ContributionTypes;
}

export interface EnvConfiguration {
  type: "env";
  key: string;
  default?: any;
  env_var_type?: string;
}

export interface Configuration {
  [key: string]:
    | null
    | string
    | number
    | boolean
    | string[]
    | EnvConfiguration
    | Configuration;
}

export interface Secret {
  [key: string]: string | EnvSecret | VaultSecret;
}

export interface EnvSecret {
  type: "env";
  key: string;
}

export interface VaultSecret {
  type: "vault";
  path: string;
}

export interface Extension {
  name: string;
  [key: string]: any;
}

export interface Control {
  name: string;
  provider: Provider;
  scope: "before" | "after";
  automatic: boolean;
}

export interface Probe {
  type: "probe";
  name: string;
  tolerance?: ScalarTolerance | ToleranceArray | Object;
  provider: Provider;
  configuration?: string;
  background?: boolean;
  controls?: Control[];
  ref?: string;
}

type ScalarTolerance = boolean | number | string;
type ToleranceArray = ScalarTolerance[];
// interface ProbeTolerance {
//   type: "probe";
//   name: string;
//   tolerance: ScalarTolerance | ToleranceArray | ProbeTolerance;
//   provider: Provider;
//   secret: Secret | null;
//   configuration?: string;
//   background?: boolean;
//   controls?: Control[];
// }

type Provider = PythonProvider | HttpProvider | ProcessProvider;

export interface PythonProvider {
  type: "python";
  module: string;
  func: string;
  arguments?: Object;
  secrets?: string[];
}

export interface HttpProvider {
  type: "http";
  url: string;
  method?: string;
  headers?: Object;
  expected_status?: number;
  arguments?: { [key: string]: string };
  timeout?: number | [number, number];
  secrets?: string[];
}

export interface ProcessProvider {
  type: "process";
  path: string;
  arguments?: unknown[] | string;
  timeout?: number;
  secrets?: string[];
}

export interface Action {
  type: "action";
  name: string;
  provider: Provider;
  controls?: Control[];
  configuration?: string;
  background?: boolean;
  pauses?: Pauses;
  ref?: string;
}

interface Pauses {
  before?: number | string;
  after?: number | string;
}

// Payload of the Reliably Prechecks and Reliably Safzguards integrations
export interface ReliablySafeguard {
  start: string;
  end: string;
  output: boolean;
  status: string;
  duration: number;
  activity: {
    name: string;
    type: string;
    provider: Provider;
    tolerance: boolean;
  };
}
