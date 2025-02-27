<template>
  <ul class="experimentMethodList list-reset pills">
    <li v-for="(item, index) in method" :key="index">
      <button
        class="experimentMethodItem pill"
        title="Click to display definition"
        @click.prevent="displayContent(item)"
      >
        {{ item.name }}
        <span
          class="experimentMethodItem__type"
          :class="`experimentMethodItem__type--${item.type}`"
        >
          {{ item.type }}
        </span>
        <span
          v-if="item.background"
          class="experimentMethodItem__type experimentMethodItem__type--background"
        >
          Background
        </span>
      </button>
      <span v-if="index < method.length - 1" role="decoration">
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
import type { Action, Probe } from "@/types/experiments";
import ModalWindow from "@/components/_ui/ModalWindow.vue";
import JsonViewer from "@/components/_ui/JsonViewer.vue";

import WorkflowArrow from "@/components/svg/WorkflowArrow.vue";

const props = defineProps<{
  method: (Action | Probe)[];
}>();
const { method } = toRefs(props);

const displayModal = ref<boolean>(false);
const modalContent = ref<string>("");
const modalTitle = ref("");
const displayContent = async (item: Action | Probe) => {
  modalContent.value = await JSON.stringify(item, null, 2);
  modalTitle.value = `${item.name} [${item.type}]`;
  displayModal.value = true;
};
const closeModal = () => {
  modalTitle.value = "";
  modalContent.value = "";
  displayModal.value = false;
};
</script>

<style lang="scss" scoped>
.experimentMethodList {
  gap: var(--workflow-arrow-spacing) !important;

  li {
    display: flex;
    align-items: center;
  }
  .experimentMethodItem {
    &__type {
      display: inline-block;
      padding: 0.1rem 0.2rem;

      border-radius: var(--border-radius-s);

      color: var(--probe-tolerance-text);
      font-size: 1.2rem;
      font-weight: 500;
      text-transform: uppercase;

      &--action {
        background-color: var(--experiment-method-action-background);

        color: var(--experiment-method-action-text);
      }

      &--probe {
        background-color: var(--experiment-method-probe-background);

        color: var(--experiment-method-probe-text);
      }

      &--background {
        margin-left: 0.6rem;

        background-color: var(--experiment-method-background-background);

        color: var(--experiment-method-background-text);
      }
    }
  }
}
</style>
