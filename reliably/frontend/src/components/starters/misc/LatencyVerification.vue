<template>
  <form class="latencyVerificationForm starterForm form">
    <fieldset>
      <div class="inputWrapper" :class="{ 'inputWrapper--error': !isUrlValid }">
        <label for="host">
          Target endpoint <span class="required">Required</span>
        </label>
        <input
          type="string"
          name="url"
          id="url"
          v-model="latUrl"
          @blur="onUrlBlur"
          placeholder="https://example.com"
          required
        />
        <p
          v-if="!isUrlValid"
          class="inputWrapper__help inputWrapper__help--error"
        >
          Endpoint doesn't seem to be a valid URL.
        </p>
      </div>
      <div
        class="inputWrapper"
        :class="{ 'inputWrapper--error': !isThresholdValid }"
      >
        <label for="host">
          Latency threshold in ms <span class="required">Required</span>
        </label>
        <input
          type="number"
          name="threshold"
          id="threshold"
          min="1"
          v-model="latThreshold"
          @blur="onThresholdBlur"
          required
        />
        <p
          v-if="!isThresholdValid"
          class="inputWrapper__help inputWrapper__help--error"
        >
          This is not a valid latency threshold. Your latency threshold must be
          a positive number, expressing the number of milliseconds your endpoint
          should respond you consider
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
  ExperimentDefinition,
  ExperimentImportPayload,
  Contributions,
  EnvConfiguration,
} from "@/types/experiments";
import { importExperiment } from "@/stores/experiments";
import ExperimentContributions from "@/components/experiments/ExperimentContributions.vue";
import ExperimentTags from "@/components/experiments/ExperimentTags.vue";

const latUrl = ref<string>("");
const isUrlValid = ref<boolean>(true);
const onUrlBlur = (): void => {
  if (latUrl.value === "") {
    isUrlValid.value = true;
  } else {
    try {
      let url = new URL(latUrl.value);
      isUrlValid.value = true;
    } catch (_) {
      isUrlValid.value = false;
    }
  }
};

const latThreshold = ref<number>(200);
const isThresholdValid = ref<boolean>(true);
const computedLatThreshold = computed<number>(() => {
  return latThreshold.value / 1000;
});
const onThresholdBlur = (): void => {
  if (latThreshold.value < 1) {
    isThresholdValid.value = false;
  } else {
    isThresholdValid.value = true;
  }
};

const contributions = ref<Contributions>({
  availability: "low",
  latency: "high",
  security: "none",
  errors: "high",
});

const tags = ref<string[]>(["latency"]);

let verification: ExperimentDefinition = {
  version: "1.0.0",
  title: "Latency remains under 200ms",
  description:
    "Verify that our endpoint responds under a reasonable amount of time",
  runtime: {
    hypothesis: {
      strategy: "after-method-only",
    },
  },
  configuration: {
    reliably_latency: {
        type: "env",
        key: "RELIABLY_PARAM_LATENCY",
        default: 0.2,
    },
    reliably_url: {
        type: "env",
        key: "RELIABLY_PARAM_URL",
        default: "https://reliably.com",
    },
  },
  "steady-state-hypothesis": {
    title: "capture-response-time-and-verify-it",
    probes: [
      {
        type: "probe",
        name: "measure-endpoint-response-time",
        tolerance: {
          type: "probe",
          name: "validate-response-time",
          provider: {
            type: "python",
            module: "chaosreliably.activities.http.tolerances",
            func: "response_time_must_be_under",
            arguments: {
              latency: "${reliably_latency}",
            },
          },
        },
        provider: {
          type: "python",
          module: "chaosreliably.activities.http.probes",
          func: "measure_response_time",
          arguments: {
            url: "${reliably_url}",
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
                content: "Can you describe the impacts of increasing latency in a complex system?",
            },
            {
                role: "user",
                content: "How about in a microservices architecture?",
            },
            {
                role: "user",
                content: "Can you suggest good SLO to monitor and alert me?",
            }
        ]
    }
  ]
};

const isSubmitDisabled = computed<boolean>(() => {
  return latUrl.value === "" || !isUrlValid.value || !isThresholdValid.value;
});

const create = async (run: boolean) => {
  if (!isSubmitDisabled.value) {
    (verification.configuration!.reliably_latency as EnvConfiguration).default = computedLatThreshold.value;
    (verification.configuration!.reliably_url as EnvConfiguration).default = latUrl.value;
    verification.contributions = contributions.value;
    verification.tags = tags.value;
    verification.title = `Latency remains under ${latThreshold.value}ms`;
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
