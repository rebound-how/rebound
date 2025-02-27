<template>
  <button
    class="deleteButton button button--iconDanger hasTooltip hasTooltip--bottom-center"
    :aria-label="label"
    :label="label"
  >
    <UserMinus v-if="type === 'user'" />
    <TrashIcon v-else />
  </button>
</template>

<script setup lang="ts">
import { toRefs, computed } from "vue";
import TrashIcon from "@/components/svg/TrashIcon.vue";
import UserMinus from "@/components/svg/UserMinus.vue";

const props = defineProps<{
  type?: string;
}>();
const { type } = toRefs(props);

const label = computed<string>(() => {
  if (type !== undefined && type.value === "user") {
    return "Remove User";
  } else {
    return "Delete";
  }
});
</script>
