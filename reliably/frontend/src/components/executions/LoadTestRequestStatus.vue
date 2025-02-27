<template>
  <div class="loadTestCharts" v-if="!isLoading">
    <div class="failuresPieChart">
      <Pie :data="failuresPieChartData" :options="pieChartOptions" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { toRefs, ref, onMounted } from "vue";

import { Pie } from "vue-chartjs";
import * as ChartImport from "chart.js";

import type { ReliablyLoadTestOutput } from "@/types/executions";
import type { ChartData, SharedChartOptions } from "@/types/ui-types";

const {
  Chart, // Global
  ArcElement, // Pie
  Tooltip, // Shared
  Legend, // Shared
} = ChartImport;

Chart.register(ArcElement, Tooltip, Legend);

const props = defineProps<{
  source: ReliablyLoadTestOutput;
}>();
const { source } = toRefs(props);

const isLoading = ref<boolean>(true);

const failuresPieChartData = ref<ChartData>({
  labels: [],
  datasets: [
    {
      backgroundColor: ["#438458", "#a82921"],
      data: [],
    },
  ],
});

const pieChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
};

function setData() {
  failuresPieChartData.value.labels = ["Success", "Failed"];
  failuresPieChartData.value.datasets[0].data = [
    source.value.num_requests - source.value.num_failures,
    source.value.num_failures,
  ];
}

onMounted(() => {
  isLoading.value = true;
  setData();
  isLoading.value = false;
});
</script>

<style lang="scss" scope>
.failuresPieChart {
  margin-right: auto;
  margin-left: auto;
  max-width: 50%;
}
</style>
