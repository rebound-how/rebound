<template>
  <div class="multiButtonIcon">
    <CopyIcon v-if="icon === 'copy'" />
    <RefreshCw v-else-if="icon === 'refresh'" />
    <TrashIcon v-else-if="icon === 'trash'" />
    <EditIcon v-else-if="icon === 'edit'" />
    <PlusIcon v-else-if="icon === 'plus'" />
  </div>
</template>

<script setup lang="ts">
import { toRefs } from "vue";

const props = defineProps<{
  icon: string | undefined;
}>();
const { icon } = toRefs(props);

import CopyIcon from "@/components/svg/CopyIcon.vue";
import RefreshCw from "@/components/svg/RefreshCw.vue";
import TrashIcon from "@/components/svg/TrashIcon.vue";
import EditIcon from "@/components/svg/EditIcon.vue";
import PlusIcon from "@/components/svg/PlusIcon.vue";
</script>

<style lang="scss" scoped>
.multiButtonIcon {
  display: inline-block;
  height: 1.6rem;
  width: 1.6rem;
  margin-right: 1rem;

  svg {
    height: 1.6rem;
  }
}
</style>
