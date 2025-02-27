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
        placeholder="Send traces to GCP"
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
      :class="{ 'inputWrapper--error': !isServiceAccountValid }"
    >
      <label for="serviceaccount">
        Service Account Credentials <span class="required">Required</span>
      </label>
      <textarea
        rows="5"
        name="serviceaccount"
        id="serviceaccount"
        v-model="serviceAccount"
        @blur="onServiceAccountBlur"
        placeholder="Paste the content of your service account JSON file"
        required
      />
      <p
        v-if="!isServiceAccountValid"
        class="inputWrapper__help inputWrapper__help--error"
      >
        Your service account is required.<br />
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

import { generateKey } from "@/utils/strings";

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

const serviceAccount = ref<string>("");
const isServiceAccountValid = ref<boolean>(true);
function onServiceAccountBlur(): void {
  if (serviceAccount.value === "") {
    isServiceAccountValid.value = false;
  } else {
    isServiceAccountValid.value = true;
  }
}

const isCreating = ref<boolean>(false);
const isSubmitDisabled = computed<boolean>(() => {
  return (
    isCreating.value ||
    !isNameValid.value ||
    name.value === "" ||
    !isServiceAccountValid.value ||
    serviceAccount.value === ""
  );
});

async function create(): Promise<void> {
  if (!isSubmitDisabled.value) {
    isCreating.value = true;
    const identifier: string = generateKey(32);
    const int: Integration = {
      name: name.value,
      provider: "opentelemetry",
      vendor: "gcp",
      environment: {
        name: "otel",
        envvars: [
          {
            var_name: "OTEL_VENDOR",
            value: "gcp",
          },
        ],
        secrets: [
          {
            key: "gcp-creds",
            var_name: "CHAOSTOOLKIT_OTEL_GCP_SA",
            value: `/home/svc/.chaostoolkit/integrations/${identifier}/sa.json`,
          },
          {
            key: "service-account",
            path: `/home/svc/.chaostoolkit/integrations/${identifier}/sa.json`,
            value: serviceAccount.value,
          },
        ],
      },
    };
    await createIntegration(int);
    isCreating.value = false;
  }
}
</script>
