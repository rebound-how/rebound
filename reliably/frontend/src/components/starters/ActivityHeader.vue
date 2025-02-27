<template>
  <div class="activityHeader">
    <div class="activityHeader__target handle">
      <ActivityLogo :target="activity.target" />
    </div>
    <div class="activityHeader__content">
      <div class="activityHeader__meta handle">
        <span :class="classType">
          {{ activity.type }}
        </span>
        <span class="activityHeader__type">{{ activity.category }}</span>
        <span
          v-if="isBackground"
          class="activityHeader__type activityHeader__type--background hasTooltip hasTooltip--top-center"
          aria-label="This activity will run in the background"
          label="This activity will run in the background"
        >
          Background
        </span>
      </div>
      <h2
        v-if="isEditing"
        class="activityHeader__title activityHeader__title--edit"
      >
        <input type="text" v-model="newTitle" /><button
          @click.prevent="cancelEdit"
          class="activityHeader__cancel button button--icon"
        >
          <span class="screen-reader-text">Cancel</span> <XIcon /></button
        ><button
          @click.prevent="saveEdit"
          class="activityHeader__save button button--icon"
        >
          <span class="screen-reader-text">Save</span><CheckIcon />
        </button>
      </h2>
      <h2 v-else class="activityHeader__title handle">
        <code v-html="breakableName(newTitle)"></code>&nbsp;<button
          v-if="isEditable"
          @click.prevent="openEdit"
          class="activityHeader__edit button button--icon"
        >
          <span class="screen-reader-text">Edit activity title</span>
          <EditIcon />
        </button>
      </h2>
      <div class="activityHeader__description handle">
        {{ activity.description }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { toRefs, computed, ref, onMounted } from "vue";
import { useStore } from "@nanostores/vue";

import { breakableName } from "@/utils/strings";

import { experiment, getActivityActualTitle } from "@/stores/experiments";

import type { Activity } from "@/types/ui-types";

import ActivityLogo from "@/components/starters/ActivityLogo.vue";

import EditIcon from "@/components/svg/EditIcon.vue";
import XIcon from "@/components/svg/XIcon.vue";
import CheckIcon from "@/components/svg/CheckIcon.vue";

const props = defineProps<{
  activity: Activity;
  isBackground?: boolean;
  isEditable?: boolean;
  editInfo?: { block: string; index: number };
}>();
const { activity, isBackground, isEditable, editInfo } = toRefs(props);

const emit = defineEmits<{
  (e: "update-title", title: string, block: string, index: number): void;
}>();

const classType = computed<string>(() => {
  return `activityHeader__type activityHeader__type--${activity.value.type}`;
});

const isEditing = ref<boolean>(false);
const newTitle = ref<string>("");

function openEdit() {
  isEditing.value = true;
}

function cancelEdit() {
  newTitle.value = activity.value.name;
  isEditing.value = false;
}

function saveEdit() {
  emit(
    "update-title",
    newTitle.value,
    editInfo!.value!.block,
    editInfo!.value!.index
  );
  isEditing.value = false;
}

function getActualTitle() {
  if (isEditable?.value) {
    const exp = useStore(experiment);
    if (exp.value) {
      let savedTitle: string | null = getActivityActualTitle(
        editInfo!.value!.block,
        editInfo!.value!.index
      );
      if (savedTitle && savedTitle !== "") {
        newTitle.value = savedTitle;
      }
    }
  }
}

onMounted(() => {
  newTitle.value = activity.value.name;
  getActualTitle();
});
</script>

<style lang="scss" scoped>
.activityHeader {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);

  .handle {
    cursor: grab;
  }

  &__target {
    display: flex;
    flex-direction: column;
    gap: var(--space-small);
    padding: var(--space-small);
  }

  &__meta {
    display: flex;
    gap: 0.6rem;
    padding-top: var(--space-small);
    padding-right: 8.4rem;
  }

  &__type {
    padding: 0.1rem 0.3rem;

    background-color: var(--grey-200);
    border-radius: var(--border-radius-s);

    font-size: 1.2rem;
    font-weight: 700;
    text-transform: uppercase;

    &--action {
      background-color: var(--pink-100);

      color: var(--pink-500);
    }

    &--probe,
    &--tolerance {
      background-color: var(--green-100);

      color: var(--green-500);
    }

    &--background {
      margin-left: auto;
      background-color: var(--blue-100);

      color: var(--blue-500);
    }
  }

  &__title {
    margin-top: 0;
    margin-bottom: 0;
    padding-right: var(--space-small);

    color: var(--text-color-bright);
    font-size: 2rem;
    text-decoration: none;

    code {
      padding: 0;

      background-color: transparent;
      border: none;
    }

    .activityHeader__edit,
    .activityHeader__cancel,
    .activityHeader__save {
      height: 2.2rem;
      width: 2.2rem;

      svg {
        height: 1.4rem;
      }
    }

    .activityHeader__edit {
      pointer-events: none;

      opacity: 0;
    }

    input {
      display: block;
      width: calc(100% - 5rem);
      padding: 0.2rem 0.5em;

      background-color: var(--form-input-background);
      border: 0.1rem solid var(--form-input-border);
      border-radius: var(--border-radius-m);

      color: var(--text-color);
      font-family: var(--body-font);
      font-size: 1.6rem;

      &:focus {
        outline: 2px solid var(--form-input-focus);
      }
    }

    .activityHeader__cancel {
      background-color: var(--red-100);

      color: var(--red-600);

      &:hover {
        background-color: var(--red-200);

        color: var(--red-800);
      }
    }
    .activityHeader__save {
      background-color: var(--green-200);

      color: var(--green-600);

      &:hover {
        background-color: var(--green-300);

        color: var(--green-800);
      }
    }

    &:hover {
      .activityHeader__edit {
        pointer-events: all;

        opacity: 1;
      }
    }

    &--edit {
      display: flex;
      gap: 0.6rem;
      padding-top: 0.5rem;
    }
  }

  &__description {
    padding: var(--space-small) var(--space-small) var(--space-small) 0;

    color: var(--text-color-dim);
    font-size: 1.4rem;
  }
}
</style>
