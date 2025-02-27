<template>
  <LoadingPlaceholder size="large" v-if="isLoading" />
  <article class="executionView" v-else-if="exec !== undefined && exec.id">
    <header class="pageHeader">
      <div>
        <h1 class="pageHeader__title">
          <ExecutionStatus
            :status="status"
            :timestamp="exec.created_date.toString()"
          />
          &nbsp;{{ exec.id }}
        </h1>
      </div>
      <div
        v-if="
          status.label === 'running' ||
          status.label === 'pause' ||
          status.label === 'pausing...' ||
          status.label === 'paused'
        "
        class="pageHeader__actions"
      >
        <button
          class="button button--destructiveLight"
          @click.prevent="displayStopExecution"
        >
          Stop execution
        </button>
        <a
          v-if="status.label === 'running'"
          class="button button--creative"
          @click.prevent="pauseExec"
        >
          Pause execution</a
        >
        <a
          v-if="
            status.label === 'pause' ||
            status.label === 'pausing...' ||
            status.label === 'paused'
          "
          class="button button--creative"
          @click.prevent="resumeExec"
        >
          Resume execution</a
        >
      </div>
      <div v-else class="pageHeader__actions">
        <button
          class="button button--destructiveLight"
          @click.prevent="displayDelete"
        >
          Delete execution
        </button>
        <MultiButton
          v-if="executionPlan"
          title="Re-run experiment"
          :options="rerunOptions"
        />
        <a
          v-else
          :href="`/plans/new/?exp=${exec.experiment_id}`"
          class="button button--creative"
        >
          Re-run experiment</a
        >
      </div>
    </header>
    <section class="executionInfo">
      <span class="executionInfo__creation">
        Created <TimeAgo :timestamp="exec.created_date" />, running experiment
        <a
          :href="`/experiments/view/?id=${exec.experiment_id}`"
          :title="exec.experiment_id"
        >
          {{ exec.result.experiment.title }}
        </a>
        <span v-if="exec.plan_id"
          >&nbsp;with plan
          <a :href="`/plans/view/?id=${exec.plan_id}`">{{
            exec.plan_id
          }}</a></span
        >
      </span>
    </section>
    <ExecutionTriggeredProbes
      v-if="triggeredProbes !== null"
      :probes="triggeredProbes"
    />
    <section class="executionSection executionSection--result">
      <header class="executionSection__header">
        <h2>Result</h2>
        <a
          v-for="(e, index) in githubLinks"
          :key="index"
          :href="e.value"
          class="button button--github"
          target="_blank"
          rel="noopener noreferer"
        >
          <GithubLogo />
          <span v-if="e.topic === 'commit'">View commit</span>
          <span v-else-if="e.topic === 'repo'">View repository</span>
          <span v-else-if="e.topic === 'run'">View Action run</span>
        </a>
        <a
          :href="`${baseApiUrl}/organization/${orgId}/experiments/${exec.experiment_id}/executions/${exec.id}/results`"
          class="button button--icon hasTooltip hasTooltip--bottom-center"
          aria-label="Journal"
          label="Journal"
          target="_blank"
          rel="noopener noreferer"
        >
          <BookOpen />
        </a>
        <a
          :href="`${baseApiUrl}/organization/${orgId}/experiments/${exec.experiment_id}/executions/${exec.id}/log`"
          class="button button--icon hasTooltip hasTooltip--bottom-center"
          aria-label="Logs"
          label="Logs"
          target="_blank"
          rel="noopener noreferer"
        >
          <FileText />
        </a>
        <button
          @click.prevent="openPrint"
          class="button button--icon hasTooltip hasTooltip--bottom-center"
          aria-label="Print this page"
          label="Print this page"
        >
          <PrinterIcon />
        </button>
      </header>
      <dl>
        <div>
          <dt>Status</dt>
          <dd>{{ exec.result.status }}</dd>
        </div>
        <div>
          <dt>Deviated</dt>
          <dd>{{ exec.result.deviated ? "Yes" : "No" }}</dd>
        </div>
        <div>
          <dt>Start</dt>
          <dd
            v-if="browserZone !== ''"
            :title="`Displayed for timezone ${browserZone}`"
          >
            {{ humanReadableTime(`${exec.result.start}+00:00`, "short") }}
          </dd>
          <dd v-else>
            {{ humanReadableTime(`${exec.result.start}+00:00`, "short") }}
          </dd>
        </div>
        <div>
          <dt>End</dt>
          <dd>{{ executionEndDate }}</dd>
        </div>
        <div>
          <dt>Duration</dt>
          <dd
            v-if="browserZone !== ''"
            :title="`Displayed for timezone ${browserZone}`"
          >
            {{ executionDuration }}
          </dd>
          <dd v-else>{{ executionDuration }}</dd>
        </div>
      </dl>
    </section>
    <section class="executionSection executionSection--platform">
      <h2>Platform</h2>
      <dl>
        <div>
          <dt>ChaosLib</dt>
          <dd>{{ exec.result["chaoslib-version"] }}</dd>
        </div>
        <div>
          <dt>Platform</dt>
          <dd :title="exec.result.platform">{{ platform }}</dd>
        </div>
        <div>
          <dt>Node</dt>
          <dd>{{ exec.result.node }}</dd>
        </div>
      </dl>
    </section>
    <section v-if="dependencies.length" class="executionSection">
      <h2>Runtime dependencies</h2>
      <ExecutionDependencies :dependencies="dependencies" />
    </section>
    <section v-if="executionEnv" class="executionSection executionSection--env">
      <h2>Environment</h2>
      <ExecutionEnvironment :env="(executionEnv as Environment)" />
    </section>
    <section
      v-if="executionConf"
      class="executionSection executionSection--env"
    >
      <h2>Configuration</h2>
      <ExecutionEnvironment :conf="executionConf" />
    </section>
    <section
      v-if="displayAssistant && gptContent !== undefined"
      class="executionSection executionSection--gpt"
    >
      <h2>Assistant</h2>
      <ChatGptChat :content="gptContent" />
    </section>
    <section class="executionSection executionSection--timeline">
      <h2>Timeline</h2>
      <ExecutionTimeline
        :execution="exec"
        :probes="triggeredProbes"
        :conf="executionConf"
        @resume-execution="resumeExec"
      />
    </section>
    <ModalWindow
      v-if="isDeleteDisplayed"
      :hasCloseButton="true"
      :hasPadding="true"
      @close="closeDelete"
    >
      <template #title>Delete Execution</template>
      <template #content>
        <ConfirmDeleteExecution
          :id="exec.id"
          :exp="exec.id"
          @close="closeDelete"
        />
      </template>
    </ModalWindow>
    <ModalWindow
      v-if="isStopDisplayed"
      :hasCloseButton="true"
      :hasPadding="true"
      @close="closeStop"
    >
      <template #title>Stop Execution</template>
      <template #content>
        <ConfirmStopExecution
          :id="exec.id"
          :exp="exec.experiment_id!"
          @close="closeAndStop"
        />
      </template>
    </ModalWindow>
  </article>
  <NoData v-else message="We couldn't find an experiment with this ID." />
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import dayjs from "dayjs";
import timezone from "dayjs/plugin/timezone";

