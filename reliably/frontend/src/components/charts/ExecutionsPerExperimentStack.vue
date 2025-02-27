<template>
  <h2>Experiment Executions Breakdown</h2>
  <div class="executionsStack">
    <Bar :data="chartData" :options="chartOptions" />
  </div>
</template>

<script setup lang="ts">
import { toRefs, ref, onMounted } from "vue";
import type { SeriesExecutionsPerExperimentDataset } from "@/types/series";
import type { StackBarsChartData } from "@/types/ui-types";
import { hasProp } from "@/utils/objects";

import { useStore } from "@nanostores/vue";
import { executionsPerExperiment, loadExePerExp } from "@/stores/series";

import { shortenUuid } from "@/utils/strings";

import { Bar } from "vue-chartjs";
import * as ChartImport from "chart.js";
const {
  Chart,
  Title,
  Tooltip,
  Legend,
  LinearScale,
  CategoryScale,
  BarElement,
} = ChartImport;

Chart.register(Title, Tooltip, Legend, LinearScale, CategoryScale, BarElement);

const props = defineProps<{
  experimentId: string;
}>();
const { experimentId } = toRefs(props);

const colorsCerulean = [
  "rgb(174, 218, 225)",
  "rgb(139, 201, 212)",
  "rgb(104, 185, 199)",
  "rgb(69, 169, 186)",
  "rgb(34, 153, 173)",
  "rgb(2, 136, 159)",
];

const colorsRose = [
  "rgb(252, 215, 234)",
  "rgb(251, 198, 224)",
  "rgb(250, 180, 215)",
  "rgb(248, 163, 206)",
  "rgb(247, 146, 197)",
  "rgb(243, 129, 186)",
];

const colorsMagma = [
  "rgb(254, 215, 184)",
  "rgb(254, 197, 154)",
  "rgb(253, 180, 123)",
  "rgb(253, 162, 93)",
  "rgb(252, 145, 62)",
  "rgb(249, 128, 34)",
];

const colorsPurple = [
  "rgb(247, 181, 235)",
  "rgb(243, 149, 227)",
  "rgb(239, 117, 218)",
  "rgb(236, 85, 209)",
  "rgb(232, 53, 201)",
  "rgb(227, 23, 191)",
];

const isLoading = ref(true);
const exeStore = useStore(executionsPerExperiment);

const chartData = ref<StackBarsChartData>({
  labels: [],
  datasets: [],
});

async function getData(): Promise<void> {
  await loadExePerExp(experimentId.value);
  exeStore.value.labels.forEach((l) => {
    chartData.value.labels.push(shortenUuid(l));
  });
  exeStore.value.datasets.forEach((d, index) => {
    const obj = {
      label: d.name,
      data: [...d.data],
      stack: d.stack,
      backgroundColor: setBackgroundColor(
        d as SeriesExecutionsPerExperimentDataset,
        index
      ),
    };
    chartData.value.datasets.push(obj);
  });
}

function setBackgroundColor(
  d: SeriesExecutionsPerExperimentDataset,
  index: number
): string {
  let color: string = "";
  let where: string = hasProp(d, "loc") ? d.loc! : d.name;
  let i: number = hasProp(d, "loc") ? index % 6 : 3;

  if (where === "ssh-before") {
    color = colorsCerulean[i];
  } else if (where === "method") {
    color = colorsRose[i];
  } else if (where === "ssh-after") {
    color = colorsMagma[i];
  } else if (where === "rollbacks") {
    color = colorsPurple[i];
  }
  return color;
}

const chartOptions = ref({
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    x: {
      stacked: true,
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

onMounted(() => {
  isLoading.value = true;
  getData();
  isLoading.value = false;
});
</script>

<style lang="scss" scoped>
.executionsStack {
  height: 44rem;
  padding: var(--space-small);

  background-color: var(--section-background);
  border-radius: var(--border-radius-s);
}
</style>
