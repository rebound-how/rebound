<template>
  <div class="templateImportPaste">
    <form class="form">
      <fieldset>
        <div
          class="inputWrapper"
          :class="{ 'inputWrapper--error': errorState }"
        >
          <label class="screen-reader-text" for="jsonInput">
            Paste the content of your experiment JSON file
          </label>
          <textarea
            name="jsonInput"
            id="jsonInput"
            wrap="off"
            v-model="rawInput"
            @keyup="checkInputIsValid"
          ></textarea>
          <div class="templateImportPaste__type">
            <div v-if="inputType !== null">
              {{ inputType }}
            </div>
            <div v-if="inputFormat !== ''">
              {{ inputFormat }}
            </div>
          </div>
          <p
            class="inputWrapper__help experimentImportPaste__info"
            v-html="message"
          ></p>
          <p
            class="inputWrapper__help experimentImportPaste__info"
            v-html="message2"
          ></p>
        </div>
      </fieldset>
    </form>
  </div>
</template>

<script setup lang="ts">
import { toRefs, ref, computed, watch } from "vue";
import * as yaml from "js-yaml";
import { isStringSerializedJson } from "@/utils/strings";
import { checkExperiment } from "@/utils/experiments";
import { checkTemplate } from "@/utils/templates";

const props = defineProps<{
  modelValue: string;
}>();
const { modelValue } = toRefs(props);

const emit = defineEmits(["update:modelValue", "setInputType"]);

const rawInput = ref<string>("");
const inputFormat = ref<string>(""); // JSON | YAML
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
const errorState = computed<boolean>(() => {
  return (
    rawInput.value !== "" &&
    (!isFileReadable.value || !isFileValidExperiment.value)
  );
});
const message = ref<string>("");
const message2 = ref<string>("");

let timeout: ReturnType<typeof setTimeout> | null = null;
const checkInputIsValid = () => {
  // clear timeout variable
  if (timeout !== null) {
    clearTimeout(timeout);
  }

  timeout = setTimeout(function () {
    if (rawInput.value !== "") {
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
        let check = checkExperiment(inputJson.value);
        if (check === "") {
          isFileValidExperiment.value = true;
          message.value = "";
          message2.value = "";
        } else {
          isFileValidExperiment.value = false;
          let check2 = checkTemplate(inputJson.value);
          if (check2 === "") {
            isFileValidTemplate.value = true;
            message.value = "";
            message2.value = "";
          } else {
            message.value = `Input is not a valid Chaos Toolkit experiment: ${check}.`;
            message2.value = `Input is not a valid Reliably template: ${check2}.`;
          }
        }
      }
    } else {
      isFileValidExperiment.value = false;
      message.value = "Input is not valid";
    }
  }, 500);
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
.templateImportPaste {
  position: relative;

  .inputWrapper {
    max-width: unset;

    textarea {
      height: 20rem;
      // resize: none;
      margin-top: 0;
    }
  }

  &__info {
    min-height: 2.1rem;
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
}
</style>
