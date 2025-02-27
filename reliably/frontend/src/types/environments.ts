export interface Environment {
  name: string;
  envvars: Var[];
  secrets: Secret[];
  id?: string;
  org_id?: string;
  created_date?: string;
  used_for?: string;
}

export interface Var {
  var_name: string;
  value: string;
}
export interface Secret {
  value: string;
  key: string;
  var_name?: string;
  path?: string;
}

export interface EnvironmentsApiJsonResponse {
  items: Environment[];
  count: number;
}

export interface EnvironmentsPage {
  page: number;
  environments: Environment[];
  total: number;
  isReady: boolean;
}
