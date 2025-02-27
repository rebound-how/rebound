<template>
  <LoadingPlaceholder v-if="isLoading" />
  <article class="planView" v-else-if="p !== undefined && p.id">
    <header class="pageHeader">
      <div>
        <h1 class="pageHeader__title" v-if="p.definition.title">
          {{ p.definition.title }}
          <div>
            <small>{{ p.id }}</small>
          </div>
        </h1>
        <h1 class="pageHeader__title" v-else>
          {{ p.id }}
        </h1>
      </div>
      <div class="pageHeader__actions">
        <MultiButton
          v-if="p !== undefined"
          title="Manage plan"
          :options="manageActions"
          @emit-action="handleMultiButtonAction"
        />
        <button
          v-if="p.definition.schedule.type === 'cron' && isSchedulePaused"
          class="button button--creative planDetails__control"
          @click.prevent="resumeSchedule"
        >
          Resume schedule
        </button>
        <button
          v-else-if="p.definition.schedule.type === 'cron'"
          class="button button--creative planDetails__control"
          @click.prevent="pauseSchedule"
        >
          Pause schedule
        </button>
      </div>
    </header>
    <section class="planInfo">
      <PlanStatus :status="computedStatus" />
      Created
      <TimeAgo :timestamp="p.created_date!" :key="timestampRefresher" /><span
        v-if="lastRunTimestamp !== null"
        >, last run
        <TimeAgo :timestamp="lastRunTimestamp" :key="timestampRefresher"
      /></span>
    </section>
    <section class="planDetails">
      <h2>Details</h2>
      <dl class="planDetails__list">
        <div
          class="planDetails__item planDetails__item--schedule"
          :class="{ 'planDetails__item--schedule--paused': isSchedulePaused }"
        >
          <dt>
            Schedule
            <span v-if="isSchedulePaused"> (Paused) </span>
          </dt>
          <dd v-if="p.definition.schedule.type === 'cron'">
            {{ p.definition.schedule.pattern }}
            <span
              v-if="
                p.definition.schedule.timezone &&
                p.definition.schedule.timezone !== ''
              "
              class="hasTooltip hasTooltip--bottom-center"
              :aria-label="`${cronstrue.toString(p.definition.schedule.pattern!)}. Created in timezone ${p.definition.schedule.timezone}`"
              :label="`${cronstrue.toString(p.definition.schedule.pattern!)}. Created in timezone ${p.definition.schedule.timezone}`"
            >
              <HelpCircle />
            </span>
            <span
              v-else
              class="hasTooltip hasTooltip--bottom-center"
              :aria-label="cronstrue.toString(p.definition.schedule.pattern!)"
              :label="cronstrue.toString(p.definition.schedule.pattern!)"
            >
              <HelpCircle />
            </span>
          </dd>
          <dd v-else>{{ p.definition.schedule.type }}</dd>
        </div>
        <div class="planDetails__item planDetails__item">
          <dt>Next run</dt>
          <dd
            v-if="p.definition.schedule.type === 'cron' && browserZone !== ''"
            :title="`Displayed for timezone: ${browserZone}`"
          >
            {{ nextRun }}
          </dd>
          <dd v-else-if="p.definition.schedule.type === 'cron'">
            {{ nextRun }}
          </dd>
          <dd v-else>-</dd>
        </div>
        <div class="planDetails__item">
          <dt>Via agent</dt>
          <dd>{{ p.definition.schedule.via_agent ? "Yes" : "No" }}</dd>
        </div>
        <div class="planDetails__item planDetails__item--env">
          <dt>Environment</dt>
          <dd v-if="hasEnvironment">
            <div
              v-if="
              p.definition.environment!.id
            "
            >
              <ReliablyLogo title="Reliably Environment" />
              <a
                v-if="env"
                :href="`/environments/view/?id=${p.definition.environment!.id}`"
                >{{ env.name }}</a
              >
              <a
                v-else
                :href="`/environments/view/?id=${p.definition.environment!.id}`"
                >{{ shortenUuid(p.definition.environment!.id) }}</a
              >
            </div>
            <div
              v-if="
              p.definition.environment!.provider === 'github'
            "
            >
              <GithubLogo title="GitHub Environment" />
              {{ p.definition.environment!.name }}
            </div>
          </dd>
          <dd v-else>-</dd>
        </div>
        <div class="planDetails__item">
          <dt>Deployment</dt>
          <dd>
            <a
              :href="`/deployments/view/?id=${p.definition.deployment.deployment_id}`"
            >
              {{ deploymentName }}
            </a>
          </dd>
        </div>
      </dl>
      <div class="planDetails__cli">
        <div class="planDetails__cliLink">
          <label for="cliCommand"> Run with the Reliably CLI</label>
          <pre
            id="cliCommand"
            @click.prevent="copyCliCommand"
          ><code><span>reliably</span> service plan execute <span v-if="
              p.definition.environment && p.definition.environment.id
            ">--load-environment </span><span>{{ id }}</span></code></pre>
          <button
            class="button button--primary"
            @click.prevent="copyCliCommand"
          >
            Copy to clipboard
          </button>
        </div>
      </div>
    </section>
    <section v-if="hasIntegrations" class="planIntegrations">
      <h2>Integrations</h2>
      <ul class="environmentsList tableList">
        <li class="tableList__row tableList__row--header">
          <div class="tableList__cell"></div>
          <div class="tableList__cell">Name</div>
          <div class="tableList__cell">Provider</div>
        </li>
        <IntegrationPreview
          v-for="i in planIntegrations"
          :integration="i"
          :index="i.id"
          :hideActions="true"
        />
      </ul>
    </section>
    <section class="planExperiments">
      <h2>Experiments</h2>
      <ul class="tableList">
        <li
          v-for="(e, index) in planExperiments"
          :key="index"
          class="tableList__row"
        >
          <div class="tableList__cell">
            <a :href="`/experiments/view/?id=${e.id}`">{{
              e.title ? e.title : shortenUuid(e.id)
            }}</a>
          </div>
        </li>
      </ul>
    </section>
    <section class="planExecutions">
      <h2>Executions</h2>
      <ul class="tableList" v-if="p.executions_count">
        <ExecutionPreview
          v-for="(ex, index) in planExecs.executions"
          :key="index"
          :execution="(ex as Execution)"
          :page="executionsPage"
          :refresher="timestampRefresher"
        />
      </ul>
      <p v-else>This plan has no executions yet.</p>
    </section>
    <ModalWindow
      v-if="isDeleteDisplayed"
      :hasCloseButton="true"
      :hasPadding="true"
      @close="closeDelete"
    >
      <template #title>Delete Experiment</template>
      <template #content>
        <ConfirmDeletePlan :id="p.id!" @close="closeDelete" />
      </template>
    </ModalWindow>
  </article>
  <NoData v-else message="We couldn't find a plan with this ID." />
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import dayjs from "dayjs";
import timezone from "dayjs/plugin/timezone";
import customParseFormat from "dayjs/plugin/customParseFormat";
import { useClipboard } from "@vueuse/core";
import cronstrue from "cronstrue";
import { useStore } from "@nanostores/vue";

