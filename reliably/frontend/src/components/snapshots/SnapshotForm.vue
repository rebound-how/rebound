<template>
  <form class="snapshotForm form">
    <fieldset>
      <div class="inputWrapper">
        <label for="integrationName">
          Name <span class="required">Required</span>
        </label>
        <input
          type="text"
          name="integrationName"
          id="integrationName"
          v-model="integrationName"
          required
        />
      </div>
    </fieldset>
    <fieldset>
      <legend>Select systems to discover resources</legend>
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
      <legend>AWS Credentials</legend>
      <div class="inputWrapper">
        <label for="awsUseSystemCreds" class="flex">
          <span>Use System Credentials</span>
        <input
          type="checkbox"
          name="awsUseSystemCreds"
          id="awsUseSystemCreds"
          v-model="var_AwsUseSystemCreds"
          autocomplete="off"
          required
        />
      </label>
      </div>
      <div class="inputWrapper" v-if="var_AwsUseSystemCreds===false">
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
      <div class="inputWrapper" v-if="var_AwsUseSystemCreds===false">
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
      <legend>Google Cloud Credentials</legend>
      <div class="inputWrapper">
        <label for="gcpUseSystemCreds" class="flex">
          <span>Use System Credentials</span>
        <input
          type="checkbox"
          name="gcpUseSystemCreds"
          id="gcpUseSystemCreds"
          v-model="var_GcpUseSystemCreds"
          autocomplete="off"
          required
        />
      </label>
      </div>
      <div class="inputWrapper" v-if="var_GcpUseSystemCreds==false">
        <label for="gcpProjectId" class="flex">
          <span class="jsonString">GOOGLE_CLOUD_PROJECT_ID</span>
          <span class="envvar flex-right">Variable</span>
        </label>
        <input
          type="text"
          name="gcpProjectId"
          id="gcpProjectId"
          v-model="var_GcpProjectId"
          autocomplete="off"
          required
        />
      </div>
      <div class="inputWrapper" v-if="var_GcpUseSystemCreds==false">
        <label for="gcpRegion" class="flex">
          <span class="jsonString">GOOGLE_CLOUD_REGION</span>
          <span class="envvar flex-right">Variable</span>
        </label>
        <input
          type="text"
          name="gcpRegion"
          id="gcpRegion"
          v-model="var_GcpRegion"
          autocomplete="off"
          placeholder="us-east1"
          required
        />
      </div>
      <div class="inputWrapper" v-if="var_GcpUseSystemCreds==false">
        <label for="gcpConfigFile" class="flex">
          <span class="jsonString">GOOGLE_APPLICATION_CREDENTIALS</span>
          <span class="required">Required</span>
          <span class="secret flex-right">Secret</span>
        </label>
        <textarea
          name="gcpConfigFile"
          id="gcpConfigFile"
          placeholder="Paste file content here"
          v-model="secret_GcpCredentials"
          autocomplete="off"
          required
        ></textarea>
      </div>
    </fieldset>
    <fieldset v-if="hasCustomKubernetes">
      <legend>Kubernetes Credentials</legend>
      <div class="inputWrapper">
        <label for="k8sUseSystemCreds" class="flex">
          <span>Use System Credentials</span>
        <input
          type="checkbox"
          name="k8sUseSystemCreds"
          id="k8sUseSystemCreds"
          v-model="var_k8sUseSystemCreds"
          autocomplete="off"
          required
        />
      </label>
      </div>
      <div class="inputWrapper" v-if="var_k8sUseSystemCreds==false">
        <label for="kubeConfigFile" class="flex">
          <span class="jsonString">KUBECONFIG</span>
          <span class="required">Required</span>
          <span class="secret flex-right">Secret</span>
        </label>
        <textarea
          name="kubeConfigFile"
          id="kubeConfigFile"
          placeholder="Paste file content here"
          v-model="secret_kubeConfig"
          autocomplete="off"
          required
        ></textarea>
      </div>
    </fieldset>
    <fieldset v-if="hasCustomGitHub">
      <legend>GitHub Credentials</legend>
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
    <fieldset>
      <div class="inputWrapper">
        <button
          @click.prevent="proceed"
          :disabled="isSubmitDisabled"
          class="button button--primary"
          :class="{ 'button--waiting': isSubmitButtonInWaitMode }"
        >
          Start discovery
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
import type { NewSnapshot } from "@/types/snapshots";
import { createIntegration } from "@/stores/integrations";
import { setupSnapshot, fetchConfig, snapshotConfig, updateSnapshotConfiguration } from "@/stores/snapshots";
import { generateKey } from "@/utils/strings";

