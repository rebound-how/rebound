<template>
  <div v-show="isMinimapDisplayed" class="minimap" ref="minimap">
    <ol class="minimap__list list-reset">
      <MinimapItem
        v-for="(activity, index) in stream"
        :activity="activity"
        :block-info="{ block: block, index: index }"
        :key="activity.suffix"
      />
    </ol>
  </div>
</template>

<script setup lang="ts">
import { toRefs, computed, ref, watch, onMounted } from "vue";

import MinimapItem from "@/components/starters/MinimapItem.vue";

// import { handleMinimapScroll } from "@/utils/builder";

import type { TemplateActivity } from "@/types/ui-types";

const props = defineProps<{
  stream: TemplateActivity[];
  block: string;
}>();

const { stream, block } = toRefs(props);

const emit = defineEmits<{
  (
    e: "scroll-sync",
    emitter: string,
    group: string,
    scrollLeft: number,
    scrollWidth: number,
    clientWidth: number,
    offsetWidth: number
  ): void;
}>();

const minimap = ref<HTMLElement | null>(null);
defineExpose({ minimap });

const items = computed<number>(() => {
  return stream.value.length;
});
const isMinimapDisplayed = ref<boolean>(false);
function updateMinimapStatus() {
  if (minimap.value) {
    const parent: HTMLElement | null = (minimap.value as HTMLElement)
      .parentElement;

    if (parent) {
      const width: number = parent.scrollWidth;
      const visibleWidth: number = width - 60; // --space-large
      const requiredWidth: number = stream.value.length * 460;

      if (requiredWidth > visibleWidth) {
        isMinimapDisplayed.value = true;
      } else {
        isMinimapDisplayed.value = false;
      }
    }
  }
  return false;
}

// function handleMinimapScroll() {
//   const { scrollLeft, scrollWidth, clientWidth, offsetWidth } =
//     minimap.value as HTMLElement;

//   console.log("handleMinimapScroll");

//   emit(
//     "scroll-sync",
//     "minimap",
//     group.value,
//     scrollLeft,
//     scrollWidth,
//     clientWidth,
//     offsetWidth
//   );
// }

watch(items, () => {
  updateMinimapStatus();
});

onMounted(() => {
  updateMinimapStatus();
});
</script>

<style lang="scss" scoped>
.minimap {
  display: block;
  width: 100%;
  overflow: auto;
  padding: var(--space-small);

  background-color: var(--grey-200);
  border-bottom-right-radius: var(--border-radius-m);
  border-bottom-left-radius: var(--border-radius-m);
  opacity: 0.5;

  transition: opacity 0.3s ease-in-out;

  &:hover {
    opacity: 1;
  }

  &__list {
    display: flex;
    gap: var(--space-medium);
  }
}
</style>
