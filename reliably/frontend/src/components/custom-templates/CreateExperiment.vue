<template>
  <LoadingPlaceholder size="large" v-if="isLoading" />
  <article
    class="experimentFromTemplate"
    v-else-if="temp !== undefined && temp !== null && temp.id !== undefined"
  >
    <header class="pageHeader">
      <div v-if="!editTitle">
        <h1 class="pageHeader__title">
          {{ temp.manifest.spec.template.title }}
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
    <p class="experimentFromTemplate__intro">
      Fill the form with the requested information, to create a new experiment
      from the template <span>{{ temp.manifest.metadata.name }}</span
      >.
    </p>
    <div class="experimentFromTemplate__form">
      <div class="experimentFromTemplate__info">
        <div
          class="experimentFromTemplate__infoWrapper experimentFromTemplate__infoWrapper--template"
        >
          <div v-if="!editDescription">
            <p>{{ temp.manifest.spec.template.description }}</p>
            <button
              class="button button--creative button--small"
              @click.prevent="toggleEditDescription"
            >
              Edit description
            </button>
          </div>
          <form v-else class="form">
            <div class="inputWrapper inputWrapper--wide">
              <textarea
                id="experimentDescription"
                v-model="experimentDescription"
              />
              <label for="experimentDescription" class="screen-reader-text">
                Edit experiment description
              </label>
              <button
                class="button button--creative button--small"
                @click.prevent="saveDescription"
              >
                Save
              </button>
              <button
                class="button button--ghost button--small"
                @click.prevent="toggleEditDescription"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      </div>
      <div>
        <section class="experimentConfiguration">
          <form class="form">
            <ul class="configurationFields list-reset">
              <li
                v-for="(conf, index) in temp.manifest.spec.schema.configuration"
                class="configurationField"
                :key="index"
              >
                <CreateExperimentField
                  :configuration="conf"
                  :index="index"
                  :force-internal="null"
                  :state="state"
                  @update-configuration="updateConfiguration"
                />
              </li>
              <li v-if="temp.manifest.spec.schema.configuration.length === 0">
                <strong>
                  This activity doesn't require any configuration.
                </strong>
              </li>
              <li>
                <details class="inputWrapper inputWrapper--details">
                  <summary>Contributions and tags</summary>
                  <ExperimentContributions v-model="contributions" />
                  <ExperimentTags v-model="tags" />
                </details>
              </li>
            </ul>
          </form>
        </section>
        <section class="experimentSave">
          <button
            @click.prevent="createExperiment"
            class="button button--primary"
            :disabled="isSubmitDisabled"
          >
            Save experiment
          </button>
        </section>
      </div>
      <div class="experimentFormTemplate__preview">
        <button
          @click.prevent="displayExperimentModal"
          class="button button--icon experimentFromTemplate__view hasTooltip hasTooltip--center-left"
          aria-label="View Experiment"
          label="View Experiment"
        >
          {&nbsp;}
        </button>
      </div>
    </div>
  </article>
  <NoData v-else message="We couldn't find an experiment with this ID." />
  <ModalWindow
    v-if="isExperimentDisplayed"
    :isUnlimited="true"
    :hasCloseButton="true"
    @close="closeExperimentModal"
  >
    <template #title>Experiment Definition</template>
    <template #content>
      <JsonViewer
        :json="JSON.stringify(experiment, null, 2)"
        :force-wrap="true"
      />
    </template>
  </ModalWindow>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import { useStore } from "@nanostores/vue";

import type {
  Configuration,
  EnvConfiguration,
  ExperimentDefinition,
  Contributions,
  Probe,
  Action,
} from "@/types/experiments";

import type { FieldsState } from "@/types/snapshots";

import type { Template } from "@/types/templates";

import {
  template,
  fetchTemplate,
  fetchActionTemplate,
} from "@/stores/templates";
import { importExperiment } from "@/stores/experiments";

import CreateExperimentField from "@/components/custom-templates/CreateExperimentField.vue";
import ExperimentContributions from "@/components/experiments/ExperimentContributions.vue";
import ActivitySelector from "@/components/starters/ActivitySelector.vue";
import ExperimentTags from "@/components/experiments/ExperimentTags.vue";
import LoadingPlaceholder from "@/components/_ui/LoadingPlaceholder.vue";
import NoData from "@/components/_ui/NoData.vue";
import ModalWindow from "@/components/_ui/ModalWindow.vue";
import JsonViewer from "@/components/_ui/JsonViewer.vue";
import TagList from "@/components/_ui/TagList.vue";
import ChevronDown from "@/components/svg/ChevronDown.vue";
import PlusIcon from "@/components/svg/PlusIcon.vue";
import TrashIcon from "@/components/svg/TrashIcon.vue";

import { hasProp } from "@/utils/objects";

const isLoading = ref(true);
const id = ref<string | undefined>(undefined);
const action = ref<string | null>(null);
const temp = useStore(template);
const experiment = ref<ExperimentDefinition | null>(null);

