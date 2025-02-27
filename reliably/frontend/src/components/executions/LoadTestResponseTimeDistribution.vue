<template>
  <div class="loadTestCharts" v-if="!isLoading">
    <div class="distributionBarChart">
      <Bar
        :data="distributionBarChartData"
        :options="distributionBarChartOptions"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { toRefs, ref, onMounted } from "vue";

import { Bar } from "vue-chartjs";
import * as ChartImport from "chart.js";

import type { ReliablyLoadTestOutput } from "@/types/executions";
import type { StackBarsChartData } from "@/types/ui-types";

const {
  Chart, // Global
  CategoryScale, // Bar
  LinearScale, // Bar
  BarElement, // Bar
  Tooltip, // Shared
  Legend, // Shared
} = ChartImport;

Chart.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend);

const props = defineProps<{
  source: ReliablyLoadTestOutput;
}>();
const { source } = toRefs(props);

const isLoading = ref<boolean>(true);

const distributionBarChartData = ref<StackBarsChartData>({
  labels: [],
  datasets: [
    {
      label: "Number of requests per response duration",
      backgroundColor: "#1c4e94",
      data: [],
    },
  ],
});

const distributionBarChartOptions = ref({
  responsive: true,
  maintainAspectRatio: false,
});

function setData() {
  const durations = Object.keys(source.value.response_times);
  durations.forEach((d) => {
    distributionBarChartData.value.labels.push(parseInt(d).toString());
    distributionBarChartData.value.datasets[0].data.push(
      source.value.response_times[d]
    );
  });
}

onMounted(() => {
  isLoading.value = true;
  setData();
  isLoading.value = false;
});
</script>
