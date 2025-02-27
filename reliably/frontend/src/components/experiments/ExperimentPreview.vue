<template>
  <li class="experimentPreview tableList__row">
    <div
      class="experimentPreview__score tableList__cell tableList__cell--center"
    >
      <ExperimentScoreBox
        v-if="experiment.score !== undefined"
        :score="experiment.score"
        :mini="true"
      />
    </div>
    <div class="experimentPreview__meta tableList__cell">
      <div class="experimentPreview__name">
        <a :href="`/experiments/view/?id=${experiment.id}`">
          {{ experiment.title }}
        </a>
      </div>
      <div class="experimentPreview__info">
        #{{ experiment.id }} created
        <TimeAgo :timestamp="experiment.created_date" />
        <span v-if="experiment.created_by">by {{ experiment.created_by }}</span>
      </div>
    </div>
    <div class="experimentPreview__freshness tableList__cell">
      <ExperimentFreshness
        v-if="experiment.last_execution !== undefined"
        :last="experiment.last_execution"
        :mini="true"
      />
    </div>
    <div class="experimentPreview__trend tableList__cell">
      <ExperimentTrend
        v-if="experiment.trend !== undefined && experiment.trend !== null"
        :trend="experiment.trend"
        :exp="experiment.id"
        :mini="true"
      />
    </div>
    <div class="experimentPreview__last tableList__cell">
      <TimeAgo v-if="lastExecution" :timestamp="lastExecution" />
    </div>
    <div
      class="experimentPreview__actions tableList__cell tableList__cell--small"
    >
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
        <ConfirmDeleteExperiment
          :id="experiment.id"
          :in-place="true"
          :page="page"
          @close="closeDelete"
        />
      </template>
    </ModalWindow>
  </li>
</template>

<script setup lang="ts">
import { toRefs, ref, computed } from "vue";
import type { SimpleExperiment } from "@/types/experiments";

import TimeAgo from "@/components/_ui/TimeAgo.vue";
import ModalWindow from "@/components/_ui/ModalWindow.vue";
import ExperimentScoreBox from "@/components/experiments/ExperimentScore.vue";
import ConfirmDeleteExperiment from "@/components/experiments/ConfirmDeleteExperiment.vue";
import ExperimentFreshness from "@/components/experiments/ExperimentFreshness.vue";
import ExperimentTrend from "@/components/experiments/ExperimentTrend.vue";
import DeleteButton from "@/components/_ui/DeleteButton.vue";

const props = defineProps<{
  experiment: SimpleExperiment;
  page: number;
}>();
const { experiment, page } = toRefs(props);

const lastStatus = computed<string>(() => {
  if (
    experiment.value.last_statuses !== undefined &&
    experiment.value.last_statuses.length
  ) {
    return experiment.value.last_statuses[0];
  } else {
    return "unknown";
  }
});

const lastExecution = computed<string | null>(() => {
  if (experiment.value.last_execution) {
    return experiment.value.last_execution.toString();
  } else {
    return null;
  }
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
.experimentPreview {
  &__score {
    width: 4.6rem;
  }

  &__name {
    a {
      font-size: 1.8rem;
      font-weight: 700;

      text-decoration: none;

      &:hover {
        color: var(--accentColorSecondary);
      }
    }
  }

  &__info {
    color: var(--text-color-dim);
    font-size: 1.2rem;
  }

  &__trend {
    vertical-align: bottom;
  }

  &__last,
  &__actions {
    vertical-align: middle;
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
