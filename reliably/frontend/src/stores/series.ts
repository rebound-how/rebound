import { map } from "nanostores";

import { useStore } from "@nanostores/vue";
import { organizationToken } from "../stores/user";
import { increaseLoaderCounter, decreaseLoaderCounter } from "../stores/loader";
import { addNotification } from "../stores/notifications";
import { contributionToNumber } from "@/utils/contributions";
import { hasProp } from "@/utils/objects";
import { handleError403 } from "../utils/user";

import type {
  SeriesContributionsForRadar,
  SeriesContributionsForRadarDataset,
  SeriesContributionsForTimeline,
  SeriesContributionsForTimelineDataset,
  SeriesExecutionsForMatrixPayload,
  SeriesExecutionsForMatrix,
  SeriesExecutionsForMatrixWeek,
  SeriesExecutionsForMatrixDataset,
  SeriesContributionsForExecutionsPayload,
  SeriesExecutionsPerExperiment,
  SeriesMetrics,
} from "@/types/series";
import type { Notification } from "@/types/ui-types";

import dayjs from "dayjs";

/* c8 ignore start */
const baseApiUrl: string =
  import.meta.env === undefined
    ? "https://62ff903e9350a1e548e1952e.mockapi.io/api"
    : import.meta.env.PUBLIC_API_URL;
const useMockApi =
  baseApiUrl === "https://62ff903e9350a1e548e1952e.mockapi.io/api";

const cfExpUrl: string = useMockApi
  ? "series-contributions-for-experiments"
  : "series/contributions/for/experiments";
const cfExeUrl: string = useMockApi
  ? "series-contributions-for-executions"
  : "series/contributions/for/executions";
const ExePExpUrl: string = useMockApi
  ? "series-executions-per-experiment"
  : "series/executions/per/experiment";
const matrixUrl: string = useMockApi
  ? "series-executions-calendar"
  : "series/executions/calendar";
const execMetricsUrl: string = useMockApi
  ? "series-executions-metrics/1"
  : "series/executions/metrics";
/* c8 ignore stop */

const context = useStore(organizationToken);

// Timeline Colors
const colorsCerulean = [
  "rgb(174, 218, 225)",
  "rgb(139, 201, 212)",
  "rgb(104, 185, 199)",
  "rgb(69, 169, 186)",
  "rgb(34, 153, 173)",
  "rgb(2, 136, 159)",
];

const colorsRose = [
  "rgb(252, 215, 234)",
  "rgb(251, 198, 224)",
  "rgb(250, 180, 215)",
  "rgb(248, 163, 206)",
  "rgb(247, 146, 197)",
  "rgb(243, 129, 186)",
];

const colorsMagma = [
  "rgb(254, 215, 184)",
  "rgb(254, 197, 154)",
  "rgb(253, 180, 123)",
  "rgb(253, 162, 93)",
  "rgb(252, 145, 62)",
  "rgb(249, 128, 34)",
];

const colorsPurple = [
  "rgb(247, 181, 235)",
  "rgb(243, 149, 227)",
  "rgb(239, 117, 218)",
  "rgb(236, 85, 209)",
  "rgb(232, 53, 201)",
  "rgb(227, 23, 191)",
];

const timelineColors = [colorsCerulean, colorsRose, colorsMagma, colorsPurple];

// Contributions for Experiments
export const contributionsForExperiments = map<SeriesContributionsForRadar>({
  labels: [],
  datasets: [],
  state: "empty",
});

export async function updateCfExp(data: SeriesContributionsForRadar) {
  contributionsForExperiments.set(data);
  return contributionsForExperiments.get();
};

const fetchCfExp = async () => {
  contributionsForExperiments.setKey("state", "loading");
  const url = `${baseApiUrl}/organization/${context.value}/${cfExpUrl}`;
  try {
    const response = await fetch(url);
    if (response.status === 403) {
      handleError403(context.value);
    } else if (!response.ok) {
      throw new Error(response.statusText);
    } else {
      const json: SeriesContributionsForRadar = await response.json();
      let data: SeriesContributionsForRadar = {
        labels: json.labels,
        datasets: json.datasets,
        state: "ready",
      };
      updateCfExp(data);
    }
  } catch (e) {
    const n: Notification = {
      title: "Contributions couldn't be fetched",
      message: (e as Error).message,
      type: "error",
    };
    addNotification(n);
    contributionsForExperiments.setKey("state", "error");
  }
};

