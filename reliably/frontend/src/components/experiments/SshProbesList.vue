<template>
  <ol class="sshProbes list-reset pills">
    <li v-for="(probe, index) in probes" :key="index" class="sshProbes__item">
      <button
        @click.prevent="displayContent(probe)"
        class="sshProbe pill"
        title="Click to display probe definition"
      >
        {{ probe.name }}
        <span class="sshProbe__tolerance" title="Tolerance">
          {{ formatTolerance(probe.tolerance) }}
        </span>
        <span v-if="probe.background" class="sshProbe__background">
          Background
        </span>
      </button>
      <span v-if="index < probes.length - 1" role="decoration">
        <WorkflowArrow />
      </span>
    </li>
  </ol>
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
import type { Probe } from "@/types/experiments";
import ModalWindow from "@/components/_ui/ModalWindow.vue";
import JsonViewer from "@/components/_ui/JsonViewer.vue";
import { formatTolerance } from "@/utils/strings";

import WorkflowArrow from "@/components/svg/WorkflowArrow.vue";

const props = defineProps<{
  probes: Probe[];
}>();
const { probes } = toRefs(props);

const displayModal = ref<boolean>(false);
const modalContent = ref<string>("");
const modalTitle = ref("");
const displayContent = async (item: Probe) => {
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
.sshProbes {
  gap: var(--workflow-arrow-spacing) !important;

  &__item {
    display: flex;
    align-items: center;
  }

  .sshProbe {
    &__tolerance,
    &__background {
      display: inline-block;
      padding: 0.1rem 0.2rem;

      border-radius: var(--border-radius-s);

      font-size: 1.2rem;
    }

    &__tolerance {
      background-color: var(--probe-tolerance-background);

      color: var(--probe-tolerance-text);
    }

    &__background {
      margin-left: 0.6rem;

      background-color: var(--experiment-method-background-background);

      color: var(--experiment-method-background-text);
      font-size: 1.2rem;
      font-weight: 500;
      text-transform: uppercase;
    }
  }
}
</style>
