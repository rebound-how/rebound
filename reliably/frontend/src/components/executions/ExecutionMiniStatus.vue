<template>
  <span class="experimentStatus" :class="statusClass" :title="displayedLabel">
    <span class="screen-reader-text">{{ displayedLabel }}</span>
  </span>
</template>

<script setup lang="ts">
import { toRefs, computed } from "vue";

import type { ExecutionUiStatus } from "@/types/ui-types";

const props = defineProps<{
  status: ExecutionUiStatus;
}>();
const { status } = toRefs(props);

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

const displayedLabel = computed<string>(() => {
  return (
    status.value.label.charAt(0).toUpperCase() + status.value.label.slice(1)
  );
});
</script>

<style lang="scss" scoped>
.experimentStatus {
  display: inline-block;
  height: 1.2rem;
  width: 1.2rem;

  border-radius: 50%;

  color: white;
  font-size: 1.4rem;
  font-weight: 500;
  text-align: center;
  text-transform: capitalize;

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

  &--paused {
    position: relative;
    z-index: 3;

    height: 0.8rem;
    width: 0.8rem;

    // background-color: var(--statusColor-ok-dim);
    background-image: linear-gradient(
      90deg,
      var(--statusColor-ok-dim) 0.3rem,
      transparent 0.3rem,
      transparent 0.5rem,
      var(--statusColor-ok-dim) 0.5rem,
      var(--statusColor-ok-dim) 0.8rem
    );
    background-size: 0.8rem 0.8rem;
    border-radius: 0;

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
