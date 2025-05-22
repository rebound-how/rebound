<template>
  <form
    class="scenarioParameter"
    :class="{
      'scenarioParameter--inactive': !isActive,
      'scenarioParameter--error': isJSONInvalid,
    }"
    @click.prevent="reactivate"
    @keyup.enter.exact.prevent="submitParameter"
  >
    <div class="scenarioParameter__inputWrapper">
      <label
        class="scenarioParameterLabel"
        :for="`scenarioParameterInput-${itemIndex}-${paramIndex}`"
      >
        <span class="scenarioParameterLabel__title">{{
          parameter.parameter.title
        }}</span>
        for
        <span
          :class="`scenarioParameterLabel__type scenarioParameterLabel__type--${parameter.item_type}`"
          >{{ parameter.item_type }}</span
        >&nbsp;
        <span
          class="scenarioParameterLabel__item"
          v-html="breakableName(parameter.item_name)"
        ></span>
      </label>
      <div class="promptWrapper">
        <textarea
          class="scenarioParameter__input"
          :name="`scenarioParameterInput-${itemIndex}-${paramIndex}`"
          :id="`scenarioParameterInput-${itemIndex}-${paramIndex}`"
          v-model="value"
          :style="`height: ${textareaHeight}px`"
          ref="input"
          data-enable-grammarly="false"
          @keydown.enter.exact.prevent
        />
        <button
          class="promptButton"
          @click.prevent="submitParameter"
          ref="questionButton"
        >
          ↵
          <span class="screen-reader-text">Submit parameter</span>
        </button>
      </div>
      <p v-if="isActive && filteredHistory.length" class="AiDialogItem__help">
        Values used for similarly named parameters:
        <button
          v-for="item in filteredHistory"
          :key="item"
          @click.prevent="setValue(item)"
          class="scenarioParameter__historyItem"
        >
          {{ trimString(item, 64) }}
        </button>
      </p>
      <p
        class="AiDialogItem__help"
        v-if="parameter.parameter.type === 'boolean'"
      >
        Expected parameter type: <strong>boolean</strong>. Type 'true' or
        'false'. All other values will be considered as a boolean 'false'.
      </p>
      <p
        class="AiDialogItem__help"
        v-else-if="parameter.parameter.type === 'object'"
      >
        Expected parameter type: <strong>JSON object or array</strong>. Use
        shift + enter for a new line. Enter to submit.
      </p>
      <p class="AiDialogItem__help" v-else>
        Expected parameter type: <strong>{{ parameter.parameter.type }}</strong>
      </p>
      <p
        class="AiDialogItem__help AiDialogItem__help--error"
        v-if="isJSONInvalid"
      >
        Input is not valid JSON.
      </p>
    </div>
  </form>
</template>

<script setup lang="ts">
import { toRefs, ref, computed, watch, onMounted, nextTick } from "vue";

import type { UiScenarioParameter } from "@/types/scenarios";

import {
  breakableName,
  isStringSerializedJson,
  trimString,
} from "@/utils/strings";

const props = defineProps<{
  parameter: UiScenarioParameter;
  itemIndex: number;
  paramIndex: number;
  history?:
    | {
        value: string | number | boolean | object;
        type: "string" | "integer" | "float" | "number" | "boolean" | "object";
      }[]
    | null
    | undefined;
}>();

const { parameter, itemIndex, paramIndex, history } = toRefs(props);

const emit = defineEmits<{
  (
    e: "update-parameter",
    value: string | number | boolean | object,
    key: string,
    itemIndex: number,
    paramIndex: number,
    reactivated?: boolean
  ): void;
}>();

const isActive = ref<boolean>(false);
const wasReactivated = ref<boolean>(false);
const value = ref<string>(typedToString(parameter.value.parameter.default));

function setValue(v: string) {
  value.value = v;
  input.value?.focus();
  nextTick(() => {
    updateTextareaHeight();
  });
}

const filteredHistory = computed<string[]>(() => {
  const filtered: string[] = [];
  if (history && history.value && history.value.length) {
    history.value.forEach((h) => {
      if (h.type === parameter.value.parameter.type) {
        filtered.push(typedToString(h.value));
      }
    });
  }
  return filtered;
});

const isJSONInvalid = ref<boolean>(false);

function submitParameter() {
  if (parameter.value.parameter.type === "object") {
    isJSONInvalid.value = !isStringSerializedJson(value.value);
  }
  if (isJSONInvalid.value === false) {
    if (wasReactivated.value) {
      emit(
        "update-parameter",
        stringToTyped(value.value),
        parameter.value.parameter.key,
        itemIndex.value,
        paramIndex.value,
        true
      );
    } else {
      emit(
        "update-parameter",
        stringToTyped(value.value),
        parameter.value.parameter.key,
        itemIndex.value,
        paramIndex.value
      );
    }
    input.value!.setAttribute("disabled", "");
    isActive.value = false;
  }
}

