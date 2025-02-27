<template>
  <div
    v-if="isOK"
    class="activityFormStatus activityFormStatus--ok hasTooltip hasTooltip--top-center"
    :class="{
      'activityFormStatus--tolerance': isTolerance,
      'activityFormStatus--mini': inMinimap,
    }"
    aria-label="This activity form is complete"
    label="This activity form is complete"
  >
    <CheckIcon />
  </div>
  <div
    v-else
    class="activityFormStatus activityFormStatus--ko hasTooltip hasTooltip--top-center"
    :class="{
      'activityFormStatus--tolerance': isTolerance,
      'activityFormStatus--mini': inMinimap,
    }"
    aria-label="This activity form has required fields empty or with errors"
    label="This activity form has required fields empty or with errors"
  >
    <XIcon />
  </div>
</template>

<script setup lang="ts">
import { toRefs, computed } from "vue";

import CheckIcon from "@/components/svg/CheckIcon.vue";
import XIcon from "@/components/svg/XIcon.vue";

const props = defineProps<{
  array: boolean[];
  isTolerance?: boolean; // Is this the status of a probe tolerance?
  inMinimap?: boolean; // Is the status displayed in the minimap?
}>();
const { array, isTolerance, inMinimap } = toRefs(props);

const isOK = computed<boolean>(() => {
  return array.value.every(Boolean);
});
</script>

<style lang="scss">
.activityFormStatus {
  position: absolute;
  top: 1.2rem;
  right: 5rem;
  z-index: 3;

  display: grid;
  place-items: center;
  height: 2rem;
  width: 2rem;

  border-radius: 50%;

  color: var(--grey-100);

  transform: translateY(0.2rem);

  &--ok {
    background-color: var(--green-500);
  }

  &--ko {
    background-color: var(--red-500);
  }

  &--tolerance {
    right: var(--space-small);
  }

  svg {
    height: 1.4rem;

    stroke-width: 3;
  }

  &--mini {
    position: relative;
    top: 0;
    right: 0;

    height: 1rem;
    width: 1rem;

    transform: none;

    svg {
      display: none;
    }
  }
}
</style>
