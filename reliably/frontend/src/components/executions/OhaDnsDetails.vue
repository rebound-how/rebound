<template>
  <div class="ohaDnsDetails">
    <h4>DNS Dialup</h4>
    <div class="ohaDnsDetails__chart" v-if="!isLoading">
      <Bar :data="dialupData" :options="chartOptions" />
    </div>
    <h4>DNS Lookup</h4>
    <div class="ohaDnsDetails__chart" v-if="!isLoading">
      <Bar :data="lookupData" :options="chartOptions" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { toRefs, ref, onMounted } from "vue";

import { Bar } from "vue-chartjs";
import * as ChartImport from "chart.js";

import { toFixedIfNecessary } from "@/utils/numbers";

import type { OhaDetails, OhaDetailsDNS } from "@/types/oha";
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
  source: OhaDetails;
}>();

const { source } = toRefs(props);

const isLoading = ref<boolean>(true);

const dialupData = ref<StackBarsChartData>({
  labels: [],
  datasets: [
    {
      label: "DNS Dialup",
      backgroundColor: [
        "hsl(103, 44%, 65%)",
        "hsl(209, 97%, 45%)",
        "hsl(0, 58%, 65%)",
      ],
      data: [],
    },
  ],
});

const lookupData = ref<StackBarsChartData>({
  labels: [],
  datasets: [
    {
      label: "DNS Lookup",
      backgroundColor: [
        "hsl(103, 44%, 65%)",
        "hsl(209, 97%, 45%)",
        "hsl(0, 58%, 65%)",
      ],
      data: [],
    },
  ],
});

const chartOptions = ref({
  responsive: true,
  maintainAspectRatio: false,
  indexAxis: "y",
  barThickness: 20,
  barPercentage: 0.8,
  plugins: {
    legend: {
      display: false,
    },
  },
  scales: {
    x: {
      title: {
        display: true,
        text: "Duration (in seconds)",
      },
    },
    y: {
      min: 0,
    },
  },
});

function setData() {
  const keys: (keyof OhaDetailsDNS)[] = [
    "fastest",
    "average",
    "slowest",
  ] as (keyof OhaDetailsDNS)[];

  keys.forEach((k) => {
    dialupData.value.datasets[0].data.push(source.value.DNSDialup[k]);
    dialupData.value.labels.push(k);

    lookupData.value.datasets[0].data.push(source.value.DNSLookup[k]);
    lookupData.value.labels.push(k);
  });
}

onMounted(() => {
  isLoading.value = true;
  setData();
  isLoading.value = false;
});
</script>

<style lang="scss" scoped>
.ohaDnsDetails {
  h4 {
    margin-top: var(--space-medium);
    margin-bottom: 0;
  }

  &__chart {
    > div {
      height: 20rem;
    }
  }
}
</style>
