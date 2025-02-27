<template>
  <button
    class="activityButton"
    :data-target="moduleArray[0]"
    :data-category="moduleArray[1]"
    :data-type="moduleArray[2]"
    @click.prevent="handleClick"
  >
    <ActivityHeader :activity="activity" />
  </button>
</template>

<script setup lang="ts">
import { toRefs, computed } from "vue";
import type { Activity } from "@/types/ui-types";
import ActivityHeader from "@/components/starters/ActivityHeader.vue";

const props = defineProps<{
  activity: Activity;
}>();
const { activity } = toRefs(props);

const moduleArray = computed<string[]>(() => {
  return activity.value.module.split(".");
});

const emit = defineEmits<{
  (e: "selectActivity", id: string): void;
}>();

function handleClick() {
  emit("selectActivity", activity.value.id);
}
</script>

<style lang="scss">
@use "../../styles/abstracts/mixins" as *;

.activityButton {
  box-sizing: border-box;
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  height: 100%;
  width: 100%;
  padding: var(--space-small);

  background-color: var(--grey-100);
  border: none;
  border-radius: var(--border-radius-m);
  cursor: pointer;

  text-align: left;

  transition: all 0.3s ease-in-out;

  &:hover {
    box-shadow: 0 0.1rem 0.3rem rgba(0, 0, 0, 0.025),
      0 0.2rem 0.4rem rgba(0, 0, 0, 0.05), 0 0.8rem 0.8rem rgba(0, 0, 0, 0.08),
      0 0.8rem 2.4rem rgba(0, 0, 0, 0.1);

    transform: translateY(-0.1rem);
    transition: all 0.1s ease-in-out;
  }
}
</style>
