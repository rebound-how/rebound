<template>
  <li class="executionEnvironmentItem">
    <div class="jsonString jsonString--envvar">{{ item.key }}</div>
    <div>
      <div
        v-if="isEditing"
        class="jsonString editor"
        :class="{ 'editor--saving': isSaving }"
      >
        <input type="text" v-model="newValue" />
        <button @click.prevent="cancelEdit" class="button button--icon">
          <XIcon />
          <span class="screen-reader-text">Cancel</span>
        </button>
        <button @click.prevent="saveEdit" class="button button--icon">
          <CheckIcon />
          <span class="screen-reader-text">Save</span>
        </button>
      </div>
      <div
        v-else-if="isEditable && experiment && !isEditing"
        class="jsonString"
        role="button"
        @click.prevent="openEdit"
      >
        {{ currentValue }}
      </div>
      <div v-else class="jsonString">
        {{ item.value }}
      </div>
    </div>
    <div>
      <button
        v-if="isEditable && experiment && !isEditing"
        @click.prevent="openEdit"
        class="button button--icon"
      >
        <EditIcon />
        <span class="screen-reader-text">Edit</span>
      </button>
    </div>
  </li>
</template>

<script setup lang="ts">
import { toRefs, ref, onMounted } from "vue";
import { useStore } from "@nanostores/vue";

import CheckIcon from "@/components/svg/CheckIcon.vue";
import EditIcon from "@/components/svg/EditIcon.vue";
import XIcon from "@/components/svg/XIcon.vue";

import { experiment, overwriteExperiment } from "@/stores/experiments";
import { addNotification } from "@/stores/notifications";

import type { Notification } from "@/types/ui-types";
import type { EnvConfiguration } from "@/types/experiments";

const props = defineProps<{
  item: { key: string; value: string };
  isEditable?: boolean;
  experimentId?: string;
}>();
const { item, isEditable, experimentId } = toRefs(props);

const exp = useStore(experiment);

const isEditing = ref<boolean>(false);
const isSaving = ref<boolean>(false);
const currentValue = ref<string>("");
const newValue = ref<string>("");
const hasError = ref<boolean>(false);

function openEdit() {
  isEditing.value = true;
}
function cancelEdit() {
  hasError.value = false;
  isEditing.value = false;
  newValue.value = currentValue.value;
}
async function saveEdit() {
  isSaving.value = true;
  if (exp.value?.id === experimentId?.value) {
    let newExp = JSON.parse(JSON.stringify(exp.value?.definition));
    const target = newExp.configuration![item.value.key];
    if (target.default) {
      if (target.env_var_type === "str" || target.env_var_type === "string") {
        newExp.configuration![item.value.key].default = newValue.value;
      } else if (target.env_var_type === "int") {
        const v = parseInt(newValue.value);
        if (!Number.isNaN(v)) {
          newExp.configuration![item.value.key].default = v;
        } else {
          hasError.value = true;
          const n: Notification = {
            title: "Wrong configuration type",
            message: "Expected value is an integer.",
            type: "error",
          };
          addNotification(n);
        }
      } else if (
        target.env_var_type === "float" ||
        target.env_var_type === "number"
      ) {
        const v = parseFloat(newValue.value);
        if (!Number.isNaN(v)) {
          newExp.configuration![item.value.key].default = v;
        } else {
          hasError.value = true;
          const n: Notification = {
            title: "Wrong configuration type",
            message: "Expected value is an float.",
            type: "error",
          };
          addNotification(n);
        }
      } else if (target.env_var_type === "bool") {
        if (newValue.value === "true") {
          newExp.configuration![item.value.key].default = true;
        } else if (newValue.value === "false") {
          newExp.configuration![item.value.key].default = false;
        } else {
          hasError.value = true;
          const n: Notification = {
            title: "Wrong configuration type",
            message:
              "Expected value is a boolean. Please type 'true' or 'false'.",
            type: "error",
          };
          addNotification(n);
        }
      } else if (target.env_var_type === "json") {
        try {
          const v = JSON.parse(newValue.value);
          newExp.configuration![item.value.key].default = v;
        } catch (e) {
          hasError.value = true;
          const n: Notification = {
            title: "Wrong configuration type",
            message:
              "Expected value is a JSON object. Please provide a valid JSON object.",
            type: "error",
          };
          addNotification(n);
        }
      }
    } else {
      newExp.configuration![item.value.key] = newValue.value;
    }
    if (!hasError.value) {
      await overwriteExperiment(
        experimentId!.value!,
        { experiment: JSON.stringify(newExp) },
        true
      );
      currentValue.value = newValue.value;
      isEditing.value = false;
    }
  } else {
    const n: Notification = {
      title: "Experiment couldn't be saved",
      message:
        "We couldn't find the experiment you're trying to edit. Please reload the page and try again.",
      type: "error",
    };
    addNotification(n);
  }
  isSaving.value = false;
}

onMounted(() => {
  if (isEditable && isEditable.value) {
    currentValue.value = item.value.value;
    if (
      (exp.value?.definition.configuration![item.value.key] as EnvConfiguration)
        .env_var_type === "json"
    ) {
      newValue.value = JSON.stringify(currentValue.value);
    } else {
      newValue.value = currentValue.value;
    }
  }
});
</script>

<style lang="scss">
.executionEnvironmentItem {
  display: table-row;

  &:hover {
    background-color: var(--grey-200);

    button {
      opacity: 1;
    }
  }

  > div {
    display: table-cell;
    padding-top: 0.6rem;
    padding-right: var(--space-small);
    padding-bottom: 0.6rem;

    &:first-child {
      padding-left: calc(var(--space-small) / 2);
      width: 40%;
    }

    &:nth-child(2) {
      padding: 0;
      width: auto;

      > div {
        padding-top: 0.6rem;
        padding-right: var(--space-small);
        padding-bottom: 0.6rem;
      }

      [role="button"] {
        cursor: pointer;
      }

      .editor {
        display: flex;
        gap: var(--space-small);

        &.saving {
          opacity: 0.5;

          pointer-events: none;
        }
      }

      input {
        display: block;
        width: calc(100% - 7.2rem);
        padding: 0 0.5em;

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

      button {
        &:nth-child(2) {
          background-color: var(--red-100);

          color: var(--red-600);

          &:hover {
            background-color: var(--red-200);

            color: var(--red-800);
          }
        }

        &:nth-child(3) {
          background-color: var(--green-200);

          color: var(--green-600);

          &:hover {
            background-color: var(--green-300);

            color: var(--green-800);
          }
        }
      }
    }

    &:last-child {
      padding-top: 0;
      padding-bottom: 0;
      width: 3.6rem;

      text-align: right;
    }
  }

  button {
    height: 2.2rem;
    width: 2.2rem;

    opacity: 0;

    svg {
      height: 1.2rem;
    }
  }
}
</style>
