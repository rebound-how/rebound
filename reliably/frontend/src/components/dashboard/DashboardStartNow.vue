<template>
  <div class="dashboardStartNow">
    <LoadingPlaceholder size="fill" v-if="isLoading" />
    <template v-else-if="hasData || isMessageDismissed">
      <section class="dashboardItem">
        <h2>
          Executions per user
          <span
            class="hasTooltip hasTooltip--bottom-right"
            aria-label="All time executions, distributed by users"
          >
            <HelpCircle />
          </span>
        </h2>
        <MetricsExecutionsPerUser client:load />
      </section>
      <section class="dashboardItem">
        <h2>
          Last 7 days
          <span
            class="hasTooltip hasTooltip--bottom-right"
            aria-label="Executions distribution during the last 7 days"
          >
            <HelpCircle />
          </span>
        </h2>
        <MetricsExecutionsLastSevenDays client:load />
      </section>
    </template>
    <div v-else class="dashboardStartNow__message">
      <h2>Welcome!</h2>
      <p class="text-center">You don't have any experiments yet.</p>
      <p class="text-center">
        You can
        <a href="/experiments/new/"
          >upload an existing Chaos Toolkit experiment</a
        ><br />
        or get started with one of our 250+ ready-to-run experiments
      </p>
      <div class="dashboardStartNow__actions">
        <a
          href="/experiments/custom-templates/create/?activity=reliably-tls-verify_certificate"
          class="button button--primary"
          >Let's go</a
        >
        <button @click.prevent="dismissMessage" class="button button--ghost">
          Dismiss
        </button>
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
import MetricsExecutionsPerUser from "@/components/charts/MetricsExecutionsPerUser.vue";
import MetricsExecutionsLastSevenDays from "@/components/charts/MetricsExecutionsLastSevenDays.vue";
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
const isMessageDismissed = ref<boolean>(false);

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

function getMessageStatus() {
  const dismissedStatus = localStorage.getItem(
    "reliably:isStartMessageDismissed"
  );
  if (dismissedStatus === "true") {
    isMessageDismissed.value = true;
  }
}
function dismissMessage() {
  localStorage.setItem("reliably:isStartMessageDismissed", "true");
  isMessageDismissed.value = true;
}

onMounted(async () => {
  isMounting.value = true;
  getMessageStatus();
  await getData();
  isMounting.value = false;
});
</script>

<style lang="scss">
.dashboardStartNow {
  display: flex;
  gap: var(--space-medium);
  grid-column-end: span 2;

  .loadingPlaceholder {
    flex: 1 0 auto;
  }

  .dashboardItem {
    flex: 1;
  }

  &__message {
    display: flex;
    flex: 1 0 auto;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: var(--space-medium);
    grid-column-end: span 2;
    padding: var(--space-small);

    background-color: var(--pink-100);
    border-radius: var(--border-radius-m);

    color: var(--pink-800);

    h2 {
      margin-bottom: 0;

      color: var(--pink-900);
      font-size: 4.8rem;
      line-height: 1;
    }

    p {
      margin-top: 0;
    }
  }

  &__actions {
    display: flex;
    justify-content: center;
    gap: var(--space-small);
  }
}
</style>
