<template>
  <div class="ohaLatencyPercentiles">
    <div class="ohaLatencyPercentiles__chart" v-if="!isLoading">
      <Line :data="chartData" :options="chartOptions" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { toRefs, ref, onMounted } from "vue";

import { Line } from "vue-chartjs";
import * as ChartImport from "chart.js";

import type { OhaLatencyPercentiles } from "@/types/oha";
import type { StackBarsChartData } from "@/types/ui-types";

const {
  Chart,
  CategoryScale,
  TimeScale,
  LinearScale,
  LogarithmicScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} = ChartImport;

Chart.register(
  CategoryScale,
  TimeScale,
  LinearScale,
  LogarithmicScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const props = defineProps<{
  source: {
    all: OhaLatencyPercentiles;
    successful: OhaLatencyPercentiles;
    notSuccessful: OhaLatencyPercentiles;
  };
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
  labels: ["All Requests", "Successful Requests", "Failed Requests"],
  datasets: [],
});

const chartOptions = ref({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: "right",
    },
  },
  scales: {
    y: {
      min: 0,
      type: "logarithmic",
      title: {
        display: true,
        text: "Latency (in seconds)",
      },
    },
  },
});

function setData() {
  const keys: (keyof OhaLatencyPercentiles)[] = (
    Object.keys(source.value.all) as (keyof OhaLatencyPercentiles)[]
  ).sort();

  keys.forEach((k, index) => {
    let dataset = {
      label: k,
      fill: true,
      backgroundColor: COLORS[index],
      borderColor: COLORS[index],
      data: [
        source.value.all[k],
        source.value.successful[k],
        source.value.notSuccessful[k],
      ],
    };
    chartData.value.datasets.push(dataset);
  });
}

onMounted(() => {
  isLoading.value = true;
  setData();
  isLoading.value = false;
});
</script>

<style lang="scss" scoped>
.ohaLatencyPercentiles {
  &__chart {
    margin-top: var(--space-medium);
    max-height: 40rem;
  }
}
</style>
