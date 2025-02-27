<template>
  <div class="contributionsRadar">
    <LoadingPlaceholder size="fill" v-if="isLoading" />
    <Radar
      v-else-if="hasData"
      :data="chartData"
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
import type { RadarChartData } from "@/types/ui-types";

import { useStore } from "@nanostores/vue";
import { contributionsForRadar, loadContributionsData } from "@/stores/series";

import PieChart from "@/components/svg/PieChart.vue";
import LoadingPlaceholder from "@/components/_ui/LoadingPlaceholder.vue";

import { Radar } from "vue-chartjs";
import * as ChartImport from "chart.js";
const {
  Chart,
  Title,
  Tooltip,
  Legend,
  PointElement,
  RadialLinearScale,
  LineElement,
  Filler,
} = ChartImport;

Chart.register(
  Title,
  Tooltip,
  Legend,
  PointElement,
  RadialLinearScale,
  LineElement,
  Filler
);

const isMounting = ref<boolean>(true);
const hasData = ref<boolean>(false);
const storedData = useStore(contributionsForRadar);
const isLoading = computed(() => {
  return (
    isMounting.value ||
    storedData.value.state === "empty" ||
    storedData.value.state === "loading"
  );
});

const chartData = ref<RadarChartData>({
  labels: [],
  datasets: [
    {
      label: "Contributions",
      backgroundColor: "hsla(16, 68%, 63%, 0.2)",
      borderColor: "hsl(16, 68%, 63%)",
      borderWidth: 2,
      pointBackgroundColor: "hsl(35, 77%, 62%)",
      pointBorderColor: "hsl(16, 68%, 63%)",
      pointHoverBackgroundColor: "hsl(16, 68%, 63%)",
      pointHoverBorderColor: "hsl(16, 68%, 63%)",
      data: [],
    },
  ],
});

async function getData(): Promise<void> {
  await loadContributionsData();
  if (storedData.value.datasets.length === 0) {
    hasData.value = false;
  } else {
    hasData.value = true;
    chartData.value.labels = [...storedData.value.labels];
    chartData.value.datasets[0].data = [...storedData.value.datasets[0].data];
  }
}

const chartOptions = {
  responsive: true,
  scales: {
    r: {
      pointLabels: {
        font: {
          size: 14,
        },
      },
      ticks: {
        display: false,
      },
    },
  },
  fill: true,
  borderWidth: "1",
  plugins: {
    legend: {
      display: false,
    },
    tooltip: {
      displayColors: false,
    },
  },
};

onMounted(async () => {
  isMounting.value = true;
  await getData();
  isMounting.value = false;
});
</script>

<style lang="scss">
.contributionsRadar {
  flex: 1 1 auto;
}
</style>
