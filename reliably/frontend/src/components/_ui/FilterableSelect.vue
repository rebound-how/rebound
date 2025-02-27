<template>
  <div class="filterableSelect">
    <label :for="`listbox-${id}`" :id="`label-${id}`">
      {{ label }} <span v-if="isRequired" class="required">Required</span>
    </label>
    <div class="filterableSelect__wrapper">
      <input
        v-if="isListDisplayed"
        class="filterableSelect__filter"
        v-model="optionFilter"
        placeholder="Type to filter"
        ref="filter"
        :aria-activedescendant="`listbox-${id}`"
        @keyup.esc="hideList"
        @keydown.up="handleKeyUp"
        @keydown.down="handleKeyDown"
        @keyup.tab.prevent="setValueByIndex"
        @keyup.enter.prevent="setValueByIndex"
        @keydown.tab.prevent
      />
      <div
        v-else
        :aria-controls="`select-${id}`"
        aria-expanded="false"
        aria-haspop="listbox"
        class="filterableSelect__chosen"
        aria-activedescendant=""
        @click.prevent="displayList"
        @keydown.up="handleKeyUp"
        @keydown.down="handleKeyDown"
        ref="chosen"
        tabindex="0"
      >
        {{ chosenText }}
      </div>
      <ul
        role="listbox"
        :aria-labelledby="`label-${id}`"
        :id="`listbox-${id}`"
        class="list-reset"
        :class="listClass"
        ref="list"
        @change="emitUpdate"
      >
        <li
          v-if="allowEmpty"
          role="option"
          aria-selected="false"
          class="filterableSelect__option"
          value=""
          @click.prevent="setValue({ label: 'None', val: '' })"
        >
          None
        </li>
        <li
          role="option"
          aria-selected="false"
          class="filterableSelect__option"
          v-for="opt in filteredOptions"
          :key="opt.val"
          :value="opt.val"
          @click.prevent="setValue(opt)"
        >
          {{ opt.label }}
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
import { toRefs, ref, computed, onMounted, nextTick } from "vue";
import { onClickOutside } from "@vueuse/core";
import { v4 as uuid } from "uuid";

import type { FilterableSelectOption } from "@/types/ui-types";

const props = defineProps<{
  modelValue: string | null;
  label: string;
  options: FilterableSelectOption[];
  isRequired?: boolean;
  allowEmpty?: boolean;
  defaultMessage?: string;
}>();

const { label, options, isRequired, allowEmpty, defaultMessage, modelValue } =
  toRefs(props);

const emit = defineEmits<{
  (e: "update:modelValue", value: string | null): void;
  (e: "emit-object", object: FilterableSelectOption): void;
}>();

function emitUpdate() {
  emit("update:modelValue", chosenVal.value);
}

const id = ref<string>("");
const filter = ref<HTMLElement | null>(null);
const chosen = ref<HTMLElement | null>(null);
const list = ref<HTMLElement | null>(null);

const isListDisplayed = ref<boolean>(false);
const optionFilter = ref<string>("");
const chosenText = ref<string>("");
const chosenVal = ref<string>("");

const elements = ref<HTMLCollection>();
const activeElementIndex = ref<number | null>(null);

const filteredOptions = computed<FilterableSelectOption[]>(() => {
  return options.value.filter((opt) => {
    return opt.label
      .toLowerCase()
      .match(optionFilter.value.trim().toLowerCase());
  });
});

function displayList() {
  isListDisplayed.value = true;
  let i: number = 0;
  for (const el of elements.value!) {
    const v: string | null = el.getAttribute("value");
    if (v === chosenVal.value) {
      el.classList.add("filterableSelect__option--current");
      el.setAttribute("aria-select", "true");
      activeElementIndex.value = i;
    } else {
      el.classList.remove("filterableSelect__option--current");
      el.setAttribute("aria-select", "false");
    }
    i++;
  }
  nextTick(() => {
    filter.value!.focus();
  });
}

