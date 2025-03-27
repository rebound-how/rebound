<template>
  <form class="integrationForm form">
    <div class="inputWrapper" :class="{ 'inputWrapper--error': !isNameValid }">
      <label for="name">Name <span class="required">Required</span></label>
      <input
        type="text"
        name="name"
        id="name"
        v-model="name"
        @blur="onNameBlur"
        placeholder="Autopause Execution"
        required
      />
      <p
        v-if="!isNameValid"
        class="inputWrapper__help inputWrapper__help--error"
      >
        A name for your integration is required.
      </p>
    </div>
    <div
      class="inputWrapper"
      :class="{ 'inputWrapper--error': !isSSHDurationValid }"
    >
      <label for="sshDuration">
        Steady-State Hypothesis Pauses Duration
        <span class="required">Required</span>
      </label>
      <input
        type="number"
        name="sshDuration"
        id="sshDuration"
        v-model="sshDuration"
        @blur="onDurationBlur(durations[0])"
        min="0"
        max="3600"
        step="1"
      />
      <p class="inputWrapper__help">
        Duration of the pause after each steady-state hypothesis probe, in
        seconds.<br />Maximum duration is 3600 seconds. 0 to disable.
      </p>
      <p
        v-if="!isSSHDurationValid"
        class="inputWrapper__help inputWrapper__help--error"
        v-html="invalidDurationMessage"
      ></p>
    </div>
    <div
      class="inputWrapper"
      :class="{ 'inputWrapper--error': !isMethodActionDurationValid }"
    >
      <label for="methodActionDuration">
        Method Action Pauses Duration
        <span class="required">Required</span>
      </label>
      <input
        type="number"
        name="methodActionDuration"
        id="methodActionDuration"
        v-model="methodActionDuration"
        @blur="onDurationBlur(durations[1])"
        min="0"
        max="3600"
        step="1"
      />
      <p class="inputWrapper__help">
        Duration of the pause after each method action, in seconds.<br />Maximum
        duration is 3600 seconds. 0 to disable.
      </p>
      <p
        v-if="!isMethodActionDurationValid"
        class="inputWrapper__help inputWrapper__help--error"
        v-html="invalidDurationMessage"
      ></p>
    </div>
    <div
      class="inputWrapper"
      :class="{ 'inputWrapper--error': !isMethodProbeDurationValid }"
    >
      <label for="methodProbeDuration">
        Method Probe Pauses Duration
        <span class="required">Required</span>
      </label>
      <input
        type="number"
        name="methodProbeDuration"
        id="methodProbeDuration"
        v-model="methodProbeDuration"
        @blur="onDurationBlur(durations[2])"
        min="0"
        max="3600"
        step="1"
      />
      <p class="inputWrapper__help">
        Duration of the pause after each method probe, in seconds.<br />Maximum
        duration is 3600 seconds. 0 to disable.
      </p>
      <p
        v-if="!isMethodProbeDurationValid"
        class="inputWrapper__help inputWrapper__help--error"
        v-html="invalidDurationMessage"
      ></p>
    </div>
    <div
      class="inputWrapper"
      :class="{ 'inputWrapper--error': !isRollbacksDurationValid }"
    >
      <label for="rollbacksDuration">
        Rollback Pauses Duration
        <span class="required">Required</span>
      </label>
      <input
        type="number"
        name="rollbacksDuration"
        id="rollbacksDuration"
        v-model="rollbacksDuration"
        @blur="onDurationBlur(durations[3])"
        min="0"
        max="3600"
        step="1"
      />
      <p class="inputWrapper__help">
        Duration of the pause after each rollback action, in seconds.<br />Maximum
        duration is 3600 seconds. 0 to disable.
      </p>
      <p
        v-if="!isRollbacksDurationValid"
        class="inputWrapper__help inputWrapper__help--error"
        v-html="invalidDurationMessage"
      ></p>
    </div>
    <div class="inputWrapper">
      <button
        @click.prevent="create"
        :disabled="isSubmitDisabled"
        class="button button--primary"
      >
        Create
      </button>
    </div>
  </form>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import type { Ref } from "vue";
import { createIntegration } from "@/stores/integrations";

