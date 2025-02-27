<template>
  <div class="metricsExecutionsPerUser">
    <p v-if="!hasData">We don't have this data yet.</p>
    <div v-else class="metricsExecutionsPerUser__wrapper">
      <Pie :data="pieData" :options="pieOptions" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from "vue";
import { useStore } from "@nanostores/vue";
import { Pie } from "vue-chartjs";
import * as ChartImport from "chart.js";

import { metrics, loadMetrics } from "@/stores/series";
import type { ChartData } from "@/types/ui-types";

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

const isMounting = ref<boolean>(true);
const isComputing = ref<boolean>(true);
const hasData = ref<boolean>(false);
const storedData = useStore(metrics);

const pieData = ref<ChartData>({
  labels: [],
  datasets: [
    {
      backgroundColor: [],
      data: [],
    },
  ],
});

const COLORS: string[] = [
  "#f3a93c",
  "#ee7d56",
  "#de6177",
  "#af588d",
  "#3b4d7c",
  "#3b4d7c",
  "#163e59",
];

async function getData(): Promise<void> {
  await loadMetrics();
}

function computeData() {
  isComputing.value = true;
  if (storedData.value.distributions.per_user.total.length === 0) {
    hasData.value = false;
  } else {
    hasData.value = true;
    const pData = storedData.value.distributions.per_user.total;
    pData.forEach((set, index) => {
      pieData.value.labels.push(set.username);
      (pieData.value.datasets[0].backgroundColor as string[]).push(
        COLORS[index % 7]
      );
      pieData.value.datasets[0].data.push(set.count);
    });
  }
  isComputing.value = false;
}

watch(storedData, () => computeData());

const pieOptions = ref({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false,
    },
  },
});

onMounted(async () => {
  isMounting.value = true;
  await getData();
  isMounting.value = false;
});
</script>

<style lang="scss" scoped>
.metricsExecutionsPerUser {
  margin-top: var(--space-medium);

  &__wrapper {
    height: 27rem;

    :deep(canvas) {
      max-width: 100%;
    }
  }

  &__controls {
    display: flex;
    justify-content: center;
    gap: var(--space-small);
    margin-bottom: var(--space-small);
  }
}
</style>
