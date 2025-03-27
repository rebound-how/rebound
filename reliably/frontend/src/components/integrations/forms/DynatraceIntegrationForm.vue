<template>
  <form class="integrationForm form">
    <div class="inputWrapper" :class="{ 'inputWrapper--error': !isNameValid }">
      <label for="name"> Name <span class="required">Required</span> </label>
      <input
        type="text"
        name="name"
        id="name"
        v-model="name"
        @blur="onNameBlur"
        placeholder="Send traces to Dynatrace"
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
        Traces Endpoint <span class="required">Required</span>
      </label>
      <input
        type="text"
        name="endpoint"
        id="endpoint"
        v-model="endpoint"
        @blur="onEndpointBlur"
        placeholder="https://{your-environment-id}.live.dynatrace.com/api/v2/otlp/v1/traces"
        required
      />
      <p
        v-if="!isEndpointValid"
        class="inputWrapper__help inputWrapper__help--error"
      >
        The Dynatrace endpoint is required.<br />
      </p>
    </div>
    <div class="inputWrapper" :class="{ 'inputWrapper--error': !isTokenValid }">
      <label for="token">
        API Token <span class="required">Required</span>
      </label>
      <input
        type="text"
        name="token"
        id="token"
        v-model="token"
        @blur="onTokenBlur"
        autocomplete="off"
        required
      />
      <p
        v-if="!isTokenValid"
        class="inputWrapper__help inputWrapper__help--error"
      >
        Your API Token is required.
      </p>
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

const token = ref<string>("");
const isTokenValid = ref<boolean>(true);
function onTokenBlur(): void {
  if (token.value === "") {
    isTokenValid.value = false;
  } else {
    isTokenValid.value = true;
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
    !isTokenValid.value ||
    token.value === ""
  );
});

async function create(): Promise<void> {
  if (!isSubmitDisabled.value) {
    isCreating.value = true;
    const int: Integration = {
      name: name.value,
      provider: "opentelemetry",
      vendor: "dynatrace",
      environment: {
        name: "otel",
        used_for: "integration",
        envvars: [
          {
            var_name: "OTEL_VENDOR",
            value: "dynatrace",
          },
          {
            var_name: "OTEL_EXPORTER_OTLP_TRACES_ENDPOINT",
            value: endpoint.value,
          },
        ],
        secrets: [
          {
            key: "dynatrace-token",
            var_name: "DYNATRACE_TOKEN",
            value: token.value,
          },
        ],
      },
    };
    await createIntegration(int);
    isCreating.value = false;
  }
}
</script>
