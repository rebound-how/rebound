<template>
  <div class="experimentImportPaste">
    <form class="form">
      <fieldset>
        <div
          class="inputWrapper"
          :class="{ 'inputWrapper--error': errorState }"
        >
          <label class="screen-reader-text" for="jsonInput">
            Paste the content of your experiment JSON or YAML file
          </label>
          <textarea
            name="jsonInput"
            id="jsonInput"
            wrap="off"
            v-model="rawInput"
            @keyup="checkInputIsValid"
          ></textarea>
          <div v-if="inputType !== ''" class="experimentImportPaste__type">
            {{ inputType }}
          </div>
          <p
            class="inputWrapper__help experimentImportPaste__info"
            v-html="message"
          ></p>
        </div>
        <ExperimentContributions
          v-if="areContributionsDisplayed"
          v-model="contributions"
          :import-mode="true"
        />
        <div class="inputWrapper">
          <button
            @click.prevent="importFromJson"
            class="button button--primary"
            :disabled="isImportDisabled"
          >
            Import
          </button>
        </div>
      </fieldset>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import * as yaml from "js-yaml";

import { importExperiment } from "@/stores/experiments";
import { isStringSerializedJson } from "@/utils/strings";
import { checkExperiment } from "@/utils/experiments";
import type {
  ExperimentImportPayload,
  ExperimentDefinition,
  Contributions,
} from "@/types/experiments";
import ExperimentContributions from "@/components/experiments/ExperimentContributions.vue";

const rawInput = ref<string>("");
const inputType = ref<string>("");
const experimentJson = ref<any>(null);
const isFileReadable = ref<boolean>(false);
const isFileValidExperiment = ref<boolean>(false);
const errorState = computed<boolean>(() => {
  return rawInput.value !== "" && !isFileValidExperiment.value;
});
const message = ref<string>("");
const contributions = ref<Contributions>({
  availability: "none",
  latency: "none",
  security: "none",
  performance: "none",
});
const areContributionsDisplayed = ref<boolean>(false);

let timeout: ReturnType<typeof setTimeout> | null = null;
const checkInputIsValid = () => {
  inputType.value = "";
  // clear timeout variable
  if (timeout !== null) {
    clearTimeout(timeout);
  }

  timeout = setTimeout(function () {
    if (rawInput.value !== "") {
      if (isStringSerializedJson(rawInput.value)) {
        experimentJson.value = JSON.parse(rawInput.value);
        isFileReadable.value = true;
        inputType.value = "JSON";
      } else {
        try {
          experimentJson.value = yaml.load(rawInput.value);
          isFileReadable.value = true;
          inputType.value = "YAML";
        } catch (e) {
          isFileReadable.value = false;
          message.value = "Input is not valid JSON nor YAML";
        }
      }
      if (isFileReadable.value) {
        let check = checkExperiment(experimentJson.value);
        if (check === "") {
          isFileValidExperiment.value = true;
          message.value = "";
          const exp = experimentJson.value as ExperimentDefinition;
          if (
            exp.contributions === undefined || Object.entries(exp.contributions!
            ).length === 0
          ) {
            areContributionsDisplayed.value = true;
          }
        } else {
          isFileValidExperiment.value = false;
          message.value = `Input is not a valid Chaos Toolkit experiment: ${check}.`;
        }
      }
    } else {
      areContributionsDisplayed.value = false;
      message.value = "";
    }
  }, 500);
};

const isImportDisabled = computed<boolean>(() => {
  return (
    rawInput.value === "" ||
    !isFileReadable.value ||
    !isFileValidExperiment.value
  );
});

const importFromJson = async () => {
  if (areContributionsDisplayed.value) {
    (experimentJson.value as ExperimentDefinition).contributions =
      contributions.value;
  }
  let e: ExperimentImportPayload = {
    experiment: JSON.stringify(experimentJson.value),
  };
  await importExperiment(e);
};
</script>

<style lang="scss" scoped>
.experimentImportPaste {
  position: relative;
  .inputWrapper {
    max-width: unset;

    textarea {
      height: 40rem;
      resize: none;
    }
  }

  &__info {
    min-height: 2.1rem;
  }

  &__type {
    position: absolute;
    top: 1.2rem;
    right: 1.2rem;

    padding: 0.3rem 0.6rem;

    background-color: var(--green-500);
    border-radius: var(--border-radius-s);

    color: white;
    font-size: 1.4rem;
    font-weight: 600;
  }
}
</style>
