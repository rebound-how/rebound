<template>
  <span class="planStatus" :class="statusClass">
    {{ statusLabel }}
    <span
      v-if="status.error"
      class="hasTooltip hasTooltip--bottom-center"
      :label="status.error"
      :aria-label="status.error"
    >
      <AlertTriangle />
    </span>
  </span>
</template>

<script setup lang="ts">
import { toRefs, computed } from "vue";
import AlertTriangle from "@/components/svg/AlertTriangle.vue";

const props = defineProps<{
  status: { status: string; error: null | string };
}>();
const { status } = toRefs(props);

const statusClass = computed<string>(() => {
  if (status.value.status === "creating") {
    return "planStatus--creating";
  } else if (
    status.value.status === "created" ||
    status.value.status === "rerunning" ||
    status.value.status === "scheduled"
  ) {
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
  } else if (
    status.value.status === "created" ||
    status.value.status === "scheduled"
  ) {
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
  } else if (status.value.status === "rerunning") {
    return "Re-running...";
  } else {
    return "Unknown";
  }
});
</script>

<style lang="scss" scoped>
.planStatus {
  display: inline-block;
  padding: 0.6rem 1.2rem;

  border-radius: 2rem;

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
    color: var(--text-color-bright);
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
    background-color: var(--statusColor-ok-dim);

    color: var(--text-color-bright);

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

  svg {
    height: 1.6rem;

    vertical-align: -0.3rem;
  }
}
</style>
