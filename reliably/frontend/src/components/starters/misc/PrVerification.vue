<template>
  <form class="prVerificationForm starterForm form">
    <fieldset>
      <div
        class="inputWrapper"
        :class="{ 'inputWrapper--error': !isRepoValid }"
      >
        <label for="repo">
          GitHub repository URL <span class="required">Required</span>
        </label>
        <input
          type="text"
          name="repo"
          id="repo"
          v-model="prRepo"
          @blur="onRepoBlur"
          placeholder="https://github.com/chaostoolkit/chaostoolkit"
          required
        />
        <p
          v-if="!isRepoValid"
          class="inputWrapper__help inputWrapper__help--error"
        >
          This URL doesn't seem to be a valid GitHub repository.
        </p>
      </div>
      <div class="inputWrapper">
        <label for="branch">
          Branch <span class="required">Required</span>
        </label>
        <input
          type="text"
          name="branch"
          id="branch"
          v-model="prBranch"
          required
        />
      </div>
      <div class="inputWrapper prVerificationForm__window">
        <label for="window">
          Time Window <span class="required">Required</span>
        </label>
        <p class="inputWrapper__help">
          The maximum allowed time before a PR is closed.
        </p>
        <div>
          <input
            type="number"
            name="window"
            id="window"
            min="1"
            :max="maxDelay"
            @blur="enforceWindowMinMax"
            v-model="prWindowNumber"
            required
          />
          <select
            name="windowUnit"
            id="windowUnit"
            v-model="prWindowUnit"
            @change="onWindowUnitChange"
            required
          >
            <option value="h">Hours</option>
            <option value="d">Days</option>
            <option value="w">Weeks</option>
          </select>
        </div>
      </div>
      <div
        class="inputWrapper"
        :class="{ 'inputWrapper--error': isTargetOutOfBounds }"
      >
        <label for="target">
          PR closing target <span class="required">Required</span>
        </label>
        <input
          type="number"
          name="target"
          id="target"
          min="0"
          max="100"
          step="0.1"
          placeholder="97.5"
          v-model="prTarget"
          required
        />
        <p class="inputWrapper__help">
          The percentage of PR that must be closed in less than the selected
          time window. If the actual number is less than this target, the
          verification will fail.
        </p>
        <p
          v-if="isTargetOutOfBounds"
          class="inputWrapper__help inputWrapper__help--error"
        >
          Target must be a number between 0 and 100.
        </p>
      </div>
      <details class="inputWrapper inputWrapper--details">
        <summary>Contributions and tags</summary>
        <ExperimentContributions v-model="contributions" />
        <ExperimentTags v-model="tags" />
      </details>
      <div class="inputWrapper">
        <button
          @click.prevent="create(false)"
          :disabled="isSubmitDisabled"
          class="button button--primary"
        >
          Create
        </button>
        <button
          @click.prevent="create(true)"
          :disabled="isSubmitDisabled"
          class="button button--creative"
        >
          Create and run
        </button>
      </div>
    </fieldset>
  </form>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import type {
  EnvConfiguration,
  ExperimentDefinition,
  ExperimentImportPayload,
  Contributions,
} from "@/types/experiments";
import { importExperiment } from "@/stores/experiments";
import ExperimentContributions from "@/components/experiments/ExperimentContributions.vue";
import ExperimentTags from "@/components/experiments/ExperimentTags.vue";
import { urlToRepository } from "@/utils/strings";

const prRepo = ref<string>("");
const isRepoValid = ref<boolean>(true);
const onRepoBlur = (): void => {
  if (prRepo.value === "") {
    isRepoValid.value = true;
  } else {
    try {
      let repo = urlToRepository(prRepo.value);
      if (repo.repository === undefined) {
        isRepoValid.value = false;
      } else {
        isRepoValid.value = true;
      }
    } catch (_) {
      isRepoValid.value = false;
    }
  }
};
const prBranch = ref<string>("main");

