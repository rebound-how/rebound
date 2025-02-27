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
        placeholder="Safeguards for an Execution"
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
      :class="{ 'inputWrapper--error': !isEndpointValid }"
    >
      <label for="endpoint">
        Endpoint to call during the execution
        <span class="required">Required</span>
      </label>
      <input
        type="text"
        name="endpoint"
        id="endpoint"
        v-model="endpoint"
        @blur="onEndpointBlur"
        required
      />
      <p
        v-if="!isEndpointValid"
        class="inputWrapper__help inputWrapper__help--error"
      >
        The endpoint is required.<br />
      </p>
    </div>
    <div
      class="inputWrapper"
      :class="{ 'inputWrapper--error': !isFrequencyValid }"
    >
      <label for="frequency">
        Endpoint call frequency in seconds
        <span class="required">Required</span>
      </label>
      <input
        type="number"
        name="frequency"
        id="frequency"
        v-model="frequency"
        @blur="onFrequencyBlur"
        min="1"
        max="300"
        required
      />
      <p
        v-if="!isFrequencyValid"
        class="inputWrapper__help inputWrapper__help--error"
      >
        The frequency is required.<br />
      </p>
    </div>
    <div class="inputWrapper" :class="{ 'inputWrapper--error': !isAuthValid }">
      <label for="auth">
        Endpoint authentication
        <span class="required">Prefixed by its scheme</span>
      </label>
      <input
        type="text"
        name="auth"
        id="auth"
        v-model="auth"
        @blur="onAuthBlur"
        placeholder="Bearer token"
      />
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
import { createIntegration } from "@/stores/integrations";

import type { Integration } from "@/types/integrations";

const name = ref<string>("");
const isNameValid = ref<boolean>(true);
function onNameBlur(): void {
  if (name.value === "") {
    isNameValid.value = false;
  } else {
    isNameValid.value = true;
  }
}

const endpoint = ref<string>("");
const isEndpointValid = ref<boolean>(true);
function onEndpointBlur(): void {
  if (endpoint.value === "") {
    isEndpointValid.value = false;
  } else {
    isEndpointValid.value = true;
  }
}

const frequency = ref<number>(1);
const isFrequencyValid = ref<boolean>(true);
function onFrequencyBlur(): void {
  if (frequency.value < 1 || frequency.value > 300) {
    isFrequencyValid.value = false;
  } else {
    isFrequencyValid.value = true;
  }
}

const auth = ref<string>("");
const isAuthValid = ref<boolean>(true);
function onAuthBlur(): void {
  if (auth.value === "") {
    isAuthValid.value = false;
  } else {
    isAuthValid.value = true;
  }
}

const isCreating = ref<boolean>(false);
const isSubmitDisabled = computed<boolean>(() => {
  return (
    isCreating.value ||
    !isNameValid.value ||
    name.value === "" ||
    !isEndpointValid.value ||
    endpoint.value === "" ||
    !isAuthValid.value ||
    auth.value === "" ||
    !isFrequencyValid.value
  );
});

function booleanToString(value: boolean): string {
  if (value) {
    return "1";
  }
  return "0";
}

async function create(): Promise<void> {
  if (!isSubmitDisabled.value) {
    isCreating.value = true;
    const int: Integration = {
      name: name.value,
      provider: "safeguards",
      vendor: "reliably",
      environment: {
        name: name.value,
        envvars: [
          {
            var_name: "RELIABLY_SAFEGUARDS_ENDPOINT",
            value: endpoint.value,
          },
          {
            var_name: "RELIABLY_SAFEGUARDS_FREQUENCY",
            value: frequency.value.toString(),
          },
        ],
        secrets: [
          {
            key: "safeguards-auth",
            var_name: "RELIABLY_SAFEGUARDS_ENDPOINT_AUTH",
            value: auth.value,
          },
        ],
      },
    };
    await createIntegration(int);
    isCreating.value = false;
  }
}
</script>