import type { Execution, ExecutionDependency } from "@/types/executions";
import type { ReliablySafeguard } from "@/types/experiments";
import type { ChatGptExtension, ExecutionUiStatus } from "@/types/ui-types";

import { useStore } from "@nanostores/vue";
import {
  execution,
  pauseExecution,
  resumeExecution,
  fetchExecution,
} from "@/stores/executions";
import { plan, fetchPlan } from "@/stores/plans";
import { environment, fetchEnvironment } from "@/stores/environments";

import { getExecutionStatusObject } from "@/utils/executions";

import LoadingPlaceholder from "@/components/_ui/LoadingPlaceholder.vue";
import ChatGptChat from "@/components/_ui/ChatGptChat.vue";
import ModalWindow from "@/components/_ui/ModalWindow.vue";
import NoData from "@/components/_ui/NoData.vue";
import TimeAgo from "@/components/_ui/TimeAgo.vue";
import MultiButton from "@/components/_ui/MultiButton.vue";
import ExperimentStatus from "@/components/experiments/ExperimentStatus.vue";
import ExecutionStatus from "@/components/executions/ExecutionStatus.vue";
import ConfirmDeleteExecution from "@/components/executions/ConfirmDeleteExecution.vue";
import ConfirmStopExecution from "@/components/executions/ConfirmStopExecution.vue";
import ExecutionDependencies from "@/components/executions/ExecutionDependencies.vue";
import ExecutionEnvironment from "@/components/executions/ExecutionEnvironment.vue";
import ExecutionTimeline from "@/components/executions/ExecutionTimeline.vue";
import ExecutionTriggeredProbes from "@/components/executions/ExecutionTriggeredProbes.vue";
import FileText from "@/components/svg/FileText.vue";
import BookOpen from "@/components/svg/BookOpen.vue";
import PrinterIcon from "@/components/svg/PrinterIcon.vue";
import GithubLogo from "@/components/svg/GithubLogo.vue";

import {
  shortenUuid,
  humanReadableTime,
  humanReadableDuration,
} from "@/utils/strings";
import { hasProp } from "@/utils/objects";
import type { Environment } from "@/types/environments";
import type { MultiButtonOption } from "@/types/ui-types";

