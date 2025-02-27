<template>
  <div class="metricsImpact">
    <div class="metricsImpact__controls">
      <button
        @click.prevent="display('plan')"
        class="pill"
        :class="{ 'pill--active': displayedChart === 'plan' }"
      >
        Per plan
      </button>
      <button
        @click.prevent="display('tag')"
        class="pill"
        :class="{ 'pill--active': displayedChart === 'tag' }"
      >
        Per tag
      </button>
    </div>
    <LoadingPlaceholder v-if="isMounting || isComputing" />
    <p v-else-if="!hasData">We don't have this data yet.</p>
    <div v-else class="metricsImpact__wrapper">
      <Scatter
        v-if="displayedChart === 'plan'"
        :data="planData"
        :options="chartOptions"
      />
      <Scatter
        v-if="displayedChart === 'tag'"
        :data="tagData"
        :options="chartOptions"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, computed } from "vue";
import { useStore } from "@nanostores/vue";
import { Scatter } from "vue-chartjs";
import * as ChartImport from "chart.js";

import { metrics, loadMetrics } from "@/stores/series";
import type {
  ChartTooltipContext,
  ScatterChartData,
  ScatterChartDataSet,
} from "@/types/ui-types";

import LoadingPlaceholder from "@/components/_ui/LoadingPlaceholder.vue";

const { Chart, Tooltip, Legend, PointElement, LineElement, LinearScale } =
  ChartImport;

Chart.register(LinearScale, PointElement, LineElement, Tooltip, Legend);

const isMounting = ref<boolean>(true);
const isComputing = ref<boolean>(false);
const hasPlanData = ref<boolean>(false);
const hasTagData = ref<boolean>(false);
const hasData = computed<boolean>(() => {
  return hasPlanData.value || hasTagData.value;
});
const storedData = useStore(metrics);

const planData = ref<ScatterChartData>({
  labels: [],
  datasets: [],
});

const tagData = ref<ScatterChartData>({
  labels: [],
  datasets: [],
});

async function getData(): Promise<void> {
  await loadMetrics();
}

function computeData() {
  isComputing.value = true;

  if (storedData.value.distributions.impacts.per_plan.length > 0) {
    hasPlanData.value = true;
  }
  if (storedData.value.distributions.impacts.per_tag?.length > 0) {
    hasTagData.value = true;
  }
  if (hasData.value) {
    const pData = storedData.value.distributions.impacts.per_plan;
    const tData = storedData.value.distributions.impacts.per_tag;

    if (hasPlanData.value) {
      pData.forEach((plan) => {
        const score: number =
          plan.deviated + plan.completed === 0
            ? NaN
            : (plan.deviated / (plan.deviated + plan.completed)) * 100;
        let dataset: ScatterChartDataSet = {
          label: plan.plan_title,
          data: [
            {
              x: plan.total,
              y: Number.isNaN(score) ? 0 : score,
            },
          ],
          backgroundColor: "#f3a93c",
        };
        if (Number.isNaN(score)) {
          dataset.backgroundColor = "hsl(285, 92%, 25%)";
        } else if (score <= 30) {
          dataset.backgroundColor = "hsl(137, 57%, 41%)";
        } else if (score >= 70) {
          dataset.backgroundColor = "hsl(0, 79%, 40%)";
        }
        planData.value.datasets.push(dataset);
      });
    }

    if (hasTagData.value) {
      tData.forEach((tag) => {
        const score: number =
          tag.deviated + tag.completed === 0
            ? NaN
            : (tag.deviated / (tag.deviated + tag.completed)) * 100;
        let dataset: ScatterChartDataSet = {
          label: tag.tag,
          data: [
            {
              x: tag.total,
              y: Number.isNaN(score) ? 0 : score,
            },
          ],
          backgroundColor: "#f3a93c",
        };
        if (Number.isNaN(score)) {
          dataset.backgroundColor = "hsl(285, 92%, 25%)";
        } else if (score <= 30) {
          dataset.backgroundColor = "hsl(137, 57%, 41%)";
        } else if (score >= 70) {
          dataset.backgroundColor = "hsl(0, 79%, 40%)";
        }
        tagData.value.datasets.push(dataset);
      });
    }
  }

  isComputing.value = false;
}

watch(storedData, () => computeData());

const displayedChart = ref<string>("plan");
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
        text: "Number of executions",
      },
      min: 0,
      suggestedMax: 10,
      ticks: {
        precision: 0,
      },
    },
    y: {
      title: {
        display: true,
        text: "Deviation percentage",
      },
      afterDataLimits: (scale: any) => {
        scale.max = 100;
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
          context.forEach((ctx) => {
            title.push(ctx.dataset.label);
          });
          return title;
        },
        label: function (context: ChartTooltipContext) {
          const originalData =
            displayedChart.value === "plan"
              ? storedData.value.distributions.impacts.per_plan[
                  context.datasetIndex
                ]
              : storedData.value.distributions.impacts.per_tag[
                  context.datasetIndex
                ];
          return `Total: ${originalData.total}. Deviated: ${
            originalData.deviated
          }. Completed: ${originalData.completed}. Unconclusive: ${
            originalData.total -
            (originalData.completed + originalData.deviated)
          }`;
        },
      },
    },
  },
});

onMounted(async () => {
  isMounting.value = true;
  await getData();
  isMounting.value = false;
});
</script>

<style lang="scss" scoped>
.metricsImpact {
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
