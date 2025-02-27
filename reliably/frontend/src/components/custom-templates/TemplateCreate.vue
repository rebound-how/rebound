<template>
  <div v-if="!isLoading" class="createTemplate">
    <section v-if="!isDuplicating" class="importExperiment">
      <h2>Import an experiment or template</h2>
      <p>
        Import a template or an existing experiment with a
        <code>configuration</code> block. In the later case, you will be able to
        create fields for users to override this configuration when using your
        template to create a new experiment.
      </p>
      <div class="importExperiment__wrapper">
        <div class="importExperiment__options">
          <input
            type="radio"
            id="paste"
            value="paste"
            v-model="displayedImport"
          />
          <label for="paste">Paste</label>
          <input
            type="radio"
            id="upload"
            value="upload"
            v-model="displayedImport"
          />
          <label for="upload">Upload</label>
        </div>
        <div
          v-if="displayedImport === 'paste'"
          class="importExperiment__option importExperiment__option--paste"
        >
          <h3 class="screen-reader-text">Paste as JSON</h3>
          <TemplateImportPaste v-model="experiment" @set-input-type="setType" />
        </div>
        <div
          v-else
          class="importExperiment__option importExperiment__option--upload"
        >
          <h3 class="screen-reader-text">Upload experiment file</h3>
          <TemplateImportUpload
            v-model="experiment"
            @set-input-type="setType"
          />
        </div>
      </div>
    </section>
    <p v-if="experiment === '' && !isDuplicating">
      Import an experiment with a <code>configuration</code> declaration.
    </p>
    <div v-else-if="inputType === 'template'">
      <section class="editSave">
        <button class="button button--primary" @click.prevent="submitTemplate">
          Save template
        </button>
      </section>
    </div>
    <div v-else-if="hasConfiguration">
      <section class="editMetadata">
        <h2>Template metadata</h2>
        <form class="form">
          <fieldset>
            <div class="inputWrapper">
              <label for="template-title">
                Title <span class="required">Required</span>
              </label>
              <input
                type="text"
                id="template-title"
                v-model="templateTitle"
                required
                placeholder="Simple experiment template..."
              />
            </div>
            <div class="inputWrapper">
              <label for="template-labels"> Labels </label>
              <input
                type="text"
                id="template-labels"
                placeholder="kubernetes, pod, aws"
                v-model="templateLabels"
              />
              <p class="inputWrapper__help">
                A list of comma-separated labels.
              </p>
              <p class="inputWrapper__help">
                Labels can be used by users to search for templates. Take some
                time to set useful ones.
              </p>
              <p v-if="templateLabels.length">
                <TagList :tags="templateLabelsArray" />
              </p>
            </div>
          </fieldset>
        </form>
      </section>
      <section class="editTemplate">
        <form class="form editTemplate__form">
          <h2>Edit template</h2>
          <p>
            Create the fields that will be displayed to users when creating an
            experiment from your template.
          </p>
          <div
            v-for="(k, index) in confKeys"
            :key="index"
            class="editTemplate__field"
          >
            <h3>
              Create a field for
              <span class="editTemplate__key">{{
                templateFields[index].key
              }}</span>
            </h3>
            <div>
              <fieldset>
                <div class="inputWrapper">
                  <label :for="`title-${index}`">
                    Title <span class="required">Required</span>
                  </label>
                  <input
                    type="text"
                    :id="`title-${index}`"
                    v-model="templateFields[index].title"
                    required
                  />
                </div>
                <div class="inputWrapper">
                  <label :for="`placeholder-${index}`">Placeholder</label>
                  <input
                    type="text"
                    :id="`placeholder-${index}`"
                    v-model="templateFields[index].placeholder"
                  />
                </div>
                <div class="inputWrapper">
                  <label :for="`help-${index}`">Field help</label>
                  <input
                    type="text"
                    :id="`help-${index}`"
                    v-model="templateFields[index].help"
                  />
                  <p class="inputWrapper__help">
                    Help text that appears under the field, like this sentence.
                  </p>
                </div>
                <div class="inputWrapper">
                  <label :for="`type-${index}`">
                    Expected data type <span class="required">Required</span>
                  </label>
                  <select
                    :id="`type-${index}`"
                    v-model="templateFields[index].type"
                    @blur="handleEnvVarType(index)"
                    required
                  >
                    <option value="-">Select a data type</option>
                    <option value="string">String</option>
                    <option value="integer">Integer</option>
                    <option value="float">Float</option>
                    <option value="boolean">Boolean</option>
                    <option value="object">Object</option>
                  </select>
                </div>
                <div class="inputWrapper inputWrapper--tick">
                  <div>
                    <input
                      :id="`no-default-${index}`"
                      type="checkbox"
                      v-model="templateFields[index].no_default"
                    />
                    <label :for="`no-default-${index}`">No default value</label>
                  </div>
                  <p class="inputWrapper__help">
                    Explicitly set no default value. This is different from
                    setting an empty string or any other empty default value and
                    is recommended to avoid unexpected behaviours.
                  </p>
                </div>
                <div
                  v-if="templateFields[index].type === 'object'"
                  class="inputWrapper"
                  :class="{
                    hasDisabledField: templateFields[index].no_default,
                  }"
                >
                  <label :for="`default-${index}`">Default value</label>
                  <textarea
                    :id="`default-${index}`"
                    v-model="(tmpObjectValues[index] as string)"
                    @blur="handleObjectValues(index)"
                    :disabled="templateFields[index].no_default"
                  />
                </div>
                <div
                  v-else-if="templateFields[index].type === 'boolean'"
                  class="inputWrapper"
                  :class="{
                    hasDisabledField: templateFields[index].no_default,
                  }"
                >
                  <label :for="`default-${index}`">Default value</label>
                  <div
                    :id="`default-${index}`"
                    class="inputWrapper inputWrapper--tick"
                  >
                    <div>
                      <input
                        :id="`default-${index}-true`"
                        type="radio"
                        :value="true"
                        v-model="templateFields[index].default"
                        :disabled="templateFields[index].no_default"
                      />
                      <label :for="`default-${index}-true`">True</label>
                    </div>
                    <div>
                      <input
                        :id="`default-${index}-false`"
                        type="radio"
                        :value="false"
                        v-model="templateFields[index].default"
                        :disabled="templateFields[index].no_default"
                      />
                      <label :for="`default-${index}-false`">False</label>
                    </div>
                    <div>
                      <button
                        @click.prevent="unsetDefault(index)"
                        class="editTemplate__unsetDefault button button--small button--tertiary"
                        :disabled="templateFields[index].no_default"
                      >
                        Unset
                      </button>
                    </div>
                  </div>
                </div>
                <div
                  v-else-if="
                    templateFields[index].type === 'integer' ||
                    templateFields[index].type === 'float'
                  "
                  class="inputWrapper"
                  :class="{
                    hasDisabledField: templateFields[index].no_default,
                  }"
                >
                  <label :for="`default-${index}`">Default value</label>
                  <input
                    type="text"
                    :id="`default-${index}`"
                    v-model.number="templateFields[index].default"
                    :disabled="templateFields[index].no_default"
                  />
                </div>
                <div
                  v-else-if="templateFields[index].type === 'string'"
                  class="inputWrapper"
                  :class="{
                    hasDisabledField: templateFields[index].no_default,
                  }"
                >
                  <label :for="`default-${index}`">Default value</label>
                  <input
                    type="text"
                    :id="`default-${index}`"
                    v-model="templateFields[index].default"
                    :disabled="templateFields[index].no_default"
                  />
                </div>
                <div
                  v-else
                  class="inputWrapper"
                  :class="{
                    hasDisabledField: templateFields[index].no_default,
                  }"
                >
                  <label :for="`default-${index}`">Default value</label>
                  <input
                    type="text"
                    :id="`default-${index}`"
                    v-model="templateFields[index].default"
                    :disabled="templateFields[index].no_default"
                  />
                </div>
                <div class="inputWrapper">
                  <label :for="`required-${index}`">Required</label>
                  <select
                    :id="`required-${index}`"
                    v-model="templateFields[index].required"
                  >
                    <option :value="true">Yes</option>
                    <option :value="false">No</option>
                  </select>
                  <p class="inputWrapper__help">Is the field required?</p>
                </div>
              </fieldset>
              <div class="editTemplate__preview">
                <template
                  v-if="experimentJson && (experimentJson as ExperimentDefinition).configuration !== undefined"
                >
                  <h4>Source</h4>
                  <p>The field will override this value:</p>
                  <JsonViewer
                    :json="
                      JSON.stringify((experimentJson as ExperimentDefinition).configuration![k], null, 2)
                    "
                  />
                </template>
                <h4>Preview</h4>
                <p>How the field will appear to users.</p>
                <div class="inputWrapper">
                  <CreateExperimentField
                    :configuration="templateFields[index]"
                    :force-internal="null"
                    :index="index"
                    :previewMode="true"
                  />
                </div>
              </div>
            </div>
          </div>
        </form>
      </section>
      <section class="editSave">
        <button
          class="button button--primary"
          @click.prevent="submitTemplate"
          :disabled="isSubmitDisabled"
        >
          Save template
        </button>
      </section>
    </div>

    <p v-else class="noConfiguration">
      This experiment has no editable configuration
    </p>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from "vue";
