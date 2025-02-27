<template>
  <li class="configurationField">
    <div class="inputWrapper">
      <label :for="`probe-tolerance-${suffix}-toleranceType`">
        Tolerance type <span class="required">Required</span>
      </label>
      <select
        v-model="type"
        :id="`probe-tolerance-${suffix}-toleranceType`"
        required
        @change="handleToleranceChange()"
      >
        <option v-for="t in TOLERANCE_TYPES" :key="t.value" :value="t.value">
          {{ t.label }}
        </option>
      </select>
    </div>
  </li>
  <li v-if="type === 'string'" class="configurationField">
    <div class="inputWrapper probeTolerance">
      <label :for="`probe-tolerance-${suffix}-tolerance`">
        Tolerance <span class="required">Required</span>
      </label>
      <input
        type="text"
        placeholder="Enter a <string> tolerance"
        required
        v-model="toleranceString"
        @change="handleToleranceChange()"
        :id="`probe-tolerance-${suffix}-tolerance`"
      />
    </div>
  </li>
  <li v-else-if="type === 'integer'">
    <div class="inputWrapper probeTolerance">
      <label :for="`probe-tolerance-${suffix}-tolerance`">
        Tolerance <span class="required">Required</span>
      </label>
      <input
        type="number"
        step="1"
        placeholder="Enter an <integer> tolerance"
        required
        v-model="toleranceInteger"
        @change="handleIntegerToleranceChange()"
        :id="`probe-tolerance-${suffix}-tolerance`"
      />
      <p class="inputWrapper__help">Float values will be rounded.</p>
    </div>
  </li>
  <li v-if="type === 'boolean'">
    <div class="inputWrapper">
      <label :id="`probe-tolerance-${suffix}-tolerance-label`">
        Tolerance
        <span class="required">Required</span>
      </label>
      <div
        class="inputWrapper inputWrapper--tick"
        :aria-labelledby="`probe-tolerance-${suffix}-tolerance-label`"
      >
        <div>
          <input
            type="radio"
            :value="true"
            v-model="toleranceBoolean"
            :id="`probe-tolerance-${suffix}-tolerance-true`"
            @change="handleToleranceChange()"
          />
          <label :for="`probe-tolerance-${suffix}-tolerance-true`">True</label>
        </div>
        <div>
          <input
            type="radio"
            :value="false"
            v-model="toleranceBoolean"
            :id="`probe-tolerance-${suffix}-tolerance-false`"
          />
          <label :for="`probe-tolerance-${suffix}-tolerance-false`"
            >False</label
          >
        </div>
      </div>
    </div>
  </li>
  <li v-else-if="type === 'range'">
    <div class="inputWrapper probeTolerance probeTolerance--range">
      <div class="inputWrapper">
        <label :for="`probe-tolerance-${suffix}-tolerance`">Min</label>
        <input
          type="number"
          step="1"
          v-model="toleranceRangeMin"
          @change="handleRangeToleranceChange()"
          :id="`probe-tolerance-${suffix}-tolerance`"
        />
      </div>
      <div class="inputWrapper">
        <label :for="`probe-tolerance-${suffix}-tolerance`">Max</label>
        <input
          type="number"
          step="1"
          v-model="toleranceRangeMax"
          @change="handleRangeToleranceChange()"
          :id="`probe-tolerance-${suffix}-tolerance`"
        />
      </div>
    </div>
  </li>
  <template v-if="type === 'jsonpath'">
    <li>
      <div class="inputWrapper probeTolerance">
        <label :for="`probe-tolerance-${suffix}-tolerance-jsonpath`">
          JSON Path <span class="required">Required</span>
        </label>
        <input
          type="text"
          placeholder="$.parent.list[0].key..."
          required
          v-model="toleranceJsonPath"
          @change="handleToleranceChange()"
          :id="`probe-tolerance-${suffix}-tolerance-jsonpath`"
        />
      </div>
    </li>
    <li>
      <div class="inputWrapper probeTolerance">
        <label :for="`probe-tolerance-${suffix}-tolerance-jsonpath-expect`">
          Expected value
        </label>
        <input
          type="text"
          placeholder=""
          v-model="toleranceJsonExpect"
          @change="handleToleranceChange()"
          :id="`probe-tolerance-${suffix}-tolerance-jsonpath-expect`"
        />
        <p class="inputWrapper__help">
          Reliably will compare each value matched by the JSON Path to this
          value. If this field is left empty, the tolerance succeeds if the JSON
          Path matched at least one item.
        </p>
      </div>
    </li>
  </template>
  <template v-if="type === 'regex'">
    <li>
      <div
        class="inputWrapper probeTolerance"
        :class="{ 'inputWrapper--error': !isRegExPatternValid }"
      >
        <label :for="`probe-tolerance-${suffix}-tolerance-regex-pattern`">
          RegEx pattern <span class="required">Required</span>
        </label>
        <input
          type="text"
          placeholder=""
          required
          v-model="toleranceRegExPattern"
          @change="handleToleranceChange()"
          :id="`probe-tolerance-${suffix}-tolerance-regex-pattern`"
        />
        <p v-if="!isRegExPatternValid" class="inputWrapper__help">
          This doesn't seem to be a valid RegEx pattern.
        </p>
      </div>
    </li>
    <li>
      <div class="inputWrapper probeTolerance">
        <label :for="`probe-tolerance-${suffix}-tolerance-regex-target`">
          RegEx target
        </label>
        <input
          type="text"
          placeholder="stdout..."
          v-model="toleranceRegExTarget"
          @change="handleToleranceChange()"
          :id="`probe-tolerance-${suffix}-tolerance-regex-target`"
        />
      </div>
    </li>
  </template>
  <li v-if="type === 'probe'">
    <div class="inputWrapper probeTolerance">
      <label :for="`probe-tolerance-${suffix}-tolerance-regex-target`">
        Select a probe <span class="required">Required</span>
      </label>
      <button
        class="probeSelector"
        :id="`probe-tolerance-${suffix}-tolerance-regex-target`"
        @click.prevent="openToleranceProbeSelector"
      >
        {{ probeSelectButtonLabel }}
        <ChevronDown />
      </button>
    </div>
    <ModalWindow
      v-if="isToleranceProbeSelectorDisplayed"
      :isUnlimited="true"
      :hasCloseButton="true"
      @close="closeToleranceProbeSelector"
    >
      <template #title>Select a tolerance probe</template>
      <template #content>
        <ActivitySelector
          to="hypothesis"
          @add-activity="addToleranceProbe"
          @close="closeToleranceProbeSelector"
        />
      </template>
    </ModalWindow>
  </li>
  <li v-if="type === 'probe' && toleranceProbeId !== '' && thisProbeTemplate">
    <form class="form probeToleranceForm">
      <h3>Probe Settings</h3>
      <ActivityFormStatus
        :array="toleranceProbeFieldsArray"
        :is-tolerance="true"
      />
      <ul class="configurationFields list-reset">
        <li
          v-for="(field, fieldIndex) in thisProbeTemplate!.manifest
            .spec.schema.configuration"
          class="configurationField"
          :key="`probe-tolerance-${suffix}-${fieldIndex}-${field.key}`"
        >
          <CreateExperimentField
            :configuration="field"
            :index="fieldIndex"
            :suffix="suffix"
            :force-internal="getProbeOriginalValue(field.key)"
            @update-configuration="updateToleranceProbeConfiguration"
          />
        </li>
        <li
          v-if="
            thisProbeTemplate!.manifest.spec.schema.configuration.length === 0
          "
        >
          <strong> This activity doesn't require any configuration. </strong>
        </li>
      </ul>
    </form>
  </li>
