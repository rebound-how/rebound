<template>
  <div v-if="isLoading" class="loader">
    <span class="screen-reader-text">Please wait while we fetch your data</span>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useStore } from "@nanostores/vue";
import { counter } from "@/stores/loader";

const loaderCounter = useStore(counter);

const isLoading = computed(() => {
  if (loaderCounter.value > 0) {
    return true;
  } else {
    return false;
  }
});
</script>

<style lang="scss" scoped>
.loader {
  position: fixed;
  top: 0;
  left: 0;
  z-index: 999;

  height: 0.4rem;
  width: 100%;

  background: linear-gradient(
    90deg,
    var(--yellow-500) 0%,
    var(--yellow-500) 45%,
    var(--pink-500) 50%,
    var(--yellow-500) 55%,
    var(--yellow-500) 100%
  );
  background-size: 200% 100%;
  animation: gradient 2s linear infinite;
}

@keyframes gradient {
  0% {
    background-position: 105% 50%;
  }
  100% {
    background-position: -5% 50%;
  }
}
</style>
