<template>
  <dl class="executionEnvironment">
    <div v-if="env" class="executionEnvironment__variables">
      <dt>Variables</dt>
      <dd>
        <ul v-if="env && sortedVars.length" class="list-reset">
          <li v-for="(v, index) in sortedVars" :key="index">
            <div class="jsonString jsonString--envvar">{{ v.var_name }}</div>
            <div class="jsonString">{{ v.value }}</div>
          </li>
        </ul>
        <p v-else>-</p>
      </dd>
    </div>
    <div v-if="env" class="executionEnvironment__secrets">
      <dt>Secrets</dt>
      <dd>
        <ul v-if="env && sortedSecrets.length" class="list-reset">
          <li v-for="(s, index) in sortedSecrets" :key="index">
            <div v-if="s.path" class="jsonString jsonString--envvar">
              {{ s.path }}
            </div>
            <div v-else-if="s.var_name" class="jsonString jsonString--envvar">
              {{ s.var_name }}
            </div>
            <div class="jsonString">{{ s.value }}</div>
          </li>
        </ul>
        <p v-else>-</p>
      </dd>
    </div>
    <div v-if="conf" class="executionEnvironment__configuration">
      <dt></dt>
      <dd>
        <ul v-if="conf && configurationArray.length" class="list-reset">
          <ExecutionEnvironmentItem
            v-for="(item, index) in configurationArray"
            :key="index"
            :item="item"
            :is-editable="isEditable"
            :experiment-id="experiment"
          />
        </ul>
        <p v-else>-</p>
      </dd>
    </div>
  </dl>
  <a
    v-if="env"
    :href="`/environments/view/?id=${env.id}`"
    class="executionEnvironment__link"
  >
    View environment details
  </a>
</template>

<script setup lang="ts">
import { toRefs, ref, computed, onMounted } from "vue";
import type { Environment, Var, Secret } from "@/types/environments";
import type { Configuration, EnvConfiguration } from "@/types/experiments";
import { hasProp } from "@/utils/objects";

import ExecutionEnvironmentItem from "@/components/executions/ExecutionEnvironmentItem.vue";

const props = defineProps<{
  env?: Environment | null;
  conf?: Configuration | null;
  isEditable?: boolean;
  experiment?: string;
}>();
const { env, conf, isEditable, experiment } = toRefs(props);

const configurationArray = ref<{ key: string; value: string }[]>([]);
function buildConfigurationArray() {
  if (conf && conf.value) {
    const keys: string[] = Object.keys(conf.value);
    const filteredKeys = keys.filter((k) => {
      return k !== "reliably_url";
    });
    filteredKeys.forEach((k) => {
      if (typeof conf!.value![k] === "string") {
        configurationArray.value.push({
          key: k,
          value: conf!.value![k] as string,
        });
      } else if (typeof conf!.value![k] === "number") {
        configurationArray.value.push({
          key: k,
          value: (conf!.value![k] as number).toString(),
        });
      } else if (Array.isArray(conf!.value![k])) {
        const v: string = (conf!.value![k] as string[]).join(", ");
        configurationArray.value.push({
          key: k,
          value: `[${v}]`,
        });
      } else if (hasProp(conf!.value![k] as Object, "key")) {
        configurationArray.value.push({
          key: k,
          value: (conf!.value![k] as EnvConfiguration).default,
        });
      } else {
        configurationArray.value.push({
          key: k,
          value: conf!.value![k] as string,
        });
      }
    });
    configurationArray.value.sort((a, b) => {
      return a.key.localeCompare(b.key);
    });
  } else {
    return [];
  }
}

const sortedVars = computed<Var[]>(() => {
  if (env?.value?.envvars.length) {
    return env.value.envvars.sort((a, b) => {
      return a.var_name.localeCompare(b.var_name);
    });
  } else {
    return [];
  }
});

const sortedSecrets = computed<Secret[]>(() => {
  if (env?.value?.secrets.length) {
    return env.value.secrets.sort((a, b) => {
      let aKey: string = a.var_name ? a.var_name : a.path!;
      let bKey: string = b.var_name ? b.var_name : b.path!;
      return aKey.localeCompare(bKey);
    });
  } else {
    return [];
  }
});

onMounted(() => {
  buildConfigurationArray();
});
</script>

<style lang="scss" scoped>
.executionEnvironment {
  display: flex;
  gap: var(--space-medium);
  margin: 0;
  padding: var(--space-small) calc(var(--space-small) / 2);

  background-color: var(--section-background);
  border-radius: var(--border-radius-s);

  @media print {
    flex-direction: column;
  }

  > div {
    flex: 1;
  }

  > div + div {
    padding-left: var(--space-small);

    border-left: 0.1rem solid var(--section-separator-color);

    @media print {
      padding-left: 0 !important;

      border: none !important;
    }
  }

  dt {
    padding-left: calc(var(--space-small) / 2);

    color: var(--text-color-dim);
    font-size: 1.4rem;
    text-transform: uppercase;
  }

  dd {
    ul {
      display: table;
      width: 100%;

      > li {
        display: table-row;

        &:hover {
          background-color: var(--grey-200);
        }

        > div {
          display: table-cell;
          padding-top: 0.6rem;
          padding-right: var(--space-small);
          padding-bottom: 0.6rem;

          &:first-child {
            padding-left: calc(var(--space-small) / 2);
          }
        }
      }
    }
  }

  &__link {
    position: absolute;

    top: 0.6rem;
    right: 0;
  }
}
</style>
