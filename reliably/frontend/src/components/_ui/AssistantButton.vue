<template>
  <button class="assistantButton">
    <span class="screen-reader-text">Reliably Assistant Message</span>
    <span v-if="count" class="assistantButton__count">{{ count }}</span>
  </button>
</template>

<script setup lang="ts">
import { toRefs } from "vue";

const props = defineProps<{
  count?: number;
}>();

const { count } = toRefs(props);
</script>

<style lang="scss" scoped>
.assistantButton {
  all: unset;

  position: relative;

  display: block;
  height: 3.2rem;
  width: 3.2rem;

  cursor: pointer;

  &::before {
    content: "";

    position: absolute;
    top: 0;
    left: 0;
    z-index: 2;

    display: block;
    height: 100%;
    width: 100%;

    background: var(--pink-500) url("/images/assistant-button.webp") no-repeat
      center center / 12.8rem;
    border-radius: 50%;
    outline: solid 0.2rem rgba(255, 255, 255, 0.5);
    outline-offset: -0.2rem;

    animation: 10s infinite assistantButton ease-in-out;
  }

  &__count {
    position: absolute;
    top: -0.4rem;
    right: -0.4rem;
    z-index: 3;

    display: grid;
    place-content: center;
    height: 1.6rem;
    width: 1.6rem;

    background-color: hsla(0, 79%, 40%, 0.9);
    border-radius: 60%;

    color: white;
    font-size: 1.2rem;
  }
}

@keyframes assistantButton {
  0% {
    transform: rotate(0) scale(1);
  }

  2% {
    transform: rotate(360deg) scale(1);
  }

  4% {
    transform: rotate(360deg) scale(1.1);
  }

  6% {
    transform: rotate(360deg) scale(0.9);
  }

  8% {
    transform: rotate(360deg) scale(1);
  }

  100% {
    transform: rotate(360deg) scale(1);
  }
}
</style>
