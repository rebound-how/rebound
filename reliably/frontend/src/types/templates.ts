import type { ExperimentDefinition } from "@/types/experiments";
export interface TemplateField {
  key: string;
  title: string;
  placeholder: string;
  help: string;
  no_default?: boolean;
  default: string | number | boolean | object | null;
  type: string;
  required: boolean;
  query?: string
}

export interface Template {
  id: string;
  org_id?: string;
  user_id?: string;
  created_date?: string;
  manifest: TemplateManifest;
}

export interface TemplateManifest {
  metadata: {
    name: string;
    labels: string[];
    annotations: string[] | null;
  };
  spec: {
    provider: "chaostoolkit";
    type: "experiment";
    schema: {
      configuration: TemplateField[];
    };
    template: ExperimentDefinition;
    related?: RelatedActivity[];
  };
}

export interface RelatedActivity {
  block?: "warmup" | "method" | "hypothesis" | "rollbacks";
  name: string;
  origin?: string;
}

export interface RelatedTemplates {
  [key: string]: Template;
}

export interface TemplateCreate {
  metadata: {
    name: string;
    labels: string[];
  };
  spec: {
    provider: "chaostoolkit";
    type: "experiment";
    schema: {
      configuration: TemplateField[];
    };
    template: ExperimentDefinition;
  };
}

export interface TemplateExport {
  metadata: {
    id: string;
    org_id: string;
    name: string;
    labels: string[];
    annotations: string[] | null;
  };
  spec: {
    provider: "chaostoolkit";
    type: "experiment";
    schema: {
      configuration: TemplateField[];
    };
    template: ExperimentDefinition;
  };
}

export interface TemplatesPage {
  page: number;
  templates: Template[];
  total: number;
  isReady: boolean;
}

export interface CatalogsApiResponse {
  items: Template[];
  count: number;
}

export interface TemplatesLabelObject {
  label: string;
  active: boolean;
}