import { useStore } from "@nanostores/vue";

import TemplateImportPaste from "@/components/custom-templates/TemplateImportPaste.vue";
import TemplateImportUpload from "@/components/custom-templates/TemplateImportUpload.vue";
import CreateExperimentField from "@/components/custom-templates/CreateExperimentField.vue";
import JsonViewer from "@/components/_ui/JsonViewer.vue";
import TagList from "@/components/_ui/TagList.vue";

import type {
  ExperimentDefinition,
  Configuration,
  EnvConfiguration,
} from "@/types/experiments";
import type { TemplateField, TemplateCreate } from "@/types/templates";

import { template, fetchTemplate, createTemplate } from "@/stores/templates";
import { hasProp } from "@/utils/objects";

const isLoading = ref<boolean>(true);
const isDuplicating = ref<boolean>(false);
const displayedImport = ref<string>("paste");
const experiment = ref<string>("");
const experimentJson = ref<ExperimentDefinition | TemplateCreate | null>(null);
const confKeys = ref<string[]>([]);

async function handleDuplication() {
  let location = window.location;
  let params = new URLSearchParams(location.search);
  if (params.has("duplicate")) {
    const id = params.get("duplicate");
    if (id !== null) {
      isDuplicating.value = true;
      await fetchTemplate(id);
      const source = useStore(template);
      setType("experiment");
      experimentJson.value = source.value?.manifest.spec
        .template! as ExperimentDefinition;
      if (source.value?.manifest.spec.schema.configuration !== undefined) {
        templateFields.value = source.value?.manifest.spec.schema
          .configuration as TemplateField[];
        source.value?.manifest.spec.schema.configuration.forEach((c) => {
          confKeys.value.push(c.key);
        });
      }
      templateTitle.value = source.value?.manifest.metadata.name!;
      if (source.value?.manifest.metadata.labels !== undefined) {
        templateLabels.value = source.value?.manifest.metadata.labels.join();
      }
    }
  }
}

