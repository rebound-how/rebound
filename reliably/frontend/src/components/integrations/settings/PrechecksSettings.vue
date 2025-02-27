<template>
  <ul class="tableList">
    <li class="tableList__row tableList__row--header">
      <div class="tableList__cell">Name</div>
      <div class="tableList__cell">Variable</div>
      <div class="tableList__cell">Value</div>
    </li>
    <li v-if="endpoint !== undefined" class="tableList__row">
      <div class="tableList__cell">Endpoint</div>
      <div class="tableList__cell jsonString jsonString--envvar">
        {{ endpoint.var_name }}
      </div>
      <div class="tableList__cell">{{ endpoint.value }}</div>
    </li>
    <li v-else class="tableList__row">
      <div class="tableList__cell">Endpoint</div>
      <div class="tableList__cell"></div>
      <div class="tableList__cell"></div>
    </li>
    <li v-if="auth !== undefined" class="tableList__row">
      <div class="tableList__cell">Endpoint authentication</div>
      <div class="tableList__cell jsonString jsonString--envvar">
        {{ auth.var_name }}
      </div>
      <div class="tableList__cell">{{ auth.value }}</div>
    </li>
    <li v-else class="tableList__row">
      <div class="tableList__cell">Endpoint authentication</div>
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

const endpoint = computed<Var | undefined>(() => {
  return settings.value.envvars.find(
    (v) => v.var_name === "RELIABLY_PRECHECKS_ENDPOINT"
  );
});

const auth = computed<Secret | undefined>(() => {
  return settings.value.secrets.find((s) => s.key === "prechecks-auth");
});
</script>
