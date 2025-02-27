<template>
  <div class="ohaRps">
    <table class="ohaRps__table">
      <tr class="ohaSummary__row ohaSummary__row--max">
        <th scope="row">Max</th>
        <td>{{ toFixedIfNecessary(source.max, 4) }} rps</td>
      </tr>
      <tr class="ohaSummary__row ohaSummary__row--mean">
        <th scope="row">Mean</th>
        <td>{{ toFixedIfNecessary(source.mean, 4) }} rps</td>
      </tr>
      <tr class="ohaSummary__row ohaSummary__row--stddev">
        <th scope="row">Standard deviation</th>
        <td>{{ toFixedIfNecessary(source.stddev, 4) }} rps</td>
      </tr>
    </table>
    <div class="ohaRps__chart" v-if="!isLoading">
      <Bar :data="chartData" :options="chartOptions" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { toRefs, ref, onMounted } from "vue";

import { Bar } from "vue-chartjs";
import * as ChartImport from "chart.js";

import { toFixedIfNecessary } from "@/utils/numbers";

import type { OhaRps, OhaRpsPercentiles } from "@/types/oha";
import type { StackBarsChartData } from "@/types/ui-types";

const {
  Chart, // Global
  CategoryScale, // Bar
  LinearScale, // Bar
  LogarithmicScale,
  BarElement, // Bar
  Tooltip, // Shared
  Legend, // Shared
} = ChartImport;

Chart.register(
  CategoryScale,
  LinearScale,
  LogarithmicScale,
  BarElement,
  Tooltip,
  Legend
);

const props = defineProps<{
  source: OhaRps;
}>();

const { source } = toRefs(props);

const isLoading = ref<boolean>(true);
const COLORS: string[] = [
  "#a6f19b",
  "#9beebf",
  "#91ecea",
  "#82cfe3",
  "#72b0d8",
  "#6590da",
  "#556dcf",
  "#7f59db",
  "#a84ec4",
];

const chartData = ref<StackBarsChartData>({
  labels: ["Percentile"],
  datasets: [],
});

const chartOptions = ref({
  responsive: true,
  maintainAspectRatio: false,
  indexAxis: "y",
  barThickness: 20,
  barPercentage: 0.8,
  plugins: {
    legend: {
      position: "bottom",
      labels: {
        boxWidth: 15,
      },
    },
  },
  scales: {
    x: {
      title: {
        display: true,
        text: "Requests/second",
      },
      type: "logarithmic",
    },
    y: {
      display: "true",
      min: 0,
    },
  },
});

function setData() {
  const keys: (keyof OhaRpsPercentiles)[] = (
    Object.keys(source.value.percentiles) as (keyof OhaRpsPercentiles)[]
  ).sort();

  keys.forEach((k, index) => {
    // chartData.value.datasets[0].data.push(source.value.percentiles[k]);
    // chartData.value.labels.push(k);
    chartData.value.datasets.push({
      label: k,
      backgroundColor: [COLORS[index]],
      data: [source.value.percentiles[k]],
    });
  });
}

onMounted(() => {
  isLoading.value = true;
  setData();
  isLoading.value = false;
});
</script>

<style lang="scss" scoped>
.ohaRps {
  &__table {
    margin-top: var(--space-small);

    th {
      &[scope="row"] {
        padding-left: 0;

        font-weight: 500;
      }
    }

    td {
      padding-left: var(--space-small);

      font-variant-numeric: tabular-nums;
    }
  }

  &__chart {
    margin-top: var(--space-medium);

    > div {
      height: 30rem;
    }
  }
}
</style>