// This is the method to call from components
export const loadCfExp = async () => {
  increaseLoaderCounter();
  let currentCfExp: SeriesContributionsForRadar =
    contributionsForExperiments.get();
  /* c8 ignore start */
  // I'll find out how to test this later ;)
  if (currentCfExp.state === "loading") {
    // Do nothing.
    // All components expecting data will be updated when stats are ready
    decreaseLoaderCounter();
    return;
  }
  /* c8 ignore stop */
  try {
    await fetchCfExp();
  } finally {
    decreaseLoaderCounter();
  }
};
// End Contributions for Experiments

// Contributions for Executions (Radar)
export const contributionsForRadar = map<SeriesContributionsForRadar>({
  labels: [],
  datasets: [],
  state: "empty",
});

export async function updateContributionsForRadar(data: SeriesContributionsForRadar) {
  contributionsForRadar.set(data);
  return contributionsForRadar.get();
};

// Contributions for Executions (Timeline)
export const contributionsForTimeline = map<SeriesContributionsForTimeline>({
  labels: [],
  datasets: [],
  state: "empty",
});

export async function updateContributionsForTimeline(data: SeriesContributionsForTimeline) {
  contributionsForTimeline.set(data);
  return contributionsForTimeline.get();
};

function setContributionsForRadar(
  json: SeriesContributionsForExecutionsPayload
) {
  let labels: string[] = [];
  let numbers: number[] = [];
  for (const [key, value] of Object.entries(json.experiments)) {
    const c = json.experiments[key].c;
    const x = json.experiments[key].x;
    for (const [key, value] of Object.entries(c)) {
      let indexToUpdate: number = -1;
      const index = labels.findIndex((e) => e === key);
      if (index !== -1) {
        indexToUpdate = index;
      } else {
        labels.push(key);
        numbers.push(0);
        indexToUpdate = labels.length - 1;
      }
      const base = contributionToNumber(value);
      let score = 0;
      if (base !== null) {
        score = base * x.length;
      }
      numbers[indexToUpdate] = numbers[indexToUpdate] + score;
    }
  }
  let data: SeriesContributionsForRadar = {
    labels: labels,
    datasets: [
      {
        data: [...numbers],
      },
    ],
    state: "ready",
  };
  updateContributionsForRadar(data);
}

function setContributionsForTimeline(
  json: SeriesContributionsForExecutionsPayload
) {
  let labels: string[] = [];
  let datasets: SeriesContributionsForTimelineDataset[] = [];
  for (const [key, value] of Object.entries(json.experiments)) {
    const c = json.experiments[key].c;
    const x = json.experiments[key].x;
    for (const execution of x) {
      labels.push(execution[1]);
      for (const [key, value] of Object.entries(c)) {
        let indexToUpdate: number = -1;
        const index = datasets.findIndex((s) => s.label === key);
        if (index !== -1) {
          datasets[index].data.push(contributionToNumber(value)!);
        } else {
          const newDataset: SeriesContributionsForTimelineDataset = {
            label: key,
            backgroundColor: timelineColorPicker(datasets.length),
            borderColor: timelineColorPicker(datasets.length),
            pointRadius: 6,
            pointHoverRadius: 8,
            data: [contributionToNumber(value)!],
          };
          datasets.push(newDataset);
        }
      }
    }
  }
  let data: SeriesContributionsForTimeline = {
    labels: labels,
    datasets: [...datasets],
    state: "ready",
  };
  updateContributionsForTimeline(data);
}

function timelineColorPicker(i: number): string {
  const shade = timelineColors[i % 4];
  const color = shade[Math.floor(i / 4) % 6];
  return color;
}

