<template>
  <div
    v-if="isInputVisible"
    class="activityStreamLink activityStreamLink--input"
  >
    <div class="activityStreamLink__port"></div>
  </div>
  <div
    v-if="isOutputVisible"
    class="activityStreamLink activityStreamLink--output"
  >
    <div class="activityStreamLink__port"></div>
    <div class="activityStreamLink__link"></div>
  </div>
</template>

<script setup lang="ts">
import { toRefs, computed } from "vue";

const props = defineProps<{
  first?: boolean;
  last?: boolean;
}>();

const { first, last } = toRefs(props);

const isInputVisible = computed<boolean>(() => {
  return first === undefined || !first.value;
});
const isOutputVisible = computed<boolean>(() => {
  return last === undefined || !last.value;
});
</script>

<style lang="scss" scoped>
.activityStreamLink {
  position: absolute;
  left: 50%;

  transform: translate(-50%, -50%);

  &--input {
    --topColor: var(--grey-400);
    --bottomColor: transparent;

    top: 4.7rem;
  }

  &--output {
    --topColor: transparent;
    --bottomColor: var(--grey-400);

    top: calc(100% - 0.1rem);
  }

  &__port {
    position: relative;
    height: 2.2rem;
    width: 2.2rem;
    z-index: 2;

    background-image: linear-gradient(
      180deg,
      var(--topColor) 0,
      var(--topColor) 50%,
      var(--bottomColor) 50%,
      var(--bottomColor) 100%
    );
    border-radius: 50%;

    &::before,
    &::after {
      content: "";

      position: absolute;
      top: 50%;
      left: 50%;

      display: block;

      border-radius: 50%;

      transform: translate(-50%, -50%);
    }

    &::before {
      height: 2rem;
      width: 2rem;

      background-color: var(--section-background);
    }

    &::after {
      height: 0.8rem;
      width: 0.8rem;

      background-color: var(--grey-400);
    }
  }

  &__link {
    position: absolute;
    top: 1.1rem;
    left: 50%;

    height: 11rem;
    width: 0.3rem;

    background-color: var(--grey-400);

    transform: translateX(-50%);
  }
}
</style>
