<template>
  <div class="loadingPlaceholder" :class="classObject">
    <ReliablyAnimated />
    <p class="screen-reader-text">Please wait while data is loading</p>
  </div>
</template>

<script setup lang="ts">
import { toRefs, computed } from "vue";
import ReliablyAnimated from "@/components/svg/ReliablyAnimated.vue";

const props = defineProps<{
  size?: string;
  transparent?: boolean;
}>();
const { size, transparent } = toRefs(props);

const classObject = computed(() => ({
  "loadingPlaceholder--large": size !== undefined && size.value === "large",
  "loadingPlaceholder--fill": size !== undefined && size.value === "fill",
  "loadingPlaceholder--transparent":
    transparent !== undefined && transparent.value === true,
}));
</script>

<style lang="scss" scoped>
.loadingPlaceholder {
  display: grid;
  place-content: center;
  height: 12rem;

  background-color: var(--grey-100);
  border-radius: var(--border-radius-s);

  svg {
    height: 4.8rem;
  }

  &--fill {
    height: 100%;
  }

  &--large {
    height: calc(100vh - 15rem);

    svg {
      height: 7.2rem;
    }
  }
}
</style>
