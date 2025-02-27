<template>
  <span
    v-if="isStatusKnown && timestamp"
    class="experimentStatus"
    :class="statusClass"
    :title="`${status} on ${humanReadableTime}`"
  >
    {{ status }}
  </span>
  <span
    v-else-if="isStatusKnown"
    class="experimentStatus"
    :class="statusClass"
    :title="status"
  >
    {{ status }}
  </span>
  <span
    v-else
    class="experimentStatus"
    :class="statusClass"
    title="This experiment hasn't run yet"
  >
    Not run yet
  </span>
</template>

<script setup lang="ts">
import { toRefs, computed } from "vue";

import dayjs from "dayjs";

const props = defineProps<{
  status: string;
  timestamp?: string | null;
}>();
const { status, timestamp } = toRefs(props);

const statuses = [
  "deviated",
  "completed",
  "interrupted",
  "aborted",
  "running",
  "pause",
  "paused",
  "pausing...",
  "failed",
  "stopping...",
];
const isStatusKnown = computed<boolean>(() => {
  return statuses.includes(status.value);
});

const statusClass = computed<string>(() => {
  if (status.value === "running") {
    return "experimentStatus--running";
  } else if (status.value === "pause" || status.value === "paused") {
    return "experimentStatus--paused";
  } else if (status.value === "deviated") {
    return "experimentStatus--deviated";
  } else if (status.value === "completed") {
    return "experimentStatus--completed";
  } else if (["aborted", "interrupted", "failed"].includes(status.value)) {
    return "experimentStatus--interrupted";
  } else {
    return "experimentStatus--never";
  }
});

const longStatus = computed<string>(() => {
  if (status.value === "pausing...") {
    return "Execution will be paused after current action";
  } else if (status.value === "stopping...") {
    return "Execution will be stopped after current action";
  } else {
    return status.value;
  }
});

const humanReadableTime = computed<string>(() => {
  return dayjs(timestamp!.value).format("D MMMM YYYY, H:mm:ss");
});
</script>

<style lang="scss" scoped>
.experimentStatus {
  display: inline-block;
  padding: 0.6rem 1.2rem;

  border-radius: 2rem;

  color: white;
  font-size: 1.4rem;
  font-weight: 500;
  text-align: center;
  text-transform: capitalize;

  @media print {
    display: block;
    padding: 0;

    font-size: 18px;
    text-align: left;

    animation: none !important;
  }

  &--running,
  &--paused {
    animation: 2.25s infinite linear runningPulse;

    @keyframes runningPulse {
      0% {
        transform: scale(1);
      }

      50% {
        transform: scale(0.9);
      }

      100% {
        transform: scale(1);
      }
    }
  }

  &--running {
    background-color: var(--statusColor-ok);
  }

  &--paused {
    background-color: var(--statusColor-ok-dim);
  }

  &--deviated {
    background-color: var(--statusColor-ko);
  }

  &--interrupted {
    background-color: var(--statusColor-warning);
  }

  &--completed {
    background-color: var(--statusColor-ok);
  }

  &--never {
    background-color: var(--statusColor-never);
  }
}
</style>
