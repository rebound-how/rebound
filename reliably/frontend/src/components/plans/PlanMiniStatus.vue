<template>
  <span class="planStatus" :class="statusClass" :title="statusLabel">
    <span class="screen-reader-text">{{ statusLabel }}</span>
  </span>
</template>

<script setup lang="ts">
import { toRefs, computed } from "vue";

const props = defineProps<{
  status: { status: string; error: null | string };
}>();
const { status } = toRefs(props);

const statusClass = computed<string>(() => {
  if (status.value.status === "creating") {
    return "planStatus--creating";
  } else if (status.value.status === "created") {
    return "planStatus--scheduled";
  } else if (
    status.value.status === "creation error" ||
    status.value.status === "deletion error" ||
    status.value.status === "suspending" ||
    status.value.status === "suspended" ||
    status.value.status === "resuming"
  ) {
    return "planStatus--warning";
  } else if (
    status.value.status === "error" ||
    status.value.status === "suspend_error" ||
    status.value.status === "resuming_error"
  ) {
    return "planStatus--error";
  } else if (status.value.status === "running") {
    return "planStatus--running";
  } else if (status.value.status === "completed") {
    return "planStatus--completed";
  } else if (status.value.status === "deleting") {
    return "planStatus--deleting";
  } else {
    return "planStatus--unknown";
  }
});

const statusLabel = computed<string>(() => {
  if (status.value.status === "creating") {
    return "Creating...";
  } else if (status.value.status === "created") {
    return status.value.error === null ? "Scheduled" : "Error after creation";
  } else if (status.value.status === "creation error") {
    return status.value.error === null
      ? "Plan couldn't be scheduled"
      : `Plan couldn't be scheduled: ${status.value.error}`;
  } else if (status.value.status === "deletion error") {
    return status.value.error === null
      ? "Plan couldn't be deleted"
      : `Plan couldn't be deleted: ${status.value.error}`;
  } else if (status.value.status === "suspend_error") {
    return status.value.error === null
      ? "Plan schedule couldn't be suspended"
      : `Plan schedule couldn't be suspended: ${status.value.error}`;
  } else if (status.value.status === "resuming_error") {
    return status.value.error === null
      ? "Plan schedule couldn't be resumed"
      : `Plan schedule couldn't be resumed: ${status.value.error}`;
  } else if (status.value.status === "error") {
    return status.value.error === null ? "error" : status.value.error;
  } else if (status.value.status === "running") {
    return "Running";
  } else if (status.value.status === "completed") {
    return "Completed";
  } else if (status.value.status === "suspended") {
    return "Suspended";
  } else if (status.value.status === "suspending") {
    return "Suspending";
  } else if (status.value.status === "resuming") {
    return "Resuming";
  } else if (status.value.status === "deleting") {
    return "Deleting";
  } else {
    return "Unknown";
  }
});
</script>

<style lang="scss" scoped>
.planStatus {
  display: inline-block;
  height: 1.2rem;
  width: 1.2rem;

  border-radius: 50%;

  color: white;
  font-size: 1.4rem;
  font-weight: 500;
  text-align: center;
  text-transform: capitalize;

  &--creating,
  &--unknown {
    background-color: var(--statusColor-never);
  }

  &--scheduled {
    background-color: var(--statusColor-warning-dim);
  }

  &--warning {
    background-color: var(--statusColor-warning);
  }

  &--error {
    background-color: var(--statusColor-ko);
  }

  &--completed {
    background-color: var(--statusColor-ok);
  }

  &--deleting {
    background-color: var(--statusColor-ko-dim);
  }

  &--running {
    position: relative;
    z-index: 3;

    height: 1rem;
    width: 1rem;

    background-color: var(--statusColor-ok-dim);

    &::before,
    &::after {
      content: "";

      position: absolute;
      top: 50%;
      left: 50%;

      display: inline-block;
      height: 1.8rem;
      width: 1.8rem;

      background-color: transparent;
      border-radius: 50%;

      transform: translate(-50%, -50%);
    }

    &::before {
      border: 0.2rem solid var(--statusColor-ok-dim);
    }

    &::after {
      border: 0.2rem solid transparent;
      border-top-color: var(--statusColor-ok);

      animation: 1s infinite linear rotateRunning;
      transform-origin: center center;

      @keyframes rotateRunning {
        0% {
          transform: translate(-50%, -50%) rotate(0deg);
        }

        50% {
          transform: translate(-50%, -50%) rotate(180deg);
        }

        100% {
          transform: translate(-50%, -50%) rotate(360deg);
        }
      }
    }
  }
}
</style>
