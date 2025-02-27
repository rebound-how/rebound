<template>
  <span class="activityInfo"></span>
  <span :class="typeClass">{{ activity.type }}</span
  >&nbsp;<span
    class="activityInfo__name"
    v-html="breakableName(activity.name)"
  ></span>
</template>

<script setup lang="ts">
import { toRefs, computed } from "vue";

import type { UiScenarioActivity } from "@/types/scenarios";
import { breakableName } from "@/utils/strings";

const props = defineProps<{
  activity: UiScenarioActivity;
}>();
const { activity } = toRefs(props);

const typeClass = computed<string>(() => {
  const base: string = "activityInfo__type";
  return `${base} ${base}--${activity.value.type}`;
});
</script>

<style lang="scss" scoped>
.activityInfo {
  &__type {
    padding: 0.1rem 0.3rem;

    background-color: var(--grey-200);
    border-radius: var(--border-radius-s);

    font-size: 1.8rem;
    font-weight: 700;
    text-transform: uppercase;

    &--action {
      background-color: var(--pink-100);

      color: var(--pink-500);
    }

    &--probe {
      background-color: var(--green-100);

      color: var(--green-500);
    }
  }

  &__name {
    color: var(--inline-code-color);
    font-family: monospace;
    font-size: 0.9em;
    font-weight: 700;
  }
}
</style>
