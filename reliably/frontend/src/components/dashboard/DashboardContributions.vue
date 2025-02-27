<template>
  <div class="dashboardContributions">
    <div class="dashboardContributions__controls">
      <button
        @click.prevent="display('experiment')"
        class="pill"
        :class="{ 'pill--active': displayedChart === 'experiment' }"
      >
        Per experiments
      </button>
      <button
        @click.prevent="display('execution')"
        class="pill"
        :class="{ 'pill--active': displayedChart === 'execution' }"
      >
        Per executions
      </button>
    </div>
    <LoadingPlaceholder v-if="isLoading" />
    <p v-else-if="!hasData">We don't have this data yet.</p>
    <div v-else class="dashboardContributions__wrapper">
      <ExperimentsContributionsRadar
        v-if="displayedChart === 'experiment'"
        client:load
      />
      <ExecutionsContributionsRadar
        v-if="displayedChart === 'execution'"
        client:load
      />
      <div class="dashboardContributions__help">
        <span
          v-if="displayedChart === 'experiment'"
          class="hasTooltip hasTooltip--top-right"
          aria-label="The contributions declared by your experiments"
        >
          <HelpCircle />
        </span>
        <span
          v-if="displayedChart === 'execution'"
          class="hasTooltip hasTooltip--top-right"
          aria-label="Aggregates the contributions 
declared by your experiments 
each time they are actually run"
        >
          <HelpCircle />
        </span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import type { RadarChartData } from "@/types/ui-types";

import { useStore } from "@nanostores/vue";
import { contributionsForRadar, loadContributionsData } from "@/stores/series";

import LoadingPlaceholder from "@/components/_ui/LoadingPlaceholder.vue";
import ExperimentsContributionsRadar from "@/components/charts/ExperimentsContributionsRadar.vue";
import ExecutionsContributionsRadar from "@/components/charts/ExecutionsContributionsRadar.vue";
import HelpCircle from "@/components/svg/HelpCircle.vue";

const isMounting = ref<boolean>(true);
const hasData = computed<boolean>(() => {
  return storedData.value.datasets.length > 0;
});
const storedData = useStore(contributionsForRadar);
const isLoading = computed(() => {
  return (
    isMounting.value ||
    storedData.value.state === "empty" ||
    storedData.value.state === "loading"
  );
});

const displayedChart = ref<string>("experiment");
function display(data: string) {
  displayedChart.value = data;
}

const chartData = ref<RadarChartData>({
  labels: [],
  datasets: [
    {
      label: "Contributions",
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

async function getData(): Promise<void> {
  await loadContributionsData();
  if (hasData.value) {
    chartData.value.labels = [...storedData.value.labels];
    chartData.value.datasets[0].data = [...storedData.value.datasets[0].data];
  }
}

onMounted(async () => {
  isMounting.value = true;
  await getData();
  isMounting.value = false;
});
</script>

<style lang="scss">
.dashboardContributions {
  margin-top: var(--space-small);

  .loadingPlaceholder {
    height: 27rem;
  }

  &__wrapper {
    position: relative;

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

  &__help {
    position: absolute;
    bottom: 0;
    right: 0;

    svg {
      height: 1.8rem;

      color: var(--text-color-dim);
    }
  }
}
</style>
