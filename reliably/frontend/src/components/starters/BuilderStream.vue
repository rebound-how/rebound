<template>
  <div v-if="stream.length === 0" class="activityWrapper">
    <button
      v-if="name === 'warmup'"
      @click.prevent="addActivity('warmup', 'before', 0)"
      class="activitySettings activitySettings--empty"
    >
      Your warm up section is currently empty.<br />
      <span>Add probes and actions</span>
    </button>
    <button
      v-else-if="name === 'method'"
      @click.prevent="addActivity('method', 'before', 0)"
      class="activitySettings activitySettings--empty"
    >
      Your turbulence section is currently empty.<br />
      <span>Add probes and actions</span>
    </button>
    <button
      v-else-if="name === 'hypothesis'"
      @click.prevent="addActivity('hypothesis', 'before', 0)"
      class="activitySettings activitySettings--empty"
    >
      Your verification section is currently empty.<br />
      <span>Add probes</span>
    </button>
    <button
      v-else-if="name === 'rollbacks'"
      @click.prevent="addActivity('rollbacks', 'before', 0)"
      class="activitySettings activitySettings--empty"
    >
      Your rollbacks are currently empty.<br />
      <span>Add actions</span>
    </button>
  </div>
  <draggable
    class="streamDraggable"
    :list="stream"
    handle=".handle"
    group="activities"
    item-key="suffix"
    @change="handleDragEvent($event, name)"
    @start="onDragStart"
    @end="onDragEnd"
  >
    <template #item="{ element, index }">
      <div class="activityWrapper">
        <details :ref="addActivityRef" class="activitySettings" open>
          <summary class="activitySettings__header">
            <ActivityFormStatus :array="element.fieldsStatus" />
            <ActivityHeader
              :activity="getActivityMeta(element)"
              :isBackground="element.background"
              :is-editable="true"
              :edit-info="{ block: name, index: index }"
              @update-title="updateActivityTitle"
            />
            <span class="activitySettings__chevron"><ChevronDown /></span>
            <button
              v-if="index === 0"
              class="activitySettings__add activitySettings__add--before hasTooltip hasTooltip--top-center"
              label="Add before"
              aria-label="Add before"
              @click.prevent="addActivity(name, 'before', index)"
            >
              <PlusIcon />
              <span class="screen-reader-text">Add before</span>
            </button>
            <button
              class="activitySettings__add activitySettings__add--after hasTooltip hasTooltip--top-center"
              label="Add after"
              aria-label="Add after"
              @click.prevent="addActivity(name, 'after', index)"
            >
              <PlusIcon />
              <span class="screen-reader-text">Add after</span>
            </button>
            <button
              class="activitySettings__remove button button--icon hasTooltip hasTooltip--bottom-center"
              label="Remove activity"
              aria-label="Remove activity"
              @click.prevent="removeActivity(name, index)"
            >
              <TrashIcon />
            </button>
            <ActivityLink :index="index" :total="stream.length" />
          </summary>
          <form class="form">
            <ul class="configurationFields list-reset">
              <li
                v-for="(field, fieldIndex) in element.template.manifest.spec
                  .schema.configuration"
                class="configurationField"
                :key="`m-${element.suffix}-${fieldIndex}`"
              >
                <CreateExperimentField
                  :configuration="field"
                  :index="fieldIndex"
                  :suffix="element.suffix"
                  :key="timestamp"
                  :force-internal="forceInternal(`${(field as TemplateField).key}_${element.suffix}`)"
                  :state="state"
                  @update-configuration="updateConfiguration"
                />
              </li>
              <li
                v-if="
                  element.template.manifest.spec.schema.configuration.length ===
                  0
                "
              >
                <strong>
                  This activity doesn't require any configuration.
                </strong>
              </li>
              <ProbeTolerance
                v-if="name === 'hypothesis'"
                :suffix="element.suffix"
                :index="index"
                :field-status-index="
                  element.template.manifest.spec.schema.configuration.length
                "
                :originalValue="getToleranceObject(element)"
                @update-tolerance="emitTolerance"
              />
              <li class="configurationField">
                <div class="inputWrapper inputWrapper--tick">
                  <div>
                    <input
                      type="checkbox"
                      value="true"
                      v-model="stream[index].background"
                      @change="handleBackgroundChange(name, index)"
                      :id="`preview-${element.suffix}-background`"
                    />
                    <label :for="`preview-${element.suffix}-background`">
                      Run in the background
                    </label>
                  </div>
                </div>
              </li>
            </ul>
          </form>
        </details>
      </div>
    </template>
  </draggable>
