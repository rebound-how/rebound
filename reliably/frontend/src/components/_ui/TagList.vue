<template>
  <ul class="tagList list-reset">
    <li v-for="(tag, index) in tags" class="tagList__item">
      <TagItem :content="tag" :key="index" />
    </li>
  </ul>
</template>

<script setup lang="ts">
import { toRefs } from "vue";
import TagItem from "@/components/_ui/TagItem.vue";

const props = defineProps<{
  tags: string[];
}>();
const { tags } = toRefs(props);
</script>

<style lang="scss" scoped>
.tagList {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-small);
}
</style>
