<template>
  <form v-if="field" class="form">
    <div class="inputWrapper">
      <label :for="`preview-${key}`">
        {{ field.title }}
        <span v-if="field.required" class="required"> Required </span>
      </label>
      <input
        type="text"
        :id="`preview-${key}`"
        :placeholder="field.placeholder"
        :required="field.required"
      />
      <p v-if="field.help !== ''" class="inputWrapper__help">
        {{ field.help }}
      </p>
    </div>
  </form>
</template>

<script setup lang="ts">
import { toRefs, computed } from "vue";

import type { TemplateField } from "@/types/templates";

const props = defineProps<{
  configuration: readonly TemplateField[];
  key: string;
}>();
const { configuration, key } = toRefs(props);

const field = computed<TemplateField | undefined>(() => {
  return configuration.value.find((f) => {
    return f.key === key.value;
  });
});
</script>