function experimentToJson() {
  if (experiment.value === "") {
    experimentJson.value = null;
  } else {
    experimentJson.value = JSON.parse(experiment.value);
  }
}

function getConfKeys() {
  if (experimentJson.value !== null) {
    const conf = (experimentJson.value as ExperimentDefinition).configuration;
    if (conf !== undefined) {
      const keys: string[] = Object.keys(conf);
      keys.forEach((k) => {
        if (k !== "reliably_url") {
          let dflt: string | number | boolean = "";
          let type: string = "string";
          let noDefault: boolean = false;
          if (conf[k] === null) {
            noDefault = true;
          } else if (typeof conf[k] === "string") {
            dflt = conf[k] as string;
          } else if (typeof conf[k] === "number") {
            dflt = conf[k] === null ? "" : (conf[k]! as string);
            type = "float";
          } else if (typeof conf[k] === "boolean") {
            dflt = conf[k] === null ? "" : (conf[k]! as string);
            type = "boolean";
          } else if (Array.isArray(conf[k])) {
            dflt = (conf[k] as string[]).join(", ");
            type = "object";
          } else {
            // Env or object
            if (hasProp(conf[k] as Object, "default")) {
              // Env
              const dt = (conf[k] as EnvConfiguration).default;
              if (dt === null) {
                noDefault = true;
              } else if (typeof dt === "string") {
                dflt = dt;
              } else if (typeof dt === "number") {
                dflt = dt;
                type = "float";
              } else if (typeof dt === "boolean") {
                dt ? (dflt = "true") : (dflt = "false");
                type = "boolean";
              } else {
                dflt = dt;
              }
            }
            if ((conf[k] as EnvConfiguration).type === "env") {
              if ((conf[k] as EnvConfiguration).env_var_type !== undefined) {
                const envVarType: string = (conf[k] as EnvConfiguration)
                  .env_var_type!;
                if (envVarType === "int") {
                  type = "integer";
                } else if (envVarType === "float") {
                  type = "float";
                } else if (envVarType === "str") {
                  type = "string";
                } else if (envVarType === "bool") {
                  type = "boolean";
                } else if (envVarType === "json") {
                  type = "object";
                } else {
                  type = "string";
                }
              }
            } else {
              // Object
              dflt = JSON.stringify(conf[k]);
              type = "object";
            }
          }
          templateFields.value.push({
            key: k,
            title: "",
            placeholder: "",
            help: "",
            no_default: noDefault,
            default: dflt,
            type: type,
            required: false,
          });
          confKeys.value.push(k);
          tmpObjectValues.value.push(null);
        }
      });
    }
  } else {
    confKeys.value = [];
  }
}

