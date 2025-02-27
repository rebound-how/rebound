<template>
  <li class="deploymentPreview tableList__row">
    <div
      class="tableList__cell tableList__cell--center tableList__cell--status deploymentPreview__icon"
    >
      <span
        v-if="deployment.definition.type === 'github'"
        title="GitHub Deployment"
      >
        <GithubLogo />
      </span>
      <span
        v-else-if="deployment.definition.type === 'reliably_cloud'"
        title="Reliably Deployment"
      >
        <ReliablyLogo />
      </span>
      <span
        v-else-if="deployment.definition.type === 'reliably_cli'"
        title="Reliably CLI Deployment"
      >
        <ReliablyLogo />
      </span>
      <span
        v-else-if="deployment.definition.type === 'container'"
        title="Docker Container Deployment"
      >
        <DockerLogo />
      </span>
      <span
        v-else-if="deployment.definition.type === 'k8s_job'"
        title="Kubernetes Deployment"
      >
        <KubernetesLogo />
      </span>
    </div>
    <div class="tableList__cell deploymentPreview__name">
      <a :href="`/deployments/view?id=${deployment.id}`">
        {{ deployment.name }}
      </a>
      <small>Created <TimeAgo :timestamp="deployment.created_date" /></small>
    </div>
    <div
      v-if="deployment.definition.type === 'github'"
      class="tableList__cell deploymentPreview__repo"
    >
      <a
        :href="(deployment.definition as GitHubDeploymentDefinition).repo"
        target="_blank"
        rel="noreferer noopener"
      >
        {{ repository!.organization }}/<strong>
          {{ repository!.repository }}
        </strong>
      </a>
      <small>
        Environment:
        {{ (deployment.definition as GitHubDeploymentDefinition).name }}
      </small>
    </div>
    <div
      v-else-if="deployment.definition.type === 'container'"
      class="tableList__cell deploymentPreview__repo"
    >
      {{ (deployment.definition as ContainerDeploymentDefinition).image }}
    </div>
    <div
      v-else-if="deployment.definition.type === 'k8s_job'"
      class="tableList__cell deploymentPreview__repo"
    >
      {{ (deployment.definition as KubernetesDeploymentDefinition).namespace }}
    </div>
    <div
      v-else-if="deployment.definition.type === 'reliably_cli'"
      class="tableList__cell deploymentPreview__repo"
    >
      {{ runMode }}
    </div>
    <div v-else></div>
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
        <ConfirmDeleteDeployment
          :id="deployment.id!"
          :page="page"
          :in-place="true"
          @close="closeDelete"
        />
      </template>
    </ModalWindow>
  </li>
</template>

<script setup lang="ts">
import { toRefs, computed, ref } from "vue";
import type {
  Deployment,
  ContainerDeploymentDefinition,
  GitHubDeploymentDefinition,
  KubernetesDeploymentDefinition,
  ReliablyDeploymentDefinition
} from "@/types/deployments";
import type { Repository } from "@/types/ui-types";

import GithubLogo from "@/components/svg/GithubLogo.vue";
import ReliablyLogo from "@/components/svg/ReliablyRLogo.vue";
import DockerLogo from "@/components/svg/DockerLogo.vue";
import KubernetesLogo from "@/components/svg/KubernetesLogo.vue";
import TimeAgo from "@/components/_ui/TimeAgo.vue";
import DeleteButton from "@/components/_ui/DeleteButton.vue";
import ModalWindow from "@/components/_ui/ModalWindow.vue";
import ConfirmDeleteDeployment from "@/components/deployments/ConfirmDeleteDeployment.vue";

import { urlToRepository } from "@/utils/strings";

const props = defineProps<{
  deployment: Deployment;
  page?: number;
}>();
const { deployment, page } = toRefs(props);

const repository = computed<Repository | null>(() => {
  if (deployment.value.definition.type === "github") {
    return urlToRepository(
      (deployment.value.definition as GitHubDeploymentDefinition).repo
    );
  } else {
    return null;
  }
});

const runMode = computed<string>(() => {
  let mode = (deployment.value?.definition as ReliablyDeploymentDefinition).mode || "manual";

  return mode == "manual" ? "Manual": "Managed";
});

const isDeleteDisplayed = ref<boolean>(false);

const displayDelete = () => {
  isDeleteDisplayed.value = true;
};
const closeDelete = () => {
  isDeleteDisplayed.value = false;
};
</script>

<style lang="scss" scoped>
.deploymentPreview {
  > .tableList__cell {
    small {
      display: block;

      color: var(--text-color-dim);
      font-size: 1.4rem;
    }
  }

  &__icon {
    svg {
      width: 2.4rem;
    }

    span[title="Kubernetes Deployment"] {
      color: hsl(220, 72%, 53%);
    }
  }

  &__name,
  &__repo {
    a {
      text-decoration: none;

      &:hover {
        color: var(--accentColorSecondary);
      }
    }
  }

  &__name {
    a {
      font-size: 1.8rem;
      font-weight: 700;
    }
  }

  &__user {
    vertical-align: top;
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
