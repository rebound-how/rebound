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
      <p class="inputWrapper__help">
        Reliably Assistant currently uses ChatGPT-4 1106 Preview (AKA ChatGPT-4
        Turbo).
      </p>
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

const model = ref<string>("gpt-4-1106-preview");

const isCreating = ref<boolean>(false);
const isSubmitDisabled = computed<boolean>(() => {
  return (
    isCreating.value ||
    !isNameValid.value ||
    name.value === "" ||
    !isKeyValid.value ||
    key.value === "" ||
    model.value === ""
  );
});

async function create(): Promise<void> {
  if (!isSubmitDisabled.value) {
    isCreating.value = true;
    const int: Integration = {
      name: name.value,
      provider: "assistant",
      vendor: "reliably",
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
        ],
      },
    };
    await createIntegration(int);
    isCreating.value = false;
  }
}
</script>
