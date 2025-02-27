<template>
  <div class="infoBox">
    <span class="infoBox__trigger">
      ?
      <span class="screen-reader-text"> Hover for additional information </span>
    </span>
    <div class="infoBox__content">
      <slot />
    </div>
  </div>
</template>

<script setup lang="ts"></script>

<style lang="scss">
.infoBox {
  position: relative;

  display: inline-block;

  &__trigger {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    height: 1.8rem;
    width: 1.8rem;

    background-color: var(--infoxBox-background);
    border-radius: 50%;

    color: var(--infoxBox-color);
    font-size: 1.4rem;
  }

  &__content {
    position: absolute;
    z-index: 99;

    display: none;
    padding: var(--space-small);
    max-width: min(90vh, 50rem);
    width: max-content;

    background-color: var(--infoxBox-background);
    border-radius: var(--border-radius-s);
    opacity: 0;

    color: var(--infoxBox-color);
    font-size: 1.4rem;

    transition: opacity 0.1s ease-in-out 0;

    > p {
      margin: 0;
    }

    > p + p {
      margin-top: var(--space-small);
    }
  }

  &:hover,
  &:focus {
    .infox__trigger {
      outline: 0.1rem solid var(--form-input-focus);
    }

    .infoBox__content {
      display: block;

      opacity: 1;

      transition: opacity 0.1s ease-in-out 0.4s;
    }
  }
}
</style>
