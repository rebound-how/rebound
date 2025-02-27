<template>
  <div v-if="isInputVisible" class="activityLink activityLink--input">
    <div class="activityLink__port"></div>
  </div>
  <div v-if="isOutputVisible" class="activityLink activityLink--output">
    <div class="activityLink__port"></div>
    <div class="activityLink__link"></div>
  </div>
</template>

<script setup lang="ts">
import { toRefs, computed } from "vue";

const props = defineProps<{
  index: number;
  total: number;
}>();

const { index, total } = toRefs(props);

const isInputVisible = computed<boolean>(() => {
  return index.value !== 0;
});
const isOutputVisible = computed<boolean>(() => {
  return index.value !== total.value - 1;
});
</script>

<style lang="scss" scoped>
.activityLink {
  position: absolute;
  top: 6.4rem;

  transform: translate(-50%, -50%);

  &--input {
    --rightColor: transparent;
    --leftColor: var(--grey-400);

    left: 0;
  }

  &--output {
    --rightColor: var(--grey-400);
    --leftColor: transparent;

    left: 100%;
  }

  &__port {
    position: relative;
    height: 1.8rem;
    width: 1.8rem;
    z-index: 2;

    background-image: linear-gradient(
      90deg,
      var(--leftColor) 0,
      var(--leftColor) 50%,
      var(--rightColor) 50%,
      var(--rightColor) 100%
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
      height: 1.6rem;
      width: 1.6rem;

      background-color: white;
    }

    &::after {
      height: 0.8rem;
      width: 0.8rem;

      background-color: var(--grey-400);
    }
  }

  &__link {
    position: absolute;
    top: 50%;
    left: 0.9rem;

    height: 3.1rem;
    width: var(--space-large);

    background-image: linear-gradient(
      180deg,
      transparent 0,
      transparent 1.4rem,
      var(--grey-400) 1.4rem,
      var(--grey-400) 1.7rem,
      transparent 1.7rem,
      transparent 3.1rem
    );

    transform: translateY(-50%);
  }
}
</style>
