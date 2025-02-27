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
      <div class="executionPreview__exp">
        <a :href="`/experiments/view/?id=${execution.experiment_id}`">
          View experiment
          <strong v-if="execution.result.experiment !== undefined">{{
            execution.result.experiment.title
          }}</strong>
        </a>
      </div>
    </div>
    <div class="tableList__cell tableList__cell--middle">
      <TimeAgo
        :timestamp="execution.created_date.toString()"
        :key="timestampRefresher"
      />
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
          :page="page"
          :in-place="true"
          @close="closeDelete"
        />
      </template>
    </ModalWindow>
  </li>
</template>

<script setup lang="ts">
import { toRefs, ref, computed } from "vue";
import type { Execution, ExecutionRollback } from "@/types/executions";
import type { ExecutionUiStatus } from "@/types/ui-types";

import { getExecutionStatusObject } from "@/utils/executions";

import TimeAgo from "@/components/_ui/TimeAgo.vue";
import ModalWindow from "@/components/_ui/ModalWindow.vue";
import ConfirmDeleteExecution from "@/components/executions/ConfirmDeleteExecution.vue";
import ExecutionMiniStatus from "@/components/executions/ExecutionMiniStatus.vue";
import DeleteButton from "@/components/_ui/DeleteButton.vue";

const props = defineProps<{
  execution: Execution;
  page?: number;
  refresher?: number;
}>();
const { execution, page, refresher } = toRefs(props);

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

const timestampRefresher = computed<number>(() => {
  if (refresher && refresher.value !== undefined) {
    return refresher.value;
  } else {
    return 0;
  }
});
</script>

<style lang="scss" scoped>
.executionPreview {
  &__meta {
    a {
      font-size: 1.8rem;
      text-decoration: none;

      &:hover {
        color: var(--accentColorSecondary);
      }
    }
  }

  &__info {
    a {
      color: var(--text-color-bright);
      font-weight: 700;

      span {
        font-weight: 500;

        &:not(:hover) {
          color: var(--text-color-dim);
        }
      }
    }
  }

  &__id {
    a {
      font-weight: 700;
    }
  }

  &__exp {
    a {
      color: var(--text-color);
      font-size: 1.2rem;
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
