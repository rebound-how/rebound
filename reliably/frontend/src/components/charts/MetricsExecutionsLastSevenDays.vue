<template>
  <div class="metricsExecutionsLastSevenDays">
    <div class="metricsExecutionsLastSevenDays__controls">
      <button
        @click.prevent="display('user')"
        class="pill"
        :class="{ 'pill--active': displayedChart === 'user' }"
      >
        Per user
      </button>
      <button
        @click.prevent="display('plan')"
        class="pill"
        :class="{ 'pill--active': displayedChart === 'plan' }"
      >
        Per plan
      </button>
    </div>
    <LoadingPlaceholder v-if="isMounting || isComputing" />
    <p v-else-if="!hasData">We don't have this data yet.</p>
    <div v-else class="metricsExecutionsLastSevenDays__wrapper">
      <Bar
        v-if="displayedChart === 'user'"
        :data="userData"
        :options="chartOptions"
      />
      <Bar
        v-if="displayedChart === 'plan'"
        :data="planData"
        :options="chartOptions"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from "vue";
import { useStore } from "@nanostores/vue";
import { Bar } from "vue-chartjs";
import * as ChartImport from "chart.js";
import dayjs from "dayjs";

import { metrics, loadMetrics } from "@/stores/series";
import type { ChartTooltipContext, StackBarsChartData } from "@/types/ui-types";

import LoadingPlaceholder from "@/components/_ui/LoadingPlaceholder.vue";

const { Chart, Tooltip, Legend, BarElement, CategoryScale, LinearScale } =
  ChartImport;

Chart.register(Tooltip, Legend, BarElement, CategoryScale, LinearScale);

const isMounting = ref<boolean>(true);
const isComputing = ref<boolean>(false);
const hasData = ref<boolean>(false);
const storedData = useStore(metrics);

const userData = ref<StackBarsChartData>({
  labels: [],
  datasets: [],
});

const planData = ref<StackBarsChartData>({
  labels: [],
  datasets: [],
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
  if (storedData.value.distributions.per_user.current_week.length === 0) {
    hasData.value = false;
  } else {
    hasData.value = true;
    const rawData = storedData.value.distributions.per_user.current_week;
    // let labels: string[] = ["S", "M", "T", "W", "T", "F", "S"];
    let labels: string[] = [];
    for (let i = 0; i++, i <= 7; ) {
      labels.unshift(
        dayjs()
          .subtract(i - 1, "days")
          .format("ddd MMM D, YYYY")
      );
    }
    const today = dayjs().day();
    const movedDays = today + 1;
    userData.value.labels = labels;
    planData.value.labels = labels;
    let userCounter: number = 0;
    let planCounter: number = 0;
    let internalUserData: {
      [key: string]: {
        label: string;
        data: number[];
        backgroundColor: string;
      };
    } = {};
    let internalPlanData: {
      [key: string]: {
        label: string;
        data: number[];
        backgroundColor: string;
      };
    } = {};
    rawData.forEach((entry) => {
      let index = dayjs(entry.started_on).day() - movedDays;
      if (index < 0) {
        index = index + 7;
      }

      const user = entry.user_id;
      if (!internalUserData[user]) {
        internalUserData[user] = {
          label: entry.username,
          data: [0, 0, 0, 0, 0, 0, 0],
          backgroundColor: COLORS[userCounter % 7],
        };
        userCounter++;
      }
      internalUserData[user].data[index]++;

      const plan = entry.plan_id;
      if (!internalPlanData[plan]) {
        internalPlanData[plan] = {
          label: entry.plan_title,
          data: [0, 0, 0, 0, 0, 0, 0],
          backgroundColor: COLORS[planCounter % 7],
        };
        planCounter++;
      }
      internalPlanData[plan].data[index]++;
    });
    Object.keys(internalUserData).forEach((user) => {
      userData.value.datasets.push(internalUserData[user]);
    });
    Object.keys(internalPlanData).forEach((plan) => {
      planData.value.datasets.push(internalPlanData[plan]);
    });
  }
}

watch(storedData, () => computeData());

const displayedChart = ref<string>("user");
function display(data: string) {
  displayedChart.value = data;
}

const chartOptions = ref({
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    x: {
      stacked: true,
      ticks: {
        callback: function (value: number): string {
          const label: string = (this as any).getLabelForValue(value);
          return dayjs(label).format("dd")[0];
        },
      },
    },
    y: {
      stacked: true,
      ticks: {
        stepSize: 1,
      },
    },
  },
  plugins: {
    legend: {
      display: false,
    },
    tooltip: {
      callbacks: {
        label: function (context: ChartTooltipContext) {
          let label: string[] = [];
          const words: string[] = context.dataset.label.split(" ");
          let line: string = "";
          words.forEach((word) => {
            if (line.length + word.length < 40) {
              line = `${line} ${word}`;
            } else {
              label.push(line);
              line = "";
              line = word;
            }
          });
          line = `${line}: ${context.dataset.data[context.dataIndex]}`;
          label.push(line);
          line = "";
          return label;
        },
      },
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
.metricsExecutionsLastSevenDays {
  margin-top: var(--space-small);

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
