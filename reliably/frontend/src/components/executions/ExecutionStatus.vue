<template>
  <span
    v-if="timestamp"
    class="experimentStatus"
    :class="statusClass"
    :title="`${longStatus} on ${humanReadableTime}`"
  >
    {{ status.label }}
  </span>
  <span
    v-else
    class="experimentStatus"
    :class="statusClass"
    :title="longStatus"
  >
    {{ status.label }}
  </span>
</template>

<script setup lang="ts">
import { toRefs, computed } from "vue";
import dayjs from "dayjs";

import type { ExecutionUiStatus } from "@/types/ui-types";

const props = defineProps<{
  status: ExecutionUiStatus;
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
// const isStatusKnown = computed<boolean>(() => {
//   return statuses.includes(status.value);
// });

// const statusClass = computed<string>(() => {
//   if (status.value === "running") {
//     return "experimentStatus--running";
//   } else if (status.value === "pause" || status.value === "paused") {
//     return "experimentStatus--paused";
//   } else if (status.value === "deviated") {
//     return "experimentStatus--deviated";
//   } else if (status.value === "completed") {
//     return "experimentStatus--completed";
//   } else if (["aborted", "interrupted", "failed"].includes(status.value)) {
//     return "experimentStatus--interrupted";
//   } else {
//     return "experimentStatus--never";
//   }
// });

const statusClass = computed<string | null>(() => {
  if (status.value.type === null) {
    if (status.value.label === "running") {
      return "experimentStatus--running";
    } else if (status.value.label === "paused") {
      return "experimentStatus--paused";
    } else {
      return "experimentStatus--blank";
    }
  } else {
    return `experimentStatus--${status.value.type}`;
  }
});

const longStatus = computed<string>(() => {
  if (status.value.label === "pausing...") {
    return "Execution will be paused after current action";
  } else if (status.value.label === "stopping...") {
    return "Execution will be stopped after current action";
  } else {
    return (
      status.value.label.charAt(0).toUpperCase() + status.value.label.slice(1)
    );
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

  &--ko {
    background-color: var(--statusColor-ko);
  }

  &--warning {
    background-color: var(--statusColor-warning);
  }

  &--ok {
    background-color: var(--statusColor-ok);
  }

  &--unknown {
    background-color: var(--statusColor-never);
  }

  &--blank {
    background-color: transparent;
  }
}
</style>
