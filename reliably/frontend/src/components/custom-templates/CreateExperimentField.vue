<template>
  <div
    class="createExperimentField inputWrapper inputWrapper--wide"
    :class="{ 'inputWrapper--error': hasError }"
  >
    <div v-if="configuration.type === 'boolean'">
      <label :id="`preview-${suffix}-${index}-label`">
        {{ configuration.title }}
        <span v-if="configuration.required" class="required">Required</span>
      </label>
      <div
        class="inputWrapper inputWrapper--tick"
        :aria-labelledby="`preview-${suffix}-${index}-label`"
      >
        <div>
          <input
            type="radio"
            value="true"
            v-model="internalValue"
            :id="`preview-${suffix}-${index}-true`"
            :required="configuration.required"
            @input="emitConfiguration"
          />
          <label :for="`preview-${suffix}-${index}-true`">True</label>
        </div>
        <div>
          <input
            type="radio"
            value="false"
            v-model="internalValue"
            :id="`preview-${suffix}-${index}-false`"
            @input="emitConfiguration"
          />
          <label :for="`preview-${suffix}-${index}-false`">False</label>
        </div>
      </div>
      <p v-if="configuration.help !== ''" class="inputWrapper__help">
        {{ configuration.help }}
      </p>
      <p v-if="hasError" class="inputWrapper__help">
        {{ errorMessage }}
      </p>
    </div>
    <div v-else-if="configuration.type === 'object'">
      <label :for="`preview-${suffix}-${index}`">
        {{ configuration.title }}
        <span v-if="configuration.required" class="required"> Required </span>
      </label>
      <textarea
        :id="`preview-${suffix}-${index}`"
        v-model="(internalValue as string)"
        :placeholder="configuration.placeholder"
        @input="emitConfiguration"
      />
      <p v-if="configuration.help !== ''" class="inputWrapper__help">
        {{ configuration.help }}
      </p>
      <p v-if="hasError" class="inputWrapper__help">
        {{ errorMessage }}
      </p>
    </div>
    <div v-else-if="configuration.type === 'integer' || configuration.type === 'float'">
      <label :for="`preview-${suffix}-${index}`">
        {{ configuration.title }}
        <span v-if="configuration.required" class="required"> Required </span>
      </label>
      <input
        type="text"
        :id="`preview-${suffix}-${index}`"
        :placeholder="configuration.placeholder"
        :required="configuration.required"
        v-model="internalValue"
        @input="emitConfiguration"
      />
      <p v-if="configuration.help !== ''" class="inputWrapper__help">
        {{ configuration.help }}
      </p>
      <p v-if="hasError" class="inputWrapper__help">
        {{ errorMessage }}
      </p>
    </div>
    <div v-else-if="configuration.type === 'string'">
      <FilterableSelect
        v-if="hasCandidates"
        :options="fieldCandidates"
        v-model="internalValue"
        :label="configuration.title"
        :is-required="true"
        :default-message="defaultValue"
        @emit-object="handleFieldChange"
      />
      <div v-else>
        <label :for="`preview-${suffix}-${index}`">
          {{ configuration.title }}
          <span v-if="configuration.required" class="required"> Required </span>
        </label>
        <input
          type="text"
          :id="`preview-${suffix}-${index}`"
          :placeholder="configuration.placeholder"
          :required="configuration.required"
          v-model="internalValue"
          @input="emitConfiguration"
        />
      </div>
      <p v-if="configuration.help !== ''" class="inputWrapper__help">
        {{ configuration.help }}
      </p>
      <p v-if="hasError" class="inputWrapper__help">
        {{ errorMessage }}
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { toRefs, ref, computed, watch, watchEffect, onMounted } from "vue";
import FilterableSelect from "@/components/_ui/FilterableSelect.vue";
import type { FieldsState } from "@/types/snapshots";

import type { FilterableSelectOption } from "@/types/ui-types";
import type { Configuration, EnvConfiguration } from "@/types/experiments";
import type { TemplateField } from "@/types/templates";
import { candidates, fetchCandidateValues } from "@/stores/snapshots";

const props = defineProps<{
  configuration: TemplateField;
  index: number;
  suffix?: string;
  forceInternal: string | boolean | number | object | null | undefined;
  previewMode?: boolean;
  state?: FieldsState[];
}>();
const { configuration, index, suffix, forceInternal, previewMode, state } = toRefs(props);

const emit = defineEmits<{
  (
    e: "updateConfiguration",
    key: string,
    type: string,
    value: string | boolean | number | string[] | Configuration | EnvConfiguration | null,
    index: number,
    newStatus: boolean,
    suffix: string | undefined
  ): void;
}>();

function handleFieldChange(f: FilterableSelectOption) {
  emitConfiguration();
}

function emitConfiguration() {
  if (previewMode === undefined || previewMode.value === false) {
    emit(
      "updateConfiguration",
      configuration.value.key,
      configuration.value.type,
      returnedValue.value,
      index.value,
      configuration.value.required
        ? returnedValue.value !== null &&
            returnedValue.value !== undefined &&
            returnedValue.value !== "" &&
            !hasError.value
        : true,
      suffix?.value
    );
  }
}