const fetchCfExe = async () => {
  contributionsForRadar.setKey("state", "loading");
  contributionsForTimeline.setKey("state", "loading");
  const url = `${baseApiUrl}/organization/${context.value}/${cfExeUrl}`;
  try {
    const response = await fetch(url);
    if (response.status === 403) {
      handleError403(context.value);
    } else if (!response.ok) {
      throw new Error(response.statusText);
    } else {
      const json: SeriesContributionsForExecutionsPayload =
        await response.json();
      setContributionsForRadar(json);
      setContributionsForTimeline(json);
    }
  } catch (e) {
    const n: Notification = {
      title: "Contributions couldn't be fetched",
      message: (e as Error).message,
      type: "error",
    };
    addNotification(n);
    contributionsForRadar.setKey("state", "error");
    contributionsForTimeline.setKey("state", "error");
  }
};

// This is the method to call from components
export const loadContributionsData = async () => {
  increaseLoaderCounter();
  let currentContributions: SeriesContributionsForRadar =
    contributionsForRadar.get();
  /* c8 ignore start */
  // I'll find out how to test this later ;)
  if (
    currentContributions.state === "loading" ||
    currentContributions.state === "ready"
  ) {
    // Do nothing.
    // All components expecting data will be updated when stats are ready
    decreaseLoaderCounter();
    return;
  }
  /* c8 ignore stop */
  try {
    await fetchCfExe();
  } finally {
    decreaseLoaderCounter();
  }
};
// End Contributions for Executions

// Executions per day (Matrix)
export const executionsForMatrix = map<SeriesExecutionsForMatrix>({
  data: {
    weeks: [],
    max: 0,
  },
  state: "empty",
});

export async function updateExecutionsForMatrix (data: SeriesExecutionsForMatrix) {
  executionsForMatrix.set(data);
  return executionsForMatrix.get();
};

function setExecutionsForMatrix(json: SeriesExecutionsForMatrixPayload) {
  let dataset: SeriesExecutionsForMatrixDataset = {
    weeks: [],
    max: 0,
  };
  // Set empty matrix
  let max: number = 0;
  const end = dayjs().startOf("day");
  const startOfWeek = end.startOf("week");
  let start = startOfWeek.subtract(6, "months").startOf("week");
  let dt = start;
  let week: SeriesExecutionsForMatrixWeek = {
    days: [],
    month: "",
  };
  let i: number = 0;
  while (dt <= end) {
    const iso = dt.format("YYYY-MM-DD");
    const v: number = hasProp(json, iso) ? json[iso].total : 0;
    max = Math.max(max, v);
    week.days.push({
      dayinweek: (((dt.day() + 6) % 7) + 1).toString(),
      date: iso,
      total: v,
    });
    if (week.month === "") {
      week.month = dayjs(dt).format("MMM");
    }
    i++;
    if (i === 7) {
      dataset.weeks.push(week);
      week = {
        days: [],
        month: "",
      };
      i = 0;
    }
    dt = dt.add(1, "day");
  }
  if (week.days.length) {
    // Add possibly incomplete last week.
    dataset.weeks.push(week);
  }
  dataset.max = max;
  let data: SeriesExecutionsForMatrix = {
    data: dataset,
    state: "ready",
  };
  updateExecutionsForMatrix(data);
}

async function fetchExecutionsMatrix() {
  executionsForMatrix.setKey("state", "loading");
  const url = `${baseApiUrl}/organization/${context.value}/${matrixUrl}`;
  try {
    const response = await fetch(url);
    if (response.status === 403) {
      handleError403(context.value);
    } else if (!response.ok) {
      throw new Error(response.statusText);
    } else {
      const json: SeriesExecutionsForMatrixPayload = await response.json();
      setExecutionsForMatrix(json);
    }
  } catch (e) {
    const n: Notification = {
      title: "Executions couldn't be fetched",
      message: (e as Error).message,
      type: "error",
    };
    addNotification(n);
    executionsForMatrix.setKey("state", "error");
  }
}

