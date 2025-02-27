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
    <li v-if="protocol !== undefined" class="tableList__row">
      <div class="tableList__cell">Protocol</div>
      <div class="tableList__cell jsonString jsonString--envvar">
        {{ protocol.var_name }}
      </div>
      <div class="tableList__cell">{{ protocol.value }}</div>
    </li>
    <li v-else class="tableList__row">
      <div class="tableList__cell">Protocol</div>
      <div class="tableList__cell"></div>
      <div class="tableList__cell"></div>
    </li>
    <li v-if="authorization !== undefined" class="tableList__row">
      <div class="tableList__cell">Authorization</div>
      <div class="tableList__cell jsonString jsonString--envvar">
        {{ authorization.var_name }}
      </div>
      <div class="tableList__cell">{{ authorization.value }}</div>
    </li>
    <li v-else class="tableList__row">
      <div class="tableList__cell">Authorization</div>
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
    (v) => v.var_name === "OTEL_EXPORTER_OTLP_TRACES_ENDPOINT"
  );
});

const protocol = computed<Var | undefined>(() => {
  return settings.value.envvars.find(
    (v) => v.var_name === "OTEL_EXPORTER_OTLP_TRACES_PROTOCOL"
  );
});

const authorization = computed<Secret | undefined>(() => {
  return settings.value.secrets.find((s) => s.key === "otel-headers");
});
</script>
