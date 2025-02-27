<template>
  <div class="executionsMatrixWrapper">
    <LoadingPlaceholder size="fill" v-if="isLoading" />
    <div v-else class="executionsMatrix">
      <svg width="480" height="120">
        <g transform="translate(40, 18)">
          <g
            v-for="(w, windex) in storedData.data.weeks"
            :transform="`translate(${windex * 16}, 0)`"
            class="executionsMatrix__week"
          >
            <rect
              v-for="(d, dindex) in w.days"
              width="10"
              height="10"
              x="0"
              :y="dindex * 15"
              class="executionsMatrix__day"
              :data-date="d.date"
              :data-level="computeDataLevel(d.total)"
              :data-day="d.dayinweek"
              :data-week="windex"
              rx="2"
              ry="2"
              @mouseenter.stop="handleMouseEnter"
              @mouseleave.stop="handleMouseLeave"
            >
              {{ computeDataText(d) }}
            </rect>
            <text
              v-if="isNewMonth(w.month)"
              class="executionsMatrix__label"
              x="0"
              y="-8"
            >
              {{ w.month }}
            </text>
          </g>
          <text
            class="executionsMatrix__label"
            text-anchor="start"
            dx="-30"
            dy="9"
            style="display: none"
          >
            Sun
          </text>
          <text
            class="executionsMatrix__label"
            text-anchor="start"
            dx="-30"
            dy="24"
          >
            Mon
          </text>
          <text
            class="executionsMatrix__label"
            text-anchor="start"
            dx="-30"
            dy="39"
            style="display: none"
          >
            Tue
          </text>
          <text
            class="executionsMatrix__label"
            text-anchor="start"
            dx="-30"
            dy="55"
          >
            Wed
          </text>
          <text
            class="executionsMatrix__label"
            text-anchor="start"
            dx="-30"
            dy="70"
            style="display: none"
          >
            Thu
          </text>
          <text
            class="executionsMatrix__label"
            text-anchor="start"
            dx="-30"
            dy="85"
          >
            Fri
          </text>
          <text
            class="executionsMatrix__label"
            text-anchor="start"
            dx="-30"
            dy="99"
            style="display: none"
          >
            Sat
          </text>
        </g>
      </svg>
      <div
        class="executionsMatrix__tip"
        :class="tipClasses"
        :style="`${tipY} ${tipX}`"
      >
        {{ tipContent }}
      </div>
      <div class="executionsMatrix__legend">
        <span>Less</span>
        <svg height="13" width="13">
          <rect
            width="10"
            height="10"
            x="2"
            y="2"
            class="executionsMatrix__day"
            data-level="0"
            rx="2"
            ry="2"
          ></rect>
        </svg>
        <svg height="13" width="13">
          <rect
            width="10"
            height="10"
            x="2"
            y="2"
            class="executionsMatrix__day"
            data-level="1"
            rx="2"
            ry="2"
          ></rect>
        </svg>
        <svg height="13" width="13">
          <rect
            width="10"
            height="10"
            x="2"
            y="2"
            class="executionsMatrix__day"
            data-level="2"
            rx="2"
            ry="2"
          ></rect>
        </svg>
        <svg height="13" width="13">
          <rect
            width="10"
            height="10"
            x="2"
            y="2"
            class="executionsMatrix__day"
            data-level="3"
            rx="2"
            ry="2"
          ></rect>
        </svg>
        <svg height="13" width="13">
          <rect
            width="10"
            height="10"
            x="2"
            y="2"
            class="executionsMatrix__day"
            data-level="4"
            rx="2"
            ry="2"
          ></rect>
        </svg>
        <svg height="13" width="13">
          <rect
            width="10"
            height="10"
            x="2"
            y="2"
            class="executionsMatrix__day"
            data-level="5"
            rx="2"
            ry="2"
          ></rect>
        </svg>
        <span>More</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";

import { useStore } from "@nanostores/vue";
import dayjs from "dayjs";

import { executionsForMatrix, loadExecutionsMatrix } from "@/stores/series";
import type { SeriesExecutionsForMatrixDay } from "@/types/series";

import LoadingPlaceholder from "@/components/_ui/LoadingPlaceholder.vue";

const isMounting = ref<boolean>(true);
const isLoading = computed<boolean>(() => {
  return (
    isMounting.value ||
    storedData.value.state === "empty" ||
    storedData.value.state === "loading"
  );
});
const storedData = useStore(executionsForMatrix);

function computeDataLevel(n: number): number {
  return Math.ceil((n * 5) / storedData.value.data.max);
}

function computeDataText(d: SeriesExecutionsForMatrixDay): string {
  if (d.total === 0) {
    return `No executions on ${dayjs(d.date).format("MMMM D, YYYY")}`;
  } else if (d.total === 1) {
    return `1 execution on ${dayjs(d.date).format("MMMM D, YYYY")}`;
  } else {
    return `${d.total} executions on ${dayjs(d.date).format("MMMM D, YYYY")}`;
  }
}

