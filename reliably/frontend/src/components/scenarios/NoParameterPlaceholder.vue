<template>
  <div v-if="debug">
    <div><strong>HERE IS A PLACEHOLDER</strong></div>
    <div>{{ item }}</div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, toRefs } from "vue";

import type { UiScenarioActivity } from "@/types/scenarios";

const props = defineProps<{
  item: UiScenarioActivity;
  debug?: boolean;
}>();

const { item, debug } = toRefs(props);

const emit = defineEmits<{
  (e: "go-to-next"): void;
}>();

onMounted(() => {
  if (debug && debug.value) {
    console.log(`Force go-to-next for item ${item.value.name}`);
  }
  emit("go-to-next");
});
</script>
