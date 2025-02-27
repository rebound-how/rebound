<template></template>

<script setup lang="ts">
import { watch } from "vue";
import { useStore } from "@nanostores/vue";

import { errors, shiftError } from "@/stores/scenarios";

import type { ScenarioError } from "@/types/scenarios";

const emit = defineEmits<{
  (e: "place-error", err: ScenarioError): void;
}>();

const list = useStore(errors);

watch(list, () => {
  placeError();
});

function placeError() {
  const currentError: ScenarioError = list.value[0];
  emit("place-error", currentError);
  shiftError();
}
</script>