function hideList() {
  isListDisplayed.value = false;
  nextTick(() => {
    chosen.value?.focus();
  });
  resetFilter();
}

function hideListWithoutFocus() {
  isListDisplayed.value = false;
  resetFilter();
}

const listClass = computed<string>(() => {
  if (isListDisplayed.value) {
    return "filterableSelect__list filterableSelect__list--visible";
  } else {
    return "filterableSelect__list";
  }
});

function setValue(opt: FilterableSelectOption, preventFocus?: boolean) {
  chosenText.value = opt.label;
  chosenVal.value = opt.val;
  emitUpdate();
  emit("emit-object", opt);
  if (preventFocus) {
    hideListWithoutFocus();
  } else {
    hideList();
  }
  resetFilter();
}

function resetFilter() {
  optionFilter.value = "";
}

function handleKeyUp() {
  if (!isListDisplayed.value) {
    displayList();
  }
  if (activeElementIndex.value === null) {
    activeElementIndex.value = 0;
  } else if (activeElementIndex.value > 0) {
    activeElementIndex.value--;
  }
  setActiveElement(activeElementIndex.value);
}

function handleKeyDown() {
  if (!isListDisplayed.value) {
    displayList();
  }
  if (activeElementIndex.value === null) {
    activeElementIndex.value = 0;
  } else {
    if (activeElementIndex.value < filteredOptions.value.length - 1) {
      activeElementIndex.value++;
    }
  }
  setActiveElement(activeElementIndex.value);
}

function setActiveElement(index: number) {
  let i: number = 0;
  for (const el of elements.value!) {
    if (i === index) {
      el.classList.add("filterableSelect__option--current");
      el.setAttribute("aria-select", "true");
    } else {
      el.classList.remove("filterableSelect__option--current");
      el.setAttribute("aria-select", "false");
    }
    i++;
  }
}

function setValueByIndex() {
  if (activeElementIndex.value !== null) {
    const opt = filteredOptions.value[activeElementIndex.value];
    setValue(opt);
  }
}

onClickOutside(list, () => {
  if (isListDisplayed.value) {
    hideList();
  }
});

onMounted(() => {
  id.value = uuid();
  elements.value = list.value!.children;
  if (defaultMessage && defaultMessage.value && defaultMessage.value !== "") {
    chosenText.value = defaultMessage.value;
  }
  if (allowEmpty?.value) {
    setValue({ label: "None", val: "" }, true);
    activeElementIndex.value = 0;
    setActiveElement(activeElementIndex.value);
  }
});
</script>

<style lang="scss" scoped>
.filterableSelect {
  &__wrapper {
    position: relative;
  }

  &__list {
    position: absolute;
    top: calc(100% + 0.3rem);
    left: 0;
    z-index: 99;

    display: none;
    max-height: calc(100vh - 6rem);
    overflow-y: auto;
    width: 100%;

    background-color: var(--form-input-background);
    border: 0.1rem solid var(--form-input-border);
    border-radius: var(--border-radius-m);
    box-shadow: 0 0.3em 0.9em rgba(0, 0, 0, 0.2);

    &--visible {
      display: block;
    }
  }

  &__option {
    margin-bottom: 0;
    padding: 0.6rem;

    cursor: default;

    &:hover {
      background-color: var(--pink-100);
    }

    &--current {
      background-color: var(--pink-100);
      outline: 0.2rem solid var(--pink-500);
      outline-offset: -0.2rem;
    }
  }

  &__chosen {
    display: block;
    height: 3.6rem;
    width: 100%;
    padding: 0.5em;

    background-color: var(--form-input-background);
    border: 0.1rem solid var(--form-input-border);
    border-radius: var(--border-radius-m);

    color: var(--text-color);
    font-family: var(--body-font);
    font-size: 1.6rem;
    line-height: 1;

    &:focus {
      outline: 2px solid var(--form-input-focus);
    }
  }
}
</style>
