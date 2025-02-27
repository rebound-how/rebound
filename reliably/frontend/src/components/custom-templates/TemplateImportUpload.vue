<template>
  <div class="templateImportUpload">
    <DropZone @files-dropped="handleExperimentFile" :status="dropZoneStatus">
      <p>Drag and drop an experiment JSON file</p>
    </DropZone>
    <div class="templateImportUpload__type">
      <div v-if="inputType !== null">
        {{ inputType }}
      </div>
      <div v-if="inputFormat !== ''">
        {{ inputFormat }}
      </div>
    </div>
    <p
      class="templateImportUpload__info"
      :class="messageClassObject"
      v-html="message"
    ></p>
    <p
      class="templateImportUpload__info"
      :class="messageClassObject"
      v-html="message2"
    ></p>
  </div>
</template>

<script setup lang="ts">
import { toRefs, ref, computed, watch } from "vue";
import * as yaml from "js-yaml";

import DropZone from "@/components/_ui/DropZone.vue";

import { isStringSerializedJson } from "@/utils/strings";
import { checkExperiment } from "@/utils/experiments";
import { checkTemplate } from "@/utils/templates";

const props = defineProps<{
  modelValue: string;
}>();
const { modelValue } = toRefs(props);

const emit = defineEmits(["update:modelValue", "setInputType"]);

const message = ref<string>("No file selected");
const message2 = ref<string>("");
const rawInput = ref<string>("");
const inputFormat = ref<string>("");
const inputType = computed<string | null>(() => {
  if (isFileValidExperiment.value) {
    return "experiment";
  } else if (isFileValidTemplate.value) {
    return "template";
  } else {
    return null;
  }
});
const inputJson = ref<any>(null);
const isFileReadable = ref<boolean>(false);
const isFileValidExperiment = ref<boolean>(false);
const isFileValidTemplate = ref<boolean>(false);
const dropZoneStatus = ref<string>("");

const messageClassObject = computed(() => ({
  "templateImportUpload__info--error":
    rawInput.value !== "" &&
    ((!isFileValidExperiment.value && !isFileValidTemplate.value) ||
      !isFileReadable),
  "templateImportUpload__info--ok":
    rawInput.value !== "" &&
    (isFileValidExperiment.value || isFileValidTemplate.value) &&
    isFileReadable,
}));

const handleExperimentFile = (data: DataTransfer) => {
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
          inputJson.value = JSON.parse(rawInput.value);
          isFileReadable.value = true;
          inputFormat.value = "JSON";
        } else {
          try {
            inputJson.value = yaml.load(rawInput.value);
            isFileReadable.value = true;
            inputFormat.value = "YAML";
          } catch (e) {
            isFileReadable.value = false;
            message.value = "Input is not valid JSON nor YAML";
          }
        }

        if (isFileReadable.value) {
          let check: string = checkExperiment(inputJson.value);
          if (check === "") {
            isFileValidExperiment.value = true;
          } else {
            isFileValidExperiment.value = false;
            let check2 = checkTemplate(inputJson.value);
            if (check2 === "") {
              isFileValidTemplate.value = true;
              message.value = "";
              message2.value = "";
            } else {
              message.value += ` is not a valid Chaos Toolkit experiment: ${check}.`;
              message2.value = `It is also not a valid Reliably template: ${check2}.`;
              dropZoneStatus.value = "has-error";
            }
          }
        }
      } else {
        isFileValidExperiment.value = false;
        message.value += " is not valid JSON nor YAML";
        dropZoneStatus.value = "has-error";
      }
    };
    reader.readAsText(file);
  }
};

// Emit to parent when there's a change
watch([isFileValidExperiment, isFileValidTemplate], async () => {
  if (isFileValidExperiment.value || isFileValidTemplate.value) {
    emit("update:modelValue", JSON.stringify(inputJson.value));
    emit("setInputType", inputType.value);
  } else {
    emit("update:modelValue", "");
    emit("setInputType", "");
  }
});
</script>

<style lang="scss" scoped>
.templateImportUpload {
  position: relative;

  display: flex;
  flex-direction: column;
  flex-grow: 1;

  p {
    margin: 0;
  }

  &__type {
    position: absolute;
    top: 1.2rem;
    right: 1.2rem;

    display: flex;
    gap: var(--space-small);

    > div {
      padding: 0.3rem 0.6rem;

      background-color: var(--green-500);
      border-radius: var(--border-radius-s);

      color: white;
      font-size: 1.4rem;
      font-weight: 600;
      text-transform: uppercase;
    }
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
