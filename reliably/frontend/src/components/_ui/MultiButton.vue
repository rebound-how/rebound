<template>
  <details class="multiButton" ref="multiButton">
    <summary>{{ title }} <ChevronDown /></summary>
    <ul class="multiButton__list list-reset">
      <li v-for="button in options" :key="button.label">
        <button
          v-if="button.action"
          class="multiButton__item"
          :class="{ 'multiButton__item--warning': button.warning }"
          @click.prevent="handleAction(button.action)"
        >
          <MultiButtonIcon :icon="button.icon" />
          {{ button.label }}
        </button>
        <a
          v-if="button.link && button.disabled === true"
          class="multiButton__item multiButton__item--disabled"
          :class="{ 'multiButton__item--warning': button.warning }"
          :title="button.reason"
          @click="closeButton()"
        >
          <MultiButtonIcon :icon="button.icon" />
          {{ button.label }}
        </a>
        <a
          v-else-if="button.link"
          class="multiButton__item"
          :class="{ 'multiButton__item--warning': button.warning }"
          :href="button.link"
          @click="closeButton()"
        >
          <MultiButtonIcon :icon="button.icon" />
          {{ button.label }}
        </a>
      </li>
    </ul>
  </details>
</template>

<script setup lang="ts">
import { toRefs, ref } from "vue";
import { onClickOutside } from "@vueuse/core";

import MultiButtonIcon from "@/components/_ui/MultiButtonIcon.vue";
import ChevronDown from "@/components/svg/ChevronDown.vue";

import type { MultiButtonOption } from "@/types/ui-types";

const props = defineProps<{
  title: string;
  options: MultiButtonOption[];
}>();
const { title, options } = toRefs(props);

const emit = defineEmits<{
  (e: "emitAction", name: string): void;
}>();

const multiButton = ref();

onClickOutside(multiButton, () => {
  closeButton();
});

function handleAction(action: string) {
  closeButton();
  emit("emitAction", action);
}

function closeButton() {
  multiButton.value.removeAttribute("open");
}
</script>

<style lang="scss" scoped>
@use "../../styles/abstracts/mixins" as *;

.multiButton {
  position: relative;
  z-index: 99;

  summary {
    position: relative;
    z-index: 1;

    display: flex;
    align-items: center;
    padding: 0.8rem 1.6rem;

    background-color: var(--button-primary-background);
    border: none;
    border-radius: var(--border-radius-s);
    cursor: pointer;

    color: var(--button-primary-text);
    font-size: 1.4rem;
    font-weight: 500;
    line-height: 1.5;
    text-decoration: none;
    white-space: nowrap;

    transition: all 0.3s ease-in-out;

    &::after {
      @include shadow;

      border-radius: var(--border-radius-s);
    }

    &:hover {
      outline: none;

      text-decoration: none;

      &::after {
        opacity: 1;
      }
    }

    &:focus-visible {
      outline: 0.2rem solid var(--blue-500);
      outline-offset: 0.1rem;
    }

    svg {
      height: 1.6rem;
      margin-left: 0.6rem;
    }
  }

  &__list {
    position: absolute;
    top: calc(100% + 0.4rem);
    right: 0;

    min-width: 110%;

    background-color: white;
    border: 0.1rem solid var(--grey-200);
    border-radius: var(--border-radius-s);

    &::after {
      @include shadow;

      border-radius: var(--border-radius-s);
    }

    li {
      &:first-child {
        button {
          border-radius: 0.3rem 0.3rem 0 0;
        }
      }

      &:last-child {
        button {
          border-radius: 0 0 0.3rem 0.3rem;
        }
      }
    }
  }

  &__item {
    all: unset;

    box-sizing: border-box;
    display: flex;
    align-items: center;
    padding: 0.8rem 1.6rem;
    width: 100%;

    cursor: pointer;

    color: var(--button-secondary-text);
    font-size: 1.4rem;
    font-weight: 500;
    line-height: 1.5;
    text-decoration: none;
    white-space: nowrap;

    &:hover {
      background-color: var(--grey-200);
    }

    &--warning {
      color: var(--statusColor-ko);

      &:hover {
        background-color: var(--red-100);
      }
    }

    &--disabled {
      cursor: not-allowed;

      color: var(--text-color-dim);
    }
  }
}
</style>
