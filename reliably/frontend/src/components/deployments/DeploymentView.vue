<template>
  <LoadingPlaceholder size="large" v-if="isLoading" />
  <article class="deploymentView" v-else-if="deploy !== undefined && deploy.id">
    <header class="pageHeader">
      <div>
        <h1 class="pageHeader__title">
          {{ deploy.name }} <small>{{ shortenUuid(deploy.id) }}</small>
        </h1>
      </div>
      <div class="pageHeader__actions">
        <MultiButton
          v-if="deploy !== undefined"
          title="Manage deployment"
          :options="manageActions"
          @emit-action="handleMultiButtonAction"
        />
        <a href="/deployments/new/" class="button button--creative">
          New deployment
        </a>
      </div>
    </header>
    <section class="deploymentInfo">
      <dl>
        <div
          class="deploymentInfo__type"
          :class="`deploymentInfo__type--${deploy.definition.type}`"
        >
          <dt>Type</dt>
          <dd v-if="deploy.definition.type === 'github'">
            <GithubLogo /> GitHub
          </dd>
          <dd v-else-if="deploy.definition.type === 'reliably_cloud'">
            <ReliablyLogo /> Reliably Cloud
          </dd>
          <dd v-else-if="deploy.definition.type === 'reliably_cli'">
            <ReliablyLogo /> Reliably CLI
          </dd>
          <dd v-else-if="deploy.definition.type === 'container'">
            <DockerLogo /> Docker
          </dd>
          <dd v-else-if="deploy.definition.type === 'k8s_job'">
            <KubernetesLogo /> Kubernetes
          </dd>
        </div>
        <div v-if="deploy.definition.type === 'reliably_cli'">
          <dt>Execution Mode</dt>
          <dd>{{ deploymentRunMode }}</dd>
        </div>
        <div v-if="deploy.definition.type === 'reliably_cli' && deploymentRunMode === 'Managed'">
          <dt>Execution Directory</dt>
          <dd>{{ deploymentRunDir }}</dd>
        </div>
        <div v-if="deploy.definition.type === 'reliably_cli' && deploymentRunMode === 'Managed'">
          <dt>Python Version</dt>
          <dd>{{ deploymentPyVer }}</dd>
        </div>
        <div v-if="deploy.definition.type === 'github'">
          <dt>Repository</dt>
          <dd>
            {{ repository?.organization }}/<strong>{{
              repository?.repository
            }}</strong>
          </dd>
        </div>
        <div v-if="deploy.definition.type === 'github'">
          <dt>Environment</dt>
          <dd>{{ (deploy.definition as GitHubDeploymentDefinition).name }}</dd>
        </div>
        <div v-if="deploy.definition.type === 'container'">
          <dt>Image</dt>
          <dd>
            {{ (deploy.definition as ContainerDeploymentDefinition).image }}
          </dd>
        </div>
        <div v-if="deploy.definition.type === 'k8s_job'">
          <dt>Namespace</dt>
          <dd>
            {{
              (deploy.definition as KubernetesDeploymentDefinition).namespace
            }}
          </dd>
        </div>
        <div v-if="deploy.definition.type === 'k8s_job'">
          <dt>Image</dt>
          <dd
            v-if="(deploy.definition as KubernetesDeploymentDefinition).image"
          >
            {{ (deploy.definition as KubernetesDeploymentDefinition).image }}
          </dd>
          <dd v-else>-</dd>
        </div>
        <div v-if="deploy.definition.type === 'k8s_job'">
          <dt>Use default manifest</dt>
          <dd
            v-if="(deploy.definition as KubernetesDeploymentDefinition).use_default_manifest"
          >
            Yes
          </dd>
          <dd v-else>No</dd>
        </div>
        <div v-if="deploy.definition.type === 'k8s_job'">
          <dt>Use in-cluster credentials</dt>
          <dd
            v-if="(deploy.definition as KubernetesDeploymentDefinition).use_in_cluster_credentials"
          >
            Yes
          </dd>
          <dd v-else>No</dd>
        </div>
        <div>
          <dt>Created</dt>
          <dd>
            <TimeAgo :timestamp="deploy.created_date" />
          </dd>
        </div>
      </dl>
    </section>
    <section class="deploymentHelp">
      <a
        href="https://reliably.com/docs/concepts/deployments/"
        rel="noopener noreferer"
        target="_blank"
      >
        Read the docs
      </a>
      to learn how to use this deployment in your Reliably plans.
    </section>
    <section class="deploymentPlans">
      <DeploymentPlans :deploymentId="deploy.id" />
    </section>
    <ModalWindow
      v-if="isDeleteDisplayed"
      :hasCloseButton="true"
      :hasPadding="true"
      @close="closeDelete"
    >
      <template #title>Delete Deployment</template>
      <template #content>
        <ConfirmDeleteDeployment :id="deploy.id" @close="closeDelete" />
      </template>
    </ModalWindow>
    <ModalWindow
      v-if="isCloneDisplayed"
      :hasCloseButton="true"
      :hasPadding="true"
      @close="closeClone"
    >
      <template #title>Clone Deployment</template>
      <template #content>
        <CloneDeploymentForm :id="deploy.id" @close="closeDelete" />
      </template>
    </ModalWindow>
    <ModalWindow
      v-if="isEditionDisplayed"
      :hasCloseButton="true"
      :hasPadding="true"
      @close="closeEdit"
    >
      <template #title>Edit Deployment</template>
      <template #content>
        <DeploymentEdit
          :current="deploy"
          :supported="supported"
          :reliably-deploy="reliablyDeploy"
          :kubernetes="kubernetes"
          @cancelled="closeEdit"
          @saved="closeEditAndFetch"
        />
      </template>
    </ModalWindow>
  </article>
  <NoData v-else message="We couldn't find a deployment with this ID." />
