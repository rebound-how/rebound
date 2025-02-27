<template>
  <form class="environmentForm form">
    <fieldset>
      <div class="inputWrapper">
        <label for="environmentName">
          Environment name <span class="required">Required</span>
        </label>
        <input
          type="text"
          name="environmentName"
          id="environmentName"
          v-model="environmentName"
          required
        />
      </div>
    </fieldset>
    <fieldset>
      <legend>Add environment from template</legend>
      <div class="templatesSelector">
        <div>
          <input
            type="checkbox"
            v-model="hasCustomAWS"
            name="environmentTemplateAWS"
            id="environmentTemplateAWS"
          />
          <label for="environmentTemplateAWS" title="AWS">
            <span class="screen-reader-text">AWS</span>
            <AwsLogo />
          </label>
        </div>
        <div>
          <input
            type="checkbox"
            v-model="hasCustomGCP"
            name="environmentTemplateGCP"
            id="environmentTemplateGCP"
          />
          <label for="environmentTemplateGCP" title="Google Cloud">
            <span class="screen-reader-text">Google Cloud</span>
            <GoogleCloudLogo />
          </label>
        </div>
        <div>
          <input
            type="checkbox"
            v-model="hasCustomAzure"
            name="environmentTemplateAzure"
            id="environmentTemplateAzure"
          />
          <label for="environmentTemplateAzure" title="Azure">
            <span class="screen-reader-text">Azure</span>
            <AzureLogo />
          </label>
        </div>
        <div>
          <input
            type="checkbox"
            v-model="hasCustomKubernetes"
            name="environmentTemplateKubernetes"
            id="environmentTemplateKubernetes"
          />
          <label for="environmentTemplateKubernetes" title="Kubernetes">
            <span class="screen-reader-text">Kubernetes</span>
            <KubernetesLogo />
          </label>
        </div>
        <div>
          <input
            type="checkbox"
            v-model="hasCustomGitHub"
            name="environmentTemplateGitHub"
            id="environmentTemplateGitHub"
          />
          <label for="environmentTemplateGitHub" title="GitHub">
            <span class="screen-reader-text">GitHub</span>
            <GitHubLogo />
          </label>
        </div>
      </div>
    </fieldset>
    <fieldset v-if="hasCustomAWS">
      <legend>AWS Vars and Secrets</legend>
      <div class="inputWrapper">
        <label for="awsKey" class="flex">
          <span class="jsonString">AWS_ACCESS_KEY_ID</span>
          <span class="required">Required </span>
          <span class="secret flex-right">Secret</span>
        </label>
        <input
          type="text"
          name="awsKey"
          id="awsKey"
          v-model="secret_AwsAccessKeyId"
          autocomplete="off"
          required
        />
      </div>
      <div class="inputWrapper">
        <label for="awsSecret" class="flex">
          <span class="jsonString">AWS_SECRET_ACCESS_KEY</span>
          <span class="required">Required</span>
          <span class="secret flex-right">Secret</span>
        </label>
        <input
          type="text"
          name="awsSecret"
          id="awsSecret"
          v-model="secret_AwsSecretAccessKey"
          autocomplete="off"
          required
        />
      </div>
    </fieldset>
    <fieldset v-if="hasCustomGCP">
      <legend>Google Cloud Vars and Secrets</legend>
      <div class="inputWrapper">
        <label for="gcpCredentials" class="flex">
          <span class="jsonString">GCP_APPLICATION_CREDENTIALS</span>
          <span class="required">Required </span>
          <span class="envvar flex-right">Variable</span>
        </label>
        <input
          type="text"
          name="gcpCredentials"
          id="gcpCredentials"
          v-model="var_GcpCredentials"
          autocomplete="off"
          required
        />
      </div>
      <div class="inputWrapper">
        <label for="gcpConfigFile" class="flex">
          <span class="jsonString">{{ var_GcpCredentials }}</span>
          <span class="required">Required</span>
          <span class="secret flex-right">Secret</span>
        </label>
        <textarea
          name="gcpConfigFile"
          id="gcpConfigFile"
          placeholder="Paste file content here"
          v-model="secret_GcpSecretConfigFile"
          autocomplete="off"
          required
        ></textarea>
      </div>
    </fieldset>
    <fieldset v-if="hasCustomAzure">
      <legend>Azure Cloud Vars and Secrets</legend>
      <div class="inputWrapper">
        <label for="azureClientId" class="flex">
          <span class="jsonString">AZURE_CLIENT_ID</span>
          <span class="required">Required </span>
          <span class="envvar flex-right">Variable</span>
        </label>
        <input
          type="text"
          name="azureClientId"
          id="azureClientId"
          v-model="var_azureClientId"
          autocomplete="off"
          required
        />
      </div>
      <div class="inputWrapper">
        <label for="azureTenantId" class="flex">
          <span class="jsonString">AZURE_TENANT_ID</span>
          <span class="required">Required </span>
          <span class="envvar flex-right">Variable</span>
        </label>
        <input
          type="text"
          name="azureTenantId"
          id="azureTenantId"
          v-model="var_azureTenantId"
          autocomplete="off"
          required
        />
      </div>
      <div class="inputWrapper">
        <label for="azureSubscriptionId" class="flex">
          <span class="jsonString">AZURE_SUBSCRIPTION_ID</span>
          <span class="required">Required</span>
          <span class="envvar flex-right">Variable</span>
        </label>
        <input
          type="text"
          name="azureSubscriptionId"
          id="azureSubscriptionId"
          v-model="var_azureSubscriptionId"
          autocomplete="off"
          required
        />
      </div>
      <div class="inputWrapper">
        <label for="azureClientSecret" class="flex">
          <span class="jsonString">AZURE_CLIENT_SECRET</span>
          <span class="required">Required </span>
          <span class="secret flex-right">Secret</span>
        </label>
        <input
          type="text"
          name="azureClientSecret"
          id="azureClientSecret"
          v-model="secret_azureClientSecret"
          autocomplete="off"
          required
        />
      </div>
    </fieldset>
    <fieldset v-if="hasCustomKubernetes">
      <legend>Kubernetes Vars and Secrets</legend>
      <div class="inputWrapper">
        <label for="kubeConfig" class="flex">
          <span class="jsonString">KUBECONFIG</span>
          <span class="required">Required </span>
          <span class="envvar flex-right">Variable</span>
        </label>
        <input
          type="text"
          name="kubeConfig"
          id="kubeConfig"
          v-model="var_kubeConfig"
          autocomplete="off"
          required
        />
      </div>
      <div class="inputWrapper">
        <label for="kubeConfigFile" class="flex">
          <span class="jsonString">{{ var_kubeConfig }}</span>
          <span class="required">Required</span>
          <span class="secret flex-right">Secret</span>
        </label>
        <textarea
          name="kubeConfigFile"
          id="kubeConfigFile"
          placeholder="Paste file content here"
          v-model="secret_kubeSecretConfigFile"
          autocomplete="off"
          required
        ></textarea>
      </div>
    </fieldset>
    <fieldset v-if="hasCustomGitHub">
      <legend>GitHub Vars and Secrets</legend>
      <div class="inputWrapper">
        <label for="gitHubToken" class="flex">
          <span class="jsonString">GITHUB_TOKEN</span>
          <span class="required">Required </span>
          <span class="secret flex-right">Secret</span>
        </label>
        <input
          type="text"
          name="gitHubToken"
          id="gitHubToken"
          v-model="secret_gitHubToken"
          autocomplete="off"
          required
        />
      </div>
    </fieldset>
    <fieldset class="environmentVars">
      <legend>Environment Variables</legend>
      <div class="inputWrapper">
        <div class="environmentVars__labels">
          <span id="varName">Name</span>
          <span id="varValue">Value</span>
        </div>
        <div
          v-for="(v, index) in envVars"
          class="environmentVars__item"
          :key="index"
        >
          <input
            type="text"
            aria-labelledby="varName"
            v-model="envVars[index].var_name"
          />
          <input
            type="text"
            aria-labelledby="varValue"
            v-model="envVars[index].value"
          />

          <button
            class="envVarButton"
            :class="{ 'envVarButton--hidden': hideRemoveVar }"
            @click.prevent="removeVar(index)"
          >
            <span class="screen-reader-text">Remove this variable</span>
            <MinusIcon />
          </button>
          <button
            class="envVarButton"
            v-if="index === envVars.length - 1"
            @click.prevent="addVar"
          >
            <span class="screen-reader-text">Add a variable</span>
            <PlusIcon />
          </button>
        </div>
      </div>
    </fieldset>
    <fieldset class="environmentSecrets">
      <legend>Environment Secrets</legend>
      <div class="inputWrapper">
        <div
          v-for="(s, index) in envSecrets"
          class="environmentSecrets__item"
          :key="index"
        >
          <template v-if="!isSecretHidden(s)">
            <div class="environmentSecrets__type">
              <label :for="`secretType-${index}`">Type</label>
              <select
                v-model="envSecretsTypes[index]"
                :id="`secretType-${index}`"
                :name="`secretType-${index}`"
                @change="onSecretTypeChange(index)"
              >
                <option value="var">Variable</option>
                <option value="path">Path</option>
              </select>
            </div>
            <div
              v-if="envSecretsTypes[index] === 'path'"
              class="environmentSecrets__path"
            >
              <label :for="`secretPath-${index}`">Path</label>
              <input
                :id="`secretPath-${index}`"
                :name="`secretPath-${index}`"
                type="text"
                v-model="envSecrets[index].path"
                autocomplete="off"
              />
            </div>
            <div v-else class="environmentSecrets__name">
              <label :for="`secretName-${index}`">Name</label>
              <input
                :id="`secretName-${index}`"
                :name="`secretName-${index}`"
                type="text"
                v-model="envSecrets[index].var_name"
                autocomplete="off"
              />
            </div>
            <div
              v-if="envSecretsTypes[index] === 'var'"
              class="environmentSecrets__value environmentSecrets__value--var"
            >
              <label :for="`secretValue-${index}`">Value</label>
              <input
                :id="`secretValue-${index}`"
                :name="`secretValue-${index}`"
                type="text"
                v-model="envSecrets[index].value"
                autocomplete="off"
              />
            </div>
            <div
              v-else-if="envSecretsTypes[index] === 'path'"
              class="environmentSecrets__value environmentSecrets__value--path"
            >
              <label :for="`secretValue-${index}`">Value</label>
              <textarea
                :id="`secretValue-${index}`"
                :name="`secretValue-${index}`"
                v-model="envSecrets[index].value"
                placeholder="Paste file content"
                autocomplete="off"
              ></textarea>
            </div>
            <div class="environmentSecrets__buttons">
              <button
                class="envVarButton"
                :class="{ 'envVarButton--hidden': hideRemoveSecret }"
                @click.prevent="removeSecret(index)"
              >
                <span class="screen-reader-text">Remove this secret</span>
                <MinusIcon />
              </button>
              <button
                class="envVarButton"
                v-if="index === envSecrets.length - 1"
                @click.prevent="addSecret"
              >
                <span class="screen-reader-text">Add a secret</span>
                <PlusIcon />
              </button>
            </div>
          </template>
        </div>
      </div>
    </fieldset>
    <fieldset>
      <div class="inputWrapper">
        <button
          @click.prevent="proceed"
          :disabled="isSubmitDisabled"
          class="button button--primary"
          :class="{ 'button--waiting': isSubmitButtonInWaitMode }"
        >
          Create environment
          <span class="button__loader">
            <ButtonLoader />
          </span>
        </button>
      </div>
    </fieldset>
  </form>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import type { Environment, Var, Secret } from "@/types/environments";
