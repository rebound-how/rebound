<template>
  <form class="planForm form">
    <fieldset>
      <div class="inputWrapper">
        <label for="planTitle">
          Plan title <span class="required">Required</span>
        </label>
        <input
          type="text"
          name="planTitle"
          id="planTitle"
          v-model="planTitle"
          ref="planTitleInput"
          required
          data-form-type="other"
          @blur="handleTitleBlur"
        />
        <p class="inputWrapper__help">
          If left empty, the title of the experiment will be used
        </p>
      </div>
      <div class="inputWrapper">
        <FilterableSelect
          v-if="deploys.length"
          :options="deploys"
          v-model="planDeploymentId"
          label="Deployment"
          :is-required="true"
          default-message="Select a deployment"
        />
        <p v-else>
          You don't seem to have created Deployments yet. Deployments are
          required to run plans.
          <a href="/deployments/new/">Create your first deployment</a>.
        </p>
      </div>
      <div class="inputWrapper">
        <FilterableSelect
          :options="environmentsList"
          v-model="planEnvId"
          label="Reliably Environment"
          :allow-empty="true"
        />
        <p class="inputWrapper__help">
          Name of the Reliably Environment where your secrets and variables are
          stored
        </p>
      </div>
      <div v-if="targetDeployment?.type === 'github'" class="inputWrapper">
        <label for="GitHubEnv">
          GitHub environment name <span class="required">Required</span>
        </label>
        <input
          type="text"
          name="GitHubEnv"
          id="GitHubEnv"
          v-model="planEnvName"
          required
        />
        <p class="inputWrapper__help">
          Name of the GitHub Environment where your secrets are stored
        </p>
      </div>
      <div class="inputWrapper">
        <FilterableSelect
          :options="exps"
          v-model="planExperiments"
          label="Experiment"
          :is-required="true"
          default-message="Select an experiment"
          @emit-object="handleExperimentsChange"
        />
      </div>
    </fieldset>
    <fieldset class="noLegend">
      <div
        class="inputWrapper"
        :class="{ 'inputWrapper--error': !isCronValid }"
      >
        <label for="schedule">
          Schedule <span class="required">Required</span>
        </label>
        <input
          type="text"
          name="schedule"
          id="schedule"
          v-model="planSchedule"
          @blur="onScheduleBlur"
          required
        />
        <p v-if="!isCronValid" class="inputWrapper__help">
          Schedule is not valid CRON.
        </p>
        <p class="inputWrapper__help">
          Schedules are specified using the
          <a
            href="https://man7.org/linux/man-pages/man5/crontab.5.html"
            target="_blank"
            rel="noopener noreferer"
            >unix-cron</a
          >
          format. Use <strong>now</strong> to run your experiments as soon as
          possible.
        </p>
        <p class="inputWrapper__help">
          Shortcuts:
          <span role="button" @click="setSchedule('*/5 * * * *')">
            Every 5 minutes</span
          >,
          <span role="button" @click="setSchedule('0 */1 * * *')">
            Every hour</span
          >,
          <span role="button" @click="setSchedule('0 9 */1 * *')">
            Every day at 9:00</span
          >,
          <span role="button" @click="setSchedule('0 9 1 * *')">
            On the first day of every month at 9:00</span
          >.
        </p>
      </div>
      <div v-if="false" class="inputWrapper inputWrapper--tick">
        <div>
          <input
            type="checkbox"
            v-model="planViaAgent"
            id="agent"
            name="agent"
          />
          <label for="agent">Run via Agent</label>
        </div>
        <p class="inputWrapper__help">
          Check this case to have the Reliably Agent run this plan. Leave
          unchecked to have the plan run by the Reliably App.
          <a href="https://reliably.com/docs/"
            >Read the docs for more details about the differences.</a
          >
        </p>
      </div>
    </fieldset>
    <fieldset>
      <legend>Integrations</legend>
      <div class="planForm__integrations inputWrapper">
        <div v-if="ints.length > 0">
          <div
            v-for="(i, index) in ints"
            :index="index"
            class="inputWrapper inputWrapper--tick"
          >
            <div>
              <input
                type="checkbox"
                :value="i.id"
                :id="`int-${index}`"
                :name="`int-${index}`"
                v-model="planIntegrations"
              />
              <label :for="`int-${index}`">
                <IntegrationVendorIcon :vendor="i.vendor" />
                {{ i.name }}
              </label>
            </div>
          </div>
        </div>
        <p v-else>You don't have any active integrations</p>
      </div>
      <div class="inputWrapper">
        <button
          @click.prevent="proceed"
          :disabled="isSubmitDisabled"
          class="button button--primary"
        >
          Create plan
        </button>
      </div>
    </fieldset>
  </form>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, nextTick } from "vue";
