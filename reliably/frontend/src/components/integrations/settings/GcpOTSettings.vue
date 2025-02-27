<template>
  <ul class="tableList">
    <li class="tableList__row tableList__row--header">
      <div class="tableList__cell">Name</div>
      <div class="tableList__cell">Path</div>
      <div class="tableList__cell">Value</div>
    </li>
    <li v-if="serviceAccount !== undefined" class="tableList__row">
      <div class="tableList__cell">Service Account</div>
      <div class="tableList__cell jsonString jsonString--path">
        {{ serviceAccount.path }}
      </div>
      <div class="tableList__cell">{{ serviceAccount.value }}</div>
    </li>
    <li v-else class="tableList__row">
      <div class="tableList__cell">Service Account</div>
      <div class="tableList__cell"></div>
      <div class="tableList__cell"></div>
    </li>
  </ul>
</template>

<script setup lang="ts">
import { toRefs, computed } from "vue";

import type { Environment, Secret } from "@/types/environments";

const props = defineProps<{
  settings: Environment;
}>();

const { settings } = toRefs(props);

const serviceAccount = computed<Secret | undefined>(() => {
  const secrets = settings.value.secrets;
  return secrets.find((s) => s.key === "service-account");
});
</script>