import { createEnvironment } from "@/stores/environments";
import { generateKey } from "@/utils/strings";
import { hasProp } from "@/utils/objects";

import PlusIcon from "@/components/svg/PlusIcon.vue";
import MinusIcon from "@/components/svg/MinusIcon.vue";
import ButtonLoader from "@/components/svg/ButtonLoader.vue";
import AwsLogo from "@/components/svg/AwsLogo.vue";
import AzureLogo from "@/components/svg/AzureLogo.vue";
import GoogleCloudLogo from "@/components/svg/GoogleCloudLogo.vue";
import KubernetesLogo from "@/components/svg/KubernetesLogoBlue.vue";
import GitHubLogo from "@/components/svg/GithubLogo.vue";

const environmentName = ref<string>("");

const hasCustomAWS = ref<boolean>(false);
const hasCustomGCP = ref<boolean>(false);
const hasCustomAzure = ref<boolean>(false);
const hasCustomKubernetes = ref<boolean>(false);
const hasCustomGitHub = ref<boolean>(false);

function getSetTemplate() {
  // I'm not sure any page redirects here using those paramters...
  let location = window.location;
  let params = new URLSearchParams(location.search);
  if (params.has("template")) {
    const t = params.get("template");
    if (t === "aws") {
      hasCustomAWS.value === true;
    } else if (t === "gcp") {
      hasCustomGCP.value === true;
    } else if (t === "azure") {
      hasCustomAzure.value === true;
    } else if (t === "kubernetes") {
      hasCustomKubernetes.value === true;
    }
  }
}

