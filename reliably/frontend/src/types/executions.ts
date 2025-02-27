import type { ExperimentDefinition, Action } from "./experiments";

export interface Execution {
  id: string;
  org_id: string;
  experiment_id?: string;
  plan_id?: string;
  created_date: Date | string;
  user_state: {
    current: string;
    duration?: number;
    finished_on?: number;
    status?: string;
    deviated?: boolean;
  } | null;
  result: ExecutionResult;
}

export interface ExecutionResult {
  deviated: boolean;
  status: string;
  experiment: ExperimentDefinition;
  [key: string]: any;
}

export interface ExecutionRollback {
  activity: Action;
  status: "succeeded" | "failed";
  start: string;
  end: string;
  duration: number;
  output: string | null;
  exception?: string | [];
}

export interface ExecutionsApiJsonResponse {
  items: Execution[];
  count: number;
}

export interface ExecutionsPage {
  page: number;
  executions: Execution[];
  total: number;
  isReady: boolean;
}

export interface ExecutionTimelineEvent {
  background?: boolean;
  content?: string | string[];
  date: string;
  details?: any;
  details_type?: string;
  display_resume?: boolean;
  execution_status?:
    | "running"
    | "deviated"
    | "completed"
    | "interrupted"
    | "aborted"
    | "";
  id?: string;
  result_link?: string;
  slack_message_channel?: string;
  slack_message_channel_index?: number;
  slack_message_raw?: SlackMessage;
  slack_message_thread?: number;
  slack_message_user?: SlackUser | undefined;
  status?: string;
  steady_state_met?: boolean;
  subtitle?: string;
  title: string;
  tolerance_met?: boolean;
  type: string;
}

export interface ExecutionDependency {
  name: string;
  version: string;
}

export interface AwsXrayItem {
  id: string;
  name: string;
  aws?: AwsXrayInfo;
  http?: AwsXrayHttp;
  cause?: AwsXrayCause;
  error?: boolean;
  fault?: boolean;
  end_time: number;
  inferred?: boolean;
  metadata?: AwsXrayMetadata;
  namespace?: string;
  parent_id?: string;
  throttle: boolean;
  trace_id: string;
  start_time: number;
  subsegments?: AwsXrayItem[];
}

interface AwsXrayInfo {
  xray: {
    sdk: string;
    sdk_version: string;
    auto_instrumentation: boolean;
  };
}

interface AwsXrayHttp {
  request: AwsXrayHttpRequest;
  response: AwsXrayHttpResponse;
}

interface AwsXrayHttpRequest {
  url: string;
  method: string;
  client_ip: string;
  user_agent: string;
}

interface AwsXrayHttpResponse {
  content_length: number;
}

interface AwsXrayCause {
  exceptions: AwsXrayException[];
}

interface AwsXrayException {
  id: string;
  type: string;
  cause?: string;
  stack: AwsXrayStackItem[];
  message: string;
}

interface AwsXrayStackItem {
  line: number;
  path: string;
  label: string;
}

interface AwsXrayMetadata {
  default: {
    "http.route": string;
    "http.flavor": string;
    "otel.resource.service.name": string;
    "otel.resource.telemetry.sdk.name": string;
    "http.request.header.x_amzn_trace_id": string[];
    "otel.resource.telemetry.sdk.version": string;
    "otel.resource.telemetry.sdk.language": string;
  };
}

export interface ReliablyLoadTestOutput {
  name: string;
  method: string;
  start_time: number;
  num_failures: number;
  num_requests: number;
  response_times: {
    [key: string]: number;
  };
  num_fail_per_sec: {
    [key: string]: number;
  };
  num_reqs_per_sec: {
    [key: string]: number;
  };
  max_response_time: number;
  min_response_time: number;
  num_none_requests: number;
  total_response_time: number;
  total_content_length: number;
  last_request_timestamp: number;
}

export interface SlackUser {
  id: string;
  name: string;
  image: string;
  real_name: string;
  display_name: string;
}

export interface SlackUsers {
  [key: string]: SlackUser;
}

export interface SlackChannel {
  id: string;
  name: string;
  conversation: SlackMessage[];
  threads: {
    [key: string]: SlackMessage[];
  };
}

export interface SlackMessage {
  ts: string;
  team: string;
  text: string;
  type: string;
  user: string;
  app_id: string;
  blocks?: SlackMessageBlock[];
  bot_id?: string;
  is_locked: boolean;
  thread_ts: string;
  subscribed: boolean;
  attachments?: SlackMessageAttachment[];
  bot_profile?: SlackMessageBotProfile;
  reply_count: number;
  reply_users: string[];
  latest_reply: string;
  reply_users_count: number;
  subtype?: string;
}

interface SlackMessageBlock {
  type: string;
  block_id: string;
  elements?: SlackMessageBlockElement[];
  text?: SlackMessageAttachmentBlockText;
  alt_text?: string;
  fallback?: string;
  image_url?: string;
  image_bytes?: number;
  image_width?: number;
  image_height?: number;
  is_animated?: boolean;
}

interface SlackMessageBlockElement {
  type: string;
  style?: {
    [key: string]: boolean;
  };
  text?: string | SlackMessageBlockElement;
  user_id?: string;
  url?: string;
  elements?: SlackMessageBlockElement[];
}

interface SlackMessageAttachment {
  id: string;
  color: string;
  fields?: SlackMessageAttachmentField[];
  blocks?: SlackMessageAttachmentBlock[];
  fallback: string;
}

interface SlackMessageAttachmentField {
  short: boolean;
  title: string;
  value: string;
}

interface SlackMessageAttachmentBlock {
  type: string;
  block_id: string;
  text?: SlackMessageAttachmentBlockText;
  elements?: SlackMessageAttachmentBlockText[];
}

interface SlackMessageAttachmentBlockText {
  text: string;
  type: string;
  verbatim: boolean;
}

export interface SlackMessageBotProfile {
  id: string;
  name: string;
  icons: {
    image_36: string;
    image_48: string;
    image_72: string;
  };
  app_id: string;
  deleted: boolean;
  team_id: string;
  updated: number;
}
