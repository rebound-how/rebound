<template>
  <div class="experimentImportUpload">
    <DropZone @files-dropped="handleExperimentFile" :status="dropZoneStatus">
      <p>Drag and drop an experiment JSON file</p>
    </DropZone>
    <p
      class="experimentImportUpload__info"
      :class="messageClassObject"
      v-html="message"
    ></p>
    <ExperimentContributions
      v-if="areContributionsDisplayed"
      v-model="contributions"
      :import-mode="true"
      :form-wrap="true"
    />
    <div class="experimentImportUpload__submit">
      <button
        @click="importFromJson"
        class="button button--primary"
        :disabled="!isFileValidExperiment"
      >
        Import
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import * as yaml from "js-yaml";

import DropZone from "@/components/_ui/DropZone.vue";

import { isStringSerializedJson } from "@/utils/strings";
import { checkExperiment } from "@/utils/experiments";
import { importExperiment } from "@/stores/experiments";

import type {
  ExperimentImportPayload,
  ExperimentDefinition,
  Contributions,
} from "@/types/experiments";

import ExperimentContributions from "@/components/experiments/ExperimentContributions.vue";

const message = ref<string>("No file selected");
const rawInput = ref<string>("");
const inputType = ref<string>("");
const experimentJson = ref<any>(null);
// const jsonString = ref<string>("");
const isFileReadable = ref<boolean>(false);
const isFileValidExperiment = ref<boolean>(false);
const dropZoneStatus = ref<string>("");

const areContributionsDisplayed = ref<boolean>(false);
const contributions = ref<Contributions>({
  availability: "none",
  latency: "none",
  security: "none",
  performance: "none",
});

const messageClassObject = computed(() => ({
  "experimentImportUpload__info--error":
    rawInput.value !== "" &&
    (!isFileReadable.value || !isFileValidExperiment.value),
  "experimentImportUpload__info--ok":
    rawInput.value !== "" && isFileReadable && isFileValidExperiment.value,
}));

const handleExperimentFile = (data: DataTransfer) => {
  inputType.value = "";
  let file: File | null = null;
  if (data.items) {
    // Use DataTransferItemList interface to access the file
    let item = data.items[0];
    // If dropped items aren't files, reject them
    if (item.kind === "file") {
      file = item.getAsFile();
      message.value = `Selected file: ${file!.name}`;
    }
  } else {
    // Use DataTransfer interface to access the file
    file = [...data.files][0];
    message.value = `Selected file: ${file!.name}`;
  }
  if (file !== null) {
    dropZoneStatus.value = "has-file";
    var reader = new FileReader();
    reader.onload = function () {
      let result = reader.result;
      if (result !== null) {
        rawInput.value = result as string;
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
          // const experimentJson = JSON.parse(experimentString.value);
          let check: string = checkExperiment(experimentJson.value);
          if (check === "") {
            isFileValidExperiment.value = true;
            if (
              (experimentJson as ExperimentDefinition).contributions ===
                undefined ||
              Object.entries(
                (experimentJson as ExperimentDefinition).contributions!
              ).length === 0
            ) {
              areContributionsDisplayed.value = true;
            }
          } else {
            isFileValidExperiment.value = false;
            message.value += ` is not a valid Chaos Toolkit experiment: ${check}.`;
            dropZoneStatus.value = "has-error";
          }
        }
      } else {
        isFileValidExperiment.value = false;
        isFileReadable.value = false;
        message.value += " is not valid JSON nor YAML";
        dropZoneStatus.value = "has-error";
      }
    };
    reader.readAsText(file);
  }
};

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
.experimentImportUpload {
  display: flex;
  flex-direction: column;
  flex-grow: 1;

  p {
    margin: 0;
  }

  &__info {
    margin: 0;

    color: var(--text-color-dim);
    font-size: 1.4rem;

    &--error {
      color: var(--statusColor-ko);
    }

    &--ok {
      color: var(--statusColor-ok);
    }
  }

  &__submit {
    margin-top: 2.4rem;
  }
}
</style>
