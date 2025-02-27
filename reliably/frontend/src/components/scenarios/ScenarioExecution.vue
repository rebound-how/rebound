<template>
  <div class="scenarioExecution">
    <div class="scenarioExecution__status text-center">
      {{ displayedStatus }}
    </div>
    <div
      v-if="loaderClass !== ''"
      class="scenarioExecution__loader"
      :class="loaderClass"
    >
      <LoaderPuff />
    </div>
    <div
      class="scenarioExecution__result text-center"
      ref="scenarioExecutionEmoji"
    >
      <span v-if="hasPlanError" class="scenarioExecution__emoji"> ⛔ </span>
      <span
        v-else-if="status.label === 'Completed'"
        class="scenarioExecution__emoji"
      >
        🎉
      </span>
      <span
        v-else-if="
          status.label === 'Deviated' || status.label === 'Rollbacks failed'
        "
        class="scenarioExecution__emoji"
      >
        💥
      </span>
      <span
        v-else-if="
          status.label === 'Aborted' ||
          status.label === 'Initial system condition not met'
        "
        class="scenarioExecution__emoji"
      >
        ⛔
      </span>
      <span
        v-else-if="status.label === 'Failed'"
        class="scenarioExecution__emoji"
      >
        &#10060;
      </span>
      <span
        v-else-if="isExecutionFinished && isUnknownEmojiDisplayed"
        class="scenarioExecution__emoji"
        >❓</span
      >
    </div>
    <div v-if="isLinkDisplayed" class="scenarioExecution__link text-center">
      <a :href="`/executions/view/?id=${id}&exp=${expId}`">
        View execution details and timeline
      </a>
    </div>
  </div>
</template>

<script setup lang="ts">
import { toRefs, ref, computed, onMounted, nextTick } from "vue";
import { useStore } from "@nanostores/vue";

import {
  plan,
  fetchPlan,
  planExecutions,
  fetchPlanExecutions,
} from "@/stores/plans";
import { execution, fetchExecution } from "@/stores/executions";

import { getExecutionStatusObject } from "@/utils/executions";

import type { Execution } from "@/types/executions";
import type { ExecutionUiStatus } from "@/types/ui-types";

import LoaderPuff from "@/components/svg/LoaderPuff.vue";

const props = defineProps<{
  planId: string;
}>();

const { planId } = toRefs(props);

const scenarioExecutionEmoji = ref<HTMLElement | null>(null);

const p = useStore(plan);
const loaderClass = ref<string>("scenarioExecution__loader--creating");
const hasPlanError = ref<boolean>(false);
let refreshPlanInterval: ReturnType<typeof setInterval>;

const id = ref<string>("");
const expId = ref<string>("");
const currentExecution = useStore(execution);

const isExecutionFinished = computed<boolean>(() => {
  return (
    currentExecution.value !== null &&
    currentExecution.value !== undefined &&
    currentExecution.value.user_state !== null &&
    currentExecution.value.user_state.current === "finished"
  );
});

const displayedStatus = ref<string>("Your experiment is being scheduled");

async function refreshPlan() {
  if (
    p.value?.status === "creating" ||
    p.value?.status === "created" ||
    p.value?.status === "scheduled"
  ) {
    loaderClass.value = "scenarioExecution__loader--creating";
    displayedStatus.value = "Your experiment is scheduled and will start soon";
    await fetchPlan(planId.value);
  } else if (p.value?.status === "creation error") {
    loaderClass.value = "";
    displayedStatus.value =
      "We encountered an error while scheduling your experiment";
    clearInterval(refreshPlanInterval);
    hasPlanError.value = true;
    makeEmojiLargeAgain();
  } else if (p.value?.status === "error") {
    loaderClass.value = "";
    displayedStatus.value =
      "We encountered an error while running your experiment";
    clearInterval(refreshPlanInterval);
    hasPlanError.value = true;
    makeEmojiLargeAgain();
  } else if (p.value?.status === "running") {
    loaderClass.value = "scenarioExecution__loader--running";
    displayedStatus.value = "Your experiment is running";
    clearInterval(refreshPlanInterval);
    refreshExecutionsListInterval = setInterval(refreshExecutionsList, 5000);
  } else {
    loaderClass.value = "scenarioExecution__loader--creating";
    displayedStatus.value = "Your experiment is scheduled and will start soon";
    await fetchPlan(planId.value);
  }
}