const hasConfiguration = computed<boolean>(() => {
  return confKeys.value.length > 0;
});

const templateFields = ref<TemplateField[]>([]);

const templateTitle = ref<string>("");
const templateLabels = ref<string>("");
const templateLabelsArray = computed<string[]>(() => {
  return templateLabels.value.split(",").map((element) => element.trim());
});

const tmpObjectValues = ref<Array<null | string>>([]);

function handleObjectValues(index: number) {
  try {
    templateFields.value[index].default = JSON.parse(
      tmpObjectValues.value[index] || ""
    );
  } catch (e) {
    // Display error
  }
}

function handleEnvVarType(index: number) {
  const key = templateFields.value[index].key;
  if (inputType.value === "experiment") {
    const value = (experimentJson.value! as ExperimentDefinition)
      .configuration![key];
    if (
      hasProp(value as Object, "type") &&
      (value as EnvConfiguration).type === "env"
    ) {
      if (templateFields.value[index].type === "string") {
        (value as EnvConfiguration).env_var_type = "str";
      } else if (templateFields.value[index].type === "integer") {
        (value as EnvConfiguration).env_var_type = "int";
      } else if (templateFields.value[index].type === "float") {
        (value as EnvConfiguration).env_var_type = "float";
      } else if (templateFields.value[index].type === "boolean") {
        (value as EnvConfiguration).env_var_type = "bool";
      } else if (templateFields.value[index].type === "object") {
        (value as EnvConfiguration).env_var_type = "json";
      }
    }
  } else if (inputType.value === "template") {
    const value = (experimentJson.value! as TemplateCreate).spec.template
      .configuration![key];
    if (
      hasProp(value as Object, "type") &&
      (value as EnvConfiguration).type === "env"
    ) {
      if (templateFields.value[index].type === "string") {
        (value as EnvConfiguration).env_var_type = "str";
      } else if (templateFields.value[index].type === "integer") {
        (value as EnvConfiguration).env_var_type = "int";
      } else if (templateFields.value[index].type === "float") {
        (value as EnvConfiguration).env_var_type = "float";
      } else if (templateFields.value[index].type === "boolean") {
        (value as EnvConfiguration).env_var_type = "bool";
      } else if (templateFields.value[index].type === "object") {
        (value as EnvConfiguration).env_var_type = "json";
      }
    }
  }
}

