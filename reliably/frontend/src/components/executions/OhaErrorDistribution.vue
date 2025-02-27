<template>
  <div class="ohaErrorDistribution">
    <div class="ohaErrorDistribution__chart" v-if="!isLoading">
      <p v-if="totalErrors === 0" class="text-center">
        No errors detected during load test
      </p>
      <Pie v-else :data="pieData" :options="pieOptions" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { toRefs, ref, onMounted } from "vue";
import { Pie } from "vue-chartjs";
import * as ChartImport from "chart.js";

import type { OhaErrorDistribution } from "@/types/oha";
import type { ChartData } from "@/types/ui-types";

const props = defineProps<{
  source: OhaErrorDistribution;
}>();

const { source } = toRefs(props);

const isLoading = ref<boolean>(true);

const totalErrors = ref<number>(0);

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

const {
  Chart,
  Tooltip,
  Legend,
  ArcElement,
  BarElement,
  CategoryScale,
  LinearScale,
} = ChartImport;

Chart.register(
  Tooltip,
  Legend,
  ArcElement,
  BarElement,
  CategoryScale,
  LinearScale
);

const pieData = ref<ChartData>({
  labels: [],
  datasets: [
    {
      backgroundColor: [],
      data: [],
    },
  ],
});

const pieOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false,
    },
  },
};

function setData() {
  const keys: string[] = Object.keys(source.value);

  keys.forEach((k, index) => {
    pieData.value.labels.push(k);

    (pieData.value.datasets[0].backgroundColor as string[]).push(
      COLORS[index % 9]
    );

    pieData.value.datasets[0].data.push(source.value[k]);
    totalErrors.value += source.value[k];
  });
}

onMounted(() => {
  isLoading.value = true;
  setData();
  isLoading.value = false;
});
</script>

<style lang="scss" scoped>
.ohaErrorDistribution {
  &__chart {
    margin-top: var(--space-medium);
    max-height: 40rem;
  }
}
</style>