const prWindowNumber = ref<number>(5);
const prWindowUnit = ref<string>("d");
const maxDelay = computed<number>(() => {
  if (prWindowUnit.value === "s" || prWindowUnit.value === "m") {
    return 60;
  } else if (prWindowUnit.value === "h") {
    return 24;
  } else if (prWindowUnit.value === "d") {
    return 31;
  } else if (prWindowUnit.value === "w") {
    return 4;
  } else {
    // Should never happen. Better safe than sorry.
    return 100;
  }
});
const onWindowUnitChange = (): void => {
  if (prWindowNumber.value > maxDelay.value) {
    prWindowNumber.value = maxDelay.value;
  }
};
const enforceWindowMinMax = (): void => {
  if (prWindowNumber.value < 0) {
    prWindowNumber.value = 0;
  }
  if (prWindowNumber.value > maxDelay.value) {
    prWindowNumber.value = maxDelay.value;
  }
};
const unitToWord = (u: string): string => {
  if (u === "d") {
    return "days";
  } else if (u === "w") {
    return "weeks";
  } else if (u === "h") {
    return "hours";
  } else {
    return u;
  }
};

const prTarget = ref<number>();
const isTargetOutOfBounds = computed<boolean>(() => {
  if (prTarget.value === undefined) {
    return false;
  } else {
    return prTarget.value < 0 || prTarget.value > 100;
  }
});

const contributions = ref<Contributions>({
  availability: "low",
  latency: "none",
  security: "low",
  errors: "none",
});

const tags = ref<string[]>(["github", "dev", "team"]);

let verification: ExperimentDefinition = {
  version: "1.0.0",
  title: "Teams can sustain a healthy capacity towards closing PRs",
  description:
    "Keep an eye on a team's health by reviewing how regularly PRs are closed in a repository. The goal is to understand if teams are over-committed and cannot respond to the influx of new work.",
  configuration: {
    reliably_gh_target: {
        type: "env",
        key: "RELIABLY_PARAM_GH_TARGET",
    },
    reliably_gh_repo: {
        type: "env",
        key: "RELIABLY_PARAM_GH_REPO",
    },
    reliably_gh_base: {
        type: "env",
        key: "RELIABLY_PARAM_GH_BASE",
    },
    reliably_gh_window: {
        type: "env",
        key: "RELIABLY_PARAM_GH_WINDOW",
    },
  },
  "steady-state-hypothesis": {
    title: "Compute a ratio of closed PRs over a specific period of time",
    probes: [
      {
        type: "probe",
        name: "compute-pr-closing-ratio",
        tolerance: {
          type: "probe",
          name: "verify-closed-prs-ratio",
          provider: {
            type: "python",
            module: "chaosreliably.activities.gh.tolerances",
            func: "ratio_above_or_equal",
            arguments: {
              target: "${reliably_gh_target}",
            },
          },
        },
        provider: {
          type: "python",
          module: "chaosreliably.activities.gh.probes",
          func: "closed_pr_ratio",
          arguments: {
            repo: "${reliably_gh_repo}",
            base: "${reliably_gh_base}",
            window: "${reliably_gh_window}",
          },
        },
      },
    ],
  },
  method: [],
  extensions: [
    {
        name: "chatgpt",
        messages: [
            {
                role: "user",
                content: "What could be the impacts on an organization if our team backlog was growing beyond our capacity to manage it?",
            }
        ]
    }
  ]
};

const isSubmitDisabled = computed<boolean>(() => {
  return (
    prRepo.value === "" ||
    !isRepoValid.value ||
    prBranch.value === "" ||
    prTarget.value === undefined
  );
});

const create = async (run: boolean) => {
  if (!isSubmitDisabled.value) {
    verification.contributions = contributions.value;
    verification.tags = tags.value;
    (verification.configuration!.reliably_gh_repo as EnvConfiguration).default = prRepo.value,
    (verification.configuration!.reliably_gh_base as EnvConfiguration).default = prBranch.value,
    (verification.configuration!.reliably_gh_window as EnvConfiguration).default = prWindowNumber.value.toString() + prWindowUnit.value,
    (verification.configuration!.reliably_gh_target as EnvConfiguration).default = prTarget.value!.toString(),

    verification.title = `Over ${prTarget.value!.toString()}% of PRs are closed in less than ${prWindowNumber.value.toString()} ${unitToWord(
      prWindowUnit.value
    )}`;
    let e: ExperimentImportPayload = {
      experiment: JSON.stringify(verification),
    };
    if (run) {
      await importExperiment(e, true);
    } else {
      await importExperiment(e);
    }
  }
};
</script>

<style lang="scss" scoped>
.prVerificationForm {
  &__window {
    > div {
      display: flex;
      flex-wrap: wrap;
      gap: var(--space-small);

      > input,
      > select {
        width: 12rem;
      }
    }
  }
}
</style>
