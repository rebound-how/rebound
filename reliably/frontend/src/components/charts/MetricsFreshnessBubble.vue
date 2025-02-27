<template>
  <div class="metricsScore">
    <div class="metricsScore__controls">
      <button
        @click.prevent="display('experiment')"
        class="pill"
        :class="{ 'pill--active': displayedChart === 'experiment' }"
      >
        Per experiment
      </button>
      <button
        @click.prevent="display('plan')"
        class="pill"
        :class="{ 'pill--active': displayedChart === 'plan' }"
      >
        Per plan
      </button>
    </div>
    <LoadingPlaceholder v-if="isMounting || isComputing" />
    <p v-else-if="!hasData">We don't have this data yet.</p>
    <div v-else class="metricsScore__wrapper">
      <Bubble
        v-if="displayedChart === 'experiment'"
        :data="experimentData"
        :options="chartOptions"
      />
      <Bubble
        v-if="displayedChart === 'plan'"
        :data="experimentData"
        :options="chartOptions"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, computed } from "vue";
import { useStore } from "@nanostores/vue";
import { Bubble } from "vue-chartjs";
import * as ChartImport from "chart.js";

import { metrics, loadMetrics } from "@/stores/series";
import type {
  ChartTooltipContext,
  BubbleChartData,
  BubbleChartCoordinates,
} from "@/types/ui-types";

import LoadingPlaceholder from "@/components/_ui/LoadingPlaceholder.vue";

const { Chart, Tooltip, Legend, PointElement, LinearScale } = ChartImport;

Chart.register(Tooltip, Tooltip, Legend, PointElement, LinearScale);

const isMounting = ref<boolean>(true);
const isComputing = ref<boolean>(false);
const hasExperimentData = ref<boolean>(false);
const hasPlanData = ref<boolean>(false);
const hasData = computed<boolean>(() => {
  return hasExperimentData.value || hasPlanData.value;
});
const storedData = useStore(metrics);

const experimentData = ref<BubbleChartData>({
  labels: [],
  datasets: [
    {
      label: "A",
      data: [],
      backgroundColor: "hsl(120, 42%, 53%)",
    },
    {
      label: "B",
      data: [],
      backgroundColor: "hsl(56, 91%, 49%)",
    },
    {
      label: "C",
      data: [],
      backgroundColor: "rgb(255, 165, 0)",
    },
    {
      label: "D",
      data: [],
      backgroundColor: "rgb(255, 60, 88)",
    },
  ],
});
const experimentTitles = ref<Array<string[]>>([[], [], [], []]);
const experimentExecutions = ref<Array<number[]>>([[], [], [], []]);

const planData = ref<BubbleChartData>({
  labels: [],
  datasets: [
    {
      label: "A",
      data: [],
      backgroundColor: "hsl(120, 42%, 53%)",
    },
    {
      label: "B",
      data: [],
      backgroundColor: "hsl(56, 91%, 49%)",
    },
    {
      label: "C",
      data: [],
      backgroundColor: "rgb(255, 165, 0)",
    },
    {
      label: "D",
      data: [],
      backgroundColor: "rgb(255, 60, 88)",
    },
  ],
});
const planTitles = ref<Array<string[]>>([[], [], [], []]);
const planExecutions = ref<Array<number[]>>([[], [], [], []]);

async function getData(): Promise<void> {
  await loadMetrics();
}