</template>

<script setup lang="ts">
import { toRefs, ref, onMounted, computed } from "vue";
import { shortenUuid, urlToRepository } from "@/utils/strings";
import type {
  Deployment,
  GitHubDeploymentDefinition,
  ContainerDeploymentDefinition,
  KubernetesDeploymentDefinition,
  ReliablyDeploymentDefinition
} from "@/types/deployments";
import type { Repository, MultiButtonOption } from "@/types/ui-types";

import { deployment, fetchDeployment } from "@/stores/deployments";

import LoadingPlaceholder from "@/components/_ui/LoadingPlaceholder.vue";
import NoData from "@/components/_ui/NoData.vue";
import MultiButton from "@/components/_ui/MultiButton.vue";
import TimeAgo from "@/components/_ui/TimeAgo.vue";
import ModalWindow from "@/components/_ui/ModalWindow.vue";
import ConfirmDeleteDeployment from "@/components/deployments/ConfirmDeleteDeployment.vue";
import CloneDeploymentForm from "@/components/deployments/CloneDeploymentForm.vue";
import DeploymentEdit from "@/components/deployments/DeploymentEdit.vue";
import DeploymentPlans from "@/components/plans/DeploymentPlans.vue";

import GithubLogo from "@/components/svg/GithubLogo.vue";
import ReliablyLogo from "@/components/svg/ReliablyRLogo.vue";
import DockerLogo from "@/components/svg/DockerLogo.vue";
import KubernetesLogo from "@/components/svg/KubernetesLogo.vue";

const props = defineProps<{
  supported: string[];
  reliablyDeploy: string;
  kubernetes: boolean;
}>();
const { supported, reliablyDeploy, kubernetes } = toRefs(props);

const isLoading = ref(true);
const id = ref<string | undefined>(undefined);
const deploy = ref<Deployment | undefined>(undefined);

const deploymentRunMode = computed<string>(() => {
  let mode = (deploy.value?.definition as ReliablyDeploymentDefinition).mode || "manual";

  return mode == "manual" ? "Manual": "Managed";
});

