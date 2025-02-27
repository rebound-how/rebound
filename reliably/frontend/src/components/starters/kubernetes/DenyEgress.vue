<template>
  <form class="denyEgressVerificationForm starterForm form">
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
          v-model="labelSelector"
          placeholder="app=my-app,other=value"
          @blur="onLabelSelectorBlur"
          required
        />
        <p class="inputWrapper__help">A list of comma-separated selectors.</p>
        <p
          v-if="!isLabelSelectorValid"
          class="inputWrapper__help inputWrapper__help--error"
        >
          Label selectors are not set or invalid.
        </p>
      </div>
      <div
        class="inputWrapper"
        :class="{ 'inputWrapper--error': !isWaitForValid }"
      >
        <label for="scaleUpNumber">
          Wait in seconds before allowing Egress again
          <span class="required">Required</span>
        </label>
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
          Invalid value. It must be a positive number or zero.
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
import { validateLabelSelector } from "@/utils/strings";

const labelSelector = ref<string>("");
const isLabelSelectorValid = ref<boolean>(true);
const onLabelSelectorBlur = (): void => {
  isLabelSelectorValid.value = validateLabelSelector(labelSelector.value);
};

const waitFor = ref<number>(30);
const isWaitForValid = ref<boolean>(true);
const onWaitFordBlur = (): void => {
  if (waitFor.value < 0) {
    isWaitForValid.value = false;
  } else {
    isWaitForValid.value = true;
  }
};

const contributions = ref<Contributions>({
  availability: "high",
  latency: "high",
  security: "low",
  errors: "medium",
});

const tags = ref<string[]>(["kubernetes", "pods", "networking"]);

let verification: ExperimentDefinition = {
  version: "1.0.0",
  title: "Losing egress from pods should be alerted in some capacity",
  description:
    "Egress loss from pods is a pretty bad condition that we need to monitor for",
  configuration: {
    reliably_pod_label_selectors: {
        type: "env",
        key: "RELIABLY_PARAM_POD_LABEL_SELECTORS",
    },
  },
  method: [
    {
      type: "action",
      name: "deny-egress-from-pods",
      provider: {
        type: "python",
        module: "chaosk8s.networking.actions",
        func: "deny_all_egress",
        arguments: {
          label_selectors: "${reliably_pod_label_selectors}",
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
      name: "undo-deny-egress-from-pods",
      provider: {
        type: "python",
        module: "chaosk8s.networking.actions",
        func: "remove_deny_all_egress",
      },
    },
  ],
  extensions: [
    {
        name: "chatgpt",
        messages: [
            {
                role: "user",
                content: "What could be impacts of losing egress from a Kubernetes pod?"
            },
            {
                role: "user",
                content: "How could I monitor the loss of egress from a Kubernetes pod?"
            },
            {
                role: "user",
                content: "How can I test for loss of egress from a Kubernetes pod?"
            },
            {
                role: "user",
                content: "Can I use ebpf to drop packets from the network?"
            },
            {
                role: "user",
                content: "Can you write an ebpf program that drops packet?"
            }
        ]
    }
  ]
};

const isSubmitDisabled = computed<boolean>(() => {
  return !isWaitForValid.value || !isLabelSelectorValid.value;
});

const create = async (run: boolean) => {
  if (!isSubmitDisabled.value) {
    verification.title = `Drop egress from pods '${labelSelector.value}' during ${waitFor.value}s`;
    verification.contributions = contributions.value;
    verification.tags = tags.value;
    (verification.configuration!.reliably_pod_label_selectors as EnvConfiguration).default = labelSelector.value;
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

<style lang="scss" scoped>
.denyEgressVerificationForm {
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
