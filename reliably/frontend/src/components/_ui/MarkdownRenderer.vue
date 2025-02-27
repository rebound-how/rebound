<template>
  <div class="markdown" v-html="parsed"></div>
</template>

<script setup lang="ts">
import { toRefs, ref, computed, onMounted } from "vue";
import { marked } from "marked";
import DOMPurify from "dompurify";

const props = defineProps<{
  src: string;
}>();
const { src } = toRefs(props);

const parsed = computed<string>(() => {
  return DOMPurify.sanitize(marked(src.value));
});
</script>

<style lang="scss">
.markdown {
  > * + * {
    margin-top: var(--space-small);
  }

  ol,
  ul {
    > li + li {
      margin-top: var(--space-small);
    }
  }
}
</style>