import type { Integration } from "@/types/integrations";

const invalidDurationMessage: string =
  "Pauses can only be between 0 and 3600 seconds.";

function onDurationBlur(duration: Ref<number>): void {
  duration.value = Math.floor(duration.value);
  if (duration.value < 0) {
    duration.value = 0;
  } else if (duration.value > 3600) {
    duration.value = 3600;
  }
}

const name = ref<string>("");
const isNameValid = ref<boolean>(true);
function onNameBlur(): void {
  if (name.value === "") {
    isNameValid.value = false;
  } else {
    isNameValid.value = true;
  }
}

const sshDuration = ref<number>(120);
const sshEnabled = computed<boolean>(() => {
  return sshDuration.value > 0;
});
const isSSHDurationValid = computed<boolean>(() => {
  return sshDuration.value >= 0 && sshDuration.value <= 3600;
});

const methodActionDuration = ref<number>(120);
const methodActionEnabled = computed<boolean>(() => {
  return methodActionDuration.value > 0;
});
const isMethodActionDurationValid = computed<boolean>(() => {
  return methodActionDuration.value >= 0 && methodActionDuration.value <= 3600;
});

const methodProbeDuration = ref<number>(120);
const methodProbeEnabled = computed<boolean>(() => {
  return methodProbeDuration.value > 0;
});
const isMethodProbeDurationValid = computed<boolean>(() => {
  return methodProbeDuration.value >= 0 && methodProbeDuration.value <= 3600;
});

const rollbacksDuration = ref<number>(120);
const rollbacksEnabled = computed<boolean>(() => {
  return rollbacksDuration.value > 0;
});
const isRollbacksDurationValid = computed<boolean>(() => {
  return rollbacksDuration.value >= 0 && rollbacksDuration.value <= 3600;
});

const isCreating = ref<boolean>(false);
const isSubmitDisabled = computed<boolean>(() => {
  return (
    isCreating.value ||
    !isNameValid.value ||
    name.value === "" ||
    !isMethodProbeDurationValid.value ||
    !isMethodActionDurationValid.value ||
    !isSSHDurationValid.value ||
    !isRollbacksDurationValid.value
  );
});

function booleanToString(value: boolean): string {
  if (value) {
    return "1";
  }
  return "0";
}

// This is a wrapper that allows to use the durations refs
// in the onDurationBlur template function whithout them unwrapping.
const durations = ref<Ref<number>[]>([
  sshDuration,
  methodActionDuration,
  methodProbeDuration,
  rollbacksDuration,
]);

async function create(): Promise<void> {
  if (!isSubmitDisabled.value) {
    isCreating.value = true;
    const int: Integration = {
      name: name.value,
      provider: "autopause",
      vendor: "reliably",
      environment: {
        name: name.value,
        used_for: "integration",
        envvars: [
          {
            var_name: "RELIABLY_AUTOPAUSE_SSH_ENABLED",
            value: booleanToString(sshEnabled.value),
          },
          {
            var_name: "RELIABLY_AUTOPAUSE_ROLLBACKS_ENABLED",
            value: booleanToString(rollbacksEnabled.value),
          },
          {
            var_name: "RELIABLY_AUTOPAUSE_METHOD_ACTION_ENABLED",
            value: booleanToString(methodActionEnabled.value),
          },
          {
            var_name: "RELIABLY_AUTOPAUSE_METHOD_PROBE_ENABLED",
            value: booleanToString(methodProbeEnabled.value),
          },
          {
            var_name: "RELIABLY_AUTOPAUSE_SSH_DURATION",
            value: rollbacksDuration.value.toString(),
          },
          {
            var_name: "RELIABLY_AUTOPAUSE_ROLLBACKS_DURATION",
            value: sshDuration.value.toString(),
          },
          {
            var_name: "RELIABLY_AUTOPAUSE_METHOD_ACTION_DURATION",
            value: methodActionDuration.value.toString(),
          },
          {
            var_name: "RELIABLY_AUTOPAUSE_METHOD_PROBE_DURATION",
            value: methodProbeDuration.value.toString(),
          },
        ],
        secrets: [],
      },
    };
    await createIntegration(int);
    isCreating.value = false;
  }
}
</script>
