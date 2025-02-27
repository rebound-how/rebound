<template>
  <ul class="experimentItems list-reset pills">
    <li v-for="(item, index) in content" :key="index">
      <button
        @click.prevent="displayContent(item)"
        class="experimentItem pill"
        title="Click to display definition"
      >
        {{ item.name }}
      </button>
      <span v-if="index < content.length - 1" role="decoration">
        <WorkflowArrow />
      </span>
    </li>
  </ul>
  <ModalWindow
    v-if="displayModal"
    :isLarge="true"
    :hasCloseButton="true"
    @close="closeModal"
  >
    <template #title>{{ modalTitle }}</template>
    <template #content>
      <JsonViewer :json="modalContent" />
    </template>
  </ModalWindow>
</template>

<script setup lang="ts">
import { toRefs, ref } from "vue";
import type { Control, Extension, Action } from "@/types/experiments";
import ModalWindow from "@/components/_ui/ModalWindow.vue";
import JsonViewer from "@/components/_ui/JsonViewer.vue";

import WorkflowArrow from "@/components/svg/WorkflowArrow.vue";

const props = defineProps<{
  content: Control[] | Extension[] | Action[];
  type?: string;
}>();
const { content } = toRefs(props);

const displayModal = ref<boolean>(false);
const modalContent = ref<string>("");
const modalTitle = ref("");
const displayContent = async (item: Control | Extension | Action) => {
  modalContent.value = await JSON.stringify(item, null, 2);
  modalTitle.value = `${item.name}`;
  displayModal.value = true;
};
const closeModal = () => {
  modalTitle.value = "";
  modalContent.value = "";
  displayModal.value = false;
};
</script>

<style lang="scss" scoped>
.experimentItems {
  gap: var(--workflow-arrow-spacing) !important;

  li {
    display: flex;
    align-items: center;
  }
}
</style>
