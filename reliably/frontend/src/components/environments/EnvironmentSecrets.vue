<template>
  <ul class="environmentSecrets tableList">
    <li class="tableList__row tableList__row--header">
      <div class="tableList__cell">Name or Path</div>
      <div class="tableList__cell"></div>
      <div class="tableList__cell tableList__cell--small">
        <span class="screen-reader-text">Actions</span>
      </div>
    </li>
    <li v-for="(s, index) in secrets" :key="index" class="tableList__row">
      <div class="tableList__cell jsonString jsonString--envvar">
        {{ pathOrEnv(s) }}
      </div>
      <div class="tableList__cell jsonString jsonString--envvar">********</div>
      <div
        class="environmentSecrets__actions tableList__cell tableList__cell--small"
      >
        <button
          class="button button--icon hasTooltip hasTooltip--bottom-center"
          label="Edit"
          aria-label="Edit"
          @click.prevent="displayEdit(s)"
        >
          <EditIcon />
        </button>
        <DeleteButton @click.prevent="displayDelete(s)" />
      </div>
    </li>
  </ul>
  <ModalWindow
    v-if="isDeleteDisplayed"
    :hasCloseButton="true"
    :hasPadding="true"
    @close="closeDelete"
  >
    <template #title>Delete Secret</template>
    <template #content>
      <ConfirmDeleteEnvironmentSecretVar
        v-if="currentSecret !== null"
        :target="currentSecret"
        type="secret"
        :env="env"
        @close="closeDelete"
        @refresh-environment="refreshEnvironment"
      />
      <div v-else>Something went wrong. Please try again.</div>
    </template>
  </ModalWindow>
  <ModalWindow
    v-if="isEditDisplayed"
    :hasCloseButton="true"
    :hasPadding="true"
    @close="closeEdit"
  >
    <template #title>Edit Secret</template>
    <template #content>
      <EditEnvironmentSecretVar
        v-if="currentSecret !== null"
        :target="currentSecret"
        type="secret"
        :env="env"
        @close="closeEdit"
        @refresh-environment="refreshEnvironment"
      />
      <div v-else>Something went wrong. Please try again.</div>
    </template>
  </ModalWindow>
</template>

<script setup lang="ts">
import { toRefs, ref } from "vue";
import type { Secret } from "@/types/environments";

import { hasProp } from "@/utils/objects";

import ConfirmDeleteEnvironmentSecretVar from "@/components/environments/ConfirmDeleteEnvironmentSecretVar.vue";
import EditEnvironmentSecretVar from "@/components/environments/EditEnvironmentSecretVar.vue";
import DeleteButton from "@/components/_ui/DeleteButton.vue";
import ModalWindow from "@/components/_ui/ModalWindow.vue";
import EditIcon from "@/components/svg/EditIcon.vue";

const props = defineProps<{
  secrets: Secret[];
  env: string;
}>();
const { secrets, env } = toRefs(props);

const emit = defineEmits<{
  (e: "refresh-environment"): void;
}>();

function pathOrEnv(s: Secret): string {
  if (hasProp(s, "path")) {
    return s.path!;
  } else if (hasProp(s, "var_name")) {
    return s.var_name!;
  } else {
    return "";
  }
}

const currentSecret = ref<Secret | null>(null);

const isDeleteDisplayed = ref<boolean>(false);
function closeDelete() {
  currentSecret.value = null;
  isDeleteDisplayed.value = false;
}
function displayDelete(s: Secret) {
  currentSecret.value = s;
  isDeleteDisplayed.value = true;
}

const isEditDisplayed = ref<boolean>(false);
function closeEdit() {
  currentSecret.value = null;
  isEditDisplayed.value = false;
}
function displayEdit(s: Secret) {
  currentSecret.value = s;
  isEditDisplayed.value = true;
}

function refreshEnvironment() {
  emit("refresh-environment");
}
</script>

<style lang="scss">
.environmentSecrets {
  li > div:first-child {
    width: 40rem;
  }

  &__actions {
    color: var(--text-color-bright);
    text-align: right;

    > * {
      visibility: hidden;
    }

    > * + * {
      margin-left: var(--space-small);
    }

    .button {
      color: var(--text-color-bright);
    }
  }

  li:hover {
    > .environmentSecrets__actions {
      > * {
        visibility: visible;
      }
    }
  }
}
</style>
