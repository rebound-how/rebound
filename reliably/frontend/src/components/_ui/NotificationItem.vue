<template>
  <li class="notification" :class="classObject">
    <article>
      <div class="notification__text">
        <h3>{{ n.title }}</h3>
        <p>{{ n.message }}</p>
      </div>
      <button @click.prevent="close">Close</button>
    </article>
  </li>
</template>

<script setup lang="ts">
import { toRefs, ref, computed } from "vue";

import { removeNotification } from "@/stores/notifications";

import type { Notification } from "@/types/ui-types";

const props = defineProps<{
  n: Notification;
}>();

const { n } = toRefs(props);

const isClosing = ref<boolean>(false);

const classObject = computed(() => ({
  "notification--closing": isClosing.value,
  "notification--error": n.value.type !== undefined && n.value.type === "error",
  "notification--warning":
    n.value.type !== undefined && n.value.type === "warning",
  "notification--success":
    n.value.type !== undefined && n.value.type === "success",
}));

const close = () => {
  isClosing.value = true;
  setTimeout(function () {
    removeNotification(n.value.id!);
    isClosing.value = false;
  }, 400);
};
</script>

<style lang="scss" scoped>
.notification {
  --notificationColor: var(--grey-100);

  max-height: 30rem;

  article {
    position: relative;

    display: flex;
    width: 100%;

    padding: var(--space-small);

    // background-color: hsla(240, 3.7%, 15.88%, 0.9);
    background: var(--grey-100);
    border-radius: var(--border-radius-s);

    color: var(--text-color);

    h3 {
      margin-bottom: 0;

      color: var(--notificationColor);
      font-size: 1.6rem;
    }

    p {
      font-size: 1.4rem;
    }

    button {
      position: absolute;
      bottom: 0.6rem;
      right: 1rem;

      display: flex;
      align-items: center;
      justify-content: center;
      padding: 0.1rem 0.3rem;

      background-color: var(--grey-400);
      border: none;
      border-radius: var(--border-radius-s);
      cursor: pointer;
      opacity: 0;
      pointer-events: none;

      color: var(--text-color-bright);

      transition: all 0.1s ease-in-out;

      &:hover {
        background-color: var(--grey-800);

        color: var(--grey-100);
      }
    }
  }

  &:hover {
    button {
      opacity: 1;
      pointer-events: all;
    }
  }

  &__icon {
    display: flex;
    flex: 1 0 auto;
    align-items: center;
    width: 4rem;

    svg {
      height: 2.4rem;
      color: var(--notificationColor);
    }
  }

  &--closing {
    max-height: 1rem;
    margin-top: 0;

    transition: all 0.1s ease-in-out 0.3s;

    article {
      opacity: 0;

      transform: translateX(30rem);
      transition: all 0.2s ease-out;
    }
  }

  &--error {
    --notificationColor: var(--red-400);
  }

  &--success {
    --notificationColor: var(--green-700);
  }

  &--warning {
    --notificationColor: var(--yellow-700);
  }
}
</style>