let currentDisplayedMonth: string = "";
function isNewMonth(month: string): boolean {
  if (month === currentDisplayedMonth) {
    return false;
  } else {
    currentDisplayedMonth = month;
    return true;
  }
}

const tipContent = ref<string>("");
const isTipVisible = ref<boolean>(false);
const tipPosition = ref<string>("left");
const tipClasses = computed(() => ({
  "executionsMatrix__tip--visible": isTipVisible.value,
  "executionsMatrix__tip--left": tipPosition.value === "left",
  "executionsMatrix__tip--right": tipPosition.value === "right",
  "executionsMatrix__tip--center": tipPosition.value === "center",
}));
const tipX = ref<string>("0");
const tipY = ref<string>("0");
function handleMouseEnter(event: MouseEvent) {
  if (event.target !== null) {
    let t = event.target;
    tipContent.value = (t as HTMLElement).innerHTML;
    tipY.value = computeTipY((t as HTMLElement).dataset.day!);
    tipX.value = computeTipX((t as HTMLElement).dataset.week!);
    isTipVisible.value = true;
  }
}
function computeTipX(week: string): string {
  let weekAsInt: number = parseInt(week);
  if (weekAsInt < 10) {
    tipPosition.value = "left";
    let value = (weekAsInt * 16 + 45).toString();
    return `left: ${value}px;`;
  } else if (weekAsInt < 20) {
    tipPosition.value = "center";
    let value = (weekAsInt * 16 + 58).toString();
    return `left: ${value}px; transform: translateX(-50%);`;
  } else {
    tipPosition.value = "right";
    let numberOfWeeks = storedData.value.data.weeks.length;
    let value = ((numberOfWeeks - weekAsInt) * 16 + 6).toString();
    return `right: ${value}px;`;
  }
}

function computeTipY(day: string): string {
  let value: string = ((parseInt(day) % 7) * 15 + 14).toString();
  return `top: ${value}px;`;
}

function handleMouseLeave() {
  isTipVisible.value = false;
}

onMounted(async () => {
  isMounting.value = true;
  await loadExecutionsMatrix();
  isMounting.value = false;
});
</script>

<style lang="scss">
.executionsMatrixWrapper {
  flex: 1 1 auto;
  padding-top: var(--space-small);
}

.executionsMatrix {
  position: relative;

  padding: var(--space-small);

  background-color: white;

  > svg {
    width: 100%;
  }

  &__day,
  &__day[data-level="0"] {
    fill: var(--grey-200);
    shape-rendering: geometricPrecision;
    background-color: var(--grey-100);
    border-radius: 0.2rem;
    outline: 0.1rem solid var(--grey-300);
  }

  &__day[data-level="1"] {
    fill: var(--green-200);
    background-color: var(--green-200);
    outline: 0.1rem solid var(--green-400);
  }

  &__day[data-level="2"] {
    fill: var(--green-300);
    background-color: var(--green-300);
    outline: 0.1rem solid var(--green-500);
  }

  &__day[data-level="3"] {
    fill: var(--green-500);
    background-color: var(--green-500);
    outline: 0.1rem solid var(--green-700);
  }

  &__day[data-level="4"] {
    fill: var(--green-600);
    background-color: var(--green-600);
    outline: 0.1rem solid var(--green-800);
  }

  &__day[data-level="5"] {
    fill: var(--green-700);
    background-color: var(--green-700);
    outline: 0.1rem solid var(--green-900);
  }

  &__label {
    padding: 0.125em 0.5em 0.125em 0;
    font-size: 1.2rem;
    font-weight: 400;
    color: var(--text-color);
    text-align: left;
    fill: var(--text-color);
  }

  &__tip {
    position: absolute;

    display: none;
    padding: 0.4rem 0.8rem;
    height: auto;
    width: auto;

    background-color: var(--grey-900);
    border-radius: var(--border-radius-s);
    pointer-events: none;

    color: white;
    font-size: 1.2rem;
    font-weight: 400;
    line-height: 1.5;
    white-space: nowrap;

    &::after {
      content: "";

      position: absolute;
      top: 100%;

      height: 0;
      width: 0;

      border: 0.6rem solid transparent;
      border-top-color: var(--grey-900);
      border-bottom: none;
    }

    &--visible {
      display: block;
    }

    &--left {
      &::after {
        left: 1rem;
      }
    }

    &--right {
      &::after {
        right: 1rem;
      }
    }

    &--center {
      &::after {
        left: calc(50% - 0.3rem);
      }
    }
  }

  &__legend {
    display: flex;
    align-items: center;
    gap: 0.2rem;
    padding-right: var(--space-small);

    color: var(--text-color-dim);
    font-size: 1.4rem;

    > :first-child {
      margin-left: auto;
    }
  }
}
</style>
