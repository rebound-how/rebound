<template>
  <li class="planPreview tableList__row">
    <div
      class="tableList__cell tableList__cell--center tableList__cell--status"
    >
      <PlanMiniStatus :status="computedStatus" />
    </div>
    <div class="tableList__cell planPreview__meta">
      <a :href="`/plans/view/?id=${plan.id}`" v-if="plan.definition.title">
        {{ plan.definition.title }}
      </a>
      <a :href="`/plans/view/?id=${plan.id}`" v-else>
        {{ shortenUuid(plan.id) }}
      </a>
      <small>{{ plan.id }}</small>
      <small>Created <TimeAgo :timestamp="plan.created_date" /></small>
    </div>
    <div class="tableList__cell planPreview__env">
      <template v-if="plan.definition.environment">
        <span v-if="plan.definition.environment.provider === 'github'">
          <GithubLogo title="GitHub Environment" />
          {{ (plan.definition.environment as PlanGitHubEnvironment).name }}
        </span>
        <span
          v-if="
            plan.definition.environment.id !== undefined &&
            plan.definition.environment.id !== null
          "
        >
          <ReliablyLogo title="Reliably Environment" />
          <a :href="`/environments/view/?id=${plan.definition.environment.id}`">
            {{ env?.name }}
          </a>
        </span>
      </template>
    </div>
    <div class="tableList__cell planPreview__dep">

      <span
        v-if="plan.definition.deployment.deployment_type === 'github'"
        title="GitHub Deployment"
      >
        <GithubLogo />
        <a
          :href="`/deployments/view/?id=${plan.definition.deployment.deployment_id}`"
        >
          {{ dep }}
        </a>
      </span>
      <span
        v-else-if="plan.definition.deployment.deployment_type === 'reliably_cloud'"
        title="Reliably Deployment"
      >
        <ReliablyLogo />
        <a
          :href="`/deployments/view/?id=${plan.definition.deployment.deployment_id}`"
        >
          {{ dep }}
        </a>
      </span>
      <span
        v-else-if="plan.definition.deployment.deployment_type === 'reliably_cli'"
        title="Reliably CLI Deployment"
      >
        <ReliablyLogo />
        <a
          :href="`/deployments/view/?id=${plan.definition.deployment.deployment_id}`"
        >
          {{ dep }}
        </a>
      </span>
      <span
        v-else-if="plan.definition.deployment.deployment_type === 'container'"
        title="Docker Container Deployment"
      >
        <DockerLogo />
        <a
          :href="`/deployments/view/?id=${plan.definition.deployment.deployment_id}`"
        >
          {{ dep }}
        </a>
      </span>
      <span
        v-else-if="plan.definition.deployment.deployment_type === 'k8s_job'"
        title="Kubernetes Deployment"
      >
        <KubernetesLogo />
        <a
          :href="`/deployments/view/?id=${plan.definition.deployment.deployment_id}`"
        >
          {{ dep }}
        </a>
      </span>
      <span v-else>
      
        <a
          :href="`/deployments/view/?id=${plan.definition.deployment.deployment_id}`"
        >
          {{ dep }}
        </a>
      </span>
    </div>
    <div class="tableList__cell planPreview__runs">
      {{ plan.executions_count ? plan.executions_count.toString() : "-" }}
    </div>
    <div class="tableList__cell planPreview__last">
      <span>{{ lastRun[0] }}</span>
      <span
        v-if="lastRun[1] !== '' && browserZone !== ''"
        :title="`Displayed for timezone ${browserZone}`"
        >{{ lastRun[1] }}</span
      >
      <span v-else-if="lastRun[1] !== ''">{{ lastRun[1] }}</span>
    </div>
    <div class="tableList__cell planPreview__next">
      <span>{{ nextRun[0] }}</span>
      <span
        v-if="nextRun[1] !== '' && browserZone !== ''"
        :title="`Displayed for timezone ${browserZone}`"
        >{{ nextRun[1] }}</span
      >
      <span v-else-if="nextRun[1] !== ''">{{ nextRun[1] }}</span>
    </div>
    <div class="tableList__cell planPreview__schedule">
      <span v-if="plan.definition.schedule.type === 'now'">
        Once
      </span>
      <span v-if="plan.definition.schedule.type === 'cron'">
        Periodic
      </span>
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
        <ConfirmDeletePlan
          :id="plan.id"
          :in-place="true"
          :store="store"
          :page="page"
          @close="closeDelete"
        />
      </template>
    </ModalWindow>
  </li>
</template>

<script setup lang="ts">
import { toRefs, ref, computed, onMounted } from "vue";
import dayjs from "dayjs";
import timezone from "dayjs/plugin/timezone";

import type {
  Plan,
  PlanGitHubEnvironment,
  PlanReliablyEnvironment,
} from "@/types/plans";
import type { Experiment } from "@/types/experiments";
import { shortenUuid } from "@/utils/strings";
import { getPlanLastRun, getPlanNextRun } from "@/utils/plans";