// // This is the method to call from components
export const loadExecutionsMatrix = async () => {
  increaseLoaderCounter();
  let currentMatrix: SeriesExecutionsForMatrix = executionsForMatrix.get();
  /* c8 ignore start */
  // I'll find out how to test this later ;)
  if (currentMatrix.state === "loading") {
    // Do nothing.
    // All components expecting data will be updated when stats are ready
    decreaseLoaderCounter();
    return;
  }
  /* c8 ignore stop */
  try {
    await fetchExecutionsMatrix();
  } finally {
    decreaseLoaderCounter();
  }
};
// End executions per day (matrix)

// Executions per Experiment
export const executionsPerExperiment = map<SeriesExecutionsPerExperiment>({
  labels: [],
  datasets: [],
  state: "empty",
});

export async function updateExePExp(data: SeriesExecutionsPerExperiment) {
  executionsPerExperiment.set(data);
  return executionsPerExperiment.get();
};

const fetchExePExp = async (id: string) => {
  executionsPerExperiment.setKey("state", "loading");
  const url = `${baseApiUrl}/organization/${context.value}/${ExePExpUrl}?exp_id=${id}`;
  try {
    const response = await fetch(url);
    if (response.status === 403) {
      handleError403(context.value);
    } else if (!response.ok) {
      throw new Error(response.statusText);
    } else {
      const json: SeriesExecutionsPerExperiment = await response.json();
      let data: SeriesExecutionsPerExperiment = {
        labels: json.labels,
        datasets: json.datasets,
        state: "ready",
      };
      updateExePExp(data);
    }
  } catch (e) {
    const n: Notification = {
      title: "Executions data couldn't be fetched",
      message: (e as Error).message,
      type: "error",
    };
    addNotification(n);
    executionsPerExperiment.setKey("state", "error");
  }
};

// This is the method to call from components
export const loadExePerExp = async (id: string) => {
  increaseLoaderCounter();
  let current: SeriesExecutionsPerExperiment = executionsPerExperiment.get();
  /* c8 ignore start */
  // I'll find out how to test this later ;)
  if (current.state === "loading") {
    // Do nothing.
    // All components expecting data will be updated when stats are ready
    decreaseLoaderCounter();
    return;
  }
  /* c8 ignore stop */
  try {
    await fetchExePExp(id);
  } finally {
    decreaseLoaderCounter();
  }
};
// End Contributions for Experiments

// Metrics
export const metrics = map<SeriesMetrics>({
  distributions: {
    per_user: {
      total: [],
      current_week: [],
    },
    per_period: {
      per_day: [],
      per_week: [],
      per_month: [],
    },
    impacts: {
      per_plan: [],
      per_tag: [],
    },
    scores: {
      per_experiment: [],
      per_plan: [],
    },
  },
  state: "empty",
});

export async function updateMetrics(data: SeriesMetrics) {
  metrics.set(data);
  return metrics.get();
};

const fetchMetrics = async () => {
  metrics.setKey("state", "loading");
  const url = `${baseApiUrl}/organization/${context.value}/${execMetricsUrl}`;
  try {
    const response = await fetch(url);
    if (response.status === 403) {
      handleError403(context.value);
    } else if (!response.ok) {
      throw new Error(response.statusText);
    } else {
      const json: SeriesMetrics = await response.json();
      let data: SeriesMetrics = {
        distributions: json.distributions,
        state: "ready",
      };
      updateMetrics(data);
    }
  } catch (e) {
    const n: Notification = {
      title: "Metrics couldn't be fetched",
      message: (e as Error).message,
      type: "error",
    };
    addNotification(n);
    metrics.setKey("state", "error");
  }
};

// This is the method to call from components
export const loadMetrics = async () => {
  increaseLoaderCounter();
  let current: SeriesMetrics = metrics.get();
  /* c8 ignore start */
  // I'll find out how to test this later ;)
  if (current.state === "loading") {
    // Do nothing.
    // All components expecting data will be updated when stats are ready
    decreaseLoaderCounter();
    return;
  }
  /* c8 ignore stop */
  try {
    await fetchMetrics();
  } finally {
    decreaseLoaderCounter();
  }
};
// End Metrics
