<template>
  <div class="contributionsRadar">
    <h2>Contributions</h2>
    <p v-if="!hasContributions">
      This experiment doesn't declare contributions.
    </p>
    <div v-else class="contributionsRadar__wrapper">
      <LoadingPlaceholder size="fill" v-if="isLoading" />
      <Radar v-else-if="hasData" :data="chartData" :options="chartOptions" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { toRefs, ref, computed, onMounted } from "vue";
import type { Contributions } from "@/types/experiments";
import type { RadarChartData } from "@/types/ui-types";

import { contributionToString } from "@/utils/contributions";

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

const props = defineProps<{
  contributions: Contributions | undefined;
}>();
const { contributions } = toRefs(props);

const isLoading = ref(true);
const hasData = ref<boolean>(false);

const chartData = ref<RadarChartData>({
  labels: [],
  datasets: [
    {
      label: "Contribution",
      backgroundColor: "hsla(329,97%,55%,0.2)",
      borderColor: "hsl(329,97%,55%)",
      pointBackgroundColor: "hsl(329,97%,55%)",
      pointBorderColor: "white",
      pointHoverBackgroundColor: "white",
      pointHoverBorderColor: "hsl(329,97%,55%)",
      data: [],
    },
  ],
});

const hasContributions = computed<boolean>(() => {
  if (contributions.value === undefined) {
    return false;
  } else {
    return Object.keys(contributions.value).length > 0;
  }
});

const getData = () => {
  if (contributions.value !== undefined) {
    const labels = Object.keys(contributions.value);
    let d: number[] = [];
    let l: string[] = [];
    labels.forEach((label) => {
      let contribution = contributions.value![label] as string;

      if (contribution === "none") {
        d.push(0);
        l.push(label);
      } else if (contribution === "low") {
        d.push(1);
        l.push(label);
      } else if (contribution === "medium") {
        d.push(2);
        l.push(label);
      } else if (contribution === "high") {
        d.push(3);
        l.push(label);
      }
    });
    chartData.value.datasets[0].data = d;
    chartData.value.labels = l;
    hasData.value = true;
  }
};

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
        stepSize: 1,
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
      callbacks: {
        label: function (context: any) {
          let label = context.formattedValue;
          let contribution: string = contributionToString(label);
          return contribution;
        },
      },
    },
  },
};

onMounted(() => {
  isLoading.value = true;
  getData();
  isLoading.value = false;
});
</script>

<style lang="scss" scoped>
.contributionsRadar {
  width: 30rem;

  h2 {
    margin-top: 0;
    margin-bottom: 0;
  }

  &__wrapper {
    height: 30rem;
  }
}
</style>
