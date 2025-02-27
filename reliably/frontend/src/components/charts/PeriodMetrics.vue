<template>
  <div class="periodMetrics">
    <div class="periodMetrics__controls">
      <button
        @click.prevent="display('day')"
        class="pill"
        :class="{ 'pill--active': displayedChart === 'day' }"
      >
        Per day
      </button>
      <button
        @click.prevent="display('week')"
        class="pill"
        :class="{ 'pill--active': displayedChart === 'week' }"
      >
        Per week
      </button>
      <button
        @click.prevent="display('month')"
        class="pill"
        :class="{ 'pill--active': displayedChart === 'month' }"
      >
        Per month
      </button>
    </div>
    <LoadingPlaceholder v-if="isMounting || isComputing" />
    <p v-else-if="!hasData">We don't have this data yet.</p>
    <div v-else class="periodMetrics__wrapper">
      <Line
        v-if="displayedChart === 'day'"
        :data="dayData"
        :options="dayChartOptions"
      />
      <Line
        v-else-if="displayedChart === 'week'"
        :data="weekData"
        :options="weekChartOptions"
      />
      <Line
        v-else-if="displayedChart === 'month'"
        :data="monthData"
        :options="monthChartOptions"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from "vue";
import { useStore } from "@nanostores/vue";
import { Line } from "vue-chartjs";
import * as ChartImport from "chart.js";
import dayjs from "dayjs";
import "chartjs-adapter-dayjs-3";

import LoadingPlaceholder from "@/components/_ui/LoadingPlaceholder.vue";
import { metrics, loadMetrics } from "@/stores/series";

import type { ChartTooltipContext } from "@/types/ui-types";

const {
  Chart,
  CategoryScale,
  TimeScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} = ChartImport;
if (typeof window !== "undefined") {
  (async () => {
    const { default: zoomPlugin } = await import("chartjs-plugin-zoom");
    Chart.register(zoomPlugin);
  })();
}

