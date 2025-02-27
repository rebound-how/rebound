<template>
  <header class="builderHeader pageHeader">
    <div v-if="!isTitleEditable">
      <h1 class="pageHeader__title">
        {{ experiment!.title }}
      </h1>
      <button
        class="button button--creative button--small"
        @click.prevent="toggleEditTitle"
      >
        Edit experiment title
      </button>
    </div>
    <div v-else>
      <div class="inputWrapper inputWrapper--wide">
        <input type="text" id="experimentTitle" v-model="experimentTitle" />
        <label for="experimentTitle" class="screen-reader-text">
          Edit experiment title
        </label>
        <button
          class="button button--creative button--small"
          @click.prevent="saveTitle"
        >
          Save
        </button>
        <button
          class="button button--ghost button--small"
          @click.prevent="toggleEditTitle"
        >
          Cancel
        </button>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { toRefs, ref, onMounted } from "vue";
import type { ExperimentDefinition } from "@/types/experiments";

const props = defineProps<{
  experiment: ExperimentDefinition | null;
}>();
const { experiment } = toRefs(props);

const emit = defineEmits<{
  (e: "update-title", title: string): void;
}>();

const experimentTitle = ref<string>("");
const isTitleEditable = ref<boolean>(false);

function toggleEditTitle() {
  isTitleEditable.value = !isTitleEditable.value;
}

function getExperimentTitle() {
  if (experiment.value) {
    experimentTitle.value = experiment.value.title;
  }
}

function saveTitle() {
  if (experiment.value !== null) {
    emit("update-title", experimentTitle.value);
    toggleEditTitle();
  }
}

onMounted(() => {
  getExperimentTitle();
});
</script>

<style lang="scss" scoped>
.builderHeader {
  > div {
    display: flex;
    align-items: flex-start;
    width: 100%;

    > button {
      margin-top: 1.2rem;
      margin-left: auto;
    }

    .inputWrapper {
      display: flex;
      align-items: center;
      width: 100%;

      input {
        flex: 0 1 auto;
        margin-right: auto;
        padding: 0.5em;
        width: calc(100% - 16rem);

        background-color: var(--form-input-background);
        border: 0.1rem solid var(--form-input-border);
        border-radius: var(--border-radius-m);

        color: var(--text-color);
        font-family: var(--body-font);
        font-size: 2.1rem;

        &:focus {
          outline: 2px solid var(--form-input-focus);
        }
      }

      button {
        margin-left: var(--space-small);
      }
    }
  }
}
</style>