// Special variables and secrets: AWS
const secret_AwsAccessKeyId = ref<string>("");
const secret_AwsSecretAccessKey = ref<string>("");

// Special variables and secrets: GCP
const var_GcpCredentials = ref<string>("/tmp/config");
const secret_GcpSecretConfigFile = ref<string>("");

// Special variables and secrets: Azure
const var_azureClientId = ref<string>("");
const var_azureTenantId = ref<string>("");
const var_azureSubscriptionId = ref<string>("");
const secret_azureClientSecret = ref<string>("");

// Special variables and secrets: Kubernetes
const var_kubeConfig = ref<string>("/tmp/kubeconfig");
const secret_kubeSecretConfigFile = ref<string>("");

// Special variables and secrets: GitHub
const secret_gitHubToken = ref<string>("");

// Environment Variables
const envVars = ref<Var[]>([{ var_name: "", value: "" }]);

const hideRemoveVar = computed<boolean>(() => {
  return envVars.value.length < 2;
});

const addVar = () => {
  envVars.value.push({ var_name: "", value: "" });
};

const removeVar = (index: number) => {
  envVars.value.splice(index, 1);
};

// Environment Secrets
const envSecrets = ref<Secret[]>([
  {
    var_name: "",
    value: "",
    key: generateKey(32),
  },
]);

