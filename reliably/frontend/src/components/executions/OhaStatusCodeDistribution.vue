<template>
  <div class="ohaStatusCodeDistribution">
    <div class="ohaStatusCodeDistribution__chart" v-if="!isLoading">
      <Pie :data="pieData" :options="pieOptions" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { toRefs, ref, onMounted } from "vue";
import { Pie } from "vue-chartjs";
import * as ChartImport from "chart.js";

import type { OhaStatusCodeDistribution } from "@/types/oha";
import type { ChartData } from "@/types/ui-types";

const props = defineProps<{
  source: OhaStatusCodeDistribution;
}>();

const { source } = toRefs(props);

const isLoading = ref<boolean>(true);

const counter_2xx = ref<number>(0);
const COLORS_2XX: string[] = [
  "hsl(120, 42%, 53%)",
  "hsl(137, 57%, 41%)",
  "hsl(150, 59%, 33%)",
  "hsl(163, 60%, 25%)",
];

const counter_4xx = ref<number>(0);
const COLORS_4XX: string[] = [
  "hsl(286, 47%, 50%)",
  "hsl(286, 75%, 38%)",
  "hsl(285, 84%, 32%)",
  "hsl(285, 92%, 25%)",
];

const counter_5xx = ref<number>(0);
const COLORS_5XX: string[] = [
  "hsl(0, 54%, 52%)",
  "hsl(0, 79%, 40%)",
  "hsl(0, 99%, 32%)",
  "hsl(0, 100%, 26%)",
];

const counter_xxx = ref<number>(0);
const COLORS_XXX: string[] = [
  "hsl(209, 82%, 57%)",
  "hsl(209, 97%, 45%)",
  "hsl(209, 100%, 37%)",
  "hsl(210, 100%, 30%)",
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

  keys.forEach((k) => {
    pieData.value.labels.push(k);
    if (parseInt(k) < 200) {
      (pieData.value.datasets[0].backgroundColor as string[]).push(
        COLORS_XXX[counter_xxx.value % 4]
      );
      counter_xxx.value++;
    } else if (parseInt(k) < 300) {
      (pieData.value.datasets[0].backgroundColor as string[]).push(
        COLORS_2XX[counter_2xx.value % 4]
      );
      counter_2xx.value++;
    } else if (parseInt(k) < 400) {
      (pieData.value.datasets[0].backgroundColor as string[]).push(
        COLORS_XXX[counter_xxx.value % 4]
      );
      counter_xxx.value++;
    } else if (parseInt(k) < 500) {
      (pieData.value.datasets[0].backgroundColor as string[]).push(
        COLORS_4XX[counter_4xx.value % 4]
      );
      counter_4xx.value++;
    } else if (parseInt(k) < 600) {
      (pieData.value.datasets[0].backgroundColor as string[]).push(
        COLORS_5XX[counter_5xx.value % 4]
      );
      counter_5xx.value++;
    } else {
      (pieData.value.datasets[0].backgroundColor as string[]).push(
        COLORS_XXX[counter_xxx.value % 4]
      );
      counter_xxx.value++;
    }

    pieData.value.datasets[0].data.push(source.value[k]);
  });
}

onMounted(() => {
  isLoading.value = true;
  setData();
  isLoading.value = false;
});
</script>

<style lang="scss" scoped>
.ohaStatusCodeDistribution {
  &__chart {
    margin-top: var(--space-medium);
    max-height: 40rem;
  }
}
</style>
