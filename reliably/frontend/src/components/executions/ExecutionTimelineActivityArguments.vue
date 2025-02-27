<template>
  <ul class="activityArguments list-reset">
    <li v-for="arg in argsList" :key="arg.key">
      <div class="jsonString jsonString--envvar">{{ arg.key }}</div>
      <div class="jsonString">{{ arg.value }}</div>
    </li>
  </ul>
</template>

<script setup lang="ts">
import { toRefs, ref, onMounted } from "vue";
import { useStore } from "@nanostores/vue";

import { execution } from "@/stores/executions";

import type { Configuration, EnvConfiguration } from "@/types/experiments";
import type { Execution } from "@/types/executions";

const props = defineProps<{
  args: { [key: string]: string };
}>();

const { args } = toRefs(props);

const argsList = ref<{ key: string; value: string }[]>([]);

function buildList() {
  const ex = useStore(execution);
  const conf = ex.value?.result.experiment.configuration;
  const keys = Object.keys(args.value);
  if (keys.length) {
    keys.forEach((key) => {
      const value = (args.value as { [key: string]: string })[key];
      if (
        typeof value === "string" &&
        value.startsWith("${") &&
        value.endsWith("}")
      ) {
        if (conf === undefined) {
          argsList.value.push({
            key: key,
            value: value,
          });
        } else {
          const trimmedValue = value.slice(2, -1);
          if (conf[trimmedValue]) {
            argsList.value.push({
              key: key,
              value: (conf[trimmedValue] as EnvConfiguration).default,
            });
          } else {
            argsList.value.push({
              key: key,
              value: value,
            });
          }
        }
      } else {
        argsList.value.push({
          key: key,
          value: value,
        });
      }
    });
  }
}

onMounted(() => {
  buildList();
});
</script>

<style lang="scss" scoped>
.activityArguments {
  display: table;
  width: 100%;

  > li {
    display: table-row;

    border-radius: var(--border-radius-s);

    &:hover {
      background-color: var(--grey-200);
    }

    > div {
      display: table-cell;
      padding-top: 0.6rem;
      padding-bottom: 0.6rem;

      &:first-child {
        padding-right: var(--space-small);
      }
    }
  }
}
</style>
