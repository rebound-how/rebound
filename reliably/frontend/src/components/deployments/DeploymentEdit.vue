<template>
  <form class="deploymentEdit form">
    <fieldset>
      <legend>Deployment</legend>
      <div class="inputWrapper">
        <label for="deploymentName">
          Deployment name <span class="required">Required</span>
        </label>
        <input
          type="text"
          name="deploymentName"
          id="deploymentName"
          v-model="deploymentName"
          required
        />
      </div>
    </fieldset>
    <fieldset>
      <legend>Definition</legend>
      <template v-if="definitionType === 'reliably_cli'">
        <div class="inputWrapper">
          <label for="deploymentCliRunMode">Execution Mode</label>
          <select name="runMode" id="runMode" v-model="definitionCliRunMode" required>
            <option value="manual">Manual</option>
            <option value="managed">Managed</option>
          </select>
          <p class="inputWrapper__help">
          In <strong>manual</strong> mode, Reliably will prepare and schedule a plan but you
          be responsible to execute it with the CLI at your own convenience.
          In <strong>managed</strong> mode, Reliably will launch the plan for you
          immediately or as per its schedule.
          </p>
        </div>
        <template v-if="definitionCliRunMode=='managed'">
          <div class="inputWrapper">
            <label for="deploymentBaseDir">
              Execution Directory
            </label>
            <input
              type="string"
              name="deploymentBaseDir"
              id="deploymentBaseDir"
              v-model="definitionBaseDir"
            />
            <p class="inputWrapper__help">
            Absolute directory where to move to first. This directory must exist.
            If not set, a temporary directory will be created when a plan runs
            </p>
          </div>
          <div class="inputWrapper">
            <label for="deploymentBaseDir">
              Install Python
            </label>
            <select name="pythonVer" id="pythonVer" v-model="definitionPyVer">
              <option value="">Select a python version</option>
              <option value="3.11">3.11</option>
              <option value="3.12">3.12</option>
              <option value="3.13">3.13</option>
              <option value="3.14">3.14</option>
            </select>
            <p class="inputWrapper__help">
            Download an install a specific Python version to run the plan. If not
            set, use the system Python
            </p>
          </div>
          <div class="inputWrapper">
            <label for="deploymentInstallDeps">
              Execution Dependencies
            </label>
            <textarea
              name="deploymentInstallDeps"
              id="deploymentInstallDeps"
              v-model="definitionInstallDeps"
              required
            />
            <p class="inputWrapper__help">
            Python dependencies to install on-the-fly. Set the content of a
            <a href="https://pip.pypa.io/en/stable/reference/requirements-file-format/">requirements.txt</a>
            file
            </p>
          </div>
        </template>
      </template>
      <template v-else-if="definitionType === 'github'">
        <div class="inputWrapper">
          <label for="deploymentRepo">
            Repository <span class="required">Required</span>
          </label>
          <input
            type="url"
            name="deploymentRepo"
            id="deploymentRepo"
            v-model="definitionRepo"
            required
          />
          <p class="inputWrapper__help">A repository URL</p>
        </div>
        <div class="inputWrapper">
          <label for="deploymentBranch">
            Branch <span class="required">Required</span>
          </label>
          <input
            type="text"
            name="deploymentBranch"
            id="deploymentBranch"
            v-model="definitionBranch"
            required
          />
          <p class="inputWrapper__help">
            An existing branch in your target repository
          </p>
        </div>
        <div class="inputWrapper">
          <label for="deploymentUsername">
            Username <span class="required">Required</span>
          </label>
          <input
            type="text"
            name="deploymentUsername"
            id="deploymentUsername"
            v-model="definitionUsername"
            required
          />
          <p class="inputWrapper__help">
            A GitHub username with access to the repository
          </p>
        </div>
        <div class="inputWrapper">
          <label for="deploymentToken">
            Token <span class="required">Required</span>
          </label>
          <input
            type="text"
            name="deploymentToken"
            id="deploymentToken"
            v-model="definitionToken"
            autocomplete="off"
            required
          />
          <p class="inputWrapper__help">
            A token granting access to the repository
          </p>
        </div>
      </template>
      <template v-else-if="definitionType === 'container'">
        <div class="inputWrapper">
          <label for="dockerName">
            Docker image name <span class="required">Required</span>
          </label>
          <input
            type="string"
            name="dockerName"
            id="dockerName"
            v-model="definitionImageName"
            required
          />
          <p class="inputWrapper__help">
            The name of the Docker image this deployment will be targeting
          </p>
        </div>
      </template>
      <template v-else-if="definitionType === 'k8s_job'">
        <div class="inputWrapper">
          <label for="k8sNamespace">
            Namespace <span class="required">Required</span>
          </label>
          <input
            type="string"
            name="k8sNamespace"
            id="k8sNamespace"
            v-model="definitionK8sNamespace"
            placeholder="default"
            required
          />
        </div>
        <div class="inputWrapper">
          <label for="k8sImage">Image</label>
          <input
            type="string"
            name="k8sImage"
            id="k8sImage"
            v-model="definitionK8sImage"
            placeholder="ghcr.io/rebound-how/reliably-job:latest"
          />
        </div>
        <div
          class="inputWrapper inputWrapper--tick"
          aria-labelledby="definitionK8sDefaultManifest"
        >
          <label id="definitionK8sDefaultManifest">
            Use default manifest
          </label>
          <div>
            <input
              type="radio"
              :value="true"
              v-model="definitionK8sUseDefaultManifest"
              id="definitionK8sDefaultManifest-true"
              name="definitionK8sDefaultManifest-true"
            />
            <label for="definitionK8sDefaultManifest-true">True</label>
          </div>
          <div>
            <input
              type="radio"
              :value="false"
              v-model="definitionK8sUseDefaultManifest"
              id="definitionK8sDefaultManifest-false"
              name="definitionK8sDefaultManifest-false"
            />
            <label for="definitionK8sDefaultManifest-false">False</label>
          </div>
        </div>
        <div v-if="!definitionK8sUseDefaultManifest" class="inputWrapper">
          <label for="k8sManifest">
            Manifest <span class="required">Required</span>
          </label>
          <textarea
            name="k8sManifest"
            id="k8sManifest"
            v-model="definitionK8sManifest"
            required
          />
          <p class="inputWrapper__help">
            If you're not using the default manifest, paste your Kubernetes
            manifest here.
          </p>
        </div>
        <div
          v-if="kubernetes"
          class="inputWrapper inputWrapper--tick"
          aria-labelledby="definitionK8sInClusterCredentials"
        >
          <label id="definitionK8sInClusterCredentials">
            Use in-cluster credentials
          </label>
          <p class="inputWrapper__help">
            If Reliably runs in your Kubernetes cluster, you can have it use the
            credentials from the cluster.
          </p>
          <div>
            <input
              type="radio"
              :value="true"
              v-model="definitionK8sUseInClusterCredentials"
              id="definitionK8sInClusterCredentials-true"
              name="definitionK8sInClusterCredentials-true"
            />
            <label for="definitionK8sInClusterCredentials-true">True</label>
          </div>
          <div>
            <input
              type="radio"
              :value="false"
              v-model="definitionK8sUseInClusterCredentials"
              id="definitionK8sInClusterCredentials-false"
              name="definitionK8sInClusterCredentials-false"
            />
            <label for="definitionK8sInClusterCredentials-false">False</label>
          </div>
        </div>
        <div v-if="!definitionK8sUseInClusterCredentials" class="inputWrapper">
          <template v-if="reliablyDeploy === 'onprem'">
            <label for="k8sCredentials"> Credentials </label>
            <textarea
              name="k8sCredentials"
              id="k8sCredentials"
              v-model="definitionK8sCredentials"
            />
            <p class="inputWrapper__help">
              If you don't want Reliably to use in-cluster credentials, you can
              provide credentials here. If no credentials are provided, the
              credentials from the machine running Reliably will be used.
            </p>
          </template>
          <template v-else>
            <label for="k8sCredentials">
              Credentials <span class="required">Required</span>
            </label>
            <textarea
              name="k8sCredentials"
              id="k8sCredentials"
              v-model="definitionK8sCredentials"
              required
            />
            <p class="inputWrapper__help">
              If you don't want Reliably to use in-cluster credentials, you must
              provide credentials here.
            </p>
          </template>
        </div>
      </template>
      <div class="inputWrapper">
        <button @click.prevent="cancel" class="button button--destructiveLight">
          Cancel
        </button>
        <button
          @click.prevent="proceed"
          :disabled="isSubmitDisabled"
          class="button button--creative"
        >
          Save changes
        </button>
      </div>
    </fieldset>
  </form>