const status = ref<ExecutionUiStatus>({ label: "Unknown", type: "unknown" });
const isUnknownEmojiDisplayed = ref<boolean>(false);
function setStatus(s: ExecutionUiStatus): void {
  status.value = s;
}
function getStatus(): void {
  const s = getExecutionStatusObject(currentExecution.value! as Execution);
  setStatus(s);
}

let refreshExecutionsListInterval: ReturnType<typeof setInterval>;
async function refreshExecutionsList() {
  await fetchPlanExecutions(planId.value, 1);
  const planExecs = useStore(planExecutions);
  if (planExecs.value.total > 0) {
    clearInterval(refreshExecutionsListInterval);
    id.value = planExecs.value.executions[0].id;
    expId.value = planExecs.value.executions[0].experiment_id!;
    await fetchExecution(id.value!, expId.value!);
    refreshExecutionInterval = setInterval(refreshExecution, 5000);
  }
}

let refreshExecutionInterval: ReturnType<typeof setInterval>;
async function refreshExecution(): Promise<void> {
  if (isExecutionFinished.value) {
    getStatus();
    loaderClass.value = "";
    clearInterval(refreshExecutionInterval);
    if (status.value.label === "Completed") {
      displayedStatus.value = "Experiment completed!";
    } else if (status.value.label === "Rollbacks failed") {
      displayedStatus.value = "Experiment is finished, but rollbacks failed";
    } else if (status.value.label === "Initial system condition not met") {
      displayedStatus.value =
        "Experiment did not run as initial condition was not met";
    } else if (status.value.label === "Deviated") {
      displayedStatus.value = "Experiment deviated...";
    } else if (status.value.label === "Aborted") {
      displayedStatus.value = "Experiment aborted...";
    } else if (status.value.label === "Failed") {
      displayedStatus.value = "Experiment failed...";
    } else {
      displayedStatus.value =
        "Experiment is finished, but its status is unknown";
      isUnknownEmojiDisplayed.value = true;
    }
    makeEmojiLargeAgain();
  } else {
    loaderClass.value = "scenarioExecution__loader--running";
    displayedStatus.value = "Your experiment is running";
    await fetchExecution(id.value, expId.value);
  }
}

const isLinkDisplayed = computed<boolean>(() => {
  return !hasPlanError.value && isExecutionFinished.value;
});

function makeEmojiLargeAgain() {
  nextTick(() => {
    if (scenarioExecutionEmoji.value) {
      scenarioExecutionEmoji.value.classList.add(
        "scenarioExecution__result--large"
      );
    }
  });
}

onMounted(async () => {
  await fetchPlan(planId.value);

  refreshPlanInterval = setInterval(refreshPlan, 5000);
});
</script>

<style lang="scss">
.scenarioExecution {
  display: flex;
  flex-direction: column;
  gap: var(-space-medium);
  align-items: center;
  height: 30rem;
  margin-top: var(--space-large);

  &__status {
    margin-bottom: var(--space-medium);
  }

  &__loader {
    display: grid;
    place-items: center;
    width: 100%;

    svg {
      height: 8.8rem;
    }

    &--creating {
      svg {
        stroke: var(--sand-500);
      }
    }

    &--running {
      svg {
        stroke: var(--statusColor-ok);
      }
    }
  }

  &__result {
    transition: font-size 0.3s ease-in-out;

    &--large {
      font-size: 9.6rem;
    }
  }

  &__link {
    margin-top: auto;

    a {
      color: var(--text-color-dim);
      font-size: 1.6rem;
    }
  }
}
</style>
