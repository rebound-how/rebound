<template>
  <div v-if="displayMessage" class="messageSent">
    <p>Your message has been sent. We will be in touch soon!</p>
    <button @click.prevent="closeMessage">
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
      <span class="screen-reader-text">Close</span>
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";

const displayMessage = ref(false);

const closeMessage = () => {
  history.pushState(
    "",
    document.title,
    window.location.pathname + window.location.search
  );
  displayMessage.value = false;
};

onMounted(() => {
  if (location.hash === "#thankyou") {
    displayMessage.value = true;
  }
});
</script>

<style lang="scss" scoped>
.messageSent {
  position: relative;

  margin: var(--space-large) auto;
  padding: var(--space-small) var(--space-medium);
  max-width: calc(60rem + 2 * var(--space-medium));

  background-color: white;
  border: 0.2rem solid var(--pink-500);
  border-radius: var(--border-radius-l);
  box-shadow: var(--box-shadow-diffuse);

  button {
    position: absolute;
    top: 0;
    right: 0;

    display: flex;
    align-items: center;
    justify-content: center;
    height: 3.2rem;
    width: 3.2rem;

    background-color: transparent;
    border: none;
    cursor: pointer;

    svg {
      height: 2rem;
    }
  }
}
</style>
