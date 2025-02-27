<template>
  <form class="starterForm form">
    <fieldset>
      <div
        class="inputWrapper"
        :class="{ 'inputWrapper--error': !isNameValid }"
      >
        <label for="name">
          Kubernetes Deployment Name <span class="required">Required</span>
        </label>
        <input
          type="text"
          name="name"
          id="name"
          v-model="deploymentName"
          @blur="onNameBlur"
          required
        />
        <p
          v-if="!isNameValid"
          class="inputWrapper__help inputWrapper__help--error"
        >
          Kubernetes deployment name must be set.
        </p>
      </div>
      <div
        class="inputWrapper"
        :class="{ 'inputWrapper--error': !isScaleDownValid }"
      >
        <label for="scaleDownNumber"
          >Number of replicas to scale down to
          <span class="required">Required</span></label
        >
        <input
          type="number"
          name="scaleDownNumber"
          id="scaleDownNumber"
          min="0"
          v-model="scaleDownNumber"
          @blur="onScaleDownValidBlur"
          required
        />
        <p
          v-if="!onScaleDownValidBlur"
          class="inputWrapper__help inputWrapper__help--error"
        >
          You cannot scale down a deployment to less than 0 replicas
        </p>
      </div>
      <div
        class="inputWrapper"
        :class="{ 'inputWrapper--error': !isScaleUpValid }"
      >
        <label for="scaleUpNumber"
          >Number of replicas to scale back up to
          <span class="required">Required</span></label
        >
        <input
          type="number"
          name="scaleUpNumber"
          id="scaleUpNumber"
          min="1"
          v-model="scaleUpNumber"
          @blur="onScaleUpValidBlur"
          required
        />
        <p
          v-if="!onScaleUpValidBlur"
          class="inputWrapper__help inputWrapper__help--error"
        >
          You cannot scale up a deployment to less than 1 replica
        </p>
      </div>
      <div
        class="inputWrapper"
        :class="{ 'inputWrapper--error': !isWaitForValid }"
      >
        <label for="scaleUpNumber"
          >Wait in seconds before scaling back up
          <span class="required">Required</span></label
        >
        <input
          type="number"
          name="waitFor"
          id="waitFor"
          min="0"
          v-model="waitFor"
          @blur="onWaitFordBlur"
          placeholder="30"
          required
        />
        <p
          v-if="!onWaitFordBlur"
          class="inputWrapper__help inputWrapper__help--error"
        >
          Waiting, before scaling nack up, must be a positive number or zero.
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
  Action,
} from "@/types/experiments";
import { importExperiment } from "@/stores/experiments";
import ExperimentContributions from "@/components/experiments/ExperimentContributions.vue";
import ExperimentTags from "@/components/experiments/ExperimentTags.vue";

const deploymentName = ref<string>("");
const isNameValid = ref<boolean>(true);
const onNameBlur = (): void => {
  if (deploymentName.value === "") {
    isNameValid.value = true;
  }
};

const scaleDownNumber = ref<number>(1);
const isScaleDownValid = ref<boolean>(true);
const onScaleDownValidBlur = (): void => {
  if (scaleDownNumber.value < 0) {
    isScaleDownValid.value = false;
  } else {
    isScaleDownValid.value = true;
  }
};
const scaleUpNumber = ref<number>(1);
const isScaleUpValid = ref<boolean>(true);
const onScaleUpValidBlur = (): void => {
  if (scaleUpNumber.value < 1) {
    isScaleUpValid.value = false;
  } else {
    isScaleUpValid.value = true;
  }
};
const waitFor = ref<number>(30);
const isWaitForValid = ref<boolean>(true);
const onWaitFordBlur = (): void => {
  if (scaleUpNumber.value < 0) {
    isScaleUpValid.value = false;
  } else {
    isScaleUpValid.value = true;
  }
};

const contributions = ref<Contributions>({
  availability: "high",
  latency: "medium",
  security: "none",
  errors: "high",
});

const tags = ref<string[]>(["kubernetes", "deployment"]);

let verification: ExperimentDefinition = {
  version: "1.0.0",
  title: "Scaling deployment down has minimum impact over our availability",
  description:
    "How far down can we scale our deployment and still meet our criteria",
  configuration: {
    reliably_deployment_name: {
        type: "env",
        key: "RELIABLY_PARAM_DEPLOYMENT_NAME",
    },
    reliably_deployment_down: {
        type: "env",
        key: "RELIABLY_PARAM_DEPLOYMENT_SCALE_DOWN_TO",
        default: 1,
    },
    reliably_deployment_up: {
        type: "env",
        key: "RELIABLY_PARAM_DEPLOYMENT_SCALE_UP_TO",
        default: 1,
    },
  },
  extensions: [
    {
        name: "chatgpt",
        messages: [
            {
                role: "user",
                content: "How does scaling Kubernetes deployments impact the resilience of a system?",
            },
            {
                role: "user",
                content: "So, I should assume that scaling down to a single replica puts my system at risk of resilience failures? Can you list some of these failures?",
            },
            {
                role: "user",
                content: "Conversely, is there a risk of scaling too much?",
            },
            {
                role: "user",
                content: "Is there a typically good number of replicas to use? Should this be an odd or even number?",
            },
            {
                role: "user",
                content: "Should I spread my replicas across nodes? What's the right approach with Kubernetes and can you show me an example?",
            },
            {
                role: "user",
                content: "Can you show me an example using topologySpreadConstraints?",
            }
        ]
    }
  ],
  method: [
    {
      type: "action",
      name: "scale-deployment-down",
      provider: {
        type: "python",
        module: "chaosk8s.deployment.actions",
        func: "scale_deployment",
        arguments: {
          name: "${reliably_deployment_name}",
          replicas: "${reliably_deployment_down}",
        },
      },
      pauses: {
        after: 30,
      },
    },
  ],
  rollbacks: [
    {
      type: "action",
      name: "scale-deployment-up",
      provider: {
        type: "python",
        module: "chaosk8s.deployment.actions",
        func: "scale_deployment",
        arguments: {
          name: "${reliably_deployment_name}",
          replicas: "${reliably_deployment_up}",
        },
      },
    },
  ],
};

const isSubmitDisabled = computed<boolean>(() => {
  return deploymentName.value === "" || !isNameValid.value;
});

const create = async (run: boolean) => {
  if (!isSubmitDisabled.value) {
    verification.title = `Scale down Kubernetes deployment '${deploymentName.value}' to ${scaleDownNumber.value} replicas during ${waitFor.value}s`;
    verification.contributions = contributions.value;
    verification.tags = tags.value;
    (verification.configuration!.reliably_deployment_name as EnvConfiguration).default = deploymentName.value;
    (verification.configuration!.reliably_deployment_down as EnvConfiguration).default = scaleDownNumber.value;
    (verification.configuration!.reliably_deployment_up as EnvConfiguration).default = scaleUpNumber.value;
    let action = verification.method?.at(0) as Action;
    action.pauses = {
      after: waitFor.value,
    };
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
