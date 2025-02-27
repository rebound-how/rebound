<template>
  <li
    class="minimapActivity"
    :class="{ 'minimapActivity--vertical': isVertical }"
    ref="item"
  >
    <button @click.prevent="handleClick">
      <ActivityFormStatus :array="activity.fieldsStatus" :in-minimap="true" />
      <span
        v-if="isNameTooLong"
        class="minimapActivity__name"
        :title="meta.name"
      >
        {{ displayedName }}
      </span>
      <span v-else class="minimapActivity__name">{{ displayedName }}</span>
      <span
        class="minimapActivity__type"
        :class="activityTypeClass"
        :title="capitalizedType"
      >
        <span role="decoration">{{ meta.type.charAt(0) }}</span>
        <span class="screen-reader-text">{{ meta.type }}</span>
      </span>
    </button>
  </li>
</template>

<script setup lang="ts">
import { toRefs, ref, computed, onMounted } from "vue";

import { getActivityMeta } from "@/utils/builder";
import { getActivityActualTitle } from "@/stores/experiments";

import ActivityFormStatus from "@/components/starters/ActivityFormStatus.vue";

import type { TemplateActivity, Activity } from "@/types/ui-types";

const props = defineProps<{
  activity: TemplateActivity;
  isVertical?: boolean;
  blockInfo: { block: string; index: number };
}>();
const { activity, isVertical, blockInfo } = toRefs(props);

const item = ref<HTMLElement | null>(null);

const meta = ref<Activity>({
  id: "",
  name: "",
  target: "",
  category: "",
  type: "",
  description: "",
  module: "",
});

const actualTitle = ref<string>("");

function getActualTitle() {
  const t = getActivityActualTitle(
    blockInfo.value.block,
    blockInfo.value.index
  );
  if (t) {
    actualTitle.value = t;
  } else {
    actualTitle.value = meta.value.name;
  }
}

const isNameTooLong = computed<boolean>(() => {
  return actualTitle.value.length > 25;
});

const displayedName = computed<string>(() => {
  if (isNameTooLong.value) {
    return `${actualTitle.value.substring(0, 24)}...`;
  } else {
    return actualTitle.value;
  }
});

const capitalizedType = computed<string>(() => {
  return `${meta.value.type.charAt(0).toUpperCase()}${meta.value.type.slice(
    1
  )}`;
});

const activityTypeClass = computed<string>(() => {
  return `minimapActivity__type--${meta.value.type}`;
});

function handleClick() {
  const index = Array.prototype.indexOf.call(
    item.value?.parentElement?.children,
    item.value
  );
  if (isVertical && isVertical.value) {
    const parentEl = item.value?.closest(".workflowOverview__stream");
    const parentIndex = Array.prototype.indexOf.call(
      parentEl?.parentElement?.children,
      parentEl
    );
    const overview = item.value?.closest(".workflowOverview");
    const streams = overview?.nextElementSibling?.querySelector(
      ".experimentWorkflow"
    )?.children;
    const stream = streams?.[parentIndex];
    const wrapper = stream?.querySelector(".experimentStream");
    const list = stream?.querySelector(".streamDraggable")?.children;
    const target = list?.[index];
    const topPos =
      (stream as HTMLElement).getBoundingClientRect().top -
      document.body.getBoundingClientRect().top;
    const leftPos = (target as HTMLElement).offsetLeft;
    window.requestAnimationFrame(() => {
      window.scrollTo({
        top: topPos,
        left: 0,
        behavior: "smooth",
      });
    });
    window.requestAnimationFrame(() => {
      wrapper!.scrollTo({
        top: 0,
        left: leftPos,
        behavior: "smooth",
      });
    });
  } else {
    const ancestor = item.value?.closest(".scrollSync");
    const sibling = ancestor?.nextElementSibling;
    const stream = sibling?.firstElementChild;
    const list = sibling?.querySelector(".streamDraggable")?.children;
    const target = list?.[index];
    const leftPos = (target as HTMLElement).offsetLeft;
    stream!.scrollTo({
      top: 0,
      left: leftPos,
      behavior: "smooth",
    });
  }
}

onMounted(() => {
  meta.value = getActivityMeta(activity.value);
  getActualTitle();
});
</script>

<style lang="scss" scoped>
.minimapActivity {
  position: relative;

  > button {
    all: unset;

    display: inline-flex;
    flex-direction: row-reverse;
    align-items: center;
    gap: 0.6rem;
    padding: 0.6rem;

    background-color: white;
    border-radius: var(--border-radius-s);
    cursor: pointer;
  }

  &__name {
    color: var(--inline-code-color);
    font-family: var(--monospace-font);
    font-size: 1.2rem;
  }

  &__type {
    height: 1.8rem;
    width: 1.8rem;

    border-radius: var(--border-radius-s);

    font-size: 1.2rem;
    font-weight: 700;
    line-height: 1.8rem;
    text-align: center;
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
}

.minimapActivity + .minimapActivity {
  position: relative;

  &::before {
    content: "";

    position: absolute;
    top: 50%;
    left: calc(-1 * var(--space-medium));

    display: block;
    height: 0.1rem;
    width: var(--space-medium);

    background-color: var(--grey-600);
  }
}

.minimapActivity--vertical + .minimapActivity--vertical {
  &::before {
    top: 0;
    left: 1.4rem;

    height: var(--space-small);
    width: 0.1rem;

    transform: translateY(-100%);
  }
}
</style>
