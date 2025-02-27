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
      <div
        v-if="displayedChart === 'plan'"
        :style="`height: ${planData.labels.length * 6}rem`"
      >
        <Bar :data="planData" :options="chartOptions" />
      </div>
      <div
        v-if="displayedChart === 'tag'"
        :style="`height: ${tagData.labels.length * 6}rem`"
      >
        <Bar :data="tagData" :options="chartOptions" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, computed } from "vue";
import { useStore } from "@nanostores/vue";
import { Bar } from "vue-chartjs";
import * as ChartImport from "chart.js";

import { metrics, loadMetrics } from "@/stores/series";
import type { ChartTooltipContext, StackBarsChartData } from "@/types/ui-types";

import LoadingPlaceholder from "@/components/_ui/LoadingPlaceholder.vue";

const { Chart, Tooltip, Legend, BarElement, CategoryScale, LinearScale } =
  ChartImport;

Chart.register(Tooltip, Legend, BarElement, CategoryScale, LinearScale);

const isMounting = ref<boolean>(true);
const isComputing = ref<boolean>(false);
const hasPlanData = ref<boolean>(false);
const hasTagData = ref<boolean>(false);
const hasData = computed<boolean>(() => {
  return hasPlanData.value || hasTagData.value;
});
const storedData = useStore(metrics);

const planData = ref<StackBarsChartData>({
  labels: [],
  datasets: [
    {
      label: "Deviated",
      data: [],
      backgroundColor: "hsl(0, 58%, 65%)",
    },
    {
      label: "Did not finish (failed, interrupted...)",
      data: [],
      backgroundColor: "hsl(234.55, 22.45%, 90.39%)",
    },
    {
      label: "Completed",
      data: [],
      backgroundColor: "hsl(103, 44%, 65%)",
    },
  ],
});

const tagData = ref<StackBarsChartData>({
  labels: [],
  datasets: [
    {
      label: "Deviated",
      data: [],
      backgroundColor: "hsl(0, 58%, 65%)",
    },
    {
      label: "Did not finish (failed, interrupted...)",
      data: [],
      backgroundColor: "hsl(234.55, 22.45%, 90.39%)",
    },
    {
      label: "Completed",
      data: [],
      backgroundColor: "hsl(103, 44%, 65%)",
    },
  ],
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
        planData.value.labels.push(plan.plan_title);
        planData.value.datasets[0].data.push(plan.deviated);
        planData.value.datasets[1].data.push(
          plan.total - (plan.deviated + plan.completed)
        );
        planData.value.datasets[2].data.push(plan.completed);
      });
    }

    if (hasTagData.value) {
      tData.forEach((tag) => {
        tagData.value.labels.push(tag.tag);
        tagData.value.datasets[0].data.push(tag.deviated);
        tagData.value.datasets[1].data.push(
          tag.total - (tag.deviated + tag.completed)
        );
        tagData.value.datasets[2].data.push(tag.completed);
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
  indexAxis: "y",
  maxBarThickness: 12,
  scales: {
    x: {
      stacked: true,
      position: "top",
      ticks: {
        stepSize: 1,
      },
    },
    y: {
      stacked: true,
      grid: {
        display: false,
      },
      ticks: {
        color: "hsl(240, 3.7%, 15.88%)",
        mirror: true,
        labelOffset: -20,
        z: 10,
        callback: function (value: number): string {
          const label: string = (this as any).getLabelForValue(value);
          if (label.length <= 42) {
            return label;
          } else {
            return `${label.substring(0, 39)}...`;
          }
        },
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
          const ctx = context[0];
          let title: string = "";
          const words: string[] = ctx.label.split(" ");
          words.every((word) => {
            if (title.length + word.length < 40) {
              title = `${title} ${word}`;
              return true;
            } else {
              return false;
            }
          });
          if (title === ctx.label) {
            return title;
          } else {
            return `${title}...`;
          }
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
    overflow-y: scroll;

    > div > div {
      height: 100%;
    }

    :deep(canvas) {
      max-width: 100%;
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