</template>

<script setup lang="ts">
import { toRefs, ref, computed, onMounted } from "vue";
import { useStore } from "@nanostores/vue";
import { cloneDeep } from "lodash-es";

import { getActivityId } from "@/utils/builder";

import type {
  Configuration,
  EnvConfiguration,
  ExperimentDefinition,
  Probe,
  PythonProvider,
} from "@/types/experiments";

import type { Template } from "@/types/templates";

import { template, fetchActionTemplate } from "@/stores/templates";

import JsonViewer from "@/components/_ui/JsonViewer.vue";
import ModalWindow from "@/components/_ui/ModalWindow.vue";
import CreateExperimentField from "@/components/custom-templates/CreateExperimentField.vue";
import ActivitySelector from "@/components/starters/ActivitySelector.vue";
import ActivityFormStatus from "@/components/starters/ActivityFormStatus.vue";
import ChevronDown from "@/components/svg/ChevronDown.vue";

const props = defineProps<{
  suffix: string;
  index: number;
  fieldStatusIndex: number; // Used to update the status of parent probe
  originalValue: { type: string; value: Probe["tolerance"] } | null;
}>();

const { suffix, index, fieldStatusIndex, originalValue } = toRefs(props);

const emit = defineEmits<{
  (
    e: "updateTolerance",
    index: number,
    type: string,
    value: Probe["tolerance"] | null,
    status: { index: number; status: boolean }
  ): void;
}>();

const type = ref<string>("string");
const toleranceString = ref<string>("");
const toleranceInteger = ref<number>(0);
const toleranceBoolean = ref<boolean>(true);
const toleranceRangeMin = ref<number>(0);
const toleranceRangeMax = ref<number>(0);
const toleranceJsonPath = ref<string>("");
const toleranceJsonExpect = ref<string>("");
const toleranceRegExPattern = ref<string>("");
const toleranceRegExTarget = ref<string>("");
const toleranceProbeId = ref<string>("");
const toleranceProbeDefinition = ref<Probe | null>(null);
const probeTemplate = useStore(template);
const thisProbeTemplate = ref<Template | null>(null);
const toleranceProbeFieldsArray = ref<boolean[]>([]);

