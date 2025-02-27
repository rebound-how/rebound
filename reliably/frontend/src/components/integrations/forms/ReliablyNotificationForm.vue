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
    <fieldset>
      <legend>Triggering Events</legend>
      <div class="inputWrapper">
        <label for="model">
          Get Notified On <span class="required">Required</span>
        </label>
        <select
            type="checkbox"
            v-model="notifyOnEvent"
            name="notifyOnEvent"
            id="notifyOnEvent"
          >
          <option value="">Select Event Type</option>
          <option value="plan-phases">Plan Phases</option>
        </select>
      </div>
        <p v-if="notifyOnEvent=='plan-phases'" class="inputWrapper__help">
          Get notified about plan start, finish, fail or state.
        </p>
    </fieldset>
    <fieldset>
      <legend>Channels</legend>
      <div class="channelSelector">
        <div>
          <input
            type="checkbox"
            v-model="useEmailChannel"
            name="channelEmail"
            id="channelEmail"
          />
          <label for="channelEmail" title="Email">
            <span class="screen-reader-text">Email</span>
            Email
          </label>
        </div>
        <div>
          <input
            type="checkbox"
            v-model="useWebhookChannel"
            name="channelWebhook"
            id="channelWebhook"
          />
          <label for="channelWebhook" title="WebHook">
            <span class="screen-reader-text">WebHook</span>
            WebHook
          </label>
        </div>
        <div>
          <input
            type="checkbox"
            v-model="useGHChannel"
            name="channelGitHub"
            id="channelGitHub"
          />
          <label for="channelGitHub" title="GitHub">
            <span class="screen-reader-text">GitHub</span>
            GitHub
          </label>
        </div>
      </div>
    </fieldset>
    <fieldset v-if="useEmailChannel">
      <legend>Email Settings</legend>
      <div class="inputWrapper">
        <label for="emailToAddresses">
          To
          <span class="required">Required</span>
        </label>
        <input
          type="text"
          name="emailToAddresses"
          id="emailToAddresses"
          v-model="emailToAddresses"
          autocomplete="off"
          placeholder="jane@example.com,peter@example.com"
          @blur="onEmailToAddressesBlur"
          required
        />
        <p class="inputWrapper__help">
          Reliably will send an email to each individual recipient with an
          appropriate message for each event type and a link to the plan.
        </p>
      </div>
    </fieldset>
    <fieldset v-if="useWebhookChannel">
      <legend>WebHook Settings</legend>
      <div class="inputWrapper">
        <label for="webhookUrl">
          URL
          <span class="required">Required</span>
        </label>
        <input
          type="text"
          name="webhookUrl"
          id="webhookUrl"
          v-model="webhookUrl"
          autocomplete="off"
          @blur="onWebhookUrlBlur"
          required
        />
        <p class="inputWrapper__help">
          Reliably will make a POST request to that endpoint with the event's
          payload as a JSON encoded string.
        </p>
      </div>
      <div class="inputWrapper">
        <label for="webhookBearerToken">
          Bearer Token
        </label>
        <input
          type="text"
          name="webhookBearerToken"
          id="webhookBearerToken"
          v-model="webhookBearerToken"
          autocomplete="off"
          @blur="onWebhookBearerTokenBlur"
        />
        <p class="inputWrapper__help">
          You can provide an authentication header value in the form of
          a bearer token if your endpoint requires it.
        </p>
      </div>
    </fieldset>
    <fieldset v-if="useGHChannel">
      <legend>GitHub Settings</legend>
      <div class="inputWrapper">
        <label for="repositoryUrl">
          Repository
          <span class="required">Required</span>
        </label>
        <input
          type="text"
          name="repositoryUrl"
          id="repositoryUrl"
          v-model="repositoryUrl"
          autocomplete="off"
          @blur="onRepositoryUrlBlur"
          required
        />
        <p class="inputWrapper__help">
          Reliably will create an issue on the given repository.
        </p>
      </div>
      <div class="inputWrapper">
        <label for="repositoryBearerToken">
          Token
          <span class="required">Required</span>
        </label>
        <input
          type="text"
          name="repositoryBearerToken"
          id="repositoryBearerToken"
          v-model="repositoryBearerToken"
          autocomplete="off"
          @blur="onRepositoryBearerTokenBlur"
          required
        />
        <p class="inputWrapper__help">
          Provide a token that has the permissions to create and update
          issues on the repository.
        </p>
      </div>
      <div class="inputWrapper">
        <label for="repositoryLabels">
          Labels
        </label>
        <input
          type="text"
          name="repositoryLabels"
          id="repositoryLabels"
          v-model="repositoryLabels"
          autocomplete="off"
          placeholder="reliability, availability"
          required
        />
        <p class="inputWrapper__help">
          Provide a comma-separated list of tags to set on the issue when it
          is created.
        </p>
      </div>
      <div class="inputWrapper inputWrapper--tick">
        <div>
          <input
            type="checkbox"
            v-model="repositoryOnFailedEventOnly"
            name="repositoryOnFailedEventOnly"
            id="repositoryOnFailedEventOnly"
            checked
          />
          <label for="repositoryOnFailedEventOnly">On Failures Only</label>
        </div>
        <p class="inputWrapper__help">
          Check this to prevent creation of issues about plans starting
          as that could quickly pollute the repository.
        </p>
      </div>
    </fieldset>
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
import type { Secret, Var } from "@/types/environments";