import { useStore } from "@nanostores/vue";
import { isValidCron } from "cron-validator";
import type { PlanCreate } from "@/types/plans";
import type { Deployment, DeploymentForPlanForm } from "@/types/deployments";
import type { Integration, IntegrationForPlanForm } from "@/types/integrations";
import type { ExperimentShortForm } from "@/types/experiments";
import type { FilterableSelectOption } from "@/types/ui-types";
import { deployments, fetchDeployments } from "@/stores/deployments";
import { integrations, fetchIntegrations } from "@/stores/integrations";
import { allExperiments, fetchAllExperiments } from "@/stores/experiments";
import { createPlan } from "@/stores/plans";
import { environments, fetchEnvironments } from "@/stores/environments";
import { formatDeploymentType } from "@/utils/deployments";

import IntegrationVendorIcon from "@/components/integrations/IntegrationVendorIcon.vue";
import FilterableSelect from "@/components/_ui/FilterableSelect.vue";

// const sourceId = ref<string | null>(null);

const planTitle = ref<string>("");
const planTitleInput = ref<HTMLElement | null>(null);
const isTitleSetAutomatically = ref<{ status: boolean; value: string }>({
  status: false,
  value: "",
});
const planDeploymentId = ref<string>("");
const targetDeployment = ref<DeploymentForPlanForm | undefined>(undefined);
const planEnvName = ref<string>("");
const onPlanDeploymentChange = async (): Promise<void> => {
  const t = deploys.value.find((d) => {
    return d.val === planDeploymentId.value;
  });
  if (t) {
    targetDeployment.value = {
      name: t.label,
      id: t.val,
      type: t.type,
    };
  }
  if (environmentsList.value.length === 0) {
    await getEnvironments();
  }
};

watch(planDeploymentId, () => {
  onPlanDeploymentChange();
});

const planEnvId = ref<string>("");
const environmentsList = ref<{ label: string; val: string }[]>([]);

async function getEnvironments() {
  let fetched: { label: string; val: string }[] = [];
  await fetchEnvironments(1);
  let stored = useStore(environments);
  stored.value.environments.forEach((e) => {
    fetched.push({ label: e.name, val: e.id! });
  });
  if (stored.value.total > 10) {
    let rounds = Math.floor(stored.value.total / 10);
    if (stored.value.total % 10 > 0) {
      rounds++;
    }
    let pages: number[] = [];
    for (var i = 2; i <= rounds; i++) {
      pages.push(i);
    }
    for (const page of pages) {
      await fetchEnvironments(page);
      let stored = useStore(environments);
      stored.value.environments.forEach((e) => {
        fetched.push({ label: e.name, val: e.id! });
      });
    }
  }
  environmentsList.value = [...fetched];
}

const planExperiments = ref<string>("");
const planSchedule = ref<string>("");
const isCronValid = ref<boolean>(true);
const planViaAgent = ref<boolean>(false);
const planIntegrations = ref<string[]>([]);

function handleTitleBlur() {
  if (planTitle.value !== isTitleSetAutomatically.value.value) {
    // User has manually changed the title
    isTitleSetAutomatically.value = {
      status: false,
      value: "",
    };
  }
}

function handleExperimentsChange(exp: FilterableSelectOption) {
  if (
    planTitle.value === "" ||
    planTitle.value === exp.label ||
    isTitleSetAutomatically.value.status === true
  ) {
    planTitle.value = exp.label;
    isTitleSetAutomatically.value = {
      status: true,
      value: exp.label,
    };
  }
}

const setSchedule = (cron: string): void => {
  planSchedule.value = cron;
};
const onScheduleBlur = (): void => {
  if (planSchedule.value === "") {
    isCronValid.value = true;
  } else if (planSchedule.value === "now") {
    isCronValid.value = true;
  } else {
    if (isValidCron(planSchedule.value)) {
      isCronValid.value = true;
    } else {
      isCronValid.value = false;
    }
  }
};

const isSubmitDisabled = computed<boolean>(() => {
  return (
    planTitle.value === "" ||
    planDeploymentId.value === "" ||
    planExperiments.value.length === 0 ||
    planSchedule.value === ""
  );
});

const deploys = ref<FilterableSelectOption[]>([]);
const totalDeploys = ref<number>(0);
const deploysPage = ref<number>(1);
const getDeployments = async () => {
  await fetchDeployments(deploysPage.value);
  let latestDeploys = useStore(deployments);
  totalDeploys.value = latestDeploys.value.total;
  latestDeploys.value.deployments.forEach((d: Deployment) => {
    deploys.value.push({
      label: `${formatDeploymentType(d.definition.type)} ${d.name}`,
      val: d.id!,
      type: d.definition.type,
    });
  });
  deploysPage.value++;
};
const getMoreDeployments = async () => {
  for (let i: number = 1; 10 * i < totalDeploys.value; i++) {
    await getDeployments();
  }
};