const envSecretsTypes = ref<string[]>(["var"]);

const hideRemoveSecret = computed<boolean>(() => {
  return envSecrets.value.length < 2;
});

const addSecret = () => {
  envSecrets.value.push({
    value: "",
    key: generateKey(32),
  });
  envSecretsTypes.value.push("var");
};

function onSecretTypeChange(index: number) {
  let secret = envSecrets.value[index];
  if (envSecretsTypes.value[index] === "var") {
    const current = secret.path;
    secret.var_name = current;
    delete secret.path;
  } else if (envSecretsTypes.value[index] === "path") {
    const current = secret.var_name;
    secret.path = current;
    delete secret.var_name;
  }
}

const removeSecret = (index: number) => {
  envSecrets.value.splice(index, 1);
  envSecretsTypes.value.splice(index, 1);
};

const isSubmitButtonInWaitMode = ref<boolean>(false);
const isSubmitDisabled = computed<boolean>(() => {
  if (environmentName.value === "" || isSubmitButtonInWaitMode.value) {
    return true;
  } else {
    return false;
  }
});

function isSecretHidden(s: Secret) {
  if (
    s.var_name !== undefined &&
    (s.var_name === "AWS_ACCESS_KEY_ID" ||
      s.var_name === "AWS_SECRET_ACCESS_KEY")
  ) {
    // Custom secrets for AWS environment should be hidden
    // from the edition fields
    return true;
  } else {
    return false;
  }
}

function filterVars() {
  envVars.value = envVars.value.filter((v) => {
    v.var_name = v.var_name.trim();
    v.value = v.value.trim();
    return v.value !== "" && v.var_name !== "";
  });
}

function filterSecrets() {
  envSecrets.value = envSecrets.value.filter((s) => {
    s.value = s.value.trim();
    if (s.value === "") {
      return false;
    } else if (hasProp(s, "var_name")) {
      s.var_name = s.var_name?.trim();
      return s.var_name !== "";
    } else if (hasProp(s, "path")) {
      s.path = s.path?.trim();
      return s.path !== "";
    }
  });
}