const baseApiUrl: string = import.meta.env.PUBLIC_API_URL;

const isLoading = ref(true);
const id = ref<string | undefined>(undefined);
const expId = ref<string | undefined>(undefined);
const exec = ref<Execution | undefined>(undefined);
const orgId = ref<string | undefined>(undefined);

const getCurrentParams = () => {
  let location = window.location;
  let params = new URLSearchParams(location.search);
  if (params.has("id")) {
    id.value = params.get("id")!;
  }
  if (params.has("exp")) {
    expId.value = params.get("exp")!;
  }
};

const getExecution = async () => {
  await fetchExecution(id.value!, expId.value!);
  exec.value = useStore(execution).value as Execution;
  orgId.value = exec.value.org_id;
};

const setTitleTag = () => {
  let title = "Experiment · Reliably";
  if (exec.value !== undefined) {
    title = `${shortenUuid(exec.value.id)} Execution · Reliably`;
  }
  document.title = title;
};

const status = ref<ExecutionUiStatus>({ label: "Unknown", type: "unknown" });
function setStatus(s: ExecutionUiStatus): void {
  status.value = s;
}
function getStatus(): void {
  const s = getExecutionStatusObject(exec.value!);
  setStatus(s);
}

const browserZone = ref<string>("");
function getBrowserZone() {
  dayjs.extend(timezone);
  browserZone.value = dayjs.tz.guess();
}

const triggeredProbes = ref<{
  type: string;
  probes: ReliablySafeguard[];
} | null>(null);
function checkTriggeredProbes() {
  if (exec.value?.result.experiment === undefined) {
    return;
  } else {
    if (hasProp(exec.value?.result.experiment, "extensions")) {
      const extensions = exec.value?.result.experiment.extensions;
      if (extensions === undefined) {
        return;
      } else {
        const reliablyExt = extensions.find((ext) => ext.name === "reliably");
        if (reliablyExt !== undefined) {
          if (hasProp(reliablyExt, "integrations")) {
            const integrations = reliablyExt.integrations;
            if (hasProp(integrations, "prechecks")) {
              if (hasProp(integrations.prechecks, "triggered_probes")) {
                triggeredProbes.value = {
                  type: "prechecks",
                  probes: integrations.prechecks.triggered_probes,
                };
              }
            } else if (hasProp(integrations, "safeguards")) {
              if (hasProp(integrations.safeguards, "triggered_probes")) {
                triggeredProbes.value = {
                  type: "safeguards",
                  probes: integrations.safeguards.triggered_probes,
                };
              }
            }
          }
        }
      }
    }
  }
}

const githubLinks = ref<
  {
    type: string;
    topic: string;
    value: string;
    provider: string;
  }[]
>([]);
function handleExtras() {
  if (exec.value?.result.experiment.extensions) {
    let reliably = exec.value?.result.experiment.extensions.find(
      (extension) => {
        return extension.name === "reliably";
      }
    );
    if (reliably !== undefined) {
      if (hasProp(reliably, "extra") && reliably.extra !== undefined) {
        githubLinks.value = []; // Reset to prevent duplication
        reliably.extra.forEach((e: any) => {
          if (e.type === "url") {
            if (e.provider === "github") {
              githubLinks.value.push(e);
            }
          }
        });
      }
    }
  }
}

const executionEndDate = computed<string>(() => {
  if (exec.value) {
    if (exec.value.result.end) {
      return humanReadableTime(exec.value.result.end, "short");
    } else {
      return "-";
    }
  } else {
    return "-";
  }
});

const executionDuration = computed<string>(() => {
  if (exec.value && exec.value.result.duration) {
    return humanReadableDuration(exec.value.result.duration);
  } else {
    return "-";
  }
});

const platform = computed<string>(() => {
  let arr: string[] = exec.value?.result.platform.split("-");
  return arr[0];
});

const dependencies = ref<ExecutionDependency[]>([]);
function getDependencies() {
  if (exec.value?.result.experiment === undefined) {
    return;
  } else {
    if (hasProp(exec.value?.result.experiment, "extensions")) {
      const extensions = exec.value?.result.experiment.extensions;
      if (extensions === undefined) {
        return;
      } else {
        const reliablyExt = extensions.find((ext) => ext.name === "reliably");
        if (reliablyExt !== undefined) {
          if (hasProp(reliablyExt, "chaostoolkit_extensions")) {
            dependencies.value.push(...reliablyExt["chaostoolkit_extensions"]);
          }
        }
      }
    }
  }
}

