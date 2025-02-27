<template>
  <form class="terminatePodVerificationForm starterForm form">
    <fieldset>
      <div
        class="inputWrapper"
        :class="{ 'inputWrapper--error': !isLabelSelectorValid }"
      >
        <label for="label_selector">
          Label Selector <span class="required">Required</span>
        </label>
        <input
          type="text"
          name="label_selector"
          id="label_selector"
          v-model="podLabelSelector"
          @blur="onLabelselectorBlur"
          placeholder="app=my-app,other=value"
          required
        />
        <p class="inputWrapper__help">A list of comma-separated selectors.</p>
        <p
          v-if="!isLabelSelectorValid"
          class="inputWrapper__help inputWrapper__help--error"
        >
          Label doesn't seem to be a valid selector.
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
import { validateLabelSelector } from "@/utils/strings";

const podLabelSelector = ref<string>("");
const isLabelSelectorValid = ref<boolean>(true);
const onLabelselectorBlur = (): void => {
  isLabelSelectorValid.value = validateLabelSelector(podLabelSelector.value);
};

const contributions = ref<Contributions>({
  availability: "high",
  latency: "medium",
  security: "none",
  errors: "medium",
});

const tags = ref<string[]>(["kubernetes", "pods"]);

let verification: ExperimentDefinition = {
  version: "1.0.0",
  title: "Temporarily losing capacity does not impact our availability",
  configuration: {
    reliably_pod_label_selector: {
        type: "env",
        key: "RELIABLY_PARAM_POD_LABEL_SELECTORS",
    },
  },
  description:
    "Evaluate the impact of randomly losing a bit of capacity in the a service. This may inform us if we need to increase or decrease it.",
    extensions: [
    {
        name: "chatgpt",
        messages: [
            {
                role: "user",
                content: "What do Kubernetes pods have to play in the resilience of a system?",
            },
            {
                role: "user",
                content: "What are the essential facets of the Kubernetes pod manifest I should be implementing properly when it comes to resilience?",
            },
            {
                role: "user",
                content: "Can you suggest good chaos engineering experiments to run for each of these points?",
            }
        ]
    }
  ],
  method: [
    {
      type: "action",
      name: "terminate-service-pod",
      provider: {
        type: "python",
        module: "chaosk8s.pod.actions",
        func: "terminate_pods",
        arguments: {
          label_selector: "${reliably_pod_label_selector}",
        },
      },
    },
  ],
};

const isSubmitDisabled = computed<boolean>(() => {
  return podLabelSelector.value === "" || !isLabelSelectorValid.value;
});

const create = async (run: boolean) => {
  if (!isSubmitDisabled.value) {
    verification.title = `Restarting pods labelled '${podLabelSelector.value}'`;
    verification.contributions = contributions.value;
    (verification.configuration!.reliably_pod_label_selector as EnvConfiguration).default = podLabelSelector.value;
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
.terminatePodVerificationForm {
  &__delay {
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
