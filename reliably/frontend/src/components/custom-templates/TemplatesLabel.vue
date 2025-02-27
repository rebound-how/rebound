<template>
  <button
    @click.prevent="updateUrlParams"
    class="templatesLabel pill"
    :class="{ 'templatesLabel--active': isActive }"
  >
    {{ label.label }}
  </button>
</template>

<script setup lang="ts">
import { toRefs, computed, ref } from "vue";
import type { TemplatesLabelObject } from "@/types/templates";

const props = defineProps<{
  label: TemplatesLabelObject;
}>();

const emit = defineEmits<{
  (e: "updateSearchParams", term: string, action: string): void;
}>();

const { label } = toRefs(props);

const isClickedActive = ref<boolean | null>(null);

const isActive = computed<boolean>(() => {
  if (isClickedActive.value !== null) {
    return isClickedActive.value;
  } else {
    return label.value.active;
  }
});

function updateUrlParams() {
  if (isClickedActive.value !== null) {
    isClickedActive.value = !isClickedActive.value;
  } else {
    isClickedActive.value = !label.value.active;
  }
  emit(
    "updateSearchParams",
    label.value.label,
    isActive.value ? "add" : "remove"
  );
}
</script>

<style lang="scss" scoped>
.templatesLabel {
  &--active {
    background-color: var(--tag-background);

    color: var(--tag-text-color);
  }
}
</style>