</template>

<script setup lang="ts">
import { toRefs, ref } from "vue";
import { useStore } from "@nanostores/vue";
import draggable from "vuedraggable";

import {
  configurationHolder,
  updateConfigurationHolder,
} from "@/stores/builder";

import { getActivityMeta } from "@/utils/builder";

import type {
  Activity,
  TemplateActivity,
  ActivityBlock,
  DraggableChangeEvent,
} from "@/types/ui-types";

import type {
  Configuration,
  EnvConfiguration,
  Probe,
} from "@/types/experiments";
import type { Template, TemplateField } from "@/types/templates";

import ActivityFormStatus from "@/components/starters/ActivityFormStatus.vue";
import ActivityHeader from "@/components/starters/ActivityHeader.vue";
import ActivityLink from "@/components/starters/ActivityLink.vue";
import ProbeTolerance from "@/components/starters/ProbeTolerance.vue";

import CreateExperimentField from "@/components/custom-templates/CreateExperimentField.vue";

import ChevronDown from "@/components/svg/ChevronDown.vue";
import PlusIcon from "@/components/svg/PlusIcon.vue";
import TrashIcon from "@/components/svg/TrashIcon.vue";
import type { FieldsState } from "@/types/snapshots";

const props = defineProps<{
  stream: TemplateActivity[];
  name: "hypothesis" | "warmup" | "method" | "rollbacks";
  activityRefArray: InstanceType<typeof HTMLDetailsElement>[];
  template: Template;
  state?: FieldsState[];
}>();

const { stream, name, activityRefArray, state } = toRefs(props);

const emit = defineEmits<{
  (e: "add-activity", to: string, where: string, index: number): void;
  (e: "remove-activity", from: string, index: number): void;
  (
    e: "update-activity-title",
    title: string,
    block: string,
    index: number
  ): void;
  (e: "handle-drag", event: DraggableChangeEvent, block: ActivityBlock): void;
  (e: "drag-start"): void;
  (
    e: "update-configuration",
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
  ): void;
  (e: "background-change", where: string, index: number): void;
  (
    e: "update-tolerance",
    index: number,
    type: string,
    value: Probe["tolerance"] | null,
    status: { index: number; status: boolean }
  ): void;
}>();

function addActivity(to: string, where: string, index: number) {
  emit("add-activity", to, where, index);
}

function removeActivity(from: string, index: number) {
  emit("remove-activity", from, index);
}

function updateActivityTitle(title: string, block: string, index: number) {
  emit("update-activity-title", title, block, index);
}

function handleDragEvent(event: DraggableChangeEvent, block: ActivityBlock) {
  emit("handle-drag", event, block);
}

// Save experiment configuration during drag to prevent a reset
const timestamp = ref<number>(0);
function onDragStart() {
  emit("drag-start");
}

function onDragEnd() {
  // This forces the component to refresh
  // and check for an existing internal value in the experiment configuration
  timestamp.value = new Date().valueOf();
}

// This is a workaround to a bug in Vue.Draggable
// where template refs don't work
// See https://github.com/SortableJS/vue.draggable.next/issues/160
function addActivityRef(element: any) {
  if (activityRefArray.value.indexOf(element as HTMLDetailsElement) === -1) {
    activityRefArray.value.push(element);
  }
}

// Save experiment configuration during drag to prevent a reset
const confHolder = useStore(configurationHolder);

// Get the internal value of the component
// from the stored experiment configuration
function forceInternal(suffixedKey: string): string | null {
  if (confHolder.value) {
    if (confHolder.value[suffixedKey]) {
      return (confHolder.value[suffixedKey] as EnvConfiguration)
        .default as string;
    }
  }
  return null;
}