</template>

<script setup lang="ts">
import { toRefs, ref, computed, onMounted } from "vue";
import type {
  Deployment,
  GitHubDeploymentDefinition,
  KubernetesDeploymentDefinition,
  ReliablyDeploymentDefinition
} from "@/types/deployments";
import { editDeployment } from "@/stores/deployments";
import type { ContainerDeploymentDefinition } from "@/types/deployments";

const props = defineProps<{
  current: Deployment;
  supported: string[];
  reliablyDeploy: string;
  kubernetes: boolean;
}>();
const { current, supported, reliablyDeploy, kubernetes } = toRefs(props);

const emit = defineEmits<{
  (e: "cancelled"): void;
  (e: "saved"): void;
}>();

function supports(type: string): boolean {
  return supported.value.includes(type);
}

const deploymentName = ref<string>("");
const definitionType = ref<string>("");
const definitionRepo = ref<string>("");
const definitionBranch = ref<string>("main");
const definitionUsername = ref<string>("");
const definitionToken = ref<string>("");
const definitionImageName = ref<string>("");
const definitionK8sNamespace = ref<string>("default");
const definitionK8sImage = ref<string>("");
const definitionK8sUseDefaultManifest = ref<boolean>(true);
const definitionK8sManifest = ref<string>("");
const definitionK8sUseInClusterCredentials = ref<boolean>(false);
const definitionK8sCredentials = ref<string>("");
const definitionCliRunMode = ref<string>("manual");
const definitionBaseDir = ref<string>("");
const definitionPyVer = ref<string>("");
const definitionInstallDeps = ref<string>("");