Chart.register(
  CategoryScale,
  TimeScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const COLORS: string[] = [
  "#f3a93c",
  "#ee7d56",
  "#de6177",
  "#af588d",
  "#3b4d7c",
  "#3b4d7c",
  "#163e59",
];

const isMounting = ref<boolean>(true);
const isComputing = ref<boolean>(true);
const hasData = ref<boolean>(false);
const storedData = useStore(metrics);

interface TimeDataSetPoint {
  x: string;
  y: number;
}

interface TimeDataSet {
  label: string;
  backgroundColor: string;
  borderColor: string;
  fill: boolean;
  tension: number;
  data: TimeDataSetPoint[];
}

const dayData = ref<{ datasets: TimeDataSet[] }>({
  datasets: [
    {
      label: "Executions",
      backgroundColor: COLORS[0],
      borderColor: COLORS[1],
      fill: false,
      tension: 0.1,
      data: [],
    },
  ],
});

const weekData = ref<{ datasets: TimeDataSet[] }>({
  datasets: [
    {
      label: "Executions",
      backgroundColor: COLORS[0],
      borderColor: COLORS[1],
      fill: false,
      tension: 0.1,
      data: [],
    },
  ],
});

const monthData = ref<{ datasets: TimeDataSet[] }>({
  datasets: [
    {
      label: "Execution",
      backgroundColor: COLORS[0],
      borderColor: COLORS[0],
      fill: false,
      tension: 0.1,
      data: [],
    },
  ],
});

const dayChartMax = dayjs().format("YYYY-MM-DD");
const dayChartMin = dayjs().subtract(31, "days").format("YYYY-MM-DD");
const dayUpperBound = ref<number>(10);

const day: number = dayjs().day();
const lastMonday = dayjs().subtract((day + 6) % 7, "days");
const weekChartMax = lastMonday.format("YYYY-MM-DD");
const weekChartMin = lastMonday.subtract(28, "days").format("YYYY-MM-DD");
const weekUpperBound = ref<number>(10);

const startOfMonth = dayjs().startOf("month");
const monthChartMax = startOfMonth.format("YYYY-MM-DD");
const monthChartMin = startOfMonth.subtract(5, "month").format("YYYY-MM-DD");
const monthUpperBound = ref<number>(10);

async function getData(): Promise<void> {
  await loadMetrics();
}

async function computeData() {
  isComputing.value = true;
  if (storedData.value.distributions.per_period.per_day.length === 0) {
    hasData.value = false;
  } else {
    hasData.value = true;
    const rawData = storedData.value.distributions.per_period;
    rawData.per_day.forEach((entry) => {
      dayData.value.datasets[0].data.push({
        x: entry.day!,
        y: entry.count,
      });
      if (entry.count >= dayUpperBound.value) {
        dayUpperBound.value = Math.ceil(entry.count / 10) * 10;
      }
    });
    rawData.per_week.forEach((entry) => {
      weekData.value.datasets[0].data.push({
        x: entry.week!,
        y: entry.count,
      });
      if (entry.count >= weekUpperBound.value) {
        weekUpperBound.value = Math.ceil(entry.count / 10) * 10;
      }
    });
    rawData.per_month.forEach((entry) => {
      monthData.value.datasets[0].data.push({
        x: entry.month!,
        y: entry.count,
      });
      if (entry.count >= monthUpperBound.value) {
        monthUpperBound.value = Math.ceil(entry.count / 10) * 10;
      }
    });
  }

  dayChartOptions.value.scales.y.max = dayUpperBound.value;
  weekChartOptions.value.scales.y.max = weekUpperBound.value;
  monthChartOptions.value.scales.y.max = monthUpperBound.value;

  isComputing.value = false;
}

watch(storedData, () => computeData());

const displayedChart = ref<string>("day");
function display(period: string) {
  displayedChart.value = period;
}

const dayChartOptions = ref({
  type: "line",
  responsive: true,
  maintainAspectRatio: false,
  datasets: {
    line: {
      spanGaps: true,
      tension: 0.2,
    },
  },
  scales: {
    x: {
      type: "time",
      time: {
        unit: "day",
        displayFormats: {
          day: "DD MMM.",
        },
      },
      min: dayChartMin,
      max: dayChartMax,
    },
    y: {
      min: 0,
      max: 10,
      ticks: {
        beginAtZero: true,
        stepSize: 1,
      },
    },
  },
  plugins: {
    legend: {
      display: false,
    },
    zoom: {
      zoom: {
        wheel: {
          enabled: false,
        },
        pinch: {
          enabled: false,
        },
      },
      pan: {
        enabled: true,
        mode: "x",
        threshold: 10,
      },
    },
    tooltip: {
      callbacks: {
        title: function (context: ChartTooltipContext[]) {
          return dayjs(context[0].label).format("MMMM D, YYYY");
        },
      },
    },
  },
});

const weekChartOptions = ref({
  type: "line",
  responsive: true,
  maintainAspectRatio: false,
  datasets: {
    line: {
      spanGaps: true,
      tension: 0.2,
    },
  },
  scales: {
    x: {
      type: "time",
      time: {
        unit: "week",
        displayFormats: {
          day: "DD MMM.",
        },
        isoWeekday: true,
      },
      min: weekChartMin,
      max: weekChartMax,
      ticks: {
        autoSkip: false,
        maxRotation: 90,
        minRotation: 90,
      },
    },
    y: {
      min: 0,
      max: 10,
      ticks: {
        beginAtZero: true,
        stepSize: 1,
      },
    },
  },
  plugins: {
    legend: {
      display: false,
    },
    zoom: {
      zoom: {
        wheel: {
          enabled: false,
        },
        pinch: {
          enabled: false,
        },
      },
      pan: {
        enabled: true,
        mode: "x",
        threshold: 10,
      },
    },
    tooltip: {
      callbacks: {
        title: function (context: ChartTooltipContext[]) {
          const monday = dayjs(context[0].parsed.x);
          return `Week starting ${monday.format("MMMM D, YYYY")}`;
        },
      },
    },
  },
});

const monthChartOptions = ref({
  type: "line",
  responsive: true,
  maintainAspectRatio: false,
  datasets: {
    line: {
      spanGaps: true,
      tension: 0.2,
    },
  },
  scales: {
    x: {
      type: "time",
      time: {
        unit: "month",
        displayFormats: {
          day: "MMM.",
        },
      },
      min: monthChartMin,
      max: monthChartMax,
      ticks: {
        autoSkip: false,
        maxRotation: 90,
        minRotation: 90,
      },
    },
    y: {
      min: 0,
      max: 10,
      ticks: {
        beginAtZero: true,
        stepSize: 1,
      },
    },
  },
  plugins: {
    legend: {
      display: false,
    },
    zoom: {
      zoom: {
        wheel: {
          enabled: false,
        },
        pinch: {
          enabled: false,
        },
      },
      pan: {
        enabled: true,
        mode: "x",
        threshold: 10,
      },
    },
    tooltip: {
      callbacks: {
        title: function (context: ChartTooltipContext[]) {
          const monday = dayjs(context[0].parsed.x);
          return monday.format("MMMM YYYY");
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
.periodMetrics {
  margin-top: var(--space-small);

  .loadingPlaceholder {
    height: 27rem;
  }

  &__wrapper {
    height: 27rem;

    :deep(canvas) {
      max-width: 100%;

      cursor: grab;
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
