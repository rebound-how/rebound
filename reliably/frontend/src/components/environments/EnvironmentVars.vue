<template>
  <ul class="environmentVars tableList">
    <li class="tableList__row tableList__row--header">
      <div class="tableList__cell">Name</div>
      <div class="tableList__cell">Value</div>
      <div class="tableList__cell tableList__cell--small">
        <span class="screen-reader-text">Actions</span>
      </div>
    </li>
    <li v-for="(v, index) in vars" :key="index" class="tableList__row">
      <div class="tableList__cell jsonString jsonString--envvar">
        {{ v.var_name }}
      </div>
      <div class="tableList__cell">{{ v.value }}</div>
      <div
        class="environmentVars__actions tableList__cell tableList__cell--small"
      >
        <button
          class="button button--icon hasTooltip hasTooltip--bottom-center"
          label="Edit"
          aria-label="Edit"
          @click.prevent="displayEdit(v)"
        >
          <EditIcon />
        </button>
        <DeleteButton @click.prevent="displayDelete(v)" />
      </div>
    </li>
  </ul>
  <ModalWindow
    v-if="isDeleteDisplayed"
    :hasCloseButton="true"
    :hasPadding="true"
    @close="closeDelete"
  >
    <template #title>Delete Environment Variable</template>
    <template #content>
      <ConfirmDeleteEnvironmentSecretVar
        v-if="currentVar !== null"
        :target="currentVar"
        type="variable"
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
    <template #title>Edit Environment Variable</template>
    <template #content>
      <EditEnvironmentSecretVar
        v-if="currentVar !== null"
        :target="currentVar"
        type="variable"
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
import type { Var } from "@/types/environments";

import ConfirmDeleteEnvironmentSecretVar from "@/components/environments/ConfirmDeleteEnvironmentSecretVar.vue";
import EditEnvironmentSecretVar from "@/components/environments/EditEnvironmentSecretVar.vue";
import DeleteButton from "@/components/_ui/DeleteButton.vue";
import ModalWindow from "@/components/_ui/ModalWindow.vue";
import EditIcon from "@/components/svg/EditIcon.vue";

const props = defineProps<{
  vars: Var[];
  env: string;
}>();
const { vars, env } = toRefs(props);

const emit = defineEmits<{
  (e: "refresh-environment"): void;
}>();

const currentVar = ref<Var | null>(null);

const isDeleteDisplayed = ref<boolean>(false);
function closeDelete() {
  currentVar.value = null;
  isDeleteDisplayed.value = false;
}
function displayDelete(v: Var) {
  currentVar.value = v;
  isDeleteDisplayed.value = true;
}

const isEditDisplayed = ref<boolean>(false);
function closeEdit() {
  currentVar.value = null;
  isEditDisplayed.value = false;
}
function displayEdit(v: Var) {
  currentVar.value = v;
  isEditDisplayed.value = true;
}

function refreshEnvironment() {
  emit("refresh-environment");
}
</script>

<style lang="scss">
.environmentVars {
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
    > .environmentVars__actions {
      > * {
        visibility: visible;
      }
    }
  }
}
</style>
