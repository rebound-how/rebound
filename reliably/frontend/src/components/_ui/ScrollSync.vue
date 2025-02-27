<template>
  <div class="scrollSync" ref="scrollWrapper" :data-id="id">
    <slot />
  </div>
</template>

<script setup lang="ts">
import { toRefs, ref, onMounted } from "vue";

import { v4 as uuid } from "uuid";

const props = defineProps<{
  group: string;
}>();
const { group } = toRefs(props);

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

defineExpose({ reactToScroll });

const scrollWrapper = ref(null);
const scrollContainer = ref<HTMLElement | null>(null);
const id = ref<string>("");

function reactToScroll(
  emitter: string,
  scrollGroup: string,
  scrollLeft: number,
  scrollWidth: number,
  clientWidth: number,
  offsetWidth: number
) {
  if (emitter !== id.value && scrollGroup === group.value) {
    scrollContainer.value!.onscroll = null;
    scrollContainer.value!.scrollLeft =
      ((scrollContainer.value!.scrollWidth - clientWidth) * scrollLeft) /
      (scrollWidth - clientWidth);
    // https://github.com/metawin-m/vue-scroll-sync/blob/master/src/ScrollSync.vue
    window.requestAnimationFrame(() => {
      // requestAnimationFrame makes sure we're done scrolling
      // before re-attaching event listeners.
      // Or so I hope.
      scrollContainer.value!.onscroll = handleScroll;
    });
  }
}

function handleScroll(event: Event) {
  if (event.target) {
    const { scrollLeft, scrollWidth, clientWidth, offsetWidth } =
      event.target as HTMLElement;

    window.requestAnimationFrame(() => {
      emit(
        "scroll-sync",
        id.value,
        group.value,
        scrollLeft,
        scrollWidth,
        clientWidth,
        offsetWidth
      );
    });
  }
}

onMounted(() => {
  id.value = uuid();
  if (scrollWrapper.value) {
    scrollContainer.value = (scrollWrapper.value! as HTMLElement)
      .firstElementChild as HTMLElement;

    scrollContainer.value.onscroll = handleScroll;
  }
});
</script>