function getToleranceObject(element: TemplateActivity) {
  if (element.toleranceType && element.tolerance) {
    return {
      type: element.toleranceType,
      value: element.tolerance,
    };
  } else {
    return null;
  }
}

function updateConfiguration(
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
  emit("update-configuration", key, type, value, index, newStatus, suffix);
}

function handleBackgroundChange(where: string, index: number) {
  emit("background-change", where, index);
}

function emitTolerance(
  index: number,
  type: string,
  value: Probe["tolerance"] | null,
  status: { index: number; status: boolean }
) {
  emit("update-tolerance", index, type, value, status);
}
</script>

<style lang="scss" scoped>
@use "../../styles/abstracts/mixins" as *;

.streamDraggable {
  // This is the Vue.Draggable wrapper
  position: relative;

  display: flex;
  align-items: flex-start;
}

.streamSettings {
  position: absolute;
  top: 0;
  right: var(--space-small);
  z-index: 2;

  height: calc(100% - var(--space-small));
  width: 40rem;

  background-color: white;
  border-radius: 0 0 var(--border-radius-m) var(--border-radius-m);

  transition: all 0.2s ease-in-out;

  &--hidden {
    pointer-events: none;

    opacity: 0;
    transform: translateY(-110%);
  }

  &::after {
    @include shadow;

    border-radius: 0 0 var(--border-radius-m) var(--border-radius-m);
  }

  > button {
    position: absolute;
    top: 0.6rem;
    right: 0.6rem;

    background-color: transparent;
  }

  form {
    max-height: 100%;
    overflow-y: auto;
    padding: var(--space-small);
  }
}

.activityWrapper {
  flex: 0 0 auto;
  padding-right: var(--space-large);
  width: calc(40rem + var(--space-large));

  &:hover {
    .activitySettings__add,
    .activitySettings__remove {
      opacity: 1;

      pointer-events: all;
    }
  }
}

.activitySettings {
  position: relative;

  background-color: white;
  border: 0.1rem solid var(--grey-400);
  border-radius: var(--border-radius-m);

  &--empty {
    display: block;
    padding: var(--space-small);
    width: 100%;

    background-color: white;
    border-style: dashed;
    cursor: pointer;

    color: var(--text-color);
    font-size: 1.6rem;
    text-align: left;

    span {
      color: var(--pink-500);
    }

    &:hover {
      span {
        text-decoration: underline;
      }
    }
  }

  &__header {
    list-style: none;
  }

  &__chevron {
    position: absolute;
    top: 1.2rem;
    right: var(--space-small);

    display: block;
    height: 2.4rem;

    transform: rotate(-90deg);
    transform-origin: center center;
    transition: transform 0.3s ease-in-out;

    svg {
      height: 2.4rem;
    }
  }

  &__add {
    position: absolute;
    top: 5.2rem;
    z-index: 3;

    display: grid;
    place-content: center;
    padding: 0;
    height: 2.2rem;
    width: 2.2rem;

    background-color: var(--grey-300);
    border: 0.1rem solid var(--grey-400);
    border-radius: 50%;
    cursor: pointer;
    opacity: 0;

    color: var(--text-color-bright);

    pointer-events: none;

    transition: all 0.1s ease-in-out;

    &--before {
      left: -1.1rem;
    }

    &--after {
      left: calc(100% + var(--space-medium));
      transform: translateX(-50%);
    }

    svg {
      height: 1.8rem;
    }
  }

  &__remove {
    position: absolute;
    top: 100%;
    left: 50%;
    z-index: 3;

    opacity: 0;

    pointer-events: none;
    transform: translate(-50%, -25%);
    transition: all 0.1s ease-in-out;
  }

  &[open] {
    .activitySettings__chevron {
      transform: rotate(0);
    }
  }
}

.configurationFields {
  padding: var(--space-small);

  background-color: var(--section-background);
  border-radius: var(--border-radius-m);

  :deep(> li + li) {
    margin-top: var(--space-medium);
  }
}
</style>
