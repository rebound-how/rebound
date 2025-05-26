<template>
  <button
    @click="toggleMenu"
    class="toggle"
    :class="{ 'toggle--open': isMenuOpen }"
    type="button"
  >
    <span class="toggleBar"></span>
    <span class="screen-reader-text">Menu</span>
  </button>
</template>

<script setup lang="ts">
import { ref } from "vue";

const isMenuOpen = ref(false);

const toggleMenu = () => {
  if (isMenuOpen.value === false) {
    isMenuOpen.value = true;
    document.body.classList.add("no-scroll");
    document.body.classList.add("mobile-sidebar-on");
  } else {
    isMenuOpen.value = false;
    document.body.classList.remove("no-scroll");
    document.body.classList.remove("mobile-sidebar-on");
  }
};
</script>

<style type="text/css" lang="scss">
.toggle {
  display: inline-block;
  height: 3.6rem;
  width: 3.6rem;
  padding: 0.3rem 0.6rem;

  background-color: transparent;
  border: none;
  border-radius: var(--border-radius-s);
  cursor: pointer;

  @media (min-width: 50rem) {
    display: none;
  }

  .toggleBar {
    position: relative;

    &,
    &::before,
    &::after {
      content: "";

      display: block;
      height: 0.4rem;
      width: 2.4rem;

      background-color: var(--grey-900);

      transition: all 0.3s ease-in-out;
    }

    &::before,
    &::after {
      position: absolute;
      left: 0;
    }

    &::before {
      top: -0.7rem;
    }

    &::after {
      bottom: -0.7rem;
    }
  }

  &--open {
    .toggleBar {
      transform: rotate(-45deg);

      &:before {
        transform: translateY(0.7rem) rotate(90deg);
      }

      &::after {
        opacity: 0;
      }
    }
  }
}
</style>
