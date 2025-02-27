export interface SeriesContributionsForRadarDataset {
  data: number[];
}

export interface SeriesContributionsForRadar {
  labels: string[];
  datasets: SeriesContributionsForRadarDataset[];
  state?: string;
}

export interface SeriesContributionsForTimelineDataset {
  label: string;
  backgroundColor: string;
  borderColor: string;
  pointRadius: number;
  pointHoverRadius: number;
  data: number[];
}

export interface SeriesContributionsForTimeline {
  labels: string[];
  datasets: SeriesContributionsForTimelineDataset[];
  state?: string;
}

export interface SeriesExecutionsForMatrixPayload {
  [key: string]: {
    deviated: number;
    failed: number;
    completed: number;
    interrupted: number;
    aborted: number;
    total: number;
  };
}

export interface SeriesExecutionsForMatrixDay {
  dayinweek: string;
  date: string;
  total: number;
}

export interface SeriesExecutionsForMatrixWeek {
  days: SeriesExecutionsForMatrixDay[];
  month: string;
}

export interface SeriesExecutionsForMatrixDataset {
  weeks: SeriesExecutionsForMatrixWeek[];
  max: number;
}

export interface SeriesExecutionsForMatrix {
  data: SeriesExecutionsForMatrixDataset;
  state?: string;
}

export interface SeriesContributionsForExecutionsPayload {
  experiments: {
    [key: string]: {
      c: {
        [key: string]: string;
      };
      x: Array<[string, string]>;
    };
  };
}

export interface SeriesExecutionsPerExperimentDataset {
  name: string;
  data: number[];
  kind?: string;
  loc?: string;
  stack: string;
}

export interface SeriesExecutionsPerExperiment {
  labels: string[];
  datasets: SeriesExecutionsPerExperimentDataset[];
  state?: string;
}

export interface SeriesMetrics {
  distributions: {
    per_user: {
      total: SeriesMetricsUserTotal[];
      current_week: SeriesMetricsUserWeek[];
    };
    per_period: {
      per_day: SeriesMetricsPeriod[];
      per_week: SeriesMetricsPeriod[];
      per_month: SeriesMetricsPeriod[];
    };
    impacts: {
      per_plan: SeriesPlanImpact[];
      per_tag: SeriesTagImpact[];
    };
    scores: {
      per_experiment: SeriesExperimentScore[];
      per_plan: SeriesPlanScore[];
    };
  };
  state?: string;
}

export interface SeriesMetricsUserTotal {
  user_id: string;
  username: string;
  count: number;
}

export interface SeriesMetricsUserWeek {
  user_id: string;
  username: string;
  execution_id: string;
  started_on: string;
  status:
    | "deviated"
    | "completed"
    | "interrupted"
    | "aborted"
    | "pause"
    | "running"
    | "failed";
  deviated: boolean;
  plan_title: string;
  plan_id: string;
  experiment_id: string;
  duration: number;
}

export interface SeriesMetricsPeriod {
  day?: string;
  week?: string;
  month?: string;
  count: number;
}

export interface SeriesPlanImpact {
  plan_id: string;
  plan_title: string;
  total: number;
  deviated: number;
  completed: number;
}

export interface SeriesTagImpact {
  tag: string;
  total: number;
  deviated: number;
  completed: number;
}

export interface SeriesPlanImpact {
  plan_id: string;
  plan_title: string;
  total: number;
  deviated: number;
  completed: number;
}

export interface SeriesExperimentScore {
  experiment_id: string;
  experiment_title: string;
  execution_count: number;
  freshness: number;
  score: number;
}

export interface SeriesPlanScore {
  plan_id: string;
  plan_title: string | null;
  execution_count: number;
  freshness: number;
  score: number;
}
