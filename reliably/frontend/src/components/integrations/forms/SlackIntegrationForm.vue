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
    <div
      class="inputWrapper"
      :class="{ 'inputWrapper--error': !isChannelValid }"
    >
      <label for="channel"
        >Channel <span class="required">Required</span></label
      >
      <input
        type="text"
        name="channel"
        id="channel"
        v-model="channel"
        @blur="onChannelBlur"
        placeholder="#channel"
        required
      />
      <p
        v-if="!isChannelValid"
        class="inputWrapper__help inputWrapper__help--error"
      >
        {{ invalidChannelMessage }}
      </p>
    </div>
    <div class="inputWrapper" :class="{ 'inputWrapper--error': !isTokenValid }">
      <label for="token"
        >Slack token <span class="required">Required</span></label
      >
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
        A
        <a
          href="https://api.slack.com/authentication/token-types"
          target="_blank"
          rel="noopener noreferer"
          >Slack access token</a
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

const channel = ref<string>("");
const isChannelValid = ref<boolean>(true);
const invalidChannelMessage = ref<string>("");
function onChannelBlur(): void {
  if (channel.value === "") {
    isChannelValid.value = false;
    invalidChannelMessage.value = "You must provide a Slack channel.";
  } else if (!channel.value.startsWith("#")) {
    isChannelValid.value = false;
    invalidChannelMessage.value = "A Slack channel must start with a #.";
  } else if (channel.value.includes(" ")) {
    isChannelValid.value = false;
    invalidChannelMessage.value = "A Slack channel can't contain spaces.";
  } else {
    isChannelValid.value = true;
    invalidChannelMessage.value = "";
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
    !isChannelValid.value ||
    channel.value === "" ||
    !isTokenValid.value ||
    token.value === ""
  );
});

async function create(): Promise<void> {
  if (!isSubmitDisabled.value) {
    isCreating.value = true;
    const int: Integration = {
      name: name.value,
      provider: "slack",
      vendor: "slack",
      environment: {
        name: "slack",
        used_for: "integration",
        envvars: [
          {
            var_name: "SLACK_CHANNEL",
            value: channel.value,
          },
        ],
        secrets: [
          {
            key: "slack-token",
            var_name: "SLACK_BOT_TOKEN",
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
