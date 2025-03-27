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
        placeholder="Create snapshot from GCP"
        required
      />
      <p
        v-if="!isNameValid"
        class="inputWrapper__help inputWrapper__help--error"
      >
        A name for your integration is required.
      </p>
    </div>
    <div class="inputWrapper" :class="{ 'inputWrapper--error': !isProjectValid }">
      <label for="project">Project <span class="required">Required</span></label>
      <input
        type="text"
        name="project"
        id="project"
        v-model="project"
        @blur="onProjectBlur"
        placeholder="A GCP project name"
        required
      />
      <p
        v-if="!isProjectValid"
        class="inputWrapper__help inputWrapper__help--error"
      >
        A project for your integration is required.
      </p>
    </div>
    <div class="inputWrapper" :class="{ 'inputWrapper--error': !isRegionValid }">
      <label for="region">Region <span class="required">Required</span></label>
      <input
        type="text"
        name="region"
        id="region"
        v-model="region"
        @blur="onRegionBlur"
        placeholder="A GCP region"
        required
      />
      <p
        v-if="!isRegionValid"
        class="inputWrapper__help inputWrapper__help--error"
      >
        A region for your integration is required.
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

const project = ref<string>("");
const isProjectValid = ref<boolean>(true);
function onProjectBlur(): void {
  if (project.value === "") {
    isProjectValid.value = false;
  } else {
    isProjectValid.value = true;
  }
}

const region = ref<string>("");
const isRegionValid = ref<boolean>(true);
function onRegionBlur(): void {
  if (region.value === "") {
    isRegionValid.value = false;
  } else {
    isRegionValid.value = true;
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
      provider: "snapshot",
      vendor: "gcp",
      environment: {
        name: `gcp-snapshot-${identifier}`,
        used_for: "integration",
        envvars: [
          {
            var_name: "LUEUR_GOOGLE_PROJECT",
            value: project.value,
          },
          {
            var_name: "LUEUR_GOOGLE_REGION",
            value: region.value,
          },
        ],
        secrets: [
          {
            key: "serviceaccount",
            var_name: "LUEUR_GOOGLE_CREDENTIALS",
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