import ButtonLoader from "@/components/svg/ButtonLoader.vue";
import AwsLogo from "@/components/svg/AwsLogo.vue";
import GoogleCloudLogo from "@/components/svg/GoogleCloudLogo.vue";
import KubernetesLogo from "@/components/svg/KubernetesLogoBlue.vue";
import GitHubLogo from "@/components/svg/GithubLogo.vue";

const integrationName = ref<string>("");
const hasCustomAWS = ref<boolean>(false);
const hasCustomGCP = ref<boolean>(false);
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
    } else if (t === "kubernetes") {
      hasCustomKubernetes.value === true;
    }
  }
}

// Special variables and secrets: AWS
const var_AwsUseSystemCreds = ref<boolean>(true);
const secret_AwsAccessKeyId = ref<string>("");
const secret_AwsSecretAccessKey = ref<string>("");

// Special variables and secrets: GCP
const var_GcpUseSystemCreds = ref<boolean>(true);
const var_GcpProjectId = ref<string>("");
const var_GcpRegion = ref<string>("");
const secret_GcpCredentials = ref<string>("");

// Special variables and secrets: Kubernetes
const var_k8sUseSystemCreds = ref<boolean>(true);
const secret_kubeConfig = ref<string>("");

// Special variables and secrets: GitHub
const secret_gitHubToken = ref<string>("");

const isSubmitButtonInWaitMode = ref<boolean>(false);
const isSubmitDisabled = computed<boolean>(() => {
  if (integrationName.value === "" || isSubmitButtonInWaitMode.value) {
    return true;
  } else {
    return false;
  }
});

function refreshConfig() {
  if (snapshotConfig.value !== null) {
    const c = snapshotConfig.value;
  
    integrationName.value = c.name;

    const vars = c.env.envvars;
    const secrets = c.env.secrets;

    const hasAws = getEnvValue(vars, "RELIABLY_EXPLORE_AWS");
    if (hasAws !== undefined) {
      hasCustomAWS.value = true;

      const useAwsCreds = getEnvValue(vars, "RELIABLY_AWS_USE_SYSTEM_CREDS");
      var_AwsUseSystemCreds.value = useAwsCreds !== undefined;

      let awsValue = getEnvValue(vars, "AWS_ACCESS_KEY_ID");
      secret_AwsAccessKeyId.value = awsValue == undefined ? "" : awsValue;

      awsValue = getEnvValue(secrets, "AWS_SECRET_ACCESS_KEY");
      secret_AwsSecretAccessKey.value = awsValue == undefined ? "" : awsValue;
    }

    const hasK8s = getEnvValue(vars, "RELIABLY_EXPLORE_K8S");
    if (hasK8s !== undefined) {
      hasCustomKubernetes.value = true;

      const useK8sCreds = getEnvValue(vars, "RELIABLY_K8S_USE_SYSTEM_CREDS");
      var_k8sUseSystemCreds.value = useK8sCreds !== undefined;

      let k8sValue = getEnvValue(secrets, "KUBECONFIG");
      secret_kubeConfig.value = k8sValue == undefined ? "" : k8sValue;
    }

    const hasGcp = getEnvValue(vars, "RELIABLY_EXPLORE_GCP");
    if (hasGcp !== undefined) {
      hasCustomGCP.value = true;

      const useK8sCreds = getEnvValue(vars, "RELIABLY_GCP_USE_SYSTEM_CREDS");
      var_GcpUseSystemCreds.value = useK8sCreds !== undefined;

      let gcpValue = getEnvValue(vars, "GOOGLE_CLOUD_PROJECT_ID");
      var_GcpProjectId.value = gcpValue == undefined ? "" : gcpValue;

      gcpValue = getEnvValue(vars, "GOOGLE_CLOUD_REGION");
      var_GcpRegion.value = gcpValue == undefined ? "" : gcpValue;

      gcpValue = getEnvValue(secrets, "GOOGLE_APPLICATION_CREDENTIALS");
      secret_GcpCredentials.value = gcpValue == undefined ? "" : gcpValue;
    }
  }
};