function computeData() {
  isComputing.value = true;

  if (storedData.value.distributions.scores.per_experiment.length > 0) {
    hasExperimentData.value = true;
  }
  if (storedData.value.distributions.scores.per_plan.length > 0) {
    hasPlanData.value = true;
  }
  if (hasData.value) {
    const eData = storedData.value.distributions.scores.per_experiment;
    const pData = storedData.value.distributions.scores.per_plan;

    let maxExperimentExecutions: number = 0;
    let maxPlanExecutions: number = 0;
    eData.forEach((experiment) => {
      if (experiment.execution_count > maxExperimentExecutions) {
        maxExperimentExecutions = experiment.execution_count;
      }
    });
    pData.forEach((plan) => {
      if (plan.execution_count > maxPlanExecutions) {
        maxPlanExecutions = plan.execution_count;
      }
    });

    if (hasExperimentData.value) {
      eData.forEach((experiment) => {
        if (experiment.score >= 0.9) {
          experimentData.value.datasets[0].data.push({
            x: experiment.freshness,
            y: experiment.score,
            r: executionCountToRadius(
              experiment.execution_count,
              maxExperimentExecutions
            ),
          });
          experimentTitles.value[0].push(experiment.experiment_title);
          experimentExecutions.value[0].push(experiment.execution_count);
        } else if (experiment.score >= 0.7) {
          experimentData.value.datasets[1].data.push({
            x: experiment.freshness,
            y: experiment.score,
            r: executionCountToRadius(
              experiment.execution_count,
              maxExperimentExecutions
            ),
          });
          experimentTitles.value[1].push(experiment.experiment_title);
          experimentExecutions.value[1].push(experiment.execution_count);
        } else if (experiment.score >= 0.5) {
          experimentData.value.datasets[2].data.push({
            x: experiment.freshness,
            y: experiment.score,
            r: executionCountToRadius(
              experiment.execution_count,
              maxExperimentExecutions
            ),
          });
          experimentTitles.value[2].push(experiment.experiment_title);
          experimentExecutions.value[2].push(experiment.execution_count);
        } else {
          experimentData.value.datasets[3].data.push({
            x: experiment.freshness,
            y: experiment.score,
            r: executionCountToRadius(
              experiment.execution_count,
              maxExperimentExecutions
            ),
          });
          experimentTitles.value[3].push(experiment.experiment_title);
          experimentExecutions.value[3].push(experiment.execution_count);
        }
      });
    }

    if (hasPlanData.value) {
      pData.forEach((plan) => {
        const p: string = plan.plan_title ? plan.plan_title : plan.plan_id;
        if (plan.score >= 0.9) {
          planData.value.datasets[0].data.push({
            x: plan.freshness,
            y: plan.score,
            r: 2 * plan.execution_count,
          });
          planTitles.value[0].push(p);
          planExecutions.value[0].push(plan.execution_count);
        } else if (plan.score >= 0.7) {
          planData.value.datasets[1].data.push({
            x: plan.freshness,
            y: plan.score,
            r: executionCountToRadius(plan.execution_count, maxPlanExecutions),
          });
          planTitles.value[1].push(p);
          planExecutions.value[1].push(plan.execution_count);
        } else if (plan.score >= 0.5) {
          planData.value.datasets[2].data.push({
            x: plan.freshness,
            y: plan.score,
            r: executionCountToRadius(plan.execution_count, maxPlanExecutions),
          });
          planTitles.value[2].push(p);
          planExecutions.value[2].push(plan.execution_count);
        } else {
          planData.value.datasets[3].data.push({
            x: plan.freshness,
            y: plan.score,
            r: executionCountToRadius(plan.execution_count, maxPlanExecutions),
          });
          planTitles.value[3].push(p);
          planExecutions.value[3].push(plan.execution_count);
        }
      });
    }
  }

  isComputing.value = false;
}

watch(storedData, () => computeData());

const displayedChart = ref<string>("experiment");
function display(data: string) {
  displayedChart.value = data;
}

