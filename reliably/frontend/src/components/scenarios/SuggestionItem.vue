<template>
  <article class="suggestionItem">
    <div class="suggestionItem__meta">
      <span :class="`suggestionItem__type suggestionItem__type--${item.type}`">
        {{ item.type }}
      </span>
    </div>
    <div class="suggestionItem__name" v-html="breakableName(item.name)"></div>
    <div class="suggestionItem__description">{{ item.purpose }}</div>
    <div
      v-if="index > 0"
      class="suggestionItem__port suggestionItem__port--input"
    ></div>
    <div
      v-if="index < total - 1"
      class="suggestionItem__port suggestionItem__port--output"
    ></div>
  </article>
</template>

<script setup lang="ts">
import { toRefs } from "vue";

import type { ScenarioItem } from "@/types/scenarios";

import { breakableName } from "@/utils/strings";

const props = defineProps<{
  item: ScenarioItem;
  index: number;
  total: number;
}>();

const { item, index, total } = toRefs(props);
</script>

<style lang="scss" scoped>
.suggestionItem {
  position: relative;
  padding: var(--space-small);
  width: 40rem;
  max-width: 100%;

  background-color: var(--grey-100);
  border: 0.1rem solid var(--grey-400);
  border-radius: var(--border-radius-m);

  &__meta {
    display: flex;
  }

  &__type {
    padding: 0.1rem 0.3rem;

    background-color: var(--grey-200);
    border-radius: var(--border-radius-s);

    font-size: 1.2rem;
    font-weight: 700;
    text-transform: uppercase;

    &--action {
      background-color: var(--pink-100);

      color: var(--pink-500);
    }

    &--probe {
      background-color: var(--green-100);

      color: var(--green-500);
    }
  }

  &__name {
    margin-top: 0.6rem;
    margin-bottom: var(--space-small);

    color: var(--inline-code-color);
    font-family: monospace;
    font-size: 2rem;
    font-weight: 700;
  }

  &__description {
    color: var(--text-color-dim);
    font-size: 1.6rem;
  }

  &__port {
    position: absolute;
    left: calc(50% - 0.9rem);
    z-index: 2;

    height: 1.8rem;
    width: 1.8rem;

    background-image: linear-gradient(
      180deg,
      var(--topColor) 0,
      var(--topColor) 50%,
      var(--bottomColor) 50%,
      var(--bottomColor) 100%
    );
    border-radius: 50%;

    &--input {
      --topColor: var(--grey-400);
      --bottomColor: transparent;

      top: -0.9rem;
    }

    &--output {
      --topColor: transparent;
      --bottomColor: var(--grey-400);

      top: calc(100% - 0.9rem);
    }

    &::before,
    &::after {
      content: "";

      position: absolute;
      top: 50%;
      left: 50%;

      display: block;

      border-radius: 50%;

      transform: translate(-50%, -50%);
    }

    &::before {
      height: 1.6rem;
      width: 1.6rem;

      background-color: var(--section-background);
    }

    &::after {
      height: 0.8rem;
      width: 0.8rem;

      background-color: var(--grey-400);
    }
  }
}
</style>