function getEnvValue(vars: Var[] | Secret[], key: string) {
  for (const v of vars) {
    if (v.var_name === key) {
      return v.value;
    }
  }
}

// Environment Variables
const envVars = ref<Var[]>([]);

// Environment Secrets
const envSecrets = ref<Secret[]>([]);

const proceed = async () => {
  isSubmitButtonInWaitMode.value = true;
  if (hasCustomAWS.value === true) {
    envVars.value.push({
      var_name: "RELIABLY_EXPLORE_AWS",
      value: "1",
    });
    if (var_AwsUseSystemCreds.value === true) {
      envVars.value.push({
        var_name: "RELIABLY_AWS_USE_SYSTEM_CREDS",
        value: "1"
      });
    } else {
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
  }
  if (hasCustomGCP.value === true) {
    envVars.value.push({
      var_name: "RELIABLY_EXPLORE_GCP",
      value: "1",
    });
    if (var_GcpUseSystemCreds.value === true) {
      envVars.value.push({
        var_name: "RELIABLY_GCP_USE_SYSTEM_CREDS",
        value: "1"
      });
    } else {
      envVars.value.push({
        var_name: "GOOGLE_CLOUD_PROJECT_ID",
        value: var_GcpProjectId.value,
      });
      envVars.value.push({
        var_name: "GOOGLE_CLOUD_REGION",
        value: var_GcpRegion.value,
      });
      envSecrets.value.push({
        var_name: "GOOGLE_APPLICATION_CREDENTIALS",
        value: secret_GcpCredentials.value,
        key: generateKey(32),
      });
    }
  }
  if (hasCustomKubernetes.value === true) {
    envVars.value.push({
      var_name: "RELIABLY_EXPLORE_K8S",
      value: "1",
    });
    if (var_k8sUseSystemCreds.value === true) {
      envVars.value.push({
        var_name: "RELIABLY_K8S_USE_SYSTEM_CREDS",
        value: "1"
      });
    } else {
      envSecrets.value.push({
        var_name: "KUBECONFIG",
        value: secret_kubeConfig.value,
        key: generateKey(32),
      });
    }
  }
  if (hasCustomGitHub.value === true) {
    envVars.value.push({
      var_name: "RELIABLY_EXPLORE_GITHUB",
      value: "1",
    });
    envSecrets.value.push({
      var_name: "GITHUB_TOKEN",
      value: secret_gitHubToken.value,
      key: generateKey(32),
    });
  }

  const environment: Environment = {
    name: integrationName.value,
    envvars: envVars.value,
    secrets: envSecrets.value,
    used_for: "snapshot"
  };

  if (snapshotConfig.value === null) {
    const integration = await createIntegration({
      name: integrationName.value,
      provider: "snapshot",
      vendor: "reliably",
      environment
    }, true);

    let snapshot: NewSnapshot = {
      integration_id: integration?.id,
    };
    await setupSnapshot(snapshot);
  } else {
    let int_id = snapshotConfig.value.integration_id;
    await updateSnapshotConfiguration(int_id, environment);
  }
  isSubmitButtonInWaitMode.value = false;
};

onMounted(async () => {
  getSetTemplate();
  await fetchConfig();
  refreshConfig();
});
</script>

<style lang="scss" scoped>
.snapshotForm {
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
