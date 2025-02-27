<template>
  <li class="executionPreview tableList__row">
    <div
      class="tableList__cell tableList__cell--center tableList__cell--status"
    >
      <ExecutionMiniStatus :status="statusObject" />
    </div>
    <div class="executionPreview__meta tableList__cell">
      <div class="executionPreview__info">
        <a
          :href="`/executions/view/?id=${execution.id}&exp=${execution.experiment_id}`"
        >
          {{ execution.id }}
        </a>
      </div>
    </div>
    <div class="tableList__cell">
      <TimeAgo :timestamp="execution.created_date.toString()" />
    </div>
    <div class="tableList__cell tableList__cell--small">
      <DeleteButton @click.prevent="displayDelete" />
    </div>
    <ModalWindow
      v-if="isDeleteDisplayed"
      :hasCloseButton="true"
      :hasPadding="true"
      @close="closeDelete"
    >
      <template #title>Delete Experiment</template>
      <template #content>
        <ConfirmDeleteExecution
          :id="execution.id"
          :exp="execution.experiment_id!"
          :onExp="true"
          :page="page"
          @close="closeDelete"
        />
      </template>
    </ModalWindow>
  </li>
</template>

<script setup lang="ts">
import { toRefs, computed, ref } from "vue";
import type { Execution } from "@/types/executions";
import type { ExecutionUiStatus } from "@/types/ui-types";

import { getExecutionStatusObject } from "@/utils/executions";

import TimeAgo from "@/components/_ui/TimeAgo.vue";
import ExecutionMiniStatus from "@/components/executions/ExecutionMiniStatus.vue";
import ModalWindow from "@/components/_ui/ModalWindow.vue";
import ConfirmDeleteExecution from "@/components/executions/ConfirmDeleteExecution.vue";
import DeleteButton from "@/components/_ui/DeleteButton.vue";

const props = defineProps<{
  execution: Execution;
  page: number;
}>();
const { execution, page } = toRefs(props);

const statusObject = computed<ExecutionUiStatus>(() => {
  return getExecutionStatusObject(execution.value);
});

const isDeleteDisplayed = ref<boolean>(false);

const displayDelete = () => {
  isDeleteDisplayed.value = true;
};
const closeDelete = () => {
  isDeleteDisplayed.value = false;
};
</script>

<style lang="scss" scoped>
.executionPreview {
  &__meta {
    a {
      text-decoration: none;

      &:hover {
        color: var(--accentColorSecondary);
      }
    }
  }

  &__info {
    a {
      color: var(--text-color);
    }
  }

  .deleteButton {
    visibility: hidden;
  }

  &:hover {
    .deleteButton {
      visibility: visible;
    }
  }
}
</style>
