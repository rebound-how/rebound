<template>
  <h3>Output (Pod Logs)</h3>
  <ul class="podsLogs list-reset">
    <li v-for="pod in pods" :key="pod" class="podLog">
      <h4 class="podLog__pod">Pod: {{ pod }}</h4>
      <p class="podLog__log" v-html="addNbsps(logs[pod])"></p>
    </li>
  </ul>
</template>

<script setup lang="ts">
import { toRefs, computed } from "vue";

const props = defineProps<{
  logs: { [key: string]: string };
}>();
const { logs } = toRefs(props);

const pods = computed<string[]>(() => {
  return Object.keys(logs.value);
});

function addNbsps(str: string): string {
  return str.replaceAll(" ", "&nbsp;");
}
</script>

<style lang="scss" scoped>
h3 {
  color: var(--text-color-dim);
  font-size: 1.4rem;
  font-weight: 400;
  text-transform: uppercase;
}
.podsLogs {
  .podLog {
    &__pod {
      margin-bottom: 0;

      font-size: 1.6rem;
    }

    &__log {
      overflow-x: auto;

      word-break: keep-all;
      font-family: var(--monospace-font);
      white-space: pre-wrap;

      @media print {
        max-width: 100%;
        overflow-x: unset;

        font-size: 10px;
        word-break: break-word;
      }
    }
  }
}
</style>