const isSubmitDisabled = computed<boolean>(() => {
  if (definitionType.value === "") {
    return true;
  } else if (definitionType.value === "github") {
    return (
      deploymentName.value === "" ||
      definitionRepo.value === "" ||
      definitionBranch.value === "" ||
      definitionUsername.value === "" ||
      definitionToken.value === ""
    );
  } else if (definitionType.value === "container") {
    return deploymentName.value === "" || definitionImageName.value === "";
  } else if (definitionType.value === "reliably_cloud") {
    return deploymentName.value === "";
  } else if (definitionType.value === "reliably_cli") {
    return deploymentName.value === "";
  } else if (definitionType.value === "kubernetes") {
    return (
      deploymentName.value === "" ||
      definitionK8sNamespace.value === "" ||
      (kubernetes.value === false &&
        definitionK8sUseDefaultManifest.value === false &&
        definitionK8sCredentials.value === "") ||
      (definitionK8sUseDefaultManifest.value === false &&
        definitionK8sManifest.value === "") ||
      (definitionK8sUseInClusterCredentials.value === false &&
        definitionK8sCredentials.value === "")
    );
  } else {
    return true;
  }
});

const cancel = () => {
  emit("cancelled");
};

const proceed = async () => {
  let deployment: Deployment = {
    name: deploymentName.value,
    definition: {
      type: definitionType.value,
    },
  };
  if (definitionType.value === "github") {
    deployment.definition = {
      type: definitionType.value,
      repo: definitionRepo.value,
      branch: definitionBranch.value,
      username: definitionUsername.value,
      token: definitionToken.value,
    };
  } else if (definitionType.value === "container") {
    deployment.definition = {
      type: definitionType.value,
      image: definitionImageName.value,
    };
  } else if (definitionType.value === "kubernetes") {
    deployment.definition = {
      type: "k8s_job",
      namespace: definitionK8sNamespace.value,
      use_default_manifest: definitionK8sUseDefaultManifest.value,
      use_in_cluster_credentials: definitionK8sUseInClusterCredentials.value,
    };
    if (definitionK8sImage.value !== "") {
      (deployment.definition as KubernetesDeploymentDefinition).image =
        definitionK8sImage.value;
    }
    if (definitionK8sManifest.value !== "") {
      (deployment.definition as KubernetesDeploymentDefinition).manifest =
        definitionK8sManifest.value;
    }
    if (definitionK8sCredentials.value !== "") {
      (deployment.definition as KubernetesDeploymentDefinition).credentials =
        definitionK8sCredentials.value;
    }
  } else if (definitionType.value === "reliably_cli") {
    deployment.definition =  {
      type: definitionType.value,
      mode: definitionCliRunMode.value,
      base_dir: definitionBaseDir.value,
      py_version: definitionPyVer.value,
      py_dependencies: definitionInstallDeps.value,
    }
  }
  await editDeployment(current.value.id!, deployment);
  emit("saved");
};

function setOriginalValues() {
  deploymentName.value = current.value.name;
  definitionType.value = current.value.definition.type;

  if (definitionType.value === "github") {
    const def = current.value.definition as GitHubDeploymentDefinition;
    definitionRepo.value = def.repo;
    if (def.branch) {
      definitionBranch.value = def.branch;
    }
    definitionUsername.value = def.username;
    definitionToken.value = def.token;
  } else if (definitionType.value === "container") {
    definitionImageName.value = (
      current.value.definition as ContainerDeploymentDefinition
    ).image;
  } else if (definitionType.value === "kubernetes") {
    const def = current.value.definition as KubernetesDeploymentDefinition;
    definitionK8sNamespace.value = def.namespace;
    definitionK8sImage.value = def.image || "";
    definitionK8sUseDefaultManifest.value = def.use_default_manifest;
    definitionK8sUseInClusterCredentials.value = def.use_in_cluster_credentials;
    definitionK8sCredentials.value = def.credentials || "";
  } else if (definitionType.value === "reliably_cli") {
    const def = current.value.definition as ReliablyDeploymentDefinition;
    definitionCliRunMode.value = def.mode || "manual";
    definitionBaseDir.value = def.base_dir || "";
    definitionPyVer.value = def.py_version || "";
    definitionInstallDeps.value = def.py_dependencies || "";
  }
}

onMounted(() => {
  setOriginalValues();
});
</script>

<style lang="scss" scoped>
.deploymentEdit {
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
</style>
