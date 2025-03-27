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
        placeholder="Send traces to Honeycomb"
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
        placeholder="https://api.honeycomb.io/..."
        required
      />
      <p
        v-if="!isEndpointValid"
        class="inputWrapper__help inputWrapper__help--error"
      >
        The Honeycomb OTLP endpoint is required.<br />
        For OTLP/gRPC: <code>api.honeycomb.io:443</code><br />
        For OTLP/HTTPS: <code>https://api.honeycomb.io/</code>
      </p>
    </div>
    <div
      class="inputWrapper"
      :class="{ 'inputWrapper--error': !isHeadersValid }"
    >
      <label for="headers">
        API Key <span class="required">(as OTLP Headers) Required</span>
      </label>
      <input
        type="text"
        name="headers"
        id="headers"
        v-model="headers"
        @blur="onHeadersBlur"
        placeholder="x-honeycomb-team=your-api-key"
        autocomplete="off"
        required
      />
      <p
        v-if="!isHeadersValid"
        class="inputWrapper__help inputWrapper__help--error"
        v-html="invalidHeadersMessage"
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
import { createIntegration } from "@/stores/integrations";

import { validateLabelSelector } from "@/utils/strings";

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

const headers = ref<string>("");
const isHeadersValid = ref<boolean>(true);
const invalidHeadersMessage = ref<string>("");
function onHeadersBlur(): void {
  if (headers.value === "") {
    isHeadersValid.value = false;
    invalidHeadersMessage.value = "You must provide your Honeycomb API Key.";
  } else if (!validateLabelSelector(headers.value)) {
    isHeadersValid.value = false;
    invalidHeadersMessage.value =
      "Honeycomb API key must be provided in the form <code>x-honeycomb-team=your-api-key</code>";
  } else {
    isHeadersValid.value = true;
    invalidHeadersMessage.value = "";
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
    !isHeadersValid.value ||
    headers.value === ""
  );
});

async function create(): Promise<void> {
  if (!isSubmitDisabled.value) {
    isCreating.value = true;
    const int: Integration = {
      name: name.value,
      provider: "opentelemetry",
      vendor: "honeycomb",
      environment: {
        name: "otel",
        used_for: "integration",
        envvars: [
          {
            var_name: "OTEL_VENDOR",
            value: "honeycomb",
          },
          {
            var_name: "OTEL_EXPORTER_OTLP_TRACES_ENDPOINT",
            value: endpoint.value,
          },
        ],
        secrets: [
          {
            key: "otel-headers",
            var_name: "OTEL_EXPORTER_OTLP_TRACES_HEADERS",
            value: headers.value,
          },
        ],
      },
    };
    await createIntegration(int);
    isCreating.value = false;
  }
}
</script>
