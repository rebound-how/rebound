<template>
  <div class="noData">
    <InfoIcon />
    <p>{{ message }}</p>
  </div>
</template>

<script setup lang="ts">
import { toRefs } from "vue";
import InfoIcon from "@/components/svg/InfoIcon.vue";

const props = defineProps<{
  message: string;
}>();
const { message } = toRefs(props);
</script>

<style lang="scss" scoped>
.noData {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: calc(100vh - 30rem);

  background-color: var(--grey-100);
  border-radius: var(--border-radius-s);

  color: var(--text-color-dim);

  svg {
    height: 3.6rem;
    margin-bottom: var(--space-small);
  }

  p {
    max-width: 60rem;
  }
}
</style>
