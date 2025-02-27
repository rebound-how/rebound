<template>
  <Transition name="slide-fade">
    <div class="tokenResponse" v-if="newToken !== undefined">
      Your token <strong>{{ newToken.name }}</strong> has been successfully
      created.
      <div class="tokenResponse__value">
        <span
          v-if="isSupported"
          @click="copy(newToken!.token!)"
          class="hasTooltip hasTooltip--bottom-center"
          label="Click to copy"
          aria-label="Click to copy"
        >
          {{ newToken.token }}
        </span>
        <span v-else>
          {{ newToken.token }}
        </span>
        <span v-if="copied"><CheckIcon />Copied to clipboard</span>
      </div>
      <button class="button button--icon" @click.prevent="close">
        <CloseIcon />
      </button>
    </div>
  </Transition>
  <form class="tokenForm form">
    <div class="inputWrapper">
      <label for="deploymentName">
        Token name <span class="required">Required</span>
      </label>
      <input
        type="text"
        name="tokenName"
        id="tokenName"
        v-model="tokenName"
        required
      />
    </div>
    <div class="inputWrapper">
      <button
        @click.prevent="proceed"
        :disabled="isSubmitDisabled"
        class="button button--primary"
      >
        Create token
      </button>
    </div>
  </form>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import { createToken } from "@/stores/user";
import { useClipboard } from "@vueuse/core";

import type { Token } from "@/types/user";

import CheckIcon from "@/components/svg/CheckIcon.vue";
import CloseIcon from "@/components/svg/CloseIcon.vue";

const tokenName = ref<string>("");
const newToken = ref<Token | undefined>(undefined);

const isSubmitDisabled = computed<boolean>(() => {
  return tokenName.value === "";
});

const proceed = async () => {
  await createToken(tokenName.value).then((response) => {
    if (response !== undefined) {
      newToken.value = response;
    }
  });
  tokenName.value = "";
};

const { text, copy, copied, isSupported } = useClipboard();
const close = () => {
  newToken.value = undefined;
};
</script>

<style lang="scss" scoped>
.tokenForm {
  position: relative;

  display: flex;
  flex-direction: column;
  gap: var(--space-medium);
  margin-right: auto;
  margin-left: auto;
  padding: var(--space-medium);
  width: 50rem;
  max-width: 100%;

  background-color: var(--section-background);
  border-radius: var(--border-radius-m);

  color: var(--text-color-bright);
}

.tokenResponse {
  position: relative;

  margin-bottom: var(--space-medium);
  padding: var(--space-medium);

  background-color: var(--statusColor-ok-dim);
  border-radius: var(--border-radius-s);

  &__value {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    margin-top: var(--space-small);

    font-family: var(--monospace-font);

    span:first-child {
      display: inline-block;
      padding: 0.6rem;

      background-color: var(--token-response-background);
      border-radius: var(--border-radius-s);
    }

    span:nth-child(2) {
      display: inline-flex;
      align-items: center;
      gap: 0.2rem;

      svg {
        height: 2.4rem;

        color: var(--statusColor-ok);
      }
    }
  }

  .button {
    position: absolute;
    top: var(--space-small);
    right: var(--space-small);
  }
}

.slide-fade-enter-active {
  transition: all 0.3s ease-in-out;
}

.slide-fade-leave-active {
  transition: all 0.3s ease-in-out;
}

.slide-fade-enter-from,
.slide-fade-leave-to {
  transform: translateY(-15rem);
  opacity: 0;
}
</style>
