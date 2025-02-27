<template>
  <div class="contributions" :class="{ form: formWrap }">
    <div class="inputWrapper">
      <h3 v-if="importMode" class="contributions__title">
        Contributions are not defined
      </h3>
      <h3
        v-else
        class="contributions__title"
        :class="{ 'screen-reader-text': hideLabel }"
      >
        Contributions
      </h3>
      <p class="inputWrapper__help">
        Contributions describe the valuable system properties an experiment
        targets as well as how much they contributes to it.
        <a
          href="https://reliably.com/docs/guides/contributions/"
          target="_blank"
          rel="noopener norefere"
        >
          Read the documentation page.
        </a>
      </p>
      <p v-if="importMode" class="inputWrapper__help">
        You can add contributions now.
      </p>
      <div class="contributions__item">
        <label for="availabityValue">Availability</label>
        <select
          name="availabilityValue"
          id="availabilityValue"
          v-model="availabilityValue"
        >
          <option value="none">None</option>
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
        </select>
      </div>
      <div class="contributions__item">
        <label for="latencyValue">Latency</label>
        <select name="latencyValue" id="latencyValue" v-model="latencyValue">
          <option value="none">None</option>
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
        </select>
      </div>
      <div class="contributions__item">
        <label for="securityValue">Security</label>
        <select name="securityValue" id="securityValue" v-model="securityValue">
          <option value="none">None</option>
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
        </select>
      </div>
      <div class="contributions__item">
        <label for="errorsValue">Errors</label>
        <select name="errorsValue" id="errorsValue" v-model="errorsValue">
          <option value="none">None</option>
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
        </select>
      </div>
      <div
        v-for="(n, index) in customContributions"
        class="contributions__item"
        :key="index"
      >
        <input type="text" v-model="customContributions[index]" />
        <select
          name="errorsValue"
          id="errorsValue"
          v-model="customContributionsValues[index]"
        >
          <option value="none">None</option>
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
        </select>
        <button
          class="customContributionButton"
          :class="{ 'customContributionButton--hidden': hideRemoveCustom }"
          @click.prevent="removeCustom(index)"
        >
          <span class="screen-reader-text">Remove this contribution</span>
          <MinusIcon />
        </button>
        <button
          class="customContributionButton"
          v-if="index === customContributions.length - 1"
          @click.prevent="addCustom"
        >
          <span class="screen-reader-text">Add a contribution</span>
          <PlusIcon />
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { toRefs, ref, computed, watch, onMounted } from "vue";
import type { ContributionTypes, Contributions } from "@/types/experiments";
import PlusIcon from "@/components/svg/PlusIcon.vue";
import MinusIcon from "@/components/svg/MinusIcon.vue";

const props = defineProps<{
  modelValue: Contributions;
  importMode?: boolean;
  formWrap?: boolean;
  hideLabel?: boolean;
}>();
const { modelValue, importMode, formWrap } = toRefs(props);

const emit = defineEmits(["update:modelValue"]);

const availabilityValue = ref<ContributionTypes>("none");
const latencyValue = ref<ContributionTypes>("none");
const securityValue = ref<ContributionTypes>("none");
const errorsValue = ref<ContributionTypes>("none");

const customContributions = ref<string[]>([""]);
const customContributionsValues = ref<ContributionTypes[]>(["none"]);
const hideRemoveCustom = computed<boolean>(() => {
  return customContributions.value.length < 2;
});

const addCustom = () => {
  customContributions.value.push("");
  customContributionsValues.value.push("none");
};

const removeCustom = (index: number) => {
  customContributions.value.splice(index, 1);
  customContributionsValues.value.splice(index, 1);
};

const contributionsObject = computed<Contributions>(() => {
  let obj: Contributions = {
    availability: availabilityValue.value,
    latency: latencyValue.value,
    security: securityValue.value,
    errors: errorsValue.value,
  };

  for (const [index, value] of customContributions.value.entries()) {
    if (value !== "") {
      obj[value] = customContributionsValues.value[index];
    }
  }

  return obj;
});

// Emit to parent when there's a change
watch(contributionsObject, async () => {
  emit("update:modelValue", contributionsObject.value);
});

function initContributions() {
  availabilityValue.value = modelValue.value.availability;
  latencyValue.value = modelValue.value.latency;
  securityValue.value = modelValue.value.security;
  errorsValue.value = modelValue.value.errors;

  const keys = Object.keys(modelValue.value);
  keys.forEach((key) => {
    if (!["availability", "latency", "security", "errors"].includes(key)) {
      const value = modelValue.value[key];
      if (["none", "low", "medium", "high"].includes(value)) {
        customContributions.value.unshift(key);
        customContributionsValues.value.unshift(value);
      }
    }
  });
}

onMounted(() => {
  initContributions();
});
</script>

<style lang="scss" scoped>
.contributions {
  margin-top: var(--space-small);
  margin-bottom: var(--space-small);

  &__title {
    margin-bottom: 0.6rem;

    font-size: 1.6rem;
    font-weight: 400;
  }

  p + p {
    margin-top: var(--space-small);
  }

  &__item {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    margin-top: var(--space-small);

    label,
    input[type="text"] {
      margin-bottom: 0;
      width: 14rem;
    }

    select {
      width: 14rem;
    }

    .customContributionButton {
      display: flex;
      align-items: center;
      justify-content: center;
      height: 2.6rem;
      width: 2.6rem;
      margin-left: 0.6rem;
      // padding: 0;

      background-color: var(--grey-300);
      border: none;
      border-radius: 50%;
      cursor: pointer;

      svg {
        height: 1.8rem;
      }

      &:hover {
        background-color: var(--grey-400);
      }

      &--hidden {
        pointer-events: none;
        visibility: hidden;
      }
    }
  }
}
</style>