import { shortenUuid } from "@/utils/strings";
import { getPlanLastRun, getPlanNextRun } from "@/utils/plans";

import type { Deployment } from "@/types/deployments";
import type {
  Plan,
  PlanGitHubEnvironment,
  PlanReliablyEnvironment,
} from "@/types/plans";
import type { Integration } from "@/types/integrations";
import type { Execution } from "@/types/executions";
import type { Notification, MultiButtonOption } from "@/types/ui-types";
import type { PagerData } from "@/types/pager";

import {
  plan,
  planExecutions,
  fetchPlan,
  fetchPlanExecutions,
  pausePlan,
  resumePlan,
  rerunPlan,
  getEnvironmentName,
} from "@/stores/plans";
import { experiment, fetchExperiment } from "@/stores/experiments";
import { integration, fetchIntegration } from "@/stores/integrations";
import { deployment, fetchDeployment } from "@/stores/deployments";
import { addNotification } from "@/stores/notifications";

import LoadingPlaceholder from "@/components/_ui/LoadingPlaceholder.vue";
import NoData from "@/components/_ui/NoData.vue";
import MultiButton from "@/components/_ui/MultiButton.vue";
import TimeAgo from "@/components/_ui/TimeAgo.vue";
import ModalWindow from "@/components/_ui/ModalWindow.vue";
import ConfirmDeletePlan from "@/components/plans/ConfirmDeletePlan.vue";
import PlanStatus from "@/components/plans/PlanStatus.vue";
import IntegrationPreview from "@/components/integrations/IntegrationPreview.vue";
import ExecutionPreview from "@/components/executions/ExecutionPreview.vue";

import GithubLogo from "@/components/svg/GithubLogo.vue";
import ReliablyLogo from "@/components/svg/ReliablyRLogo.vue";
import HelpCircle from "@/components/svg/HelpCircle.vue";