function reactivate() {
  if (!isActive.value) {
    isActive.value = true;
    wasReactivated.value = true;
    input.value!.removeAttribute("disabled");
  }
}

// Utils
const input = ref<HTMLElement | null>(null);
const textareaHeight = ref<number>(0);
function updateTextareaHeight() {
  if (input.value) {
    input.value.style.height = "5px";
    input.value.style.height = input.value.scrollHeight + "px";
  }
}

function stringToTyped(value: string): string | number | boolean | object {
  const t = parameter.value.parameter.type;
  if (t === "string") {
    return value;
  } else if (t === "boolean") {
    if (value === "true") {
      return true;
    } else if (value === "false") {
      return false;
    } else {
      return false;
    }
  } else if (t === "float" || t === "number") {
    return parseFloat(value);
  } else if (t === "integer") {
    return parseInt(value);
  } else if (t === "object") {
    return JSON.parse(value);
  } else {
    return value;
  }
}

function typedToString(value: string | number | boolean | object): string {
  const t = parameter.value.parameter.type;
  if (t === "string") {
    return value as string;
  } else if (t === "boolean") {
    if (value === true) {
      return "true";
    } else if (value === false) {
      return "false";
    } else {
      return "false";
    }
  } else if (t === "float" || t === "number" || t === "integer") {
    return value.toString();
  } else if (t === "object") {
    return JSON.stringify(value);
  } else {
    return value.toString();
  }
}

watch(value, () => {
  updateTextareaHeight();
});

onMounted(() => {
  isActive.value = true;
  input.value?.focus();
});
</script>

<style lang="scss" scoped>
.scenarioParameter {
  position: relative;

  &--inactive {
    cursor: pointer;
    opacity: 0.5;

    * {
      pointer-events: none;
    }

    &:hover {
      opacity: 1;
    }
  }

  &--error {
    textarea {
      outline: 0.3rem solid var(--statusColor-ko);
      outline-offset: 0.2rem;
    }
  }

  .scenarioParameterLabel {
    color: var(--text-color-dim);

    &__title {
      color: var(--text-color);
    }

    &__type {
      padding: 0.1rem 0.3rem;

      background-color: var(--grey-200);
      border-radius: var(--border-radius-s);

      font-size: 1.8rem;
      font-weight: 700;
      text-transform: uppercase;

      &--action {
        background-color: var(--pink-100);

        color: var(--pink-500);
      }

      &--probe {
        background-color: var(--green-100);

        color: var(--green-500);
      }
    }

    &__item {
      color: var(--inline-code-color);
      font-family: monospace;
      font-size: 2rem;
      font-weight: 700;
    }
  }

  .promptWrapper {
    position: relative;

    display: flex;
  }

  .promptButton {
    all: unset;

    position: absolute;
    right: 0.7rem;
    bottom: 0.8rem;

    box-sizing: border-box;
    display: block;
    height: 3.4rem;
    width: 3.4rem;
    padding: 0.6rem 0.6rem 0.3rem;

    border: 0.1rem solid var(--grey-400);
    border-radius: var(--border-radius-s);
    background-color: var(--grey-200);
    cursor: pointer;

    color: var(--text-color);
    font-size: 1.6rem;
    text-align: center;

    &:hover {
      background-color: var(--green-400);
      border-color: var(--green-500);

      color: var(--green-900);
    }

    &--hidden {
      position: absolute;

      height: 0;
      width: 0;

      opacity: 0;
    }

    &:focus {
      outline: 0.2rem solid red;
    }
  }

  &__input {
    overflow: hidden;
    padding: 0.6rem 4.6rem 0.6rem 1rem;
    min-height: 4.8rem;
    width: 100%;

    background-color: var(--grey-100);
    border: 0.1rem solid var(--grey-400);
    border-radius: var(--border-radius-s);
    resize: none;

    font-family: var(--body-font);
    font-size: 2.4rem;
    line-height: 1.5;
  }

  &__historyItem {
    all: unset;

    cursor: pointer;

    color: var(--blue-500);

    &:hover {
      text-decoration: underline;
    }

    &:not(:last-child) {
      &::after {
        content: ", ";

        display: inline-block;

        color: var(--text-color-dim);
        text-decoration: none !important;
        white-space: pre;
      }
    }
  }
}
</style>