import TimeAgo from "@/components/_ui/TimeAgo.vue";
import GithubLogo from "@/components/svg/GithubLogo.vue";
import ReliablyLogo from "@/components/svg/ReliablyRLogo.vue";
import DockerLogo from "@/components/svg/DockerLogo.vue";
import KubernetesLogo from "@/components/svg/KubernetesLogo.vue";
import ModalWindow from "@/components/_ui/ModalWindow.vue";
import ConfirmDeletePlan from "@/components/plans/ConfirmDeletePlan.vue";
import PlanMiniStatus from "@/components/plans/PlanMiniStatus.vue";

import { experiment, fetchExperiment } from "@/stores/experiments";
import { getEnvironmentName, getDeploymentName } from "@/stores/plans";

import DeleteButton from "@/components/_ui/DeleteButton.vue";

const props = defineProps<{
  plan: Plan;
  page: number;
  store?: { name: string; id: string };
  // Which store should be refreshed after plan has been deleted
}>();
const { plan, page, store } = toRefs(props);

const computedStatus = computed<{ status: string; error: null | string }>(
  () => {
    return {
      status: plan.value.status,
      error: plan.value.error ? plan.value.error : null,
    };
  }
);

const lastRun = ref<[string, string]>(["-", ""]);
const nextRun = ref<[string, string]>(["-", ""]);
const browserZone = ref<string>("");
function getLastNext() {
  const l = getPlanLastRun(plan.value!);
  if (l !== null) {
    const arr = l.split(" ");
    if (arr[0] && arr[0] !== "") {
      lastRun.value[0] = arr[0];
    }
    if (arr[1] && arr[1] !== "") {
      lastRun.value[1] = arr[1];
    }
  }
  const n = getPlanNextRun(plan.value?.definition.schedule, l);
  if (n !== null) {
    const arr = n.split(" ");
    if (arr[0] && arr[0] !== "") {
      nextRun.value[0] = arr[0];
    }
    if (arr[1] && arr[1] !== "") {
      nextRun.value[1] = arr[1];
    }
  }

  dayjs.extend(timezone);
  browserZone.value = dayjs.tz.guess();
}

const experiments = computed<string[]>(() => {
  return plan.value.definition.experiments;
});
const exp = ref<Experiment | null>(null);

const displayedExperimentName = ref<string>("");
const getExperiment = async () => {
  await fetchExperiment(experiments.value[0]);
  exp.value = experiment.get();
  displayedExperimentName.value =
    exp.value === null
      ? shortenUuid(experiments.value[0])
      : exp.value.definition.title;
};

const env = ref<{ provider: string; name: string } | null>(null);
async function getEnvName() {
  if (
    plan.value.definition.environment &&
    plan.value.definition.environment.id
  ) {
    const e = await getEnvironmentName(
      (plan.value.definition.environment as PlanReliablyEnvironment).id!,
      (plan.value.definition.environment as PlanReliablyEnvironment).provider
    );
    if (e) {
      env.value = e;
    }
  }
}

const dep = ref<string>("");
async function getDepName() {
  if (plan.value.definition.deployment.deployment_id) {
    const d = await getDeploymentName(
      plan.value.definition.deployment.deployment_id
    );
    if (d) {
      dep.value = d;
    } else {
      dep.value = plan.value.definition.deployment.deployment_id;
    }
  }
}

const isDeleteDisplayed = ref<boolean>(false);

const displayDelete = () => {
  isDeleteDisplayed.value = true;
};
const closeDelete = () => {
  isDeleteDisplayed.value = false;
};

onMounted(async () => {
  await getExperiment();
  getLastNext();
  await getEnvName();
  await getDepName();
});
</script>

<style lang="scss" scoped>
.planPreview {
  > .tableList__cell {
    small {
      display: block;

      color: var(--text-color-dim);
      font-size: 1.4rem;
    }
  }

  &__meta {
    a {
      font-size: 1.8rem;
      font-weight: 700;
      text-decoration: none;

      &:hover {
        color: var(--accentColorSecondary);
      }
    }
  }

  &__env {
    > span {
      display: flex;
      align-items: center;
      gap: 0.6rem;

      svg {
        flex-shrink: 0;
        height: 1.6rem;
      }
    }

    a {
      color: inherit;

      &:hover {
        color: var(--accentColorSecondary);
      }
    }
  }

  &__dep {
    > span {
      display: flex;
      align-items: center;
      gap: 0.6rem;

      svg {
        flex-shrink: 0;
        height: 1.6rem;
      }
    }

    a {
      color: inherit;

      &:hover {
        color: var(--accentColorSecondary);
      }
    }
  }

  &__runs,
  &__last,
  &__next {
    padding-right: var(--space-medium);

    text-align: right;
  }

  &__runs {
    font-variant-numeric: tabular-nums;
  }

  &__last,
  &__next {
    span {
      display: block;
      white-space: nowrap;

      &:last-child {
        color: var(--text-color-dim);
        font-size: 1.4rem;
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
