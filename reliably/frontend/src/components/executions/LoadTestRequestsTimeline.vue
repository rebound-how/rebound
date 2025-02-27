<template>
  <div class="loadTestCharts" v-if="!isLoading">
    <div class="timelineBarChart">
      <Bar
        :data="timelineBarChartData"
        :options="timelineBarChartOptions"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { toRefs, ref, onMounted } from "vue";

import { Pie, Bar } from "vue-chartjs";
import * as ChartImport from "chart.js";
import "chartjs-adapter-dayjs-3";
import dayjs from "dayjs";

import type { ReliablyLoadTestOutput } from "@/types/executions";
import type {
  ChartData,
  StackBarsChartData,
  SharedChartOptions,
} from "@/types/ui-types";

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

const timelineBarChartData = ref<StackBarsChartData>({
  labels: [],
  datasets: [
    {
      label: "Successful requests",
      backgroundColor: "#438458",
      data: [],
    },
    {
      label: "Failed requests",
      backgroundColor: "#a82921",
      data: [],
    },
  ],
});

const timelineBarChartOptions = ref({
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    x: {
      type: "time",
      time: {
        unit: "second",
        displayFormats: {
          day: "H:M:S",
        },
      },
      // min: startingPoint,
      // max: endingPoint,
      ticks: {
        align: "center",
        labelOffset: 84,
      },
    },
    y: {
      stacked: true,
    },
  },
  plugins: {
    legend: {
      display: false,
    },
  },
});

function setData() {
  const ts = Object.keys(source.value.num_reqs_per_sec);
  ts.forEach((t: string) => {
    timelineBarChartData.value.labels.push(
      dayjs(parseInt(t) * 1000).format("HH:mm:ss")
    );

    if (source.value.num_fail_per_sec[t]) {
      timelineBarChartData.value.datasets[0].data.push(
        source.value.num_reqs_per_sec[t] - source.value.num_fail_per_sec[t]
      );
      timelineBarChartData.value.datasets[1].data.push(
        source.value.num_fail_per_sec[t]
      );
    } else {
      timelineBarChartData.value.datasets[0].data.push(
        source.value.num_reqs_per_sec[t]
      );
      timelineBarChartData.value.datasets[1].data.push(0);
    }
  });
}

onMounted(() => {
  isLoading.value = true;
  setData();
  isLoading.value = false;
});
</script>
