<template>
  <ul class="tableList">
    <li class="tableList__row tableList__row--header">
      <div class="tableList__cell">Name</div>
      <div class="tableList__cell">Variable</div>
      <div class="tableList__cell">Value</div>
    </li>
    <li v-if="channel !== undefined" class="tableList__row">
      <div class="tableList__cell">Channel</div>
      <div class="tableList__cell jsonString jsonString--envvar">
        {{ channel.var_name }}
      </div>
      <div class="tableList__cell">{{ channel.value }}</div>
    </li>
    <li v-else class="tableList__row">
      <div class="tableList__cell">Channel</div>
      <div class="tableList__cell"></div>
      <div class="tableList__cell"></div>
    </li>
    <li v-if="token !== undefined" class="tableList__row">
      <div class="tableList__cell">Token</div>
      <div class="tableList__cell jsonString jsonString--envvar">
        {{ token.var_name }}
      </div>
      <div class="tableList__cell">{{ token.value }}</div>
    </li>
    <li v-else class="tableList__row">
      <div class="tableList__cell">Token</div>
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

const channel = computed<Var | undefined>(() => {
  return settings.value.envvars.find((v) => v.var_name === "SLACK_CHANNEL");
});

const token = computed<Secret | undefined>(() => {
  return settings.value.secrets.find((s) => s.key === "slack-token");
});
</script>