const internalValue = ref<string | null>("");
const hasError = ref<boolean>(false);
const errorMessage = ref<string>("");

const defaultValue = computed<string>(() => {
  if (configuration.value.type === "string") {
    return configuration.value.default;
  }

  return "";
})

const fieldCandidates = ref<FilterableSelectOption[]>([]);
const hasCandidates = computed<boolean>(() => {
  return fieldCandidates.value.length > 0;
});

function handleNoDefault() {
  if (configuration.value.no_default) {
    configuration.value.default = null;
  }
}

const returnedValue = computed<
  string | boolean | number | string[] | Configuration | EnvConfiguration | null
>(() => {
  hasError.value = false;
  errorMessage.value = "";
  if (configuration.value.type === "string") {
    return internalValue.value;
  } else if (
    configuration.value.type === "integer" ||
    configuration.value.type === "float"
  ) {
    if (internalValue.value === null || internalValue.value === "") {
      return null;
    } else {
      const n: number = parseFloat(internalValue.value);
      if (isNaN(n)) {
        hasError.value = true;
        errorMessage.value = "Value must be a number";
      } else {
        hasError.value = false;
        errorMessage.value = "";
        return n;
      }
    }
  } else if (configuration.value.type === "boolean") {
    if (internalValue.value === "false") {
      return false;
    } else if (internalValue.value === "true") {
      return true;
    } else {
      return null;
    }
  } else if (configuration.value.type === "object") {
    hasError.value = false;
    errorMessage.value = "";
    try {
      return JSON.parse(internalValue.value!);
    } catch (e) {
      hasError.value = true;
      errorMessage.value = "Object is not valid JSON";
    }
  }
});

const envVarType = computed<string | null>(() => {
  if (configuration.value.type === "string") {
    return "str";
  } else if (configuration.value.title === "number") {
    return "int";
  } else {
    return null;
  }
});

function refreshInternals() {
  const isForced: boolean =
    forceInternal !== undefined &&
    forceInternal.value !== null &&
    forceInternal.value !== undefined;
  const hasConfig: boolean =
    configuration.value.default !== null && configuration.value.default !== undefined;
  const type: string = configuration.value.type;

  if (type === "string") {
    if (isForced) {
      internalValue.value = forceInternal!.value as string;
    } else if (hasConfig) {
      internalValue.value = configuration.value.default as string;
    } else {
      internalValue.value = null;
    }
  } else if (type === "float" || type === "integer") {
    if (isForced) {
      internalValue.value = (forceInternal!.value as number).toString();
    } else if (hasConfig) {
      internalValue.value = (configuration.value.default as number).toString();
    } else {
      internalValue.value = null;
    }
  } else if (type === "boolean") {
    if (isForced) {
      if (forceInternal!.value !== "") {
        internalValue.value = forceInternal!.value ? "true" : "false";
      } else {
        internalValue.value = null;
      }
    } else if (hasConfig) {
      if (configuration.value.default !== "") {
        internalValue.value = configuration.value.default ? "true" : "false";
      } else {
        internalValue.value = null;
      }
    } else {
      internalValue.value = null;
    }
  } else {
    if (isForced) {
      if (forceInternal!.value !== "") {
        internalValue.value = JSON.stringify(forceInternal!.value, null, 2);
      } else {
        internalValue.value = null;
      }
    } else if (hasConfig) {
      if (configuration.value.default !== "") {
        internalValue.value = JSON.stringify(configuration.value.default, null, 2);
      } else {
        internalValue.value = null;
      }
    } else {
      internalValue.value = null;
    }
  }
}

async function getCandidates() {
  const s = getCurrentState();

  if (!(configuration.value.query === undefined) || configuration.value.query === null) {
    await fetchCandidateValues(configuration.value.query);

    const fc: FilterableSelectOption[] = [];
    candidates.value.candidates.forEach((c) => {
      fc.push({ label: c.label, val: c.val });
    });
    fieldCandidates.value = fc;
  }
}

function getCurrentState() {
  if (suffix.value === undefined) {
    return state.value;
  }

  if (state.value === undefined) {
    return [];
  }

  const s: FieldsState[] = [];
  const keySuffix = `_${suffix.value}`;

  for (const entry of state.value) {
    if (entry.key.endsWith(keySuffix)) {
      s.push({
        val: entry.val,
        key: entry.key.replace(keySuffix, "")
      });
    }
  }

  return s;
}

watch(
  configuration,
  () => {
    handleNoDefault();
    refreshInternals();
  },
  { deep: true },
);

watchEffect(
  async () => {
    state.value = props.state;
    await getCandidates();
  }
);

onMounted(async () => {
  handleNoDefault();
  refreshInternals();
  await getCandidates();
  emitConfiguration(); // Send internal value to override defaults
});
</script>

<style lang="scss" scoped>
.createExperimentField {
  textarea {
    height: 12rem;
  }
}
</style>