const executionPlan = useStore(plan);
const executionEnv = useStore(environment);
const executionConf = computed(() => {
  if (exec.value?.result.experiment.configuration) {
    return exec.value.result.experiment.configuration;
  } else {
    return null;
  }
});
async function getPlanEnv() {
  if (exec.value?.plan_id) {
    await fetchPlan(exec.value.plan_id);
    if (executionPlan.value && executionPlan.value.definition.environment) {
      const e = executionPlan.value.definition.environment;
      if (e.provider === "reliably_cloud" && e.id) {
        await fetchEnvironment(e.id);
      }
    }
  }
}

const gptContent = ref<ChatGptExtension | undefined>(undefined);
function getGpt() {
  if (exec.value) {
    const exp = exec.value.result.experiment;
    if (hasProp(exp, "extensions")) {
      gptContent.value = exp.extensions?.find((e) => e.name === "chatgpt") as
        | ChatGptExtension
        | undefined;
    }
  }
}
const displayAssistant = computed<boolean>(() => {
  if (
    gptContent.value !== undefined &&
    gptContent.value?.results !== undefined
  ) {
    return gptContent.value?.results.length > 0;
  } else {
    return false;
  }
});

const rerunOptions = ref<MultiButtonOption[]>([
  {
    label: "Use existing plan",
    link: "#",
    icon: "refresh",
  },
  {
    label: "Create new plan",
    link: "#",
    icon: "copy",
  },
]);

function updateRerunOptionsLinks() {
  if (executionPlan.value) {
    rerunOptions.value[0].link = `/plans/view/?id=${executionPlan.value.id}&rerun=true`;
  } else {
    rerunOptions.value.shift();
  }

  if (exec.value) {
    rerunOptions.value[1].link = `/plans/new/?exp=${exec.value.experiment_id}`;
  } else {
    rerunOptions.value.pop();
  }
}

const isDeleteDisplayed = ref<boolean>(false);

const displayDelete = () => {
  isDeleteDisplayed.value = true;
};
const closeDelete = () => {
  isDeleteDisplayed.value = false;
};

const isStopDisplayed = ref<boolean>(false);
function displayStopExecution(): void {
  isStopDisplayed.value = true;
}
function closeStop(): void {
  isStopDisplayed.value = false;
}
function closeAndStop(isStopping: boolean): void {
  isStopDisplayed.value = false;
  if (isStopping) {
    setStatus({ label: "stopping...", type: "warning" });
  }
}

function pauseExec(): void {
  setStatus({ label: "pausing...", type: "warning" });
  pauseExecution(exec.value!.id, exec.value!.experiment_id!);
}

function resumeExec(): void {
  setStatus({ label: "running", type: "ok" });
  resumeExecution(exec.value!.id, exec.value!.experiment_id!);
}

var refreshInterval: ReturnType<typeof setInterval>;
async function refreshExecution(): Promise<void> {
  if (exec.value!.user_state && exec.value!.user_state.current === "finished") {
    clearInterval(refreshInterval);
  } else {
    await getExecution();
    getStatus();
    handleExtras();
    getGpt();
  }
}

function openPrint() {
  window.print();
}

onMounted(async () => {
  isLoading.value = true;
  getCurrentParams();
  await getExecution();
  getStatus();
  setTitleTag();
  handleExtras();
  getDependencies();
  getGpt();
  checkTriggeredProbes();
  getBrowserZone();
  await getPlanEnv();
  isLoading.value = false;

  updateRerunOptionsLinks();

  refreshInterval = setInterval(refreshExecution, 10000);
});
</script>

<style lang="scss">
.executionView {
  @media print {
    font-size: 12px;

    h1 {
      flex-direction: column !important;
      align-items: flex-start;

      font-size: 20px !important;
    }

    h2 {
      margin-bottom: 0;

      font-size: 16px;
    }
  }

  .executionInfo {
    margin-bottom: var(--space-large);
  }
  .executionSection {
    &__header {
      display: flex;
      gap: var(--space-small);

      h2 {
        margin-right: auto;
      }

      a,
      button {
        @media print {
          display: none;
        }
      }
    }

    > div,
    > dl {
      margin: 0;
      padding: var(--space-small);

      background-color: var(--section-background);
      border-radius: var(--border-radius-s);
    }

    dl {
      display: flex;
      gap: var(--space-medium);

      > div {
        flex: 1;

        @media print {
          flex: auto;
        }
      }

      > div + div {
        padding-left: var(--space-small);

        border-left: 1px solid var(--section-separator-color);
      }

      dt {
        color: var(--text-color-dim);
        font-size: 1.4rem;
        text-transform: uppercase;

        @media print {
          font-size: 10px;
        }
      }
    }

    &--env {
      position: relative;
    }
  }

  .executionSection + .executionSection {
    margin-top: var(--space-medium);
  }
}
</style>
