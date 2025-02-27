<template>
  <div
    class="modal"
    :class="{ 'modal--large': isLarge, 'modal--unlimited': isUnlimited }"
  >
    <section
      class="modal__wrapper"
      ref="modalWindow"
      :style="`max-width: ${specialWidth ? specialWidth + 'rem' : 'inherit'}`"
    >
      <header v-if="hasTitle" class="modal__header">
        <h2
          class="modal__title"
          :class="{ 'modal__title--close': displayCloseButton }"
        >
          <slot name="title"></slot>
        </h2>
        <button
          v-if="displayCloseButton"
          @click="close"
          class="button button--icon tooltipped"
          aria-label="Close"
          label="Close"
        >
          <CloseIcon />
        </button>
      </header>
      <div
        class="modal__content"
        :class="{ 'modal__content--padded': hasPadding }"
      >
        <slot name="content"></slot>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, useSlots, computed, onMounted, onUnmounted } from "vue";
import { onClickOutside } from "@vueuse/core";

import CloseIcon from "@/components/svg/CloseIcon.vue";

interface Props {
  isLarge?: boolean;
  isUnlimited?: boolean;
  hasCloseButton?: boolean;
  hasPadding?: boolean;
  specialWidth?: number;
}

const props = withDefaults(defineProps<Props>(), {
  isLarge: false,
  isUnlimited: false,
  hasCloseButton: false,
  hasPadding: false,
  specialWidth: undefined,
});

const slots = useSlots();

const hasTitle = computed((): boolean => {
  return slots.title !== undefined;
});

const displayCloseButton = computed((): boolean => {
  return props.hasCloseButton !== false;
});

const emit = defineEmits<{
  (e: "close"): void;
}>();

const close = () => {
  emit("close");
};

const modalWindow = ref();

onClickOutside(modalWindow, (event) => {
  close();
});

const preventBodyScroll = (): void => {
  document.body.classList.add("no-scroll");
};

const allowBodyScroll = (): void => {
  document.body.classList.remove("no-scroll");
};

onMounted(() => {
  preventBodyScroll();
});

onUnmounted(() => {
  allowBodyScroll();
});
</script>

<style lang="scss" scoped>
.modal {
  position: fixed;
  top: 0;
  right: 0;
  bottom: 0;
  left: 0;
  z-index: 99;

  display: flex;
  align-items: center;
  justify-content: center;

  background-color: var(--modal-background);

  color: var(--text-color);

  &__wrapper {
    background-color: var(--modal-content-background);
    border-radius: var(--border-radius-l);
    box-shadow: 0 0.3em 0.9em rgba(0, 0, 0, 0.2);

    overflow-y: auto;
    max-height: 90vh;
    max-width: 40rem;
  }

  &__header {
    position: relative;
    z-index: 2;

    padding: 1.6rem;

    background-color: var(--modal-header-background);

    h2 {
      text-transform: capitalize;
    }

    button {
      position: absolute;
      top: 1.6rem;
      right: 1.6rem;

      background-color: transparent;

      color: var(--modal-close-color);

      &:hover {
        background-color: var(--modal-close-background);
      }
    }
  }

  &__title {
    margin: 0;

    color: var(--modal-title-color);

    &--close {
      padding-right: var(--space-large);
    }
  }

  &__cta {
    margin-top: var(--space-small);

    .button + .button {
      margin-left: var(--space-small);
    }
  }

  &__content {
    overflow-y: auto;

    &--padded {
      padding: var(--space-small);
    }
  }

  &--large {
    .modal__wrapper {
      max-width: 60rem;
    }
  }

  &--unlimited {
    .modal__wrapper {
      max-width: 90vw;
    }
  }
}
</style>
