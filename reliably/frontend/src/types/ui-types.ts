import type { Template } from "@/types/templates";
import type { Configuration, Probe } from "@/types/experiments";

export interface PageHeaderAction {
  label: string;
  to?: string;
  method?: string;
  buttonClass?: string;
}

export interface NavLink {
  path: string;
  label: string;
  separator?: boolean;
}

export interface MultiButtonOption {
  label: string;
  icon: string;
  link?: string;
  disabled?: boolean;
  reason?: string;
  action?: string;
  warning?: boolean;
}

// Builder
export interface BuilderWorkflow {
  hypothesis: TemplateActivity[];
  warmup: TemplateActivity[];
  method: TemplateActivity[];
  rollbacks: TemplateActivity[];
  configuration?: Configuration;
}

export interface Activity {
  id: string;
  name: string;
  target: string;
  category: string;
  type: string;
  description: string;
  module: string;
}

export interface TemplateActivity {
  template: Template;
  suffix: string;
  fieldsStatus: boolean[];
  background: boolean;
  toleranceType?: string;
  tolerance?: Probe["tolerance"];
}

export type ActivityBlock = "warmup" | "method" | "hypothesis" | "rollbacks";
// End Builder types

// Experiment/Execution
export interface ExecutionUiStatus {
  label: string;
  type: "ko" | "warning" | "ok" | "unknown" | null;
}

// Draggable
export interface DraggableChangeEvent {
  moved?: DraggableMoved;
  added?: DraggableAdded;
  removed?: DraggableRemoved;
}

interface DraggableMoved {
  newIndex: number;
  oldIndex: number;
  element: any;
}

interface DraggableAdded {
  newIndex: number;
  element: any;
}

interface DraggableRemoved {
  oldIndex: number;
  element: any;
}
// End draggable types

export interface DashboardNumber {
  legend: string;
  value: string;
}

export interface Repository {
  organization: string;
  repository: string;
}

export interface Notification {
  id?: string;
  title: string;
  message: string;
  type?: string | null;
  autoClose?: boolean;
  hide?: boolean;
  createdAt?: Date | string;
}

export interface ExperimentStarter {
  title: string;
  description: string;
  tags: string[];
  url: string;
  color?: "pink" | "yellow" | "darkBlue" | "k8sBlue";
  icon?: string;
}

export interface IntegrationDescription {
  title: string;
  description: string;
  type: string;
  url: string;
  icon?: string;
  alpha?: boolean;
}

// Assistant
export interface ChatGptExtension {
  name: "chatgpt";
  messages: ChatGptMessage[];
  results: ChatGptResult[];
}

export interface ChatGptMessage {
  role: string;
  content: string;
}

interface ChatGptResult {
  id: string;
  model: string;
  object: string;
  created: number;
  choices: ChatGptResultChoice[];
  usage: ChatGptUsage;
}

interface ChatGptResultChoice {
  index: string;
  message: ChatGptMessage;
  finish_reason: string;
}

interface ChatGptUsage {
  prompt_tokens: number;
  completion_tokens: number;
  total_tokens: number;
}
// End Assistant types

// Chart Types
export interface RadarChartDataSet {
  label: string;
  backgroundColor: string;
  borderColor: string;
  borderWidth?: number;
  pointBackgroundColor: string;
  pointBorderColor: string;
  pointHoverBackgroundColor: string;
  pointHoverBorderColor: string;
  data: number[];
}

export interface RadarChartData {
  labels: string[];
  datasets: RadarChartDataSet[];
}

export interface PieChartDataSet {
  backgroundColor: string[];
  data: number[];
}

export interface LineChartDataSet {
  label: string;
  backgroundColor: string;
  data: number[];
}

export interface StackBarsChartDataSet {
  label: string;
  // name: string;
  // kind: string;
  // loc: string;
  // stack: string;

  backgroundColor?: string | string[];
  // borderColor: string;
  // pointBackgroundColor: string;
  // pointBorderColor: string;
  // pointHoverBackgroundColor: string;
  // pointHoverBorderColor: string;
  data: number[];
}

export interface ChartCoordinates {
  x: number;
  y: number;
}

export interface BubbleChartCoordinates {
  x: number;
  y: number;
  r: number;
}

export interface ScatterChartDataSet {
  label: string;
  backgroundColor?: string | string[];
  data: ChartCoordinates[];
}

export interface BubbleChartDataSet {
  label: string;
  backgroundColor?: string | string[];
  data: BubbleChartCoordinates[];
}

export interface ChartData {
  labels: string[];
  datasets:
    | PieChartDataSet[]
    | LineChartDataSet[]
    | RadarChartDataSet[]
    | StackBarsChartDataSet[];
}

export interface StackBarsChartData {
  labels: string[];
  datasets: StackBarsChartDataSet[];
}

export interface ScatterChartData {
  labels: string[];
  datasets: ScatterChartDataSet[];
}

export interface BubbleChartData {
  labels: string[];
  datasets: BubbleChartDataSet[];
}

export interface SharedChartOptions {
  responsive: boolean;
  maintainAspectRatio: boolean;
}

export interface ChartTooltipContext {
  label: string;
  dataset: {
    label: string;
    backgroundColor: string;
    data: number[] | ChartCoordinates[];
  };
  datasetIndex: number;
  dataIndex: number;
  parsed: {
    x: number;
    y: number;
  };
  [key: string]: any;
}

export interface FilterableSelectOption {
  val: string;
  label: string;
  [key: string]: string;
}
