<template>
  <div class="workflowOverview">
    <div class="workflowOverview__wrapper">
      <button
        @click.prevent="toggleWorkflow"
        class="workflowOverview__toggle button button--icon"
      >
        <template v-if="isWorkflowDisplayed">
          <EyeOffIcon />
          <span class="screen-reader-text">Close overview</span>
        </template>
        <template v-else>
          <EyeIcon />
          <span class="screen-reader-text">Open overview</span>
        </template>
      </button>
      <div v-if="isWorkflowDisplayed" class="workflowOverview__content">
        <div class="workflowOverview__stream">
          <p class="workflowOverview__title">Warm-up</p>
          <ul class="workflowOverview__list list-reset">
            <MinimapItem
              v-for="(activity, index) in warmupActivities"
              :activity="activity"
              :is-vertical="true"
              :block-info="{ block: 'warmup', index: index }"
              :key="activity.suffix"
            />
          </ul>
        </div>
        <div class="workflowOverview__stream">
          <p class="workflowOverview__title">Turbulence</p>
          <ul class="workflowOverview__list list-reset">
            <MinimapItem
              v-for="(activity, index) in turbulenceActivities"
              :activity="activity"
              :is-vertical="true"
              :block-info="{ block: 'turbulence', index: index }"
              :key="activity.suffix"
            />
          </ul>
        </div>
        <div class="workflowOverview__stream">
          <p class="workflowOverview__title">Verification</p>
          <ul class="workflowOverview__list list-reset">
            <MinimapItem
              v-for="(activity, index) in verificationActivities"
              :activity="activity"
              :is-vertical="true"
              :block-info="{ block: 'verification', index: index }"
              :key="activity.suffix"
            />
          </ul>
        </div>
        <div class="workflowOverview__stream">
          <p class="workflowOverview__title">Rollbacks</p>
          <ul class="workflowOverview__list list-reset">
            <MinimapItem
              v-for="(activity, index) in rollbacksActivities"
              :activity="activity"
              :is-vertical="true"
              :block-info="{ block: 'rollbacks', index: index }"
              :key="activity.suffix"
            />
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { toRefs, ref, computed } from "vue";

const props = defineProps<{
  workflow: BuilderWorkflow;
}>();
const { workflow } = toRefs(props);

import type { BuilderWorkflow, TemplateActivity } from "@/types/ui-types";

import MinimapItem from "@/components/starters/MinimapItem.vue";

import EyeIcon from "@/components/svg/EyeIcon.vue";
import EyeOffIcon from "@/components/svg/EyeOffIcon.vue";

const isWorkflowDisplayed = ref<boolean>(false);
function toggleWorkflow() {
  isWorkflowDisplayed.value = !isWorkflowDisplayed.value;
}

const warmupActivities = computed<TemplateActivity[]>(() => {
  return workflow.value.warmup;
});
const turbulenceActivities = computed<TemplateActivity[]>(() => {
  return workflow.value.method;
});
const verificationActivities = computed<TemplateActivity[]>(() => {
  return workflow.value.hypothesis;
});
const rollbacksActivities = computed<TemplateActivity[]>(() => {
  return workflow.value.rollbacks;
});
</script>

<style lang="scss" scoped>
.workflowOverview {
  position: sticky;
  top: var(--space-medium);
  left: 100%;
  z-index: 9;

  display: block;
  padding-left: var(--space-small);
  height: 0;
  width: calc((100vw - var(--max-width)) / 2);
  min-width: 30rem;

  transform: translateX(min(calc(100%), calc((100vw - var(--max-width)) / 2)));

  &__wrapper {
    position: relative;

    padding-top: var(--space-large);
  }

  &__toggle {
    position: absolute;
    top: 0;
    right: 0;
  }

  &__content {
    position: relative;

    max-height: calc(100vh - 12rem);
    overflow: auto;
    padding: var(--space-small);

    background-color: var(--grey-100);
    border-radius: var(--border-radius-s);
    box-shadow: 0px 0.2px 0.2px rgba(0, 0, 0, 0.042),
      0px 0.4px 0.5px rgba(0, 0, 0, 0.061), 0px 0.7px 1px rgba(0, 0, 0, 0.075),
      0px 1.2px 1.8px rgba(0, 0, 0, 0.089), 0px 2.1px 3.3px rgba(0, 0, 0, 0.108),
      0px 5px 8px rgba(0, 0, 0, 0.15);
  }

  &__stream {
    overflow-x: hidden;

    &:not(:last-child) {
      margin-bottom: var(--space-medium);
    }
  }

  &__title {
    margin-bottom: var(--space-small);
    color: var(--text-color-dim);
    font-size: 1.2rem;
    text-transform: uppercase;
  }

  &__list {
    li {
      &:not(:last-child) {
        margin-bottom: var(--space-small);
      }
    }
  }
}
</style>
