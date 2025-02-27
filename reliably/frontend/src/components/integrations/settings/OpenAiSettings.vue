<template>
  <ul class="tableList">
    <li class="tableList__row tableList__row--header">
      <div class="tableList__cell">Name</div>
      <div class="tableList__cell">Variable</div>
      <div class="tableList__cell">Value</div>
    </li>
    <li v-if="model !== undefined" class="tableList__row">
      <div class="tableList__cell">Model</div>
      <div class="tableList__cell jsonString jsonString--envvar">
        {{ model.var_name }}
      </div>
      <div class="tableList__cell">{{ model.value }}</div>
    </li>
    <li v-else class="tableList__row">
      <div class="tableList__cell">Model</div>
      <div class="tableList__cell"></div>
      <div class="tableList__cell"></div>
    </li>
    <li v-if="apiKey !== undefined" class="tableList__row">
      <div class="tableList__cell">API Key</div>
      <div class="tableList__cell jsonString jsonString--envvar">
        {{ apiKey.var_name }}
      </div>
      <div class="tableList__cell">{{ apiKey.value }}</div>
    </li>
    <li v-else class="tableList__row">
      <div class="tableList__cell">API Key</div>
      <div class="tableList__cell"></div>
      <div class="tableList__cell"></div>
    </li>
    <li v-if="org !== undefined" class="tableList__row">
      <div class="tableList__cell">OpenAI Organization</div>
      <div class="tableList__cell jsonString jsonString--envvar">
        {{ org.var_name }}
      </div>
      <div class="tableList__cell">{{ org.value }}</div>
    </li>
    <li v-else class="tableList__row">
      <div class="tableList__cell">OpenAI Organization</div>
      <div class="tableList__cell"></div>
      <div class="tableList__cell"></div>
    </li>
  </ul>
</template>

<script setup lang="ts">
import { toRefs, computed } from "vue";

import type { Environment, Secret, Var } from "@/types/environments";

const props = defineProps<{
  settings: Environment;
}>();

const { settings } = toRefs(props);

const model = computed<Var | undefined>(() => {
  return settings.value.envvars.find((v) => v.var_name === "OPENAI_MODEL");
});

const apiKey = computed<Secret | undefined>(() => {
  return settings.value.secrets.find((s) => s.key === "openapi-key");
});

const org = computed<Secret | undefined>(() => {
  return settings.value.secrets.find((s) => s.key === "openapi-organization");
});
</script>