const isLoading = ref(true);
const id = ref<string | undefined>(undefined);
const executionsPage = ref<number>(1);
const p = ref<Plan | undefined>(undefined);
const hasEnvironment = computed<boolean>(() => {
  if (p.value === undefined || p.value.definition === null) {
    return false;
  } else if (p.value.definition.environment === null) {
    return false;
  } else if (p.value.definition.environment.id) {
    return true;
  } else if ((p.value.definition.environment as PlanGitHubEnvironment).name) {
    return true;
  } else {
    return false;
  }
});

const getCurrentId = () => {
  let location = window.location;
  let params = new URLSearchParams(location.search);
  if (params.has("id")) {
    id.value = params.get("id")!;
  }
  if (params.has("rerun")) {
    if (params.get("rerun") === "true") {
      shouldRerun.value = true;
      // We will rerun the plan as soon as it's fetched.
    }
  }
};

const getPlanExecutionsPage = () => {
  let location = window.location;
  let params = new URLSearchParams(location.search);
  if (params.has("executions")) {
    executionsPage.value = parseInt(params.get("executions")!);
  }
};

const getPlan = async () => {
  await fetchPlan(id.value!);
  p.value = plan.get() as Plan;
};

const pagerData = ref<PagerData>({
  currentPage: 1,
  lastPage: 1,
  urlBase: "",
});

const getPagerData = () => {
  let pager: PagerData = {
    currentPage: executionsPage.value!,
    lastPage: Math.ceil(planExecs.value.total / 10),
    urlBase: `/plans/view?id=${p.value?.id}&page=`,
  };
  pagerData.value = pager;
};

const setTitleTag = () => {
  let title = "Plan · Reliably";
  if (p.value !== undefined) {
    title = `Plan ${p.value.id} · Reliably`;
  }
  document.title = title;
};

const computedStatus = computed<{ status: string; error: null | string }>(
  () => {
    return {
      status:
        forcedStatus.value !== null ? forcedStatus.value : p.value!.status,
      error: p.value!.error ? p.value!.error : null,
    };
  }
);

const forcedStatus = ref<string | null>(null);
function resetForcedStatus() {
  forcedStatus.value = null;
}

const sanitizeSchedule = (s: Plan["definition"]["schedule"]): string => {
  if (s.type !== "now" && s.type !== "cron") {
    return "";
  } else {
    let schedule: string =
      s.type === "now" ? "now" : s.pattern!.replaceAll(" ", "_");
    if (s.via_agent) {
      return `&s=${schedule}&a=true`;
    } else {
      return `&s=${schedule}&va=false`;
    }
  }
};

async function pauseSchedule() {
  await pausePlan(p.value!.id);
  forcedStatus.value = "suspending";
}

async function resumeSchedule() {
  await resumePlan(p.value!.id);
  forcedStatus.value = "resuming";
}

const isSchedulePaused = computed<boolean>(() => {
  return (
    p.value !== undefined &&
    p.value.definition.schedule.type === "cron" &&
    (p.value.status === "suspended" || p.value.status === "suspending")
  );
});

const lastRun = ref<string>("-");
const lastRunTimestamp = ref<string | null>(null);
const nextRun = ref<string>("-");
const browserZone = ref<string>("");
function getLastNext() {
  const l = getPlanLastRun(p.value!);
  if (l !== null) {
    lastRun.value = l;
    dayjs.extend(customParseFormat);
    lastRunTimestamp.value = dayjs(l, "DD-MM-YYYY H:mm:ss").toISOString();
  }
  const n = getPlanNextRun(p.value?.definition.schedule, l);
  if (n !== null) {
    nextRun.value = n;
  }

  dayjs.extend(timezone);
  browserZone.value = dayjs.tz.guess();
}

const deploymentName = ref<string | null>(null);
const getDeployment = async () => {
  await fetchDeployment(p.value?.definition.deployment.deployment_id!);
  let deploy = deployment.get() as Deployment;
  if (deploy) {
    deploymentName.value = deploy.name;
  } else {
    deploymentName.value = p.value?.definition.deployment.deployment_id!;
  }
};

const env = ref<{ provider: string; name: string } | null>(null);
async function getEnvName() {
  if (p.value!.definition.environment && p.value!.definition.environment.id) {
    const e = await getEnvironmentName(
      (p.value!.definition.environment as PlanReliablyEnvironment).id!,
      (p.value!.definition.environment as PlanReliablyEnvironment).provider
    );
    if (e) {
      env.value = e;
    }
  }
}

