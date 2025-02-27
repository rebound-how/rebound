<template>
  <LoadingPlaceholder size="large" v-if="isLoading" />
  <article class="environmentView" v-else-if="env !== undefined && env.id">
    <header class="pageHeader">
      <div>
        <h1 class="pageHeader__title">
          {{ env.name }}
        </h1>
      </div>
      <div class="pageHeader__actions">
        <button
          class="button button--destructiveLight"
          @click.prevent="displayDelete"
        >
          Delete environment
        </button>
        <button class="button button--primary" @click.prevent="openClone">
          Clone environment
        </button>
        <a href="/environments/new/" class="button button--creative"
          >New environment</a
        >
      </div>
    </header>
    <section class="environmentInfo">
      Created <TimeAgo :timestamp="env.created_date" />
    </section>
    <section class="environmentVarsWrapper">
      <header>
        <h2>Environment Secrets</h2>
        <button
          @click.prevent="displayAdd('secret')"
          class="button button--creative button--small"
        >
          Add a secret
        </button>
      </header>
      <p>
        Secrets are encrypted environment variables. They are accessible only by
        Reliably in the context of this environment.
      </p>
      <EnvironmentSecrets
        :secrets="env.secrets"
        :env="id!"
        @refresh-environment="getEnvironment"
      />
    </section>
    <section class="environmentVarsWrapper">
      <header>
        <h2>Environment Variables</h2>
        <button
          @click.prevent="displayAdd('variable')"
          class="button button--creative button--small"
        >
          Add a variable
        </button>
      </header>
      <p>
        Variables are used for non-sensitive configuration data. They are
        accessible only by Reliably in the context of this environment.
      </p>
      <EnvironmentVars
        :vars="env.envvars"
        :env="id!"
        @refresh-environment="getEnvironment"
      />
    </section>
    <ModalWindow
      v-if="isDeleteDisplayed"
      :hasCloseButton="true"
      :hasPadding="true"
      @close="closeDelete"
    >
      <template #title>Delete Environment</template>
      <template #content>
        <ConfirmDeleteEnvironment :id="env.id" @close="closeDelete" />
      </template>
    </ModalWindow>
    <ModalWindow
      v-if="isCloneDisplayed"
      :hasCloseButton="true"
      :hasPadding="true"
      @close="closeClone"
    >
      <template #title>Clone Environment</template>
      <template #content>
        <CloneEnvironmentForm
          :id="env.id"
          :name="env.name"
          @close="closeClone"
        />
      </template>
    </ModalWindow>
    <ModalWindow
      v-if="isAddDisplayed"
      :hasCloseButton="true"
      :hasPadding="true"
      @close="closeAdd"
    >
      <template #title>Add Environment {{ typeToAdd }}</template>
      <template #content>
        <AddEnvironmentSecretVar
          v-if="typeToAdd !== null"
          :type="typeToAdd"
          :env="env.id"
          @close="closeAdd"
          @refresh-environment="getEnvironment"
        />
        <div v-else>Something went wrong. Please try again.</div>
      </template>
    </ModalWindow>
  </article>
  <NoData v-else message="We couldn't find a deployment with this ID." />
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import type { Environment } from "@/types/environments";

import { environment, fetchEnvironment } from "@/stores/environments";

import EnvironmentVars from "@/components/environments/EnvironmentVars.vue";
import EnvironmentSecrets from "@/components/environments/EnvironmentSecrets.vue";
import LoadingPlaceholder from "@/components/_ui/LoadingPlaceholder.vue";
import NoData from "@/components/_ui/NoData.vue";
import TimeAgo from "@/components/_ui/TimeAgo.vue";
import ModalWindow from "@/components/_ui/ModalWindow.vue";
import ConfirmDeleteEnvironment from "@/components/environments/ConfirmDeleteEnvironment.vue";
import CloneEnvironmentForm from "@/components/environments/CloneEnvironmentForm.vue";
import AddEnvironmentSecretVar from "@/components/environments/AddEnvironmentSecretVar.vue";

const isLoading = ref(true);
const id = ref<string | undefined>(undefined);
const env = ref<Environment | undefined>(undefined);

const getCurrentId = () => {
  let location = window.location;
  let params = new URLSearchParams(location.search);
  if (params.has("id")) {
    id.value = params.get("id")!;
  }
};

const getEnvironment = async () => {
  await fetchEnvironment(id.value!);
  env.value = environment.get() as Environment;
};

const setMetaData = () => {
  let title = "Environment · Reliably";
  let description = "View your Reliably deployment details";
  if (env.value !== undefined) {
    title = `${env.value.name} environment · Reliably`;
  }
  document.title = title;
};

const isDeleteDisplayed = ref<boolean>(false);
const displayDelete = () => {
  isDeleteDisplayed.value = true;
};
const closeDelete = () => {
  isDeleteDisplayed.value = false;
};

const isCloneDisplayed = ref<boolean>(false);
function openClone() {
  isCloneDisplayed.value = true;
}
function closeClone() {
  isCloneDisplayed.value = false;
}

const typeToAdd = ref<"secret" | "variable" | null>(null);
const isAddDisplayed = ref<boolean>(false);
function closeAdd() {
  typeToAdd.value = null;
  isAddDisplayed.value = false;
}
function displayAdd(type: string) {
  if (type === "secret" || type === "variable") {
    typeToAdd.value = type;
  }
  isAddDisplayed.value = true;
}

onMounted(async () => {
  isLoading.value = true;
  getCurrentId();
  await getEnvironment();
  setMetaData();
  isLoading.value = false;
});
</script>

<style lang="scss" scoped>
.environmentView {
  .environmentInfo {
    &__creation {
      margin-left: var(--space-small);

      color: var(--text-color-dim);
    }
  }

  > section + section {
    margin-top: var(--space-large);
  }

  .environmentVarsWrapper {
    header {
      display: flex;
      justify-content: space-between;
    }

    h2 {
      margin-bottom: 0;
    }

    p {
      margin-bottom: var(--space-small);
      max-width: 70rem;

      color: var(--text-color-dim);
    }
  }
}
</style>
