<template>
  <section
    class="notifications"
    :class="{ 'notifications--hidden': notifs.length === 0 }"
  >
    <h2>
      Notifications
      <span
        >{{ notifs.length }} <button @click.prevent="clear">Clear</button></span
      >
    </h2>
    <ul v-if="notifs.length > 0" class="notifications__lastest list-reset">
      <NotificationItem :n="notifs[0]" />
    </ul>
    <ul class="notifications__all list-reset">
      <NotificationItem :n="n" v-for="(n, index) in notifs" :key="index" />
    </ul>
  </section>
</template>

<script setup lang="ts">
import { onMounted } from "vue";
import { useStore } from "@nanostores/vue";
import NotificationItem from "@/components/_ui/NotificationItem.vue";
import { notifications, clearNotifications } from "@/stores/notifications";

const notifs = useStore(notifications);

function clear() {
  clearNotifications();
}

onMounted(() => {});
</script>

<style lang="scss">
@use "../../styles/abstracts/mixins" as *;

.notifications {
  @include shadow;

  position: fixed;
  top: 5.2rem;
  right: var(--space-small);
  left: unset;
  z-index: 99;

  padding: var(--space-small);
  height: auto;
  width: 32rem;
  max-width: 90vw;

  background-color: white;
  border-radius: var(--border-radius-m);

  transition: transform 0.3s ease-in-out;

  h2 {
    display: flex;
    justify-content: space-between;
    margin-bottom: 0;

    span {
      position: relative;

      display: flex;
      align-items: center;
      justify-content: center;
      height: 2.4rem;
      width: 2.4rem;

      background-color: var(--red-500);
      border-radius: 1.2rem;

      color: white;
      font-size: 1.4rem;
      font-weight: 400;
      text-align: center;

      transition: width 0.3s ease-in-out;

      button {
        pointer-events: none;

        position: absolute;

        margin-left: 0.6rem;

        background-color: transparent;
        border: none;
        cursor: pointer;
        opacity: 0;

        color: white;

        transition: all 0.1s ease-in-out 0.2s;
      }
    }
  }

  ul {
    > li {
      position: relative;

      display: flex;
      align-items: flex-end;
      height: auto;
      margin-top: var(--space-small);
    }
  }

  &__all {
    height: 0;
    margin-top: 0;
    margin-bottom: 0;
    overflow: hidden;
  }

  &--hidden {
    transform: translateX(200%);
  }

  &:hover {
    h2 {
      span {
        width: 7.2rem;

        button {
          pointer-events: all;

          position: relative;

          opacity: 1;

          transition: all 0s ease-in-out;
        }
      }
    }

    .notifications__all {
      height: auto;
      max-height: 80vh;
      overflow-y: auto;
    }

    .notifications__lastest {
      display: none;
    }
  }
}
</style>
