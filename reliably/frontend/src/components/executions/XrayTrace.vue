<template>
  <div class="xrayTrace">
    <p class="xrayTrace__timestamp">
      Trace starts {{ humanReadableTime(start, "short", true) }}
    </p>
    <ol class="xrayTrace__list list-reset">
      <li class="xrayTrace__header">
        <div>Name</div>
        <div>Status</div>
        <div>Duration</div>
        <div>
          <span class="screen-reader-text">Timeline</span>
          <span class="timeline">
            <span
              v-for="(m, index) in marks"
              class="timeline__mark"
              :style="`left: ${(100 * index) / (marks.length - 1)}%`"
            >
              <span :class="{ 'screen-reader-text': !m.displayLegend }">
                {{ m.legend }}
              </span>
            </span>
          </span>
        </div>
      </li>
      <XrayTraceItem
        v-for="trace in source"
        :key="trace.id"
        :item="trace"
        :level="1"
        :start="start"
        :end="end"
        @update-end="updateEnd"
      />
    </ol>
  </div>
</template>

<script setup lang="ts">
import { toRefs, computed, ref } from "vue";
import XrayTraceItem from "@/components/executions/XrayTraceItem.vue";
import { humanReadableTime } from "@/utils/strings";

import type { AwsXrayItem } from "@/types/executions";

const props = defineProps<{
  source: AwsXrayItem[];
}>();

const { source } = toRefs(props);

const start = computed<number>(() => {
  return source.value[0].start_time;
});

const end = ref<number>(0);

function updateEnd(incomingEnd: number) {
  if (incomingEnd > end.value) {
    end.value = Math.ceil(incomingEnd);
  }
  generateTimeline();
}

const marks = ref<
  {
    legend: string;
    displayLegend: boolean;
  }[]
>([]);
function generateTimeline() {
  marks.value = [];

  // 20 marks at most
  // Find step between each mark
  const step: number = Math.ceil(end.value / 20);

  const totalSteps: number = end.value / step + 1;

  for (let i: number = 0; i <= totalSteps; i++) {
    marks.value.push({
      legend: `${step * i}ms`,
      displayLegend: totalSteps < 11 || i % 2 === 0,
    });
  }
}
</script>

<style lang="scss" scoped>
.xrayTrace {
  margin-top: var(--space-small);
  overflow-x: auto;

  @media print {
    overflow-x: visible;
  }

  &__timestamp {
    color: var(--text-color-dim);
    font-size: 1.4rem;
  }

  &__list {
    display: table;
    margin-top: var(--space-small);
    width: 100%;
  }

  &__header {
    display: table-row;

    color: var(--text-color-bright);
    font-weight: 500;

    > div {
      display: table-cell;

      &:not(:last-child) {
        padding-right: 1.2rem;
      }

      &:first-child {
        width: 20rem;
      }

      &:nth-child(2),
      &:nth-child(3) {
        width: 12rem;
      }

      &:nth-child(2) {
        @media print {
          display: none;
        }
      }

      &:nth-child(3) {
        padding-right: 3rem;
      }

      &:nth-child(4) {
        position: relative;

        min-width: 50rem;

        font-weight: 400;

        @media print {
          min-width: unset;
          // width: 100%;
        }
      }
    }
  }

  .timeline {
    position: absolute;
    bottom: 0;
    left: 0;

    height: 0.2rem;
    min-width: 30rem;
    width: 100%;

    background-color: var(--grey-800);

    @media print {
      display: none;
    }

    &__mark {
      position: absolute;

      bottom: 0.6rem;

      font-size: 1.4rem;
      text-align: center;

      transform: translateX(-50%);

      &--hidden {
        opacity: 0;

        pointer-events: none;
      }

      &::after {
        content: "";

        position: absolute;
        top: 100%;
        left: 50%;

        display: block;
        height: 0.6rem;
        width: 0.2rem;

        background-color: var(--grey-800);

        transform: translateX(-0.1rem);
      }
    }
  }
}
</style>
