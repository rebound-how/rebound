<template>
  <div class="ohaResponseTimeHistogram">
    <select v-model="dataType" @change="updateChartData">
      <option value="all">All requests</option>
      <option value="successful">Only successful requests</option>
      <option value="notSuccessful">Only failed requests</option>
    </select>
    <div class="ohaResponseTimeHistogram__chart" v-if="!isLoading">
      <Bar :data="chartData" :options="chartOptions" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { toRefs, ref, onMounted } from "vue";

import { Bar } from "vue-chartjs";
import * as ChartImport from "chart.js";

import { toFixedIfNecessary } from "@/utils/numbers";

import type { OhaResponseTimeHistogram } from "@/types/oha";
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
  source: {
    all: OhaResponseTimeHistogram;
    successful: OhaResponseTimeHistogram;
    notSuccessful: OhaResponseTimeHistogram;
  };
}>();

const { source } = toRefs(props);

const isLoading = ref<boolean>(true);
const dataType = ref<"all" | "successful" | "notSuccessful">("all");
const upperBound = ref<number>(0);

const chartData = ref<StackBarsChartData>({
  labels: [],
  datasets: [
    {
      label: "",
      backgroundColor: [],
      data: [],
    },
  ],
});

const chartDataAll = ref<StackBarsChartData>({
  labels: [],
  datasets: [
    {
      label: "",
      backgroundColor: [],
      data: [],
    },
  ],
});

const chartDataSuccessful = ref<StackBarsChartData>({
  labels: [],
  datasets: [
    {
      label: "",
      backgroundColor: [],
      data: [],
    },
  ],
});

const chartDataNotSuccessful = ref<StackBarsChartData>({
  labels: [],
  datasets: [
    {
      label: "",
      backgroundColor: [],
      data: [],
    },
  ],
});

const chartOptions = ref({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false,
      position: "bottom",
    },
  },
  scales: {
    y: {
      min: 0,
      max: 80,
    },
  },
});

function setData() {
  // const dataKeys = Object.keys(source.value);
  const dataKeys: ["all", "successful", "notSuccessful"] = [
    "all",
    "successful",
    "notSuccessful",
  ];

  dataKeys.forEach((d) => {
    const orderedKeys = Object.keys(source.value[d]).sort();
    const goodBound = Math.ceil(orderedKeys.length / 4);
    const badBound = orderedKeys.length - goodBound;
    let counter: number = 1;
    orderedKeys.forEach((k) => {
      const formatedKey: string = toFixedIfNecessary(
        parseFloat(k || "0"),
        3
      ).toString();
      const val: number = source.value[d][k];
      chartData.value.datasets[0].data.push(val);
      chartData.value.labels.push(formatedKey);

      if (val > upperBound.value) {
        upperBound.value = Math.ceil(val / 10) * 10;
      }

      if (counter <= goodBound) {
        (chartData.value.datasets[0].backgroundColor! as string[]).push(
          "hsl(103, 44%, 65%)"
        );
      } else if (counter > badBound) {
        (chartData.value.datasets[0].backgroundColor! as string[]).push(
          "hsl(0, 58%, 65%)"
        );
      } else {
        (chartData.value.datasets[0].backgroundColor! as string[]).push(
          "hsl(39, 76%, 66%)"
        );
      }

      counter++;
    });

    if (d === "all") {
      chartDataAll.value = chartData.value;
    } else if (d === "successful") {
      chartDataSuccessful.value = chartData.value;
    } else if (d === "notSuccessful") {
      chartDataNotSuccessful.value = chartData.value;
    }

    chartData.value = {
      labels: [],
      datasets: [
        {
          label: "",
          backgroundColor: [],
          data: [],
        },
      ],
    };
  });
}

function updateChartData() {
  if (dataType.value === "all") {
    chartData.value = chartDataAll.value;
  } else if (dataType.value === "successful") {
    chartData.value = chartDataSuccessful.value;
  } else if (dataType.value === "notSuccessful") {
    chartData.value = chartDataNotSuccessful.value;
  }
}

onMounted(() => {
  isLoading.value = true;
  setData();
  chartData.value = chartDataAll.value;
  chartOptions.value.scales.y.max = upperBound.value;
  isLoading.value = false;
});
</script>

<style lang="scss" scoped>
.ohaResponseTimeHistogram {
  &__chart {
    margin-top: var(--space-medium);
    max-height: 40rem;
  }
}
</style>