const deploymentRunDir = computed<string>(() => {
  return (deploy.value?.definition as ReliablyDeploymentDefinition).base_dir || "Dynamically Generated";
});

const deploymentPyVer = computed<string>(() => {
  return (deploy.value?.definition as ReliablyDeploymentDefinition).py_version || "System";
});

const manageActions = ref<MultiButtonOption[]>([
  {
    label: "Clone",
    action: "clone",
    icon: "copy",
  },
  {
    label: "Edit",
    action: "edit",
    icon: "edit",
  },
  {
    label: "Delete",
    action: "delete",
    icon: "trash",
    warning: true,
  },
]);

const getCurrentId = () => {
  let location = window.location;
  let params = new URLSearchParams(location.search);
  if (params.has("id")) {
    id.value = params.get("id")!;
  }
};

const getDeployment = async () => {
  await fetchDeployment(id.value!);
  deploy.value = deployment.get() as Deployment;
};

const repository = ref<Repository | null>(null);

const setMetaData = () => {
  let title = "Deployment · Reliably";
  let description = "View your Reliably deployment details";
  if (deploy.value !== undefined) {
    title = `${deploy.value.name} · Reliably`;
  }
  document.title = title;
  const meta: HTMLElement | null = document.querySelector(
    "meta[name='description']"
  );
  if (meta instanceof HTMLMetaElement) {
    meta.content = description;
  }
};

async function handleMultiButtonAction(action: string) {
  if (action === "delete") {
    displayDelete();
  } else if (action === "edit") {
    displayEdit();
  } else if (action === "clone") {
    displayClone();
  }
}

const isDeleteDisplayed = ref<boolean>(false);
const displayDelete = () => {
  isDeleteDisplayed.value = true;
};
const closeDelete = () => {
  isDeleteDisplayed.value = false;
};

const isEditionDisplayed = ref<boolean>(false);
function displayEdit() {
  isEditionDisplayed.value = true;
}
function closeEdit() {
  isEditionDisplayed.value = false;
}
async function closeEditAndFetch() {
  await getData();
  isEditionDisplayed.value = false;
}

const isCloneDisplayed = ref<boolean>(false);
function displayClone() {
  isCloneDisplayed.value = true;
}
function closeClone() {
  isCloneDisplayed.value = false;
}

async function getData() {
  isLoading.value = true;
  getCurrentId();
  await getDeployment();
  if (deploy.value?.definition.type === "github") {
    repository.value = urlToRepository(
      (deploy.value?.definition as GitHubDeploymentDefinition).repo!
    );
  }
  setMetaData();
  isLoading.value = false;
}

onMounted(async () => {
  await getData();
});
</script>

<style lang="scss" scoped>
.deploymentView {
  .deploymentInfo {
    dl {
      display: flex;
      margin: 0;
      padding: var(--space-small);

      background-color: var(--section-background);
      border-radius: var(--border-radius-m);

      > div {
        flex: 1 0 auto;
        padding-right: var(--space-small);
      }

      > div + div {
        padding-left: var(--space-small);

        border-left: 1px solid var(--section-separator-color);
      }

      dt {
        color: var(--text-color-dim);
        font-size: 1.4rem;
        text-transform: uppercase;
      }

      dd {
        svg {
          height: 2.4rem;

          vertical-align: -0.6rem;
        }
      }
    }

    &__type {
      &--k8s_job {
        svg {
          color: hsl(220, 72%, 53%);
        }
      }
    }
  }

  > section + section {
    margin-top: var(--space-large);
  }

  .experimentMeta {
    display: grid;
    grid-template-columns: 1fr 2fr;
    gap: var(--space-medium);

    padding: var(--space-small);

    background-color: var(--section-background);
    border-radius: var(--border-radius-s);

    .experimentSsh {
      h2 {
        margin-top: 0;
      }

      &__title {
        font-size: 1.8rem;
        font-weight: 500;
      }

      &__label {
        color: var(--text-color-dim);
        font-size: 1.4rem;
        text-transform: uppercase;
      }
    }
  }
}
</style>