const chartOptions = ref({
  responsive: true,
  maintainAspectRatio: false,
  pointRadius: 6,
  scales: {
    x: {
      title: {
        display: true,
        text: "Freshness",
      },
      suggestedMin: -10,
      suggestedMax: 110,
      // grid: {
      //   display: false,
      // },
      ticks: {
        precision: 0,
        stepSize: 10,
        callback: function (value: number, index: number) {
          if (value === 90) {
            return "Fresh";
          } else if (value === 70) {
            return "Good";
          } else if (value === 40) {
            return "Old";
          } else if (value === 10) {
            return "Too old";
          } else {
            return "";
          }
        },
        font: {
          weight: "bold",
        },
        color: (c: {
          index: number;
          tick: { value: number; label: string };
          type: "tick";
        }) => {
          if (c.tick.label === "Fresh") {
            return "hsl(124, 32%, 48%)";
          } else if (c.tick.label === "Good") {
            return "hsl(56, 94%, 40%)";
          } else if (c.tick.label === "Old") {
            return "rgb(255, 165, 0)";
          } else if (c.tick.label === "Too old") {
            return "hsl(0, 79%, 40%)";
          }
        },
      },
      afterDataLimits: (scale: any) => {
        scale.max = 100;
        scale.min = 0;
      },
    },
    y: {
      title: {
        display: true,
        text: "Score",
      },
      ticks: {
        precision: 1,
        labelOffset: 12,
        callback: function (value: number, index: number) {
          if (value === 1) {
            return "A";
          } else if (value === 0.9) {
            return "B";
          } else if (value === 0.7) {
            return "C";
          } else if (value === 0.5) {
            return "D";
          }
        },
      },
      afterDataLimits: (scale: any) => {
        scale.max = 1;
        scale.min = 0;
      },
    },
  },
  plugins: {
    legend: {
      display: false,
    },
    tooltip: {
      callbacks: {
        title: function (context: ChartTooltipContext[]) {
          const title: string[] = [];
          const titles: Array<string[]> =
            displayedChart.value === "experiment"
              ? experimentTitles.value
              : planTitles.value;
          context.forEach((ctx) => {
            const datasetIndex: number = ctx.datasetIndex;
            const index: number = ctx.dataIndex;
            title.push(titles[datasetIndex][index]);
          });
          return title;
        },
        label: function (context: ChartTooltipContext) {
          const d: BubbleChartCoordinates = context.dataset.data[
            context.dataIndex
          ] as BubbleChartCoordinates;
          const score: string = scoreNumberToLetter(d.y);
          const freshness: string = `${d.x.toString()}%`;
          const executions: Array<number[]> =
            displayedChart.value === "experiment"
              ? experimentExecutions.value
              : planExecutions.value;
          const datasetIndex: number = context.datasetIndex;
          const index: number = context.dataIndex;
          const count: string = executions[datasetIndex][index].toString();
          return `Score: ${score}. Freshness: ${freshness}. Executions: ${count}`;
        },
      },
    },
  },
});

// Helpers
function executionCountToRadius(count: number, max: number): number {
  if (count > 0.9 * max) {
    return 14;
  } else if (count > 0.8 * max) {
    return 13;
  } else if (count > 0.7 * max) {
    return 12;
  } else if (count > 0.6 * max) {
    return 11;
  } else if (count > 0.5 * max) {
    return 10;
  } else if (count > 0.4 * max) {
    return 9;
  } else if (count > 0.3 * max) {
    return 8;
  } else if (count > 0.2 * max) {
    return 7;
  } else if (count > 0.1 * max) {
    return 6;
  } else {
    return 5;
  }
}

function scoreNumberToLetter(score: number): string {
  if (score >= 0.9) {
    return "A";
  } else if (score >= 0.7) {
    return "B";
  } else if (score >= 0.5) {
    return "C";
  } else {
    return "D";
  }
}

onMounted(async () => {
  isMounting.value = true;
  await getData();
  isMounting.value = false;
});
</script>

<style lang="scss" scoped>
.metricsScore {
  margin-top: var(--space-small);

  &__wrapper {
    height: 27rem;

    > div {
      max-height: 100%;
    }
  }

  &__controls {
    display: flex;
    justify-content: center;
    gap: var(--space-small);
    margin-bottom: var(--space-small);
  }
}
</style>