const proceed = async () => {
  isSubmitButtonInWaitMode.value = true;
  await filterVars();
  await filterSecrets();
  if (hasCustomAWS.value === true) {
    envSecrets.value.push({
      var_name: "AWS_ACCESS_KEY_ID",
      value: secret_AwsAccessKeyId.value,
      key: generateKey(32),
    });
    envSecrets.value.push({
      var_name: "AWS_SECRET_ACCESS_KEY",
      value: secret_AwsSecretAccessKey.value,
      key: generateKey(32),
    });
  }
  if (hasCustomGCP.value === true) {
    envVars.value.push({
      var_name: "GCP_APPLICATION_CREDENTIALS",
      value: var_GcpCredentials.value,
    });
    envSecrets.value.push({
      path: var_GcpCredentials.value,
      value: secret_GcpSecretConfigFile.value,
      key: generateKey(32),
    });
  }
  if (hasCustomAzure.value === true) {
    envVars.value.push({
      var_name: "AZURE_CLIENT_ID",
      value: var_azureClientId.value,
    });
    envVars.value.push({
      var_name: "AZURE_TENANT_ID",
      value: var_azureTenantId.value,
    });
    envVars.value.push({
      var_name: "AZURE_SUBSCRIPTION_ID",
      value: var_azureSubscriptionId.value,
    });
    envSecrets.value.push({
      var_name: "AZURE_CLIENT_SECRET",
      value: secret_azureClientSecret.value,
      key: generateKey(32),
    });
  }
  if (hasCustomKubernetes.value === true) {
    envVars.value.push({
      var_name: "KUBECONFIG",
      value: var_kubeConfig.value,
    });
    envSecrets.value.push({
      path: var_kubeConfig.value,
      value: secret_kubeSecretConfigFile.value,
      key: generateKey(32),
    });
  }
  if (hasCustomGitHub.value === true) {
    envSecrets.value.push({
      var_name: "GITHUB_TOKEN",
      value: secret_gitHubToken.value,
      key: generateKey(32),
    });
  }
  let environment: Environment = {
    name: environmentName.value,
    envvars: envVars.value,
    secrets: envSecrets.value,
  };
  await createEnvironment(environment);
  isSubmitButtonInWaitMode.value = false;
};

onMounted(() => {
  getSetTemplate();
});
</script>

<style lang="scss" scoped>
.environmentForm {
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

  .templatesSelector {
    display: flex;
    // justify-content: space-between;
    gap: var(--space-medium);

    > div {
      position: relative;

      input {
        position: absolute;

        height: 0;
        width: 0;

        opacity: 0;
      }

      label {
        display: grid;
        place-content: center;
        height: 6rem;
        width: 6rem;

        background-color: transparent;
        border-radius: var(--border-radius-m);
        cursor: pointer;

        transition: background-color 0.2s ease-in-out;

        &:hover {
          background-color: var(--grey-200);
        }

        svg {
          width: 3.6rem;
        }
      }

      input:checked + label {
        outline: 0.2rem solid var(--pink-500);
      }
    }
  }

  .environmentVars {
    &__labels {
      display: flex;
      gap: 0.6rem;
      margin-bottom: 0.6rem;

      > span {
        flex: 0 1 auto;
        flex-shrink: 0;
        width: 12rem;
      }
    }
    &__item {
      display: flex;
      align-items: center;
      gap: 0.6rem;

      &:not(:nth-child(2)) {
        margin-top: var(--space-small);
      }

      label,
      input[type="text"],
      textarea {
        flex: 0 1 auto;
        margin-bottom: 0;
        width: 12rem;
      }

      textarea {
        align-self: flex-start;
      }

      select {
        flex-shrink: 0;
        width: 12rem;
      }
    }
  }

  .environmentSecrets {
    .inputWrapper {
      max-width: 100%;
    }

    &__item {
      display: grid;
      grid-template-columns: repeat(3, 11rem) 1fr;
      gap: 0.6rem;

      &:not(:first-child) {
        margin-top: var(--space-medium);
      }
    }

    &__type {
      grid-column: 1 / span 1;
    }

    &__name {
      grid-column: 2 / span 1;
    }

    &__path {
      grid-column: 2 / span 2;
    }

    &__value {
      &--var {
        grid-column: 3 / span 1;
      }

      &--path {
        grid-column: 1 / span 3;
      }
    }

    &__buttons {
      grid-column: 4 / span 1;
      grid-row: 1 / span 1;
      align-self: stretch;

      display: flex;
      gap: 0.6rem;
      padding-top: 3.6rem;
    }
  }

  .envVarButton {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 2.6rem;
    width: 2.6rem;
    margin-left: 0.6rem;
    // padding: 0;

    background-color: var(--grey-300);
    border: none;
    border-radius: 50%;
    cursor: pointer;

    svg {
      height: 1.8rem;
    }

    &:hover {
      background-color: var(--grey-400);
    }

    &--hidden {
      pointer-events: none;
      visibility: hidden;
    }
  }
}
</style>