const cliCommand = computed<string>(() => {
  if (p.value!.definition.environment && p.value!.definition.environment.id) {
    return `reliably service plan execute --load-environment ${id.value}`;
  } else {
    return `reliably service plan execute ${id.value}`;
  }
});
const { text, copy, copied, isSupported } = useClipboard();
const copyCliCommand = () => {
  copy(cliCommand.value);
  const n: Notification = {
    title: "Command copied to clipboard",
    message:
      "The Reliably CLI command has been copied to your clipboard. Use it to run your plan with the CLI.",
    type: "success",
  };
  addNotification(n);
};

const planExperiments = ref<{ title: string; id: string }[]>([]);
const planExpsIds = ref<string>("");
const buildExperimentsList = async () => {
  for (const e of p.value?.definition.experiments!) {
    await fetchExperiment(e);
    let exp = experiment.get();
    planExperiments.value.push({
      title: exp?.definition.title!,
      id: e,
    });
    if (planExpsIds.value === "") {
      planExpsIds.value = e;
    } else {
      planExpsIds.value = planExpsIds.value.concat(",", e);
    }
  }
};

const hasIntegrations = computed<boolean>(() => {
  const i = p.value?.definition.integrations;
  return i !== undefined && i.length > 0;
});
const planIntegrations = ref<Integration[]>([]);
const planIntsIds = ref<string>("");
async function buildIntegrationsList() {
  if (hasIntegrations.value) {
    p.value?.definition.integrations!.forEach(async (i) => {
      await fetchIntegration(i);
      let int = integration.get();
      if (int !== null) {
        planIntegrations.value.push(int);
        if (planIntsIds.value === "") {
          planIntsIds.value = int.id!;
        } else {
          planIntsIds.value = planIntsIds.value.concat(",", int.id!);
        }
      }
    });
  }
}

const planExecs = useStore(planExecutions);

async function handleMultiButtonAction(action: string) {
  if (action === "delete") {
    displayDelete();
  } else if (action === "rerun") {
    rerun();
  }
}

const shouldRerun = ref<boolean>(false);
async function rerun() {
  await rerunPlan(p.value!.id);
  forcedStatus.value = "rerunning";
  refreshInterval = setInterval(refreshPlan, 10000);
}

// const duplicateEnvironment = computed<string>(() => {
//   if (p.value === undefined || !p.value.definition.environment) {
//     return "null";
//   } else if (p.value.definition.environment.provider === "github") {
//     return `github-${p.value.definition.environment.name}`;
//   } else if (p.value.definition.environment.provider === "reliably_cloud") {
//     return p.value.definition.environment.id!;
//   } else {
//     return "null";
//   }
// });

const duplicateGHEnv = computed<string>(() => {
  if (p.value === undefined || !p.value.definition.environment) {
    return "null";
  } else if (p.value.definition.environment.provider === "github") {
    return p.value.definition.environment.name!;
  } else {
    return "null";
  }
});

const duplicateReliablyEnv = computed<string>(() => {
  if (p.value === undefined || !p.value.definition.environment) {
    return "null";
  } else if (p.value.definition.environment.id) {
    return p.value.definition.environment.id;
  } else {
    return "null";
  }
});

function updateManageActions() {
  if (p.value) {
    manageActions.value[0].link = `/plans/new/?exp=${
      planExpsIds.value
    }${sanitizeSchedule(p.value.definition.schedule)}&d=${
      p.value.definition.deployment.deployment_id
    }&envid=${duplicateReliablyEnv.value}&envgh=${duplicateGHEnv.value}&int=${
      planIntsIds.value
    }`;

    if (p.value.definition.schedule.type === "now") {
      manageActions.value.unshift({
        label: "Re-run",
        action: "rerun",
        icon: "refresh",
      });
    }
  }
}

const manageActions = ref<MultiButtonOption[]>([
  {
    label: "Duplicate",
    link: "#",
    icon: "copy",
  },
  {
    label: "Delete",
    action: "delete",
    icon: "trash",
    warning: true,
  },
]);

const isDeleteDisplayed = ref<boolean>(false);

const displayDelete = () => {
  isDeleteDisplayed.value = true;
};
const closeDelete = () => {
  isDeleteDisplayed.value = false;
};

const expectingExecution = ref<boolean>(false);
const timestampRefresher = ref<number>(0);

