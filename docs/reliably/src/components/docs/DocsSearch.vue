<template>
  <div class="search">
    <button @click="openSearch" type="button" class="searchButton">
      <svg
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
        class="feather feather-search"
      >
        <circle cx="11" cy="11" r="8" />
        <line x1="21" y1="21" x2="16.65" y2="16.65" />
      </svg>
      <span>Search</span>...
    </button>
    <div class="searchModal" v-if="displaySearch">
      <div class="searchModal__content">Algolia goes there</div>
      <div @click="closeSearch" class="searchModal__overlay"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";

const displaySearch = ref(false);

const openSearch = () => {
  preventBodyScroll();
  displaySearch.value = true;
};

const closeSearch = () => {
  displaySearch.value = false;
  allowBodyScroll();
};

const preventBodyScroll = (): void => {
  document.body.classList.add("no-scroll");
};

const allowBodyScroll = (): void => {
  document.body.classList.remove("no-scroll");
};
</script>

<style lang="scss" scoped>
.search {
  .searchButton {
    display: flex;
    align-items: center;
    padding: 0.8rem 1.6rem;
    width: clamp(8rem, calc(100vw - 40rem), 50rem);
    // max-width: 32rem;

    background-color: var(--blue-800);
    border: none;
    border-radius: var(--border-radius-m);
    outline: 0.2rem solid transparent;

    color: var(--text-color);
    font-weight: 500;

    transition: all 0.3s ease-in-out;

    svg {
      height: 2rem;
      margin-right: var(--space-small);
    }

    span {
      display: none;

      @media (min-width: 42rem) {
        display: inline;
      }
    }

    &:hover {
      outline: 0.2rem solid var(--accentColorPrimary);
    }
  }

  .searchModal {
    position: fixed;
    top: 0;
    right: 0;
    bottom: 0;
    left: 0;
    z-index: 99;

    display: flex;
    align-items: flex-start;
    justify-content: center;
    padding-top: var(--header-height);

    background-color: hsla(209, 99%, 16%, 0.8); // --blue-800 at 80% opacity

    &__content {
      position: relative;
      z-index: 101;

      min-height: 32rem;
      width: 32rem;
      max-width: 90%;
      padding: var(--space-medium);

      background-color: var(--blue-900);
      border-radius: var(--border-radius-l);
      box-shadow: var(--box-shadow-diffuse);
    }

    &__overlay {
      position: absolute;
      top: 0;
      right: 0;
      bottom: 0;
      left: 0;
      z-index: 100;
    }
  }
}
</style>