const populateFromParams = () => {
  let location = window.location;
  let params = new URLSearchParams(location.search);
  if (params.has("exp")) {
    const exp = params.get("exp")!;
    planExperiments.value = exp;
    const selected = exps.value.find((e) => {
      return e.val === exp;
    });
    if (selected) {
      planTitle.value = selected.label;
    }
  }
  if (params.has("s")) {
    let s = params.get("s");
    if (s !== null) {
      if (s === "now") {
        planSchedule.value = "now";
      } else {
        planSchedule.value = s.replaceAll("_", " ");
      }
    }
  }
  if (params.has("a")) {
    let a = params.get("a");
    if (a !== null && a === "true") {
      planViaAgent.value = true;
    }
  }
  if (params.has("d")) {
    let d = params.get("d");
    if (d !== null) {
      planDeploymentId.value = d;
      onPlanDeploymentChange();
    }
  }
  if (params.has("envid")) {
    const envId = params.get("envid");
    if (envId !== null && envId !== "null") {
      planEnvId.value = envId;
    }
  }
  if (params.has("envgh")) {
    const envName = params.get("envgh");
    if (envName !== null && envName !== "null") {
      planEnvName.value = envName;
    }
  }
  if (params.has("int")) {
    let ids = params.get("int")!;
    if (ids !== "") {
      let idsArr = ids.split(",");
      planIntegrations.value = [...idsArr];
    }
  }
};

const exps = ref<{ label: string; val: string }[]>([]);
const getExperiments = async () => {
  await fetchAllExperiments();
  let allExps = useStore(allExperiments);
  allExps.value.forEach((e: ExperimentShortForm) => {
    exps.value.push({ label: e.title, val: e.id });
  });
  // TODO add message in form when no experiments exist
};

const ints = ref<IntegrationForPlanForm[]>([]);
const totalInts = ref<number>(0);
const intsPage = ref<number>(1);
const getIntegrations = async () => {
  await fetchIntegrations(intsPage.value);
  let latestInts = useStore(integrations);
  totalInts.value = latestInts.value.total;
  latestInts.value.integrations.forEach((i) => {
    if (!((i.vendor == "reliably") && ((i.provider == "assistant") || (i.provider == "snapshot") || (i.provider == "notification")))) {
      ints.value.push({
        name: i.name,
        provider: i.provider,
        id: i.id!,
        vendor: i.vendor!,
      });
    }
  });
  intsPage.value++;
};
const getMoreIntegrations = async () => {
  for (let i: number = 1; 10 * i < totalInts.value; i++) {
    await getIntegrations();
  }
};

const proceed = async () => {
  let schedulePayload: PlanCreate["schedule"] = {
    type: "now",
  };
  if (planSchedule.value !== "now") {
    schedulePayload = {
      type: "cron",
      pattern: planSchedule.value,
      // get client current timezone
      timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
    };
  }
  if (planViaAgent.value) {
    schedulePayload.via_agent = true;
  }
  let newPlan: PlanCreate = {
    title: planTitle.value,
    environment: null,
    deployment: {
      deployment_id: targetDeployment.value?.id!,
      deployment_type: targetDeployment.value?.type!,
    },
    schedule: schedulePayload,
    experiments: [planExperiments.value],
    integrations: planIntegrations.value,
  };
  if (targetDeployment.value!.type === "github") {
    newPlan.environment = {
      provider: "github",
      name: planEnvName.value,
    };
    if (planEnvId.value !== "") {
      newPlan.environment.id = planEnvId.value;
    }
  } else if (
    targetDeployment.value!.type === "reliably_cloud" ||
    targetDeployment.value!.type === "reliably_cli" ||
    targetDeployment.value!.type === "container" ||
    targetDeployment.value!.type === "k8s_job"
  ) {
    if (planEnvId.value !== "") {
      newPlan.environment = {
        provider: "reliably_cloud",
        id: planEnvId.value,
      };
    }
  }
  createPlan(newPlan);
};

onMounted(async () => {
  await getDeployments();
  await getMoreDeployments();
  await getIntegrations();
  await getMoreIntegrations();
  await getExperiments();
  populateFromParams();
  nextTick(() => {
    planTitleInput.value!.focus();
  });
});
</script>

<style lang="scss" scoped>
.planForm {
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

  &__experiments {
    position: relative;

    > div {
      margin-top: calc(-1 * var(--space-small));
      max-height: 30rem;
      overflow-y: auto;
      padding: var(--space-medium) 0;
    }

    &::after,
    &::before {
      content: "";

      position: absolute;
      left: 0;
      z-index: 2;

      display: block;
      height: var(--space-small);
      width: 100%;
    }

    &::before {
      top: 0;

      background: linear-gradient(
        to top,
        transparent,
        var(--section-background)
      );
    }

    &::after {
      bottom: 0;

      background: linear-gradient(
        to bottom,
        transparent,
        var(--section-background)
      );
    }
  }

  &__integrations {
    label {
      svg {
        height: 1.6rem;
        margin-left: 0.3rem;
      }
    }
  }

  span[role="button"] {
    cursor: pointer;

    &:hover {
      color: var(--pink-500);
    }
  }
}
</style>