let refreshInterval: ReturnType<typeof setInterval>;
async function refreshPlan(): Promise<void> {
  timestampRefresher.value = dayjs().valueOf();
  if (p.value!.status === "created" || p.value!.status === "running") {
    // When re-running a plan, it's status might still be "Completed" on the
    // first refresh. If it's the case, we force it to still display
    // "Re-running..."
    resetForcedStatus();
  }
  await getPlan();
  getLastNext();
  if (p.value?.executions_count) {
    await fetchPlanExecutions(p.value!.id, executionsPage.value);
  }
  if (computedStatus.value.status === "running") {
    expectingExecution.value = false;
    resetForcedStatus();
  }
  if (
    computedStatus.value.status === "creation error" ||
    computedStatus.value.status === "deletion error" ||
    computedStatus.value.status === "error"
  ) {
    clearInterval(refreshInterval);
  } else if (p.value!.definition.schedule.type === "now") {
    if (computedStatus.value.status === "completed") {
      clearInterval(refreshInterval);
    }
  } else if (p.value!.definition.schedule.type === "cron") {
    if (
      computedStatus.value.status === "completed" ||
      computedStatus.value.status === "scheduled" ||
      computedStatus.value.status === "created"
    ) {
      const n = getPlanNextRun(p.value?.definition.schedule, null, "date");
      const now = dayjs();
      const when = -1 * now.diff(n, "minute");
      if (when > 1) {
        if (expectingExecution.value === false) {
          forcedStatus.value = "scheduled";
          // Next run is in more than on minute.
          // No need to refresh every 10 seconds.
          clearInterval(refreshInterval);
          // We'll one minute before next planned run.
          refreshInterval = setInterval(refreshPlan, 60000 + (when - 1));
        }
      } else {
        // More often than not, the cron "resets" (meaning when > 1) before the
        // execution actualy starts and the plan status is changed. In this
        // case, we stil want to continue fetching every 10 seconds.
        expectingExecution.value = true;
        clearInterval(refreshInterval);
        refreshInterval = setInterval(refreshPlan, 10000);
      }
    }
  }
}

onMounted(async () => {
  isLoading.value = true;
  getCurrentId();
  getPlanExecutionsPage();
  await getPlan();
  setTitleTag();
  getLastNext();
  await getDeployment();
  await getEnvName();
  await buildIntegrationsList();
  await buildExperimentsList();
  if (p.value?.executions_count) {
    await fetchPlanExecutions(p.value!.id, executionsPage.value);
  }
  updateManageActions();
  getPagerData();

  if (shouldRerun.value) {
    await rerun();
  }

  isLoading.value = false;

  refreshInterval = setInterval(refreshPlan, 10000);
});
</script>

<style lang="scss" scoped>
.planView {
  .pageHeader__title {
    display: block;

    small {
      margin-left: 0;
    }
  }
  > section + section {
    margin-top: var(--space-medium);
  }

  .planDetails {
    &__list {
      display: flex;
      // flex-direction: column;
      gap: var(--space-medium);
      padding: var(--space-small);

      background-color: var(--section-background);
      border-radius: var(--border-radius-s);

      > div + div {
        padding-left: var(--space-small);

        border-left: 1px solid var(--section-separator-color);
      }
    }

    &__item {
      flex: 1 0 auto;

      dt {
        color: var(--text-color-dim);
        font-size: 1.4rem;
        text-transform: uppercase;
      }

      a {
        color: var(--text-color);

        &:hover {
          color: var(--link-color);
        }
      }

      &--schedule {
        font-family: var(--monospace-font);

        dd {
          font-size: 1.4rem;

          span {
            font-family: var(--body-font);

            svg {
              height: 1.4rem;
            }
          }
        }

        &--paused {
          color: var(--statusColor-ko);
        }
      }

      &--env {
        dd {
          svg {
            height: 2rem;
            margin-right: 0.4rem;
            vertical-align: -0.3rem;
          }
        }
      }
    }

    &__control {
      margin-left: var(--space-small);
    }

    &__cli {
      margin-bottom: var(--space-small);

      background-color: var(--section-background);
      border-radius: var(--border-radius-s);
    }

    &__cliLink {
      display: flex;
      align-items: center;
      gap: var(--space-small);
      padding: var(--space-small);

      label {
        flex: 1 0 auto;

        font-weight: 500;
      }

      pre {
        position: relative;

        display: block;
        width: 100%;
        margin: 0;
        padding: 0.5em 0.5rem 0.5rem 2rem;

        background-color: white;
        border: 0.1rem solid var(--form-input-border);
        border-radius: var(--border-radius-m);

        color: var(--text-color);
        font-size: 1.6rem;

        &:focus {
          outline: 2px solid var(--form-input-focus);
        }

        &[readonly] {
          &:focus {
            outline: none;
          }
        }

        &::before {
          content: "$";

          display: block;

          position: absolute;
          top: 0.8rem;
          left: 0.5rem;
        }

        code {
          > span {
            &:first-child {
              color: var(--green-500);
              font-weight: 700;
            }

            &:last-child {
              color: var(--pink-500);
            }
          }
        }
      }
    }
  }
}
</style>
