<template>
  <span class="tag">
    {{ content }}
  </span>
</template>

<script setup lang="ts">
import { toRefs } from "vue";

const props = defineProps<{
  content: string;
}>();
const { content } = toRefs(props);
</script>

<style lang="scss" scoped>
.tag {
  padding: 0.2rem 0.4rem;

  background-color: var(--tag-background);
  border-radius: var(--border-radius-s);

  color: var(--tag-text-color);
}
</style>
