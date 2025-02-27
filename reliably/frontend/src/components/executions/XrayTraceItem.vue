<template>
  <li class="xrayTraceItem" :data-level="level">
    <div>{{ item.name }}</div>
    <div :class="statusClass">
      <CloseIcon v-if="status.startsWith('F') || status.startsWith('E')" />
      <CheckIcon v-if="status.startsWith('O')" />
      {{ status }}
    </div>
    <div>{{ duration }}</div>
    <div class="traceWrapper">
      <span
        :class="traceClass"
        :style="`right: ${rightPosition}; left: ${leftPosition}`"
      ></span>
      <span class="traceLegend" :style="`left: ${leftPosition}`">
        {{ legend }}
      </span>
    </div>
  </li>
  <template v-if="item.subsegments && item.subsegments.length">
    <XrayTraceItem
      v-for="t in item.subsegments"
      :key="t.id"
      :item="t"
      :level="level + 1"
      :start="start"
      :end="end"
    />
  </template>
</template>

<script setup lang="ts">
import { toRefs, computed, ref, onMounted } from "vue";
import CloseIcon from "@/components/svg/CloseIcon.vue";
import CheckIcon from "@/components/svg/CheckIcon.vue";

import type { AwsXrayItem } from "@/types/executions";

const props = defineProps<{
  item: AwsXrayItem;
  level: number;
  start: number;
  end: number;
}>();
const { item, level, start, end } = toRefs(props);

const emit = defineEmits<{
  (e: "update-end", incomingEnd: number): void;
}>();

const legend = computed<string>(() => {
  let l = "";
  if (item.value.http) {
    l = `${item.value.http.request.method} ${item.value.http.request.url}`;

    if (item.value.namespace) {
      const ns = item.value.namespace;
      l = `${ns.charAt(0).toUpperCase() + ns.slice(1)}: ${l}`;
    }
  }
  return l;
});

const duration = computed<string>(() => {
  let d = Math.round(1000 * (item.value.end_time - item.value.start_time));
  return d.toString() + "ms";
});

const relativeStart = computed<number>(() => {
  const ms = 1000 * (item.value.start_time - start.value);
  return Math.round((ms + Number.EPSILON) * 100) / 100;
});

const relativeEnd = ref<number>(0);
function handleRelativeEnd() {
  const ms = 1000 * (item.value.end_time - start.value);
  relativeEnd.value = Math.round((ms + Number.EPSILON) * 100) / 100;
  emit("update-end", relativeEnd.value);
}

const status = ref<string>("");
const statusClass = ref<string>("status");
const traceClass = ref<string>("trace");
function handleStatus() {
  if (item.value.fault && item.value.fault === true) {
    status.value = "Fault (5xx)";
    statusClass.value += " status--ko";
    traceClass.value += " trace--ko";
  } else if (item.value.error && item.value.error === true) {
    status.value = "Error (4xx)";
    statusClass.value += " status--ko";
    traceClass.value += " trace--ko";
  } else {
    status.value = "OK";
    statusClass.value += " status--ok";
    traceClass.value += " trace--ok";
  }
}

const rightPosition = computed<string>(() => {
  return ((100 * (end.value - relativeEnd.value)) / end.value).toString() + "%";
});
const leftPosition = computed<string>(() => {
  return ((100 * relativeStart.value) / end.value).toString() + "%";
});

onMounted(() => {
  handleRelativeEnd();
  handleStatus();
});
</script>

<style lang="scss">
.xrayTraceItem {
  --topPadding: 0.6rem;

  display: table-row;

  > div {
    padding-bottom: 0.6rem;

    &:not(:last-child) {
      padding-right: 1.2rem;
    }

    &:nth-child(2) {
      svg {
        height: 1.4rem;
        vertical-align: middle;
      }

      @media print {
        display: none;
      }
    }
  }

  &[data-level="1"]:not(:nth-child(2)) {
    --topPadding: 1.8rem;

    > div {
      position: relative;

      &::before {
        content: "";

        position: absolute;
        top: 0.6rem;
        left: 0;

        display: block;
        height: 0.1rem;
        width: 100%;

        background-color: var(--grey-400);
      }
    }
  }

  &[data-level="2"] {
    > div:first-child {
      padding-left: var(--space-small);
    }
  }

  > div {
    display: table-cell;
    padding-top: var(--topPadding);

    white-space: nowrap;

    &.status {
      &--ko {
        color: var(--statusColor-ko);
      }

      &--ok {
        color: var(--statusColor-ok);
      }
    }
  }

  .traceWrapper {
    position: relative;
    width: 30rem;

    .trace {
      position: absolute;
      top: var(--topPadding);
      bottom: 0.6rem;

      display: block;

      border-radius: var(--border-radius-s);
      opacity: 40%;

      -webkit-print-color-adjust: exact !important;
      print-color-adjust: exact !important;

      &--ko {
        background-color: var(--statusColor-ko);
      }

      &--ok {
        background-color: var(--statusColor-ok);
      }
    }

    .traceLegend {
      position: absolute;
      left: 0;
      z-index: 2;

      display: inline-block;
      padding-left: 0.6rem;

      color: var(--text-color-bright);
      font-size: 1.4rem;
      line-height: 1.65;
    }
  }
}
</style>