const useEmailChannel = ref<boolean>(false);
const useWebhookChannel = ref<boolean>(false);
const useGHChannel = ref<boolean>(false);
const notifyOnEvent = ref<string>("");

const name = ref<string>("");
const isNameValid = ref<boolean>(true);
function onNameBlur(): void {
  if (name.value === "") {
    isNameValid.value = false;
  } else {
    isNameValid.value = true;
  }
}

const emailToAddresses = ref<string>("");
const isEmailToAddressesValid = ref<boolean>(false);
function onEmailToAddressesBlur(): void {
  if (emailToAddresses.value === "") {
    isEmailToAddressesValid.value = false;
  } else {
    isEmailToAddressesValid.value = true;
  }
}

const webhookUrl = ref<string>("");
const isWebhookUrlValid = ref<boolean>(false);
function onWebhookUrlBlur(): void {
  if (webhookUrl.value === "") {
    isWebhookUrlValid.value = false;
  } else {
    isWebhookUrlValid.value = true;
  }
}

const webhookBearerToken = ref<string>("");
const isWebhookBearerTokenValid = ref<boolean>(false);
function onWebhookBearerTokenBlur(): void {
  if (webhookBearerToken.value === "") {
    isWebhookBearerTokenValid.value = false;
  } else {
    isWebhookBearerTokenValid.value = true;
  }
}

const repositoryUrl = ref<string>("");
const isRepositoryUrlValid = ref<boolean>(false);
function onRepositoryUrlBlur(): void {
  if (repositoryUrl.value === "") {
    isRepositoryUrlValid.value = false;
  } else {
    isRepositoryUrlValid.value = true;
  }
}

const repositoryBearerToken = ref<string>("");
const isRepositoryBearerTokenValid = ref<boolean>(false);
function onRepositoryBearerTokenBlur(): void {
  if (repositoryBearerToken.value === "") {
    isRepositoryBearerTokenValid.value = false;
  } else {
    isRepositoryBearerTokenValid.value = true;
  }
}

const repositoryLabels = ref<string>("");
const repositoryOnFailedEventOnly = ref<boolean>(true);

const isCreating = ref<boolean>(false);
const isSubmitDisabled = computed<boolean>(() => {
  return (
    isCreating.value ||
    !isNameValid.value ||
    name.value === "" ||
    (!notifyOnEvent.value) ||
    (!useEmailChannel.value && !useWebhookChannel.value && !useGHChannel.value) ||
    (useEmailChannel.value && !isEmailToAddressesValid.value) ||
    (useWebhookChannel.value && (
      !isWebhookUrlValid.value && !isEmailToAddressesValid.value
    )) || 
    (useGHChannel.value && (
      !isRepositoryUrlValid.value && !isRepositoryBearerTokenValid.value
    ))
  );
});

async function create(): Promise<void> {
  if (!isSubmitDisabled.value) {

    let vars: Var[] = [];
    let secrets: Secret[] = [];

    let eventTypes: string[] = [];

    if (notifyOnEvent.value) {
      eventTypes.push(notifyOnEvent.value);
    }

    vars.push({
      var_name: "RELIABLY_NOTIFICATION_EVENT_TYPES",
      value: eventTypes.join(","),
    });

    if (useEmailChannel.value) {
      vars.push({
        var_name: "RELIABLY_NOTIFICATION_USE_EMAIL",
        value: "1",
      });

      vars.push({
        var_name: "RELIABLY_NOTIFICATION_TO_ADDRESSES",
        value: emailToAddresses.value
      });
    }

    if (useWebhookChannel.value) {
      vars.push({
        var_name: "RELIABLY_NOTIFICATION_USE_WEBHOOK",
        value: "1",
      });

      vars.push({
        var_name: "RELIABLY_NOTIFICATION_WEBHOOK_URL",
        value: webhookUrl.value
      });

      secrets.push({
        var_name: "RELIABLY_NOTIFICATION_WEBHOOK_BEARER_TOKEN",
        value: webhookBearerToken.value,
        key: generateKey(32),
      });
    }

    if (useGHChannel.value) {
      vars.push({
        var_name: "RELIABLY_NOTIFICATION_USE_GITHUB",
        value: "1",
      });

      vars.push({
        var_name: "RELIABLY_NOTIFICATION_GITHUB_URL",
        value: repositoryUrl.value
      });

      if (repositoryLabels.value) {
        vars.push({
          var_name: "RELIABLY_NOTIFICATION_GITHUB_LABELS",
          value: repositoryLabels.value
        });
      }

      if (repositoryOnFailedEventOnly.value) {
        vars.push({
          var_name: "RELIABLY_NOTIFICATION_GITHUB_ON_FAILURE_EVENTS",
          value: "1"
        });
      }

      secrets.push({
        var_name: "RELIABLY_NOTIFICATION_GITHUB_TOKEN",
        value: repositoryBearerToken.value,
        key: generateKey(32),
      });
    }

    isCreating.value = true;
    const int: Integration = {
      name: name.value,
      provider: "notification",
      vendor: "reliably",
      environment: {
        name: name.value,
        used_for: "notification",
        envvars: vars,
        secrets: secrets,
      },
    };
    await createIntegration(int);
    isCreating.value = false;
  }
}
</script>
