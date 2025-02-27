<template>
  <ol
    v-if="trend !== null"
    class="list-reset experimentTrend"
    :class="mini ? 'experimentTrend--mini' : ''"
  >
    <li v-for="t in fullTrend" :key="t[0]" class="experimentTrend__item">
      <a
        v-if="t[0] !== ''"
        :href="`/executions/view/?id=${t[0]}&exp=${exp}`"
        class="experimentTrend__dot hasTooltip hasTooltip--bottom-center"
        :label="humanReadableTime(t[1])"
        :aria-label="humanReadableTime(t[1])"
        :class="scoreToClass(t[2])"
      >
        <span></span>
        <span class="screen-reader-text">
          Score: {{ t[2] }}, date: {{ humanReadableTime(t[1]) }}. View
          execution.
        </span>
      </a>
      <span v-else class="experimentTrend__dot experimentTrend__dot--empty">
        <span></span>
      </span>
    </li>
  </ol>
</template>

<script setup lang="ts">
import { toRefs, ref, onMounted } from "vue";

import { humanReadableTime } from "@/utils/strings";

const props = defineProps<{
  exp: string;
  trend: [string, string, number][] | null;
  mini?: boolean;
}>();
const { exp, trend } = toRefs(props);

const fullTrend = ref<[string, string, number][]>([]);
function fillTrend() {
  if (trend.value === null) {
    fullTrend.value = Array.from({ length: 10 }, (_, i) => ["", "", 0]);
  } else {
    fullTrend.value = trend.value;
    const toReach: number = 10 - fullTrend.value.length;
    for (let i: number = 0; i < toReach; i++) {
      fullTrend.value.unshift(["", "", 0]);
    }
  }
}

function scoreToClass(s: number): string {
  if (s === 0) {
    return "experimentTrend__dot--bad";
  } else if (s === 0.5) {
    return "experimentTrend__dot--ok";
  } else if (s === 1) {
    return "experimentTrend__dot--good";
  } else {
    return "";
  }
}

onMounted(() => {
  fillTrend();
});
</script>

<style lang="scss" scoped>
.experimentTrend {
  --base: 1.2rem;
  --hsmall: var(--base);
  --hmedium: calc(2 * var(--base));
  --hlarge: calc(3 * var(--base));

  display: flex;
  align-items: flex-end;
  gap: calc(0.5 * var(--base));

  &__item {
    display: flex;
    align-items: flex-end;
    height: var(--hlarge);
    width: var(--base);
  }

  &__dot {
    --bg: var(--grey-500);

    > span:first-child {
      display: inline-block;
      height: var(--h);
      width: var(--base);

      border-radius: calc(0.5 * var(--base));
      background-color: var(--bg);

      transition: transform 0.2s ease-in-out;
    }

    &--bad {
      --bg: rgb(255, 60, 88);

      --h: var(--hsmall);
    }

    &--ok {
      --bg: orange;

      --h: var(--hmedium);
    }

    &--good {
      --bg: var(--green-400);

      --h: var(--hlarge);
    }

    &--empty {
      --bg: transparent;

      --h: var(--hlarge);

      > span {
        border: 0.1rem dashed var(--grey-600);
      }
    }

    &:not(span):hover {
      > span:first-child {
        transform: scaleX(1.2);
      }
    }
  }

  &--mini {
    --base: 0.8rem;
  }
}
</style>