let probeToleranceArgumentsHolder: any = null;

const isRegExPatternValid = computed<boolean>(() => {
  if (type.value !== "regex") {
    return true;
  } else {
    if (toleranceRegExPattern.value === "") {
      return true;
    } else {
      try {
        new RegExp(toleranceRegExPattern.value);
      } catch (e) {
        return false;
      }
      return true;
    }
  }
});

const tolerance = computed<Probe["tolerance"] | null>(() => {
  if (type.value === "string") {
    return toleranceString.value;
  } else if (type.value === "integer") {
    return toleranceInteger.value as number;
  } else if (type.value === "boolean") {
    return toleranceBoolean.value;
  } else if (type.value === "range") {
    return {
      type: "range",
      range: [toleranceRangeMin.value, toleranceRangeMax.value],
    };
  } else if (type.value === "jsonpath") {
    let t: {
      type: "jsonpath";
      path: string;
      expect?: string;
    } = {
      type: "jsonpath",
      path: toleranceJsonPath.value,
    };
    if (toleranceJsonExpect.value && toleranceJsonExpect.value !== "") {
      t.expect = toleranceJsonExpect.value;
    }
    return t;
  } else if (type.value === "regex") {
    return {
      type: "regex",
      pattern: toleranceRegExPattern.value,
      target: toleranceRegExTarget.value,
    };
  } else if (type.value === "probe") {
    return toleranceProbeDefinition.value;
  } else {
    return null;
  }
});

const TOLERANCE_TYPES = ref<
  {
    label: string;
    value: string;
  }[]
>([
  { label: "String", value: "string" },
  { label: "Integer", value: "integer" },
  { label: "Range", value: "range" },
  { label: "Boolean", value: "boolean" },
  { label: "Regex", value: "regex" },
  { label: "JSON Path", value: "jsonpath" },
  { label: "Probe", value: "probe" },
]);

function handleToleranceChange() {
  let status = false;
  if (type.value === "probe") {
    status =
      toleranceProbeId.value !== "" &&
      toleranceProbeFieldsArray.value.every(Boolean);
  } else {
    status = tolerance.value !== "";
  }
  const emittedStatus: { index: number; status: boolean } = {
    index: fieldStatusIndex.value,
    status: status,
  };
  emit(
    "updateTolerance",
    index.value,
    type.value,
    tolerance.value,
    emittedStatus
  );
}

function handleStringToleranceChange() {}

function handleIntegerToleranceChange() {
  if (toleranceInteger.value) {
    toleranceInteger.value = Math.round(toleranceInteger.value);
  } else {
    toleranceInteger.value = 0;
  }
  handleToleranceChange();
}

function handleRangeToleranceChange() {
  if (!toleranceRangeMin.value) {
    toleranceRangeMin.value = 0;
  }
  if (!toleranceRangeMax.value) {
    toleranceRangeMax.value = 1;
  }
  handleToleranceChange();
}

