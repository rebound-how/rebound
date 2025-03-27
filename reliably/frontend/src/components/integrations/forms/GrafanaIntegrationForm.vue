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
        placeholder="Send traces to Grafana"
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
        placeholder="https://otlp-gateway-<zone>.grafana.net/otlp/v1/traces"
        required
      />
      <p
        v-if="!isEndpointValid"
        class="inputWrapper__help inputWrapper__help--error"
      >
        The Grafana OTLP traces endpoint is required. Supported zones can be found on <a href="https://grafana.com/docs/grafana-cloud/monitor-infrastructure/otlp/send-data-otlp/#before-you-begin">Grafana documentation</a>.<br />
        For OTLP/HTTPS: <code>https://otlp-gateway-[zone].grafana.net/otlp/v1/traces</code>
      </p>
    </div>
    <div
      class="inputWrapper"
      :class="{ 'inputWrapper--error': !isUsernameValid }"
    >
      <label for="headers">
        Username <span class="required"> Required</span>
      </label>
      <input
        type="text"
        name="username"
        id="username"
        v-model="username"
        @blur="onUsernameBlur"
        autocomplete="off"
        required
      />
      <p
        v-if="!isUsernameValid"
        class="inputWrapper__help inputWrapper__help--error"
        v-html="invalidUsernameMessage"
      ></p>
    </div>
    <div
      class="inputWrapper"
      :class="{ 'inputWrapper--error': !isTokenValid }"
    >
      <label for="headers">
        Password <span class="required">Required</span>
      </label>
      <input
        type="text"
        name="headers"
        id="headers"
        v-model="token"
        @blur="onTokenBlur"
        autocomplete="off"
        required
      />
      <p
        v-if="!isTokenValid"
        class="inputWrapper__help inputWrapper__help--error"
        v-html="invalidTokenMessage"
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

const username = ref<string>("");
const isUsernameValid = ref<boolean>(true);
const invalidUsernameMessage = ref<string>("");
function onUsernameBlur(): void {
  if (username.value === "") {
    isUsernameValid.value = false;
    invalidUsernameMessage.value = "The username is the instance ID of the Grafana instance.";
  } else {
    isUsernameValid.value = true;
    invalidUsernameMessage.value = "";
  }
}

const token = ref<string>("");
const isTokenValid = ref<boolean>(true);
const invalidTokenMessage = ref<string>("");
function onTokenBlur(): void {
  if (token.value === "") {
    isTokenValid.value = false;
    invalidTokenMessage.value = "The password is a cloud access policy token.";
  } else {
    isTokenValid.value = true;
    invalidTokenMessage.value = "";
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
    token.value === "" ||
    !isUsernameValid.value ||
    username.value === ""
  );
});

async function create(): Promise<void> {
  if (!isSubmitDisabled.value) {
    isCreating.value = true;
    const int: Integration = {
      name: name.value,
      provider: "opentelemetry",
      vendor: "grafana",
      environment: {
        name: "otel",
        used_for: "integration",
        envvars: [
          {
            var_name: "OTEL_VENDOR",
            value: "grafana",
          },
          {
            var_name: "OTEL_EXPORTER_OTLP_TRACES_PROTOCOL",
            value: "http/protobuf",
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
            value: "Authorization=" + encodeURIComponent("Basic ")+window.btoa(`${username.value}:${token.value}`),
          },
        ],
      },
    };
    await createIntegration(int);
    isCreating.value = false;
  }
}
</script>