function getCurrentId() {
  let location = window.location;
  let params = new URLSearchParams(location.search);
  if (params.has("id")) {
    id.value = params.get("id")!;
  } else if (params.has("activity")) {
    action.value = params.get("activity");
  }
}

async function getTemplate() {
  if (id.value) {
    await fetchTemplate(id.value!);
  } else if (action.value) {
    await fetchActionTemplate(action.value);
  }
}

function getExperimentFromTemplate() {
  if (temp.value !== null) {
    experiment.value = temp.value.manifest.spec
      .template as ExperimentDefinition;
  }
}

const setMetaData = () => {
  let title = "Template · Reliably";
  if (temp.value !== undefined && temp.value !== null) {
    title = `Create experiment from template ${temp.value.manifest.metadata.name} · Reliably`;
  }
  document.title = title;
};

const editTitle = ref<boolean>(false);
const experimentTitle = ref<string>("");
function toggleEditTitle() {
  editTitle.value = !editTitle.value;
}
function getExperimentTitle() {
  if (experiment.value) {
    experimentTitle.value = experiment.value.title;
  }
}
function saveTitle() {
  if (experiment.value !== null) {
    experiment.value.title = experimentTitle.value;
    toggleEditTitle();
  }
}

const editDescription = ref<boolean>(false);
const experimentDescription = ref<string>("");
function toggleEditDescription() {
  editDescription.value = !editDescription.value;
}
function getExperimentDescription() {
  if (experiment.value) {
    experimentDescription.value = experiment.value.description;
  }
}
function saveDescription() {
  if (experiment.value !== null) {
    experiment.value.description = experimentDescription.value;
    toggleEditDescription();
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
  if (experiment.value?.configuration !== undefined) {
    const target = experiment.value.configuration[key];
    if (
      hasProp(target as object, "type") &&
      (target as EnvConfiguration).type === "env"
    ) {
      if (value !== null && value !== undefined) {
        (experiment.value.configuration[key] as EnvConfiguration).default =
          value;
      } else {
        const evt = (experiment.value.configuration[key] as EnvConfiguration)
          .env_var_type;
        if (evt === "int" || evt === "float" || evt === "bool") {
          delete (experiment.value.configuration[key] as EnvConfiguration)
            .default;
        } else if (evt === "str") {
          (experiment.value.configuration[key] as EnvConfiguration).default =
            "";
        } else if (evt === "json") {
          (experiment.value.configuration[key] as EnvConfiguration).default =
            null;
        } else {
          delete (experiment.value.configuration[key] as EnvConfiguration)
            .default;
        }
      }
    } else {
      let evt: string = "";
      if (type === "string") {
        evt = "str";
      } else if (type === "integer") {
        evt = "int";
      } else if (type === "float") {
        evt = "float";
      } else if (type === "boolean") {
        evt = "bool";
      } else if (type === "object") {
        evt = "json";
      }
      if (value !== null && value !== undefined) {
        experiment.value.configuration[key] = {
          key: key.toUpperCase(),
          type: "env",
          env_var_type: evt,
          default: value,
        };
      } else if (evt === "int" || evt === "float" || evt === "bool") {
        experiment.value.configuration[key] = {
          key: key.toUpperCase(),
          type: "env",
          env_var_type: evt,
        };
      } else if (evt === "str") {
        experiment.value.configuration[key] = {
          key: key.toUpperCase(),
          type: "env",
          env_var_type: evt,
          default: "",
        };
      } else if (evt === "json") {
        experiment.value.configuration[key] = {
          key: key.toUpperCase(),
          type: "env",
          env_var_type: evt,
          default: null,
        };
      } else {
        experiment.value.configuration[key] = {
          key: key.toUpperCase(),
          type: "env",
          env_var_type: evt,
        };
      }
    }
  }
  requiredFieldsStatus.value[index] = newStatus;
}

const contributions = ref<Contributions>({
  availability: "none",
  latency: "none",
  security: "none",
  errors: "none",
});
function getExperimentContributions() {
  const c: Contributions | undefined = experiment.value?.contributions;
  if (c !== undefined) {
    contributions.value = c;
  }
}

const tags = ref<string[]>([]);
function getExperimentTags() {
  const t: string[] | undefined = experiment.value?.tags;
  if (t !== undefined) {
    tags.value = t;
  } else if (temp.value?.manifest.metadata.labels !== undefined) {
    tags.value = temp.value?.manifest.metadata.labels;
  }
}

const state = ref<FieldsState[]>([]);

const requiredFieldsStatus = ref<boolean[]>([]);
function setRequiredFieldStatus() {
  temp.value?.manifest.spec.schema.configuration.forEach((field) => {
    if (field.required) {
      if (field.default !== null && field.default !== "") {
        requiredFieldsStatus.value.push(true);
      } else {
        requiredFieldsStatus.value.push(false);
      }
    } else {
      requiredFieldsStatus.value.push(true);
    }
  });
}
const isSubmitDisabled = computed<boolean>(() => {
  let allGood = requiredFieldsStatus.value.every((s) => {
    return s;
  });
  return !allGood;
});

async function createExperiment() {
  if (experiment.value !== null) {
    if (action.value !== null && id.value === undefined) {
      postProcessExperiment(experiment.value);
    }
    experiment.value.contributions = contributions.value;
    experiment.value.tags = tags.value;
    importExperiment({ experiment: JSON.stringify(experiment.value) });
  }
}

/*
 * postProcessExperiment() delete the method arguments for which the
 * configuration environment variable provides no default value.
 * It also deletes the environment variable.
 * This aims at preventing unwanted behaviours when Chaos Toolkit runs the
 * experiment and expects a null value when no default is set, while maintaining
 * the Reliably app behaviour of not setting a default value to null when none
 * is provided.
 * IT SHOULD ONLY BE CALLED WHEN THE TEMPLATE HAS BEEN CALLED FROM A STARTER,
 * that is if action.value !== null and id.value === undefined
 * (one should never go without the other).
 */
function postProcessExperiment(e: ExperimentDefinition) {
  if (e.configuration !== undefined) {
    const keys = Object.keys(e.configuration);
    const ssh = e["steady-state-hypothesis"];
    const method = e.method;
    const rollbacks = e.rollbacks;
    const argsArrays = [];
    if (ssh !== undefined && ssh.probes !== undefined && ssh.probes.length) {
      argsArrays.push(ssh.probes[0]);
    }
    if (method !== undefined && method.length) {
      argsArrays.push(method[0]);
    }
    if (rollbacks !== undefined && rollbacks?.length) {
      argsArrays.push(rollbacks[0]);
    }
    argsArrays.forEach((arr) => {
      const args = arr.provider.arguments;
      if (args !== undefined) {
        keys.forEach((key) => {
          if (
            (e.configuration![key] as EnvConfiguration).default === undefined
          ) {
            delete (args as { [key: string]: string })[key];
            delete e.configuration![key];
          }
        });
      }
    });
  }
}

const isExperimentDisplayed = ref<boolean>(false);
function displayExperimentModal() {
  isExperimentDisplayed.value = true;
}
function closeExperimentModal() {
  isExperimentDisplayed.value = false;
}

onMounted(async () => {
  isLoading.value = true;
  getCurrentId();
  await getTemplate();
  setRequiredFieldStatus();
  setMetaData();
  getExperimentFromTemplate();
  getExperimentTitle();
  getExperimentDescription();
  getExperimentContributions();
  getExperimentTags();
  isLoading.value = false;
});
</script>

<style lang="scss" scoped>
.experimentFromTemplate {
  header > div {
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

  &__intro {
    span {
      color: var(--text-color);
    }
  }

  > section + section {
    margin-top: var(--space-large);
  }

  &__info {
    button {
      margin-top: var(--space-small);
    }

    textarea {
      font-size: 2rem;
      height: 12rem;
    }
  }

  &__view {
    font-size: 1.8rem;
    font-weight: 500;
  }

  .experimentConfiguration,
  .experimentSave {
    margin-right: auto;
    margin-left: auto;
    max-width: 100%;
    width: 50rem;
  }

  .experimentConfiguration {
    margin-right: auto;
    margin-left: auto;
    max-width: 100%;
    width: 50rem;

    &__block {
      margin-top: var(--space-small);
      margin-bottom: var(--space-medium);

      &--empty {
        padding: var(--space-small);

        background-color: var(--section-background);
        border-radius: var(--border-radius-s);
      }

      .activitySettings {
        position: relative;

        background-color: var(--section-background);
        border-radius: var(--border-radius-s);

        &:not(:first-child) {
          margin-top: var(--space-small);
        }

        &__header {
          padding: var(--space-small);

          cursor: pointer;
          list-style: none;
        }

        &__title {
          margin-top: 0;
          margin-bottom: 0;

          font-family: var(--monospace-font);
        }

        &__chevron {
          position: absolute;
          top: var(--space-small);
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
          left: -1.2rem;

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
            top: 0;
            transform: translateY(calc(-100% + 1rem));
          }

          &--after {
            top: 100%;
            transform: translateY(-1rem);
          }

          svg {
            height: 1.8rem;
          }
        }

        &__remove {
          position: absolute;
          top: 50%;
          left: 100%;

          opacity: 0;

          pointer-events: none;
          transform: translate(-25%, -50%);
          transition: all 0.1s ease-in-out;
        }

        &[open] {
          .activitySettings__chevron {
            transform: rotate(0);
          }
        }

        &:hover {
          .activitySettings__add,
          .activitySettings__remove {
            opacity: 1;

            pointer-events: all;
          }
        }
      }
    }

    .configurationFields {
      padding: var(--space-small);

      background-color: var(--section-background);
      border-radius: var(--border-radius-m);

      li + li {
        margin-top: var(--space-medium);
      }
    }
  }

  .experimentSave {
    display: flex;
    gap: var(--space-small);
    margin-top: var(--space-medium);
  }

  .experimentPreview {
    > div {
      margin-top: var(--space-medium);

      background-color: var(--section-background);
      border-radius: var(--border-radius-m);
    }
  }
}
</style>