const probeSelectButtonLabel = computed<string>(() => {
  if (toleranceProbeId.value === "") {
    return "Select probe";
  } else if (thisProbeTemplate.value) {
    return `[${thisProbeTemplate.value.manifest.metadata.labels[0]}] [${thisProbeTemplate.value.manifest.metadata.labels[1]}] ${thisProbeTemplate.value.manifest.metadata.name}`;
  } else {
    return toleranceProbeId.value;
  }
});
const isToleranceProbeSelectorDisplayed = ref<boolean>(false);
function openToleranceProbeSelector() {
  isToleranceProbeSelectorDisplayed.value = true;
}
function closeToleranceProbeSelector() {
  isToleranceProbeSelectorDisplayed.value = false;
}
async function addToleranceProbe(id: string, to: string) {
  toleranceProbeId.value = id;
  await fetchActionTemplate(id);
  thisProbeTemplate.value = cloneDeep(probeTemplate.value);
  if (thisProbeTemplate.value) {
    const probeExperiment: ExperimentDefinition = JSON.parse(
      JSON.stringify(thisProbeTemplate.value.manifest.spec.template)
    );

    if (probeExperiment["steady-state-hypothesis"] === undefined) {
      probeExperiment["steady-state-hypothesis"] = {
        title: "Steady-State Hypothesis",
        probes: [],
      };
    }
    if (probeExperiment.method === undefined) {
      probeExperiment.method = [];
    }
    if (probeExperiment.rollbacks === undefined) {
      probeExperiment.rollbacks = [];
    }

    let probeType = "method";
    if (probeExperiment.method!.length === 0) {
      if (probeExperiment["steady-state-hypothesis"].probes!.length) {
        probeType = "hypothesis";
      }
    }

    // Insert tolerance
    if (probeType === "method") {
      toleranceProbeDefinition.value = probeExperiment.method[0] as Probe;
    } else if ((probeType = "hypothesis")) {
      toleranceProbeDefinition.value = probeExperiment[
        "steady-state-hypothesis"
      ].probes![0] as Probe;
    }

    // Reset fields status
    toleranceProbeFieldsArray.value = [];

    // Update argument value.
    Object.keys(
      toleranceProbeDefinition.value?.provider.arguments as {
        [key: string]: string;
      }
    ).forEach((a) => {
      const def = (probeExperiment.configuration![a] as EnvConfiguration)
        .default;
      if (def) {
        (
          toleranceProbeDefinition.value?.provider.arguments! as {
            [key: string]: string;
          }
        )[a] = def;
      } else {
        delete (
          toleranceProbeDefinition.value?.provider.arguments! as {
            [key: string]: string;
          }
        )[a];
      }
    });

    // Send this initial value
    handleToleranceChange();
  }
}
function updateToleranceProbeConfiguration(
  key: string,
  type: string,
  value:
    | string
    | boolean
    | number
    | string[]
    | Configuration
    | EnvConfiguration
    | null,
  index: number,
  newStatus: boolean,
  suffix: string | undefined
) {
  if (toleranceProbeDefinition.value?.provider.arguments) {
    if (value) {
      (
        toleranceProbeDefinition.value?.provider.arguments! as {
          [key: string]: any;
        }
      )[key] = value;
    } else {
      delete (
        toleranceProbeDefinition.value?.provider.arguments! as {
          [key: string]: any;
        }
      )[key];
    }
    toleranceProbeFieldsArray.value[index] = newStatus;
  }
  handleToleranceChange();
}

async function setOriginalValue() {
  if (originalValue.value) {
    type.value = originalValue.value.type;

    if (type.value === "string") {
      toleranceString.value = originalValue.value.value as string;
    } else if (type.value === "integer") {
      toleranceInteger.value = originalValue.value.value as number;
    } else if (type.value === "boolean") {
      toleranceBoolean.value = originalValue.value.value as boolean;
    } else if (type.value === "range") {
      const range = (
        originalValue.value.value! as { type: "range"; range: number[] }
      ).range;
      toleranceRangeMin.value = range[0];
      toleranceRangeMax.value = range[1];
    } else if (type.value === "jsonpath") {
      const val = originalValue.value.value! as {
        type: "jsonpath";
        path: string;
        expect?: string;
      };
      toleranceJsonPath.value = val.path;
      if (val.expect) {
        toleranceJsonExpect.value = val.expect;
      }
    } else if (type.value === "regex") {
      const val = originalValue.value.value! as {
        type: "regex";
        pattern: string;
        target: string;
      };
      toleranceRegExPattern.value = val.pattern;
      toleranceRegExTarget.value = val.target;
    } else if (type.value === "probe") {
      probeToleranceArgumentsHolder = cloneDeep(
        (originalValue.value.value as Probe).provider.arguments
      );
      const val = originalValue.value.value! as Probe;
      const id = getActivityId(val.provider as PythonProvider);
      await addToleranceProbe(id, "");
    }
  }
}

function getProbeOriginalValue(key: string) {
  if (probeToleranceArgumentsHolder[key]) {
    return probeToleranceArgumentsHolder[key];
  } else {
    return null;
  }
}

onMounted(async () => {
  await setOriginalValue();
  // This emits the tolerance status and update the parent probe status.
  handleToleranceChange();
});
</script>

<style lang="scss">
.probeTolerance {
  &--range {
    display: flex;
    gap: var(--space-small);

    > div.inputWrapper {
      margin-top: 0 !important;
    }
  }
}

.probeSelector {
  all: unset;

  position: relative;

  box-sizing: border-box;
  display: block;
  width: 100%;
  padding: 0.5em;

  background-color: var(--form-input-background);
  border: 0.1rem solid var(--form-input-border);
  border-radius: var(--border-radius-m);

  color: var(--text-color);
  font-family: var(--body-font);
  font-size: 1.6rem;

  &:focus {
    outline: 2px solid var(--form-input-focus);
  }

  svg {
    position: absolute;
    top: 50%;
    right: 0.4rem;

    height: 1.2rem;

    transform: translateY(-50%);
  }
}

.probeToleranceForm {
  position: relative;

  padding: var(--space-small);

  border: 0.1rem solid var(--grey-400);
  border-radius: var(--border-radius-small);

  h3 {
    margin-top: 0;

    font-size: 1.6rem;
  }

  > ul > li + li {
    margin-top: var(--space-medium);
  }
}
</style>
