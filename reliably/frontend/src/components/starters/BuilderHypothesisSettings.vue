<template>
  <div
    class="streamSettings"
    :class="{
      'streamSettings--hidden': !isOpen,
    }"
  >
    <form class="form">
      <div class="inputWrapper">
        <label for="verificationSettingsStrategy">
          Verification Strategy
        </label>
        <select
          id="verificationSettingsStrategy"
          name="verificationSettingsStrategy"
          v-model="settings.strategy"
        >
          <option value="default">Before and after turbulence (default)</option>
          <option value="before-method-only">Before turbulence</option>
          <option value="after-method-only">After turbulence</option>
          <option value="during-method-only">During turbulence</option>
          <option value="continuously">Continuously</option>
        </select>
        <p class="inputWrapper__help">
          When do you want to run your verification?
        </p>
      </div>
      <div
        class="inputWrapper"
        :class="{
          'inputWrapper--disabled':
            settings.strategy !== 'continuously' &&
            settings.strategy !== 'during-method-only',
        }"
      >
        <label for="verificationSettingsFrequency">
          Frequency
          <span class="required">Required</span>
        </label>
        <input
          type="number"
          id="verificationSettingsFrequency"
          name="verificationSettingsFrequency"
          v-model="settings.frequency"
        />
        <p class="inputWrapper__help">
          Number of seconds before Reliably runs your verification again, if
          your strategy is "Continuously".
        </p>
      </div>
      <div
        class="inputWrapper inputWrapper--tick"
        :class="{
          'inputWrapper--disabled':
            settings.strategy !== 'continuously' &&
            settings.strategy !== 'during-method-only',
        }"
      >
        <div>
          <input
            type="checkbox"
            id="verificationSettingsFailFast"
            name="verificationSettingsFailFast"
            v-model="settings.fail_fast"
          />
          <label for="verificationSettingsFailFast">
            Stop experiment if verification fails
          </label>
        </div>
        <p class="inputWrapper__help">
          If your strategy is "Continuously", decide if the experiment should
          stop after a failed verification.
        </p>
      </div>
    </form>
    <button @click.prevent="close" class="button button--icon">
      <XIcon />
      <span class="screen-reader-text"> Close Hypothesis Settings </span>
    </button>
  </div>
</template>

<script setup lang="ts">
import { toRefs, ref, watch, onMounted } from "vue";

import type { HypothesisRuntime } from "@/types/experiments";

import XIcon from "@/components/svg/XIcon.vue";

const props = defineProps<{
  isOpen: boolean;
  modelValue: HypothesisRuntime;
}>();

const { modelValue, isOpen } = toRefs(props);

const emit = defineEmits<{
  (e: "close"): void;
  (e: "update:modelValue", settings: HypothesisRuntime): void;
}>();

const settings = ref<HypothesisRuntime>({
  strategy: "default",
  frequency: 1,
  fail_fast: false,
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
