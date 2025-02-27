<template>
  <div class="executionsScatter">
    <Line
      v-if="hasData"
      :data="(storedData as any)"
      :options="chartOptions"
    />
    <div class="emptyChart" v-else>
      <PieChart />
      <p>
        You have no executions yet, or your experiments don't declare
        contributions. <a href="/experiments/new/">Create an experiment</a> or
        <a
          href="https://reliably.com/docs/"
          target="_blank"
          rel="noopener noreferer"
          >read the docs about contributions</a
        >.
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";

import { useStore } from "@nanostores/vue";
import {
  contributionsForTimeline,
  loadContributionsData,
} from "@/stores/series";

import dayjs from "dayjs";

import PieChart from "@/components/svg/PieChart.vue";

import * as ChartImport from "chart.js";
import "chartjs-adapter-dayjs-3";
import { Line } from "vue-chartjs";
const {
  Chart,
  Title,
  Tooltip,
  Legend,
  LinearScale,
  TimeScale,
  PointElement,
  LineElement,
} = ChartImport;
if (typeof window !== "undefined") {
  (async () => {
    const { default: zoomPlugin } = await import("chartjs-plugin-zoom");
    Chart.register(zoomPlugin);
  })();
}

Chart.register(
  Title,
  Tooltip,
  Legend,
  LinearScale,
  TimeScale,
  PointElement,
  LineElement
);

const isLoading = ref<boolean>(true);
const storedData = useStore(contributionsForTimeline);
const hasData = computed<boolean>(() => {
  return storedData.value.datasets.length > 0;
});

const startingPoint = computed<string>(() => {
  return dayjs(storedData.value.labels[storedData.value.labels.length - 1])
    .subtract(6, "days")
    .startOf("day")
    .format("YYYY-MM-DD HH:mm:ss");
});
const endingPoint = computed<string>(() => {
  return dayjs(storedData.value.labels[storedData.value.labels.length - 1])
    .endOf("day")
    .format("YYYY-MM-DD HH:mm:ss");
});

const chartOptions = ref({
  type: "line",
  showLine: false, // disable for all datasets
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    x: {
      type: "time",
      time: {
        unit: "day",
        displayFormats: {
          day: "DD MMM.",
        },
      },
      min: startingPoint,
      max: endingPoint,
      ticks: {
        align: "center",
        labelOffset: 84,
      },
    },
    y: {
      ticks: {
        beginAtZero: true,
        min: 0,
        max: 3,
        callback: function (value: number) {
          if (!Number.isInteger(value)) {
            return null;
          } else {
            if (value === 3) {
              return "High";
            } else if (value === 2) {
              return "Medium";
            } else if (value === 1) {
              return "Low";
            } else {
              return "None";
            }
          }
        },
      },
    },
  },
  plugins: {
    legend: {
      display: true,
      labels: {
        usePointStyle: true,
        pointStyle: "circle",
      },
    },
    zoom: {
      zoom: {
        wheel: {
          enabled: false,
        },
        pinch: {
          enabled: false,
        },
      },
      pan: {
        enabled: true,
        mode: "x",
        threshold: 10,
      },
    },
  },
});

onMounted(async () => {
  isLoading.value = true;
  await loadContributionsData();
  isLoading.value = false;
});
</script>

<style lang="scss" scoped>
.executionsStack {
  height: 44rem;
  padding: var(--space-small);

  background-color: var(--section-background);
  border-radius: var(--border-radius-s);
}
</style>
