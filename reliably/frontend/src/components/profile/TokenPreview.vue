<template>
  <li class="tokenPreview tableList__row">
    <div class="tableList__cell tokenPreview__name">
      {{ t.name }}
    </div>
    <div class="tableList__cell tokenPreview__value">
      <span
        v-if="hidden"
        role="button"
        @click="getTokenValue"
        class="hasTooltip hasTooltip--bottom-center"
        label="Click to reveal"
        aria-label="Click to reveal"
      >
        {{ tokenValue }}
        <span v-if="copied"><CheckIcon />Copied to clipboard</span>
      </span>
      <span
        v-else-if="isSupported"
        role="button"
        @click="copyTokenAndHide"
        class="hasTooltip hasTooltip--bottom-center"
        label="Click to copy to clipboard"
        aria-label="Click to copy to clipboard"
      >
        {{ tokenValue }}
      </span>
      <span
        v-else
        role="button"
        @click="hideTokenValue"
        class="hasTooltip hasTooltip--bottom-center"
        label="Click to hide"
        aria-label="Click to hide"
      >
        {{ tokenValue }}
      </span>
    </div>
    <div class="tableList__cell tokenPreview__date">
      <TimeAgo :timestamp="t.created_date" />
    </div>
    <div class="tableList__cell tableList__cell--small">
      <DeleteButton @click.prevent="displayDelete" />
    </div>
    <ModalWindow
      v-if="isDeleteDisplayed"
      :hasCloseButton="true"
      :hasPadding="true"
      @close="closeDelete"
    >
      <template #title>Delete Experiment</template>
      <template #content>
        <ConfirmDeleteToken :id="t.id" :org="org" @close="closeDelete" />
      </template>
    </ModalWindow>
  </li>
</template>

<script setup lang="ts">
import { toRefs, ref, computed } from "vue";
import { useClipboard } from "@vueuse/core";

import { token, fetchToken } from "@/stores/user";
import type { Token } from "@/types/user";

import TimeAgo from "@/components/_ui/TimeAgo.vue";
import DeleteButton from "@/components/_ui/DeleteButton.vue";
import ModalWindow from "@/components/_ui/ModalWindow.vue";
import ConfirmDeleteToken from "@/components/profile/ConfirmDeleteToken.vue";
import CheckIcon from "@/components/svg/CheckIcon.vue";

const props = defineProps<{
  t: Token;
  org: string;
}>();
const { t, org } = toRefs(props);

const tokenValue = ref<string>("********");
const hidden = computed<boolean>(() => {
  return tokenValue.value === "********";
});

const getTokenValue = async () => {
  await fetchToken(t.value.id);
  const to: Token = token.get();
  tokenValue.value = to.token!;
};

const { text, copy, copied, isSupported } = useClipboard();
const copyTokenAndHide = () => {
  copy(tokenValue.value);
  hideTokenValue();
};

const hideTokenValue = () => {
  tokenValue.value = "********";
};

const isDeleteDisplayed = ref<boolean>(false);

const displayDelete = () => {
  isDeleteDisplayed.value = true;
};
const closeDelete = () => {
  isDeleteDisplayed.value = false;
};
</script>

<style lang="scss" scoped>
.tokenPreview {
  &__value {
    span {
      display: inline-flex;
      align-items: center;
      gap: 0.6rem;
      min-width: 33ch;
      padding: 0.2rem 0.6rem;

      background-color: var(--table-header-color);
      border-radius: var(--border-radius-s);
      cursor: pointer;

      font-family: var(--monospace-font);

      span {
        display: inline-flex;
        align-items: center;
        gap: 0.2rem;
        min-width: 0;
        padding: 0;

        font-family: var(--body-font);
        line-height: 1;

        svg {
          height: 2.4rem;

          color: var(--statusColor-ok);
        }
      }
    }
  }

  .deleteButton {
    visibility: hidden;
  }

  &:hover {
    .deleteButton {
      visibility: visible;
    }
  }
}
</style>
