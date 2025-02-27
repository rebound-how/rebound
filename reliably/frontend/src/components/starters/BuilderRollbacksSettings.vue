<template>
  <div
    class="streamSettings"
    :class="{
      'streamSettings--hidden': !isOpen,
    }"
  >
    <form class="form">
      <div class="inputWrapper">
        <label for="rollbacksSettingsStrategy"> Rollbacks Strategy </label>
        <select
          id="rollbacksSettingsStrategy"
          name="rollbacksSettingsStrategy"
          v-model="settings.strategy"
        >
          <option value="default">
            If experiment didn't deviate (default)
          </option>
          <option value="always">Always (recommended)</option>
          <option value="never">Never</option>
          <option value="deviated">If experiment deviated</option>
        </select>
        <p class="inputWrapper__help">
          When do you want to run your rollbacks?
        </p>
      </div>
    </form>
    <button @click.prevent="close" class="button button--icon">
      <XIcon />
      <span class="screen-reader-text"> Close Rollbacks Settings </span>
    </button>
  </div>
</template>

<script setup lang="ts">
import { toRefs, ref, watch, onMounted } from "vue";

import type { RollbacksRuntime } from "@/types/experiments";

import XIcon from "@/components/svg/XIcon.vue";

const props = defineProps<{
  isOpen: boolean;
  modelValue: RollbacksRuntime;
}>();

const { modelValue, isOpen } = toRefs(props);

const emit = defineEmits<{
  (e: "close"): void;
  (e: "update:modelValue", settings: RollbacksRuntime): void;
}>();

const settings = ref<RollbacksRuntime>({
  strategy: "default",
});

watch(
  settings,
  async () => {
    emit("update:modelValue", settings.value);
  },
  { deep: true }
);

function close() {
  emit("close");
}

onMounted(() => {
  settings.value = modelValue.value;
});
</script>

<style lang="scss">
@use "../../styles/abstracts/mixins" as *;

.streamSettings {
  position: absolute;
  top: 0;
  right: var(--space-small);
  z-index: 2;

  height: calc(100% - var(--space-small));
  width: 40rem;

  background-color: white;
  border-radius: 0 0 var(--border-radius-m) var(--border-radius-m);

  transition: all 0.2s ease-in-out;

  &--hidden {
    pointer-events: none;

    opacity: 0;
    transform: translateY(-110%);
  }

  &::after {
    @include shadow;

    border-radius: 0 0 var(--border-radius-m) var(--border-radius-m);
  }

  > button {
    position: absolute;
    top: 0.6rem;
    right: 0.6rem;

    background-color: transparent;
  }

  form {
    max-height: 100%;
    overflow-y: auto;
    padding: var(--space-small);
  }
}
</style>
