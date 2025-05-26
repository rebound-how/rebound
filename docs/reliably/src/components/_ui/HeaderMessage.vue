<template>
  <div
    v-if="isChaosIqMessageDisplayed"
    class="headerMessage headerMessage--ok"
    id="headerMessage"
  >
    <div class="container">
      <p>
        ChaosIQ is now Reliably.
        <a
          href="/blog/hello-reliably"
          target="_blank"
          rel="noopener no referer"
        >
          Read More
        </a>
      </p>
    </div>
    <button
      @click.prevent="hideMessage"
      class="button button--icon button--noshadow"
    >
      <span class="screen-reader-text"> Close </span>
      <svg
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
        class="feather feather-x"
      >
        <line x1="18" y1="6" x2="6" y2="18"></line>
        <line x1="6" y1="6" x2="18" y2="18"></line>
      </svg>
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { localStorageToBoolean, booleanToLocalStorage } from "@/utils/strings";

const isChaosIqMessageDisplayed = ref<boolean>(false);

const setLocalStorage = (b: boolean): void => {
  localStorage.setItem(
    "reliably:displayChaosIQMessage",
    booleanToLocalStorage(b)
  );
};

const hideMessage = () => {
  isChaosIqMessageDisplayed.value = false;
  setLocalStorage(isChaosIqMessageDisplayed.value);
};

onMounted(() => {
  if (!localStorage.getItem("reliably:displayChaosIQMessage")) {
    setLocalStorage(true);
  }
  isChaosIqMessageDisplayed.value = localStorageToBoolean(
    localStorage.getItem("reliably:displayChaosIQMessage")
  );
});
</script>

<style lang="scss">
.headerMessage {
  position: relative;

  padding-top: 0.6rem;
  padding-bottom: 0.6rem;

  background-color: var(--accentColorPrimary);

  color: var(--text-color-bright);

  &--warning {
    background-color: #b51515;
  }

  &--ok {
    background-color: var(--pink-500);

    color: var(--pink-100);
  }

  p {
    margin: 0;

    font-weight: 500;
    text-align: center;
  }

  a {
    color: inherit;
    text-decoration: underline;
  }

  .button {
    position: absolute;
    top: 50%;
    right: 0;

    transform: translateY(-50%);

    @media (min-width: 42rem) {
      right: var(--space-medium);
    }
  }
}
</style>
