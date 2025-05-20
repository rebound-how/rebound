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
        required
      />
      <p
        v-if="!isNameValid"
        class="inputWrapper__help inputWrapper__help--error"
      >
        A name for your integration is required.
      </p>
    </div>
    <div class="inputWrapper" :class="{ 'inputWrapper--error': !isKeyValid }">
      <label for="key">
        OpenAI API key <span class="required">Required</span>
      </label>
      <input
        type="text"
        name="key"
        id="key"
        v-model="key"
        @blur="onKeyBlur"
        autocomplete="off"
        required
      />
      <p
        v-if="!isKeyValid"
        class="inputWrapper__help inputWrapper__help--error"
      >
        An
        <a
          href="https://help.openai.com/en/articles/4936850-where-do-i-find-my-secret-api-key"
          target="_blank"
          rel="noopener noreferer"
          >OpenAI API key</a
        >
        is required.
      </p>
    </div>
    <div
      class="inputWrapper"
      :class="{ 'inputWrapper--error': !isOrganizationValid }"
    >
      <label for="organization">
        OpenAI organization name <span class="required">Required</span>
      </label>
      <input
        type="text"
        name="organization"
        id="organization"
        v-model="organization"
        @blur="onOrganizationBlur"
        required
      />
      <p
        v-if="!isOrganizationValid"
        class="inputWrapper__help inputWrapper__help--error"
      >
        An OpenAI organization name is required.
      </p>
    </div>
    <div class="inputWrapper">
      <label for="model">
        OpenAI model <span class="required">Required</span>
      </label>
      <select
        name="model"
        id="model"
        v-model="model"
        @blur="onModelBlur"
        required
      >
        <option value="">Select GPT model</option>
        <option value="o4-mini">o4-mini</option>
        <option value="o3-mini">o3-mini</option>
        <option value="chatgpt-4o-latest">ChatGPT-4o</option>
        <option value="gpt-4.1">gpt-4.1</option>
      </select>
      <p
        v-if="!isModelValid"
        class="inputWrapper__help inputWrapper__help--error"
      >
        Please select a GPT model to use.
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

const key = ref<string>("");
const isKeyValid = ref<boolean>(true);
function onKeyBlur(): void {
  if (key.value === "") {
    isKeyValid.value = false;
  } else {
    isKeyValid.value = true;
  }
}

const organization = ref<string>("");
const isOrganizationValid = ref<boolean>(true);
function onOrganizationBlur(): void {
  if (organization.value === "") {
    isOrganizationValid.value = false;
  } else {
    isOrganizationValid.value = true;
  }
}

const model = ref<string>("");
const isModelValid = ref<boolean>(true);
function onModelBlur(): void {
  if (model.value === "") {
    isModelValid.value = false;
  } else {
    isModelValid.value = true;
  }
}

const isCreating = ref<boolean>(false);
const isSubmitDisabled = computed<boolean>(() => {
  return (
    isCreating.value ||
    !isNameValid.value ||
    name.value === "" ||
    !isKeyValid.value ||
    key.value === "" ||
    !isOrganizationValid.value ||
    organization.value === "" ||
    !isModelValid.value ||
    model.value === ""
  );
});

async function create(): Promise<void> {
  if (!isSubmitDisabled.value) {
    isCreating.value = true;
    const int: Integration = {
      name: name.value,
      provider: "chatgpt",
      vendor: "openai",
      environment: {
        name: "openai",
        used_for: "integration",
        envvars: [
          {
            var_name: "OPENAI_MODEL",
            value: model.value,
          },
        ],
        secrets: [
          {
            key: "openai-key",
            var_name: "OPENAI_API_KEY",
            value: key.value,
          },
          {
            key: "openai-organization",
            var_name: "OPENAI_ORG",
            value: organization.value,
          },
        ],
      },
    };
    await createIntegration(int);
    isCreating.value = false;
  }
}
</script>