function initiallySetEnvVarTypes() {
  confKeys.value.forEach((k, index) => {
    handleEnvVarType(index);
  });
}

function unsetDefault(index: number) {
  templateFields.value[index].default = "";
}

const isSubmitDisabled = computed<boolean>(() => {
  let areFieldsReady: boolean = false;
  let numberOfReadyFields: number = 0;
  templateFields.value.every((f) => {
    if (f.title === "" || f.type === "") {
      return false;
    } else {
      numberOfReadyFields++;
      return true;
    }
  });
  if (numberOfReadyFields === templateFields.value.length) {
    areFieldsReady = true;
  }
  return templateTitle.value === "" || !areFieldsReady;
});

const inputType = ref<string>("");
function setType(type: string) {
  inputType.value = type;
}

const payload = ref<TemplateCreate | null>(null);
function buildPayload() {
  if (inputType.value === "template") {
    payload.value = experimentJson.value as TemplateCreate;
  } else {
    if (!isSubmitDisabled.value && experimentJson.value !== null) {
      let p: TemplateCreate = {
        metadata: {
          name: templateTitle.value,
          labels: templateLabelsArray.value.filter((l) => {
            return l !== "";
          }),
        },
        spec: {
          provider: "chaostoolkit",
          type: "experiment",
          schema: {
            configuration: templateFields.value,
          },
          template: experimentJson.value as ExperimentDefinition,
        },
      };
      payload.value = p;
    }
  }
}

async function submitTemplate() {
  buildPayload();
  if (payload.value !== null) {
    createTemplate(payload.value);
  }
}

watch(experiment, async () => {
  experimentToJson();
  getConfKeys();
  initiallySetEnvVarTypes();
});

onMounted(async () => {
  isLoading.value = true;
  await handleDuplication();
  isLoading.value = false;
});
</script>

<style lang="scss" scoped>
.createTemplate {
  counter-reset: section;

  h2 {
    &::before {
      counter-increment: section;
      content: counter(section) ". ";
    }
  }

  p {
    max-width: 70ch;
  }

  .importExperiment {
    margin-bottom: var(--space-large);

    &__wrapper {
      margin-top: var(--space-medium);
      padding: var(--space-small);

      background-color: var(--section-background);
      border-radius: var(--border-radius-m);
    }

    &__options {
      input {
        height: 0;
        width: 0;
        opacity: 0;
      }

      label {
        display: inline-block;
        padding: 0.2rem 0.4rem 0;

        background-color: var(--grey-400);
        border: 0.1rem solid var(--grey-400);
        border-bottom: 0.3rem solid transparent;
        border-radius: var(--border-radius-s) var(--border-radius-s) 0 0;
        cursor: pointer;
      }

      input:checked + label {
        background-color: var(--pink-500);
        border-color: var(--pink-500);

        color: white;
      }
    }
  }
  .editTemplate {
    margin-bottom: var(--space-large);

    > div + div {
      margin-top: var(--space-medium);
    }

    &__field {
      margin-top: var(--space-medium);
      padding: var(--space-small);

      background-color: var(--section-background);
      border-radius: var(--border-radius-m);

      > div {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: var(--space-medium);

        > :first-child {
          padding-right: var(--space-small);

          border-right: 0.1rem solid var(--section-separator-color);
        }
      }

      div.hasDisabledField {
        cursor: not-allowed;
        opacity: 0.5;

        * {
          pointer-events: none;
        }
      }
    }

    &__key {
      font-family: var(--monospace-font);
    }

    &__preview {
      h4 {
        margin-bottom: 0;

        &:not(:first-child) {
          margin-top: var(--space-large);
        }
      }

      p {
        margin-bottom: var(--space-medium);
      }
    }
  }

  .editMetadata {
    margin-bottom: var(--space-large);

    fieldset {
      margin-top: var(--space-medium);
      padding: var(--space-small);

      background-color: var(--section-background);
      border-radius: var(--border-radius-m);
    }
  }
}
</style>
