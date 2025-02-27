export interface Scenario {
  id: string;
  org_id: string;
  user_id: string;
  experiment_id: string | null;
  plan_id: string | null;
  integration_id: string | null;
  created_date: string;
  completed: boolean;
  query: ScenarioQuery;
  suggestion: {
    items: ScenarioItem[];
  };
  meta: {
    error: string | null;
  };
}

export interface ScenarioLight {
  id: string;
  org_id: string;
  user_id: string;
  experiment_id: string | null;
  plan_id: string | null;
  integration_id: string | null;
  created_date: string;
  completed: boolean;
  query: ScenarioQuery;
  meta: {
    error: string | null;
  };
}

export interface ScenarioQuery {
  question: string;
  tags: string[];
  integration_id: string;
}

export interface ScenarioItem {
  name: string;
  ref: string;
  type: "action" | "probe";
  tags: string[];
  purpose: string;
  parameters: ScenarioItemParameter[];
}

export interface ScenarioItemParameter {
  key: string;
  title: string;
  type: "string" | "integer" | "float" | "number" | "boolean" | "object";
  required: boolean;
}

export interface UiScenarioParameter {
  item_name: string;
  item_ref: string;
  item_type: string;
  parameter: ScenarioItemParameter;
  user_value: string | number | boolean | object | null;
}

export interface UiScenarioActivity {
  name: string;
  type: string;
  count: number;
  parameters: UiScenarioParameter[];
}

export interface ParameterHistory {
  [key: string]: {
    value: string | number | boolean | object;
    type: "string" | "integer" | "float" | "number" | "boolean" | "object";
  }[];
}

export interface ScenarioError {
  title: string;
  message: string;
  id?: string;
  created_at?: string;
}
