<template>
  <LoadingPlaceholder size="large" v-if="isLoading" />
  <article
    class="builder"
    v-else-if="
      (temp !== undefined && temp !== null && temp.id !== undefined) ||
      experiment !== null
    "
  >
    <BuilderHeader :experiment="experiment" @update-title="updateTitle" />
    <p class="builder__intro">
      Add one or more activities and fill the form with the requested
      information, to create a new experiment. You can then run it wherever you
      want: on your own system, with a Reliably Deployment, or in the Reliably
      Cloud.
    </p>
    <BuilderMeta
      :experiment="experiment"
      @update-description="updateDescription"
      @update-tags="updateTags"
      @update-contributions="updateContributions"
    />
    <BuilderAssistant
      :experiment="experiment"
      @update-assistant="updateAssistant"
    />
    <div class="builder__form">
      <WorkflowOverview :workflow="fullModeTemplate" />
      <div>
        <section class="experimentWorkflow">
          <div ref="warmupWrapper">
            <h3>
              Warm up
              <span
                class="hasTooltip hasTooltip--center-right"
                aria-label="Prepare your system for the experiment turbulence. While this phase is optional, people like to use it to inject traffic, set up some resources, or any other action or probe you want to run before turbulence."
              >
                <HelpCircle />
              </span>
            </h3>
            <div class="experimentStreamWrapper">
              <div class="experimentStreamActions">
                <AssistantButton
                  v-if="possibleRelated.warmup.length"
                  :count="possibleRelated.warmup.length"
                  @click.prevent="handleRelatedAssistant('warmup')"
                />
              </div>
              <ScrollSync
                @scroll-sync="handleScrollSync"
                group="warmup"
                :ref="addScrollElementRef"
              >
                <BuilderMinimap
                  :stream="fullModeTemplate.warmup"
                  block="warmup"
                />
              </ScrollSync>
              <ScrollSync
                @scroll-sync="handleScrollSync"
                group="warmup"
                :ref="addScrollElementRef"
              >
                <div class="experimentStream" ref="warmupStream">
                  <BuilderStream
                    :stream="fullModeTemplate.warmup"
                    name="warmup"
                    :activityRefArray="everyActivity"
                    :template="(temp as Template)"
                    @add-activity="addActivity"
                    @remove-activity="removeActivity"
                    @update-activity-title="updateActivityTitle"
                    @handle-drag="handleDragEvent"
                    @drag-start="onDragStart"
                    @update-configuration="updateFullModeConfiguration"
                    @background-change="handleBackgroundChange"
                  />
                </div>
              </ScrollSync>
            </div>
            <ActivityStreamLink :first="true" />
          </div>
          <div ref="methodWrapper">
            <h3>
              Turbulence
              <span
                class="hasTooltip hasTooltip--center-right"
                aria-label="Turbulence is the core of your experiments. Use actions to interact with your system and probes to measure the result."
              >
                <HelpCircle />
              </span>
            </h3>
            <div class="experimentStreamWrapper">
              <div class="experimentStreamActions">
                <AssistantButton
                  v-if="possibleRelated.method.length"
                  :count="possibleRelated.method.length"
                  @click.prevent="handleRelatedAssistant('method')"
                />
              </div>
              <ScrollSync
                @scroll-sync="handleScrollSync"
                group="method"
                :ref="addScrollElementRef"
              >
                <BuilderMinimap
                  :stream="fullModeTemplate.method"
                  ref="methodMinimap"
                  block="turbulence"
                />
              </ScrollSync>
              <ScrollSync
                @scroll-sync="handleScrollSync"
                group="method"
                :ref="addScrollElementRef"
              >
                <div class="experimentStream" ref="methodStream">
                  <BuilderStream
                    :stream="fullModeTemplate.method"
                    name="method"
                    :activityRefArray="everyActivity"
                    :template="(temp as Template)"
                    :state="state"
                    @add-activity="addActivity"
                    @remove-activity="removeActivity"
                    @update-activity-title="updateActivityTitle"
                    @handle-drag="handleDragEvent"
                    @drag-start="onDragStart"
                    @update-configuration="updateFullModeConfiguration"
                    @background-change="handleBackgroundChange"
                  />
                </div>
              </ScrollSync>
            </div>
            <ActivityStreamLink />
          </div>
          <div ref="hypothesisWrapper">
            <h3>
              Verification
              <span
                class="hasTooltip hasTooltip--center-right"
                aria-label="Verify your systems state with probes before and after the turbulence phase."
              >
                <HelpCircle />
              </span>
            </h3>
            <div class="experimentStreamWrapper">
              <div class="experimentStreamActions">
                <AssistantButton
                  v-if="possibleRelated.hypothesis.length"
                  :count="possibleRelated.hypothesis.length"
                  @click.prevent="handleRelatedAssistant('hypothesis')"
                />
                <button
                  @click.prevent="openHypothesisSettings"
                  class="button button--icon openExperimentStreamSettings"
                >
                  <SettingsIcon />
                  <span class="screen-reader-text">
                    Open Verification Settings
                  </span>
                </button>
              </div>
              <ScrollSync
                @scroll-sync="handleScrollSync"
                group="hypothesis"
                :ref="addScrollElementRef"
              >
                <BuilderMinimap
                  :stream="fullModeTemplate.hypothesis"
                  ref="hypothesisMinimap"
                  block="verification"
                />
              </ScrollSync>
              <ScrollSync
                @scroll-sync="handleScrollSync"
                group="hypothesis"
                :ref="addScrollElementRef"
              >
                <div class="experimentStream" ref="hypothesisStream">
                  <BuilderStream
                    :stream="fullModeTemplate.hypothesis"
                    name="hypothesis"
                    :activityRefArray="everyActivity"
                    :template="(temp as Template)"
                    @add-activity="addActivity"
                    @remove-activity="removeActivity"
                    @update-activity-title="updateActivityTitle"
                    @handle-drag="handleDragEvent"
                    @drag-start="onDragStart"
                    @update-configuration="updateFullModeConfiguration"
                    @background-change="handleBackgroundChange"
                    @update-tolerance="updateTolerance"
                  />
                  <BuilderHypothesisSettings
                    :is-open="areHypothesisSettingsDisplayed"
                    v-model="(experiment!.runtime!.hypothesis as HypothesisRuntime)"
                    @close="closeHypothesisSettings"
                  />
                </div>
              </ScrollSync>
            </div>
            <ActivityStreamLink />
          </div>
          <div ref="rollbacksWrapper">
            <h3>
              Rollbacks
              <span
                class="hasTooltip hasTooltip--center-right"
                aria-label="Use rollbacks at the end of your experiments to play actions that will put it back in its original state."
              >
                <HelpCircle />
              </span>
            </h3>
            <div class="experimentStreamWrapper">
              <div class="experimentStreamActions">
                <AssistantButton
                  v-if="possibleRelated.rollbacks.length"
                  :count="possibleRelated.rollbacks.length"
                  @click.prevent="handleRelatedAssistant('rollbacks')"
                />
                <button
                  class="button button--icon openExperimentStreamSettings"
                  @click.prevent="openRollbacksSettings"
                >
                  <SettingsIcon />
                  <span class="screen-reader-text">
                    Open Rollbacks Settings
                  </span>
                </button>
              </div>
              <ScrollSync
                @scroll-sync="handleScrollSync"
                group="rollbacks"
                :ref="addScrollElementRef"
              >
                <BuilderMinimap
                  :stream="fullModeTemplate.rollbacks"
                  ref="rollbacksMinimap"
                  block="rollbacks"
                />
              </ScrollSync>
              <ScrollSync
                @scroll-sync="handleScrollSync"
                group="rollbacks"
                :ref="addScrollElementRef"
              >
                <div class="experimentStream" ref="rollbacksStream">
                  <BuilderStream
                    :stream="fullModeTemplate.rollbacks"
                    name="rollbacks"
                    :activityRefArray="everyActivity"
                    :template="(temp as Template)"
                    @add-activity="addActivity"
                    @remove-activity="removeActivity"
                    @update-activity-title="updateActivityTitle"
                    @handle-drag="handleDragEvent"
                    @drag-start="onDragStart"
                    @update-configuration="updateFullModeConfiguration"
                    @background-change="handleBackgroundChange"
                  />
                  <BuilderRollbacksSettings
                    :is-open="areRollbacksSettingsDisplayed"
                    v-model="(experiment!.runtime!.rollbacks as RollbacksRuntime)"
                    @close="closeRollbacksSettings"
                  />
                </div>
              </ScrollSync>
            </div>
            <ActivityStreamLink :last="true" />
          </div>
        </section>
      </div>
      <section v-if="mode && mode.type === 'edit'" class="experimentSave">
        <button
          @click.prevent="createExperiment"
          class="button button--primary"
          :disabled="isSubmitDisabled"
        >
          Save as new
        </button>
        <button
          @click.prevent="editExperiment"
          class="button button--creative"
          :disabled="isSubmitDisabled"
        >
          Save changes
        </button>
      </section>
      <section v-else class="experimentSave">
        <button
          @click.prevent="createExperiment"
          class="button button--primary"
          :disabled="isSubmitDisabled"
        >
          Save experiment
        </button>
      </section>
    </div>
    <div v-if="false">
      <div>EXPERIMENT</div>
      <pre style="background-color: rgb(157, 244, 199); overflow: auto">{{
        JSON.stringify(experiment, null, 2)
      }}</pre>
      <div>END EXPERIMENT</div>
      <div>TEMPLATE</div>
      <pre style="background-color: rgb(221, 208, 236); overflow: auto">{{
        JSON.stringify(fullModeTemplate, null, 2)
      }}</pre>
      <div>END TEMPLATE</div>
    </div>
  </article>
  <NoData
    v-else
    message="We couldn't find an activity or experiment with this ID."
  />
  <ModalWindow
    v-if="isPopulateHypothesisDisplayed"
    :isUnlimited="true"
    :hasCloseButton="true"
    @close="closePopulateHypothesis"
  >
    <template #title>Add a probe to your verification</template>
    <template #content>
      <ActivitySelector
        to="hypothesis"
        :where="populateType!"
        :index="populateIndex!"
        @add-activity="insertActivity"
        @close="closePopulateHypothesis"
      />
    </template>
  </ModalWindow>
  <ModalWindow
    v-if="isPopulateWarmupDisplayed"
    :isUnlimited="true"
    :hasCloseButton="true"
    @close="closePopulateWarmup"
  >
    <template #title>Add an action or probe to your warm up</template>
    <template #content>
      <ActivitySelector
        to="warmup"
        :where="populateType!"
        :index="populateIndex!"
        @add-activity="insertActivity"
        @close="closePopulateWarmup"
      />
    </template>
  </ModalWindow>
  <ModalWindow
    v-if="isPopulateMethodDisplayed"
    :isUnlimited="true"
    :hasCloseButton="true"
    @close="closePopulateMethod"
  >
    <template #title>Add an action or probe to your turbulence</template>
    <template #content>
      <ActivitySelector
        to="method"
        :where="populateType!"
        :index="populateIndex!"
        @add-activity="insertActivity"
        @close="closePopulateMethod"
      />
    </template>
  </ModalWindow>
  <ModalWindow
    v-if="isPopulateRollbacksDisplayed"
    :isUnlimited="true"
    :hasCloseButton="true"
    @close="closePopulateRollbacks"
  >
    <template #title>Add an action to your rollbacks</template>
    <template #content>
      <ActivitySelector
        to="rollbacks"
        :where="populateType!"
        :index="populateIndex!"
        @add-activity="insertActivity"
        @close="closePopulateRollbacks"
      />
    </template>
  </ModalWindow>
  <ModalWindow
    v-if="areRelatedActivitiesDisplayed"
    :specialWidth="84.8"
    :hasCloseButton="true"
    @close="closeRelatedActivities"
  >
    <template #title>Reliably Assistant message</template>
    <template #content>
      <RelatedActivitiesModal
        v-if="areRelatedTemplatesReady"
        :related="(relatedActivitiesTemplates as RelatedTemplates)"
        :origin="experiment!.title"
        @add-activities="addRelatedActivities"
        @discard="closeRelatedActivities"
      />
    </template>
  </ModalWindow>
  <ModalWindow
    v-if="isRelatedAssistantDisplayed"
    :specialWidth="84.8"
    :hasCloseButton="true"
    @close="closeRelatedAssistant"
  >
    <template #title>Reliably Assistant message</template>
    <template #content>
      <RelatedActivitiesModal
        v-if="areRelatedTemplatesReady"
        :related="(relatedActivitiesTemplates as RelatedTemplates)"
        :origin="experiment?.title"
        :destination="relatedActivitiesDestination"
        @add-activities="addRelatedActivities"
        @discard="discardActivitiesFromAssistant"
      />
    </template>
  </ModalWindow>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import { useStore } from "@nanostores/vue";
import { cloneDeep } from "lodash-es";

import type {
  Configuration,
  EnvConfiguration,
  ExperimentDefinition,
  Contributions,
  Probe,
  Action,
  HypothesisRuntime,
  RollbacksRuntime,
} from "@/types/experiments";

import type {
  Template,
  RelatedActivity,
  RelatedTemplates,
} from "@/types/templates";
import type {
  ActivityBlock,
  BuilderWorkflow,
  ChatGptExtension,
  DraggableChangeEvent,
  Notification,
} from "@/types/ui-types";

import {
  template,
  relatedTemplates,
  fetchActionTemplate,
  fetchRelatedActionTemplates,
} from "@/stores/templates";
import { importExperiment, overwriteExperiment } from "@/stores/experiments";
import { addNotification } from "@/stores/notifications";
import { updateConfigurationHolder } from "@/stores/builder";

import {
  defineMode,
  setExperimentFromId,
  setExperimentFromTemplate,
  getRelatedActivities,
  postProcessExperiment,
  addExperimentWorkflow,
  addAssistantQuestions,
  // handleMinimapScroll,
  // performScroll,
} from "@/utils/builder";

import ActivitySelector from "@/components/starters/ActivitySelector.vue";
import ActivityStreamLink from "@/components/starters/ActivityStreamLink.vue";
import BuilderHeader from "@/components/starters/BuilderHeader.vue";
import BuilderHypothesisSettings from "@/components/starters/BuilderHypothesisSettings.vue";
import BuilderMeta from "@/components/starters/BuilderMeta.vue";
import BuilderRollbacksSettings from "@/components/starters/BuilderRollbacksSettings.vue";
import BuilderStream from "@/components/starters/BuilderStream.vue";
import BuilderMinimap from "@/components/starters/BuilderMinimap.vue";
import BuilderAssistant from "@/components/starters/BuilderAssistant.vue";
import RelatedActivitiesModal from "@/components/starters/RelatedActivitiesModal.vue";
import WorkflowOverview from "@/components/starters/WorkflowOverview.vue";
import ProbeTolerance from "@/components/starters/ProbeTolerance.vue";

import AssistantButton from "@/components/_ui/AssistantButton.vue";
import LoadingPlaceholder from "@/components/_ui/LoadingPlaceholder.vue";
import ModalWindow from "@/components/_ui/ModalWindow.vue";
import NoData from "@/components/_ui/NoData.vue";
import ScrollSync from "@/components/_ui/ScrollSync.vue";

import HelpCircle from "@/components/svg/HelpCircle.vue";
import SettingsIcon from "@/components/svg/SettingsIcon.vue";

import { hasProp } from "@/utils/objects";
import type { FieldsState } from "@/types/snapshots";

const isLoading = ref(true);
const mode = ref<{ type: "build" | "edit"; id: string } | null>(null);
const temp = useStore(template);
const starterType = ref<string>("");
const experiment = ref<ExperimentDefinition | null>(null);
const relatedActivities = ref<RelatedActivity[]>([]);
const relatedActivitiesTemplates = useStore(relatedTemplates);
const areRelatedTemplatesReady = ref<boolean>(false);

const fullModeTemplate = ref<BuilderWorkflow>({
  hypothesis: [],
  warmup: [],
  method: [],
  rollbacks: [],
  configuration: {},
});

const possibleRelated = ref<{
  hypothesis: RelatedActivity[];
  warmup: RelatedActivity[];
  method: RelatedActivity[];
  rollbacks: RelatedActivity[];
}>({
  hypothesis: [],
  warmup: [],
  method: [],
  rollbacks: [],
});

async function setup() {
  const { e, type } = await setExperimentFromTemplate(temp.value as Template);
  experiment.value = e;
  starterType.value = type;

  relatedActivities.value = await getRelatedActivities(temp.value as Template);
  areRelatedTemplatesReady.value = true;
  if (relatedActivities.value.length) {
    openRelatedActivities();
  }
}

const setMetaData = () => {
  let title = "Template · Reliably";
  if (temp.value !== undefined && temp.value !== null) {
    title = `Create experiment from template ${temp.value.manifest.metadata.name} · Reliably`;
  }
  document.title = title;
};

function updateTitle(title: string) {
  if (experiment.value !== null) {
    experiment.value.title = title;
  }
}

const metaKey = ref<number>(0);

function updateDescription(description: string) {
  if (experiment.value !== null) {
    experiment.value.description = description;
  }
}

function updateTags(tags: string[]) {
  if (experiment.value !== null) {
    experiment.value.tags = tags;
  }
}

function updateContributions(contributions: Contributions) {
  if (experiment.value !== null) {
    experiment.value.contributions = contributions;
  }
}

function updateAssistant(questions: ChatGptExtension) {
  if (experiment.value!.extensions === undefined) {
    experiment.value!.extensions = [];
  }
  experiment.value!.extensions.push(questions);
}

function handleBackgroundChange(where: string, index: number) {
  if (where === "hypothesis") {
    const background: boolean =
      fullModeTemplate.value.hypothesis[index].background;
    experiment.value!["steady-state-hypothesis"]!.probes![index].background =
      background;
  } else if (where === "warmup") {
    const background: boolean = fullModeTemplate.value.warmup[index].background;
    experiment.value!.method![index].background = background;
  } else if (where === "method") {
    const background: boolean = fullModeTemplate.value.method[index].background;
    // We need to account for the number of activities in the warm up
    const warmupLength: number = fullModeTemplate.value.warmup.length;
    const newIndex: number = index + warmupLength;
    experiment.value!.method![newIndex].background = background;
  } else {
    if (where === "rollbacks") {
      const background: boolean =
        fullModeTemplate.value.rollbacks[index].background;
      experiment.value!.rollbacks![index].background = background;
    }
  }
}

function setRequiredFieldStatus(t: Template): boolean[] {
  const arr: boolean[] = [];
  t.manifest.spec.schema.configuration.forEach((field) => {
    if (field.required) {
      if (field.default !== null && field.default !== "") {
        arr.push(true);
      } else {
        arr.push(false);
      }
    } else {
      arr.push(true);
    }
  });
  return arr;
}
const isSubmitDisabled = computed<boolean>(() => {
  const isHypothesisReady: boolean = fullModeTemplate.value.hypothesis.every(
    (h) => {
      return h.fieldsStatus.every(Boolean);
    }
  );
  if (!isHypothesisReady) {
    return true;
  } else {
    const isMethodReady: boolean = fullModeTemplate.value.method.every((m) => {
      return m.fieldsStatus.every(Boolean);
    });
    if (!isMethodReady) {
      return true;
    } else {
      const isRollbacksReady: boolean = fullModeTemplate.value.rollbacks.every(
        (r) => {
          return r.fieldsStatus.every(Boolean);
        }
      );
      if (!isRollbacksReady) {
        return true;
      } else {
        const isWarmupReady: boolean = fullModeTemplate.value.warmup.every(
          (r) => {
            return r.fieldsStatus.every(Boolean);
          }
        );
        return !isWarmupReady;
      }
    }
  }
});

async function createExperiment() {
  if (experiment.value !== null) {
    postProcessExperiment(experiment.value);
    addExperimentWorkflow(experiment.value, fullModeTemplate.value);
    importExperiment({ experiment: JSON.stringify(experiment.value) });
  }
}

async function editExperiment() {
  if (experiment.value !== null) {
    postProcessExperiment(experiment.value);
    addExperimentWorkflow(experiment.value, fullModeTemplate.value);
    overwriteExperiment(mode.value!.id, {
      experiment: JSON.stringify(experiment.value),
    });
  }
}

const suffixCounter = ref<number>(1);
function initializeForm() {
  if (temp.value !== null) {
    let background = false;
    let suffixPrefix = "M";
    if (starterType.value === "hypothesis") {
      suffixPrefix = "H";
      background = temp.value.manifest.spec.template["steady-state-hypothesis"]?.probes?.at(0)?.background || false;
    } else if (starterType.value === "rollbacks") {
      suffixPrefix = "R";
      background = temp.value.manifest.spec.template.rollbacks?.at(0)?.background || false;
    } else {
      background = temp.value.manifest.spec.template.method?.at(0)?.background || false;
    }
    const suffix: string = `${suffixPrefix}${suffixCounter.value
      .toString()
      .padStart(3, "0")}`;
    const fieldsStatus = setRequiredFieldStatus(temp.value as Template);
    const formInfo = {
      template: temp.value,
      suffix: suffix,
      fieldsStatus: fieldsStatus,
      background,
    };
    if (starterType.value === "method") {
      fullModeTemplate.value.method.push(formInfo);
    } else if (starterType.value === "hypothesis") {
      fullModeTemplate.value.hypothesis.push(formInfo);
    } else if (starterType.value === "rollbacks") {
      fullModeTemplate.value.rollbacks.push(formInfo);
    }
    const existingKeys = Object.keys(experiment.value!.configuration!);
    existingKeys.forEach((key) => {
      const suffixedKey: string = `key_${suffix}`;
      fullModeTemplate.value.configuration![suffixedKey] =
        experiment.value!.configuration![key];
    });
  }
  suffixCounter.value++;
}

const isPopulateHypothesisDisplayed = ref<boolean>(false);
function openPopulateHypothesis() {
  isPopulateHypothesisDisplayed.value = true;
}
function closePopulateHypothesis() {
  isPopulateHypothesisDisplayed.value = false;
}

const areHypothesisSettingsDisplayed = ref<boolean>(false);
function openHypothesisSettings() {
  areHypothesisSettingsDisplayed.value = true;
}
function closeHypothesisSettings() {
  areHypothesisSettingsDisplayed.value = false;
}

const populateIndex = ref<number | null>(null);
const populateType = ref<string | null>(null);

const isPopulateMethodDisplayed = ref<boolean>(false);
function openPopulateMethod() {
  isPopulateMethodDisplayed.value = true;
}
function closePopulateMethod() {
  isPopulateMethodDisplayed.value = false;
}

const isPopulateWarmupDisplayed = ref<boolean>(false);
function openPopulateWarmup() {
  isPopulateWarmupDisplayed.value = true;
}
function closePopulateWarmup() {
  isPopulateWarmupDisplayed.value = false;
}

const isPopulateRollbacksDisplayed = ref<boolean>(false);
function openPopulateRollbacks() {
  isPopulateRollbacksDisplayed.value = true;
}
function closePopulateRollbacks() {
  isPopulateRollbacksDisplayed.value = false;
}

const areRollbacksSettingsDisplayed = ref<boolean>(false);
function openRollbacksSettings() {
  areRollbacksSettingsDisplayed.value = true;
}
function closeRollbacksSettings() {
  areRollbacksSettingsDisplayed.value = false;
}

const areRelatedActivitiesDisplayed = ref<boolean>(false);
function openRelatedActivities() {
  areRelatedActivitiesDisplayed.value = true;
}
function closeRelatedActivities() {
  // Reset related activities
  relatedActivities.value = [];
  areRelatedActivitiesDisplayed.value = false;
}
function addRelatedActivities(ids?: string[], block?: ActivityBlock) {
  // if IDs are provided, we only want to insert those
  if (ids) {
    relatedActivities.value = [];
    ids.forEach((id) => {
      relatedActivities.value.push({
        block: block,
        name: id,
      });
    });
  }
  if (relatedActivities.value) {
    relatedActivities.value.forEach((a) => {
      let index: number = 0;
      if (a.block === "method") {
        index = fullModeTemplate.value.method.length;
      } else if (a.block === "hypothesis") {
        index = fullModeTemplate.value.hypothesis.length;
      } else if (a.block === "rollbacks") {
        index = fullModeTemplate.value.rollbacks.length;
      } else if (a.block === "warmup") {
        index = fullModeTemplate.value.warmup.length;
      }
      handleInsertActivity(
        null,
        a.block!,
        index,
        relatedActivitiesTemplates.value[a.name] as Template
      );
      suffixCounter.value++;
    });
  }
  closeRelatedActivities();
  if (block) {
    discardActivitiesFromAssistant(block, ids);
  }
}

const isRelatedAssistantDisplayed = ref<boolean>(false);
const relatedActivitiesDestination = ref<ActivityBlock | null>(null);
function openRelatedAssistant() {
  isRelatedAssistantDisplayed.value = true;
}
function closeRelatedAssistant() {
  relatedActivities.value = [];
  relatedActivitiesDestination.value = null;
  isRelatedAssistantDisplayed.value = false;
}
function discardActivitiesFromAssistant(block?: ActivityBlock, ids?: string[]) {
  if (block) {
    if (ids) {
      ids.forEach((id) => {
        const index = possibleRelated.value[block].findIndex((r) => {
          return r.name === id;
        });
        if (index > -1) {
          possibleRelated.value[block].splice(index, 1);
        }
      });
    } else {
      possibleRelated.value[block] = [];
    }
  }
  relatedActivities.value = [];
  closeRelatedAssistant();
}

// We sometimes have to hold the configuration to prevent it being overwritten
// when moving items, or when inserting an item before another one.
function holdConfiguration() {
  if (experiment.value?.configuration) {
    updateConfigurationHolder(
      JSON.parse(JSON.stringify(experiment.value?.configuration))
    );
  }
}

// Drag and drop
// moveActivityTo is used to temporarily store an activity destination
// when it's moved from one stream ("block") to another
// Indeed, Draggable first triggers to "added" event , meaning we can store the
// destination first, then triggers the "removed" event, which we use to pick
// the activity
const moveActivityTo = ref<{
  index: number;
  block: ActivityBlock;
} | null>(null);

function handleDragEvent(event: DraggableChangeEvent, block: ActivityBlock) {
  if (event.moved) {
    const moved = event.moved;
    if (block === "method") {
      // We need to account for the number of activities in the warm up
      const warmupLength: number = fullModeTemplate.value.warmup.length;
      const target: number = moved.oldIndex + warmupLength;
      const destination: number = moved.newIndex + warmupLength;
      experiment.value!.method!.splice(
        destination,
        0,
        experiment.value!.method!.splice(target, 1)[0]
      );
    } else if (block === "warmup") {
      experiment.value!.method!.splice(
        moved.newIndex,
        0,
        experiment.value!.method!.splice(moved.oldIndex, 1)[0]
      );
    } else if (block === "hypothesis") {
      experiment.value!["steady-state-hypothesis"]!.probes!.splice(
        moved.newIndex,
        0,
        experiment.value!["steady-state-hypothesis"]!.probes!.splice(
          moved.oldIndex,
          1
        )[0]
      );
    } else if (block === "rollbacks") {
      experiment.value!.rollbacks!.splice(
        moved.newIndex,
        0,
        experiment.value!.rollbacks!.splice(moved.oldIndex, 1)[0]
      );
    }
  }
  if (event.added) {
    const added = event.added;
    moveActivityTo.value = { index: added.newIndex, block: block };
  }
  if (event.removed) {
    const removed = event.removed;
    // First we store the activity and remove it from the old block
    let activity: Probe | Action | null = null;
    if (block === "method") {
      // We need to account for the number of activities in the warm up
      const warmupLength: number = fullModeTemplate.value.warmup.length;
      const target: number = removed.oldIndex + warmupLength;
      activity = experiment.value!.method![target];
      experiment.value!.method!.splice(target, 1);
    } else if (block === "warmup") {
      activity = experiment.value!.method![removed.oldIndex];
      experiment.value!.method!.splice(removed.oldIndex, 1);
    } else if (block === "hypothesis") {
      activity =
        experiment.value!["steady-state-hypothesis"]!.probes![removed.oldIndex];
      // When a probe is removed from the SSH,
      // it doesn't need it's tolerance declartion anymore
      delete activity.tolerance;
      delete fullModeTemplate.value[moveActivityTo.value!.block][
        moveActivityTo.value!.index
      ].toleranceType;
      delete fullModeTemplate.value[moveActivityTo.value!.block][
        moveActivityTo.value!.index
      ].tolerance;
      // We also need to update its fieldStatus by removing the last item
      // which concerns the tolerance
      fullModeTemplate.value[moveActivityTo.value!.block][
        moveActivityTo.value!.index
      ].fieldsStatus.pop();

      experiment.value!["steady-state-hypothesis"]!.probes!.splice(
        removed.oldIndex,
        1
      );
    } else if (block === "rollbacks") {
      activity = experiment.value!.rollbacks![removed.oldIndex];
      experiment.value!.rollbacks!.splice(removed.oldIndex, 1);
    }
    // Then we insert it in the destination block
    if (activity) {
      if (moveActivityTo.value?.block === "warmup") {
        experiment.value!.method!.splice(
          moveActivityTo.value.index,
          0,
          activity
        );
      } else if (moveActivityTo.value?.block === "method") {
        // We need to account for the number of activities in the warm up
        const warmupLength: number = fullModeTemplate.value.warmup.length;
        const target: number = moveActivityTo.value.index + warmupLength;
        experiment.value!.method!.splice(target, 0, activity);
      } else if (moveActivityTo.value?.block === "hypothesis") {
        if (activity.type === "probe") {
          // When a probe is moved to SSH, it requires a tolerance
          fullModeTemplate.value.hypothesis[
            moveActivityTo.value.index
          ].toleranceType = "string";
          fullModeTemplate.value.hypothesis[
            moveActivityTo.value.index
          ].tolerance = "";

          experiment.value!["steady-state-hypothesis"]!.probes!.splice(
            moveActivityTo.value.index,
            0,
            activity
          );
        } else {
          // User tried to move an Action to the SSH
          // We don't modify the experiment
          // But we have to revert the change in the template
          moveBackTemplate(
            "hypothesis",
            moveActivityTo.value.index,
            block,
            removed.oldIndex
          );
          const n: Notification = {
            title: "Actions can't be added to your Verification",
            message:
              "The Verification block can only use Probes. Your Action was put back to its original place.",
            type: "error",
          };
          addNotification(n);
        }
      } else if (moveActivityTo.value?.block === "rollbacks") {
        if (activity.type === "action") {
          experiment.value!.rollbacks!.splice(
            moveActivityTo.value.index,
            0,
            activity
          );
        } else {
          // User tried to move a Probe to the rollbacks
          // We don't modify the experiment
          // But we have to revert the change in the template
          moveBackTemplate(
            "rollbacks",
            moveActivityTo.value.index,
            block,
            removed.oldIndex
          );
          const n: Notification = {
            title: "Probes can't be added to your Rollbacks",
            message:
              "The Rollbacks block can only use Actions. Your Probe was put back to its original place.",
            type: "error",
          };
          addNotification(n);
        }
      }
    }
  }
}

// Save experiment configuration during drag to prevent a reset
const timestamp = ref<number>(0);

function onDragStart() {
  holdConfiguration();
}

// This function is used to revert an activity to it's original block
// when a move was rejected (moving an Action to the Verification block
// or a Probe to the Rollbacks block).
function moveBackTemplate(
  from: ActivityBlock,
  fromIndex: number,
  to: ActivityBlock,
  toIndex: number
) {
  if (from === "hypothesis") {
    const activity = fullModeTemplate.value.hypothesis[fromIndex];
    fullModeTemplate.value[to].splice(toIndex, 0, activity);

    // Reset fields status because moving to SSH adds tolerance fields with a
    // "false" status that is then unreachable
    fullModeTemplate.value[to][moveActivityTo.value!.index].fieldsStatus = [];

    fullModeTemplate.value.hypothesis.splice(fromIndex, 1);
  } else if (from === "rollbacks") {
    const activity = fullModeTemplate.value.rollbacks[fromIndex];
    fullModeTemplate.value[to].splice(toIndex, 0, activity);
    fullModeTemplate.value.rollbacks.splice(fromIndex, 1);
  }
}

const everyActivity = ref<InstanceType<typeof HTMLDetailsElement>[]>([]);
const hypothesisWrapper = ref();
const warmupWrapper = ref();
const methodWrapper = ref();
const rollbacksWrapper = ref();

function addActivity(to: string, where: string, index: number) {
  populateIndex.value = index;
  populateType.value = where;

  if (to === "hypothesis") {
    openPopulateHypothesis();
  } else if (to === "method") {
    openPopulateMethod();
  } else if (to === "rollbacks") {
    openPopulateRollbacks();
  } else if (to === "warmup") {
    openPopulateWarmup();
  }
}

function removeActivity(from: string, index: number) {
  let activity: Action | Probe | null = null;
  if (from === "method") {
    // As warmup and method ("turbulence") activities all end up
    // in the experiment method, with warmup activities first,
    // we have to compute the index of turbulence activity
    // in the experiment method
    const indexInExperiment = index + fullModeTemplate.value.warmup.length;
    activity = experiment.value?.method![index] as Action | Probe;
    fullModeTemplate.value.method.splice(index, 1);
    experiment.value?.method!.splice(indexInExperiment, 1);
  } else if (from === "warmup") {
    activity = experiment.value?.method![index] as Action | Probe;
    fullModeTemplate.value.warmup.splice(index, 1);
    experiment.value?.method!.splice(index, 1);
  } else if (from === "hypothesis") {
    activity = experiment.value?.["steady-state-hypothesis"]!.probes![
      index
    ] as Probe;
    fullModeTemplate.value.hypothesis.splice(index, 1);
    experiment!.value!["steady-state-hypothesis"]!.probes!.splice(index, 1);
  } else if (from === "rollbacks") {
    activity = experiment.value?.rollbacks![index] as Action;
    fullModeTemplate.value.rollbacks.splice(index, 1);
    experiment.value?.rollbacks!.splice(index, 1);
  }
  if (activity !== null) {
    const args = activity?.provider.arguments as { [key: string]: string };
    removeUnusedArguments(args);
  }
}

function updateActivityTitle(title: string, block: string, index: number) {
  if (block === "warmup") {
    experiment.value!.method![index].name = title;
  } else if (block === "method") {
    const indexInExperiment = index + fullModeTemplate.value.warmup.length;
    experiment.value!.method![indexInExperiment].name = title;
  } else if (block === "hypothesis") {
    experiment.value!["steady-state-hypothesis"]!.probes![index].name = title;
  } else if (block === "rollbacks") {
    experiment.value!.rollbacks![index].name = title;
  }
}

function removeUnusedArguments(args: { [key: string]: string }) {
  Object.keys(args).forEach((k) => {
    const argName = args[k].substring(2, args[k].length - 1);
    delete experiment.value?.configuration![argName];
  });
}

async function handleInsertActivity(
  id: string | null,
  to: string,
  index: number,
  template?: Template | null
) {
  // This will be useful if we insert an activity before another one
  holdConfiguration();
  let templateToInsert: Template | null = null;
  if (id) {
    await fetchActionTemplate(id);
    if (temp.value?.manifest.spec.template !== undefined) {
      templateToInsert = temp.value as Template;
    }
  } else if (template) {
    templateToInsert = template;
  }
  if (templateToInsert) {
    const fieldsStatus = setRequiredFieldStatus(templateToInsert);
    const suffixNumber: string = `${suffixCounter.value
      .toString()
      .padStart(3, "0")}`;
    if (to === "method") {
      const activity = JSON.parse(
        JSON.stringify(templateToInsert.manifest.spec.template.method![0])
      );
      fullModeTemplate.value.method.splice(index, 0, {
        template: templateToInsert,
        suffix: `M${suffixNumber}`,
        fieldsStatus: fieldsStatus,
        background: activity.background,
      });
      if (activity.provider.arguments) {
        Object.keys(activity.provider.arguments).forEach((k) => {
          const value = (
            activity.provider.arguments as { [key: string]: string }
          )[k];
          const newValue = [
            value.slice(0, value.length - 1),
            `_M${suffixNumber}`,
            value.slice(value.length - 1),
          ].join(""); // Looks like "${something_M001}"
          (activity.provider.arguments as { [key: string]: string })[k] =
            newValue;
        });
      }
      // As warmup and method ("turbulence") activities all end up
      // in the experiment method, with warmup activities first,
      // we have to compute the index of turbulence activity
      // in the experiment method
      const indexInExperiment = index + fullModeTemplate.value.warmup.length;
      experiment.value?.method!.splice(
        indexInExperiment,
        0,
        activity as Probe | Action
      );
    } else if (to === "warmup") {
      const activity = JSON.parse(
        JSON.stringify(templateToInsert.manifest.spec.template.method![0])
      );
      fullModeTemplate.value.warmup.splice(index, 0, {
        template: templateToInsert,
        suffix: `W${suffixNumber}`,
        fieldsStatus: fieldsStatus,
        background: activity.background,
      });
      if (activity.provider.arguments) {
        Object.keys(activity.provider.arguments).forEach((k) => {
          const value = (
            activity.provider.arguments as { [key: string]: string }
          )[k];
          const newValue = [
            value.slice(0, value.length - 1),
            `_W${suffixNumber}`,
            value.slice(value.length - 1),
          ].join(""); // Looks like "${something_M001}"
          (activity.provider.arguments as { [key: string]: string })[k] =
            newValue;
        });
      }
      experiment.value?.method!.splice(index, 0, activity as Probe | Action);
    } else if (to === "hypothesis") {
      const activity = JSON.parse(
        JSON.stringify(templateToInsert.manifest.spec.template.method![0])
      );
      fullModeTemplate.value.hypothesis.splice(index, 0, {
        template: templateToInsert,
        suffix: `H${suffixNumber}`,
        fieldsStatus: fieldsStatus,
        background: activity.background,
        toleranceType: "string",
        tolerance: "",
      });
      if (activity.provider.arguments) {
        Object.keys(activity.provider.arguments).forEach((k) => {
          const value = (
            activity.provider.arguments as { [key: string]: string }
          )[k];
          const newValue = [
            value.slice(0, value.length - 1),
            `_H${suffixNumber}`,
            value.slice(value.length - 1),
          ].join(""); // Looks like "${something_M001}"
          (activity.provider.arguments as { [key: string]: string })[k] =
            newValue;
        });
      }
      experiment!.value!["steady-state-hypothesis"]!.probes!.splice(
        index,
        0,
        activity as Probe
      );
    } else if (to === "rollbacks") {
      const activity = JSON.parse(
        JSON.stringify(templateToInsert.manifest.spec.template.method![0])
      );
      fullModeTemplate.value.rollbacks.splice(index, 0, {
        template: templateToInsert,
        suffix: `R${suffixNumber}`,
        fieldsStatus: fieldsStatus,
        background: activity.background,
      });
      if (activity.provider.arguments) {
        Object.keys(activity.provider.arguments).forEach((k) => {
          const value = (
            activity.provider.arguments as { [key: string]: string }
          )[k];
          const newValue = [
            value.slice(0, value.length - 1),
            `_R${suffixNumber}`,
            value.slice(value.length - 1),
          ].join(""); // Looks like "${something_M001}"
          (activity.provider.arguments as { [key: string]: string })[k] =
            newValue;
        });
      }
      experiment.value?.rollbacks!.splice(index, 0, activity as Action);
    }
    addAssistantQuestions(templateToInsert, experiment.value!);
    // Force refresh to re-inject existing values
    // that might have been overwritten
    timestamp.value = new Date().valueOf();
  }
  if (id) {
    // Template was inserted by the user, not by the assistant
    // Handle related activities
    if (templateToInsert!.manifest.spec.related) {
      templateToInsert!.manifest.spec.related.forEach((a: RelatedActivity) => {
        // Check if related activity is already present
        const index = possibleRelated.value[a.block!].findIndex((activity) => {
          return activity.name === a.name;
        });
        // If not, add it
        if (index === -1) {
          possibleRelated.value[a.block!].push({
            name: a.name,
            origin: templateToInsert?.manifest.metadata.name,
          });
        }
      });
    }

    // We also want to scroll the stream to put the activity into view
    let wrapper: HTMLElement | null = null;
    if (to === "method") {
      wrapper = methodWrapper.value;
    } else if (to === "warmup") {
      wrapper = warmupWrapper.value;
    } else if (to === "hypothesis") {
      wrapper = hypothesisWrapper.value;
    } else if (to === "rollbacks") {
      wrapper = rollbacksWrapper.value;
    }
    if (wrapper) {
      const stream = wrapper.querySelector(".experimentStream");
      const list = wrapper.querySelector(".streamDraggable")?.children;
      const target = list?.[index];
      let leftPos: number = 0;
      if (target) {
        // This is triggered before actual insertion into DOM. So if adding
        // adding as last item, index target will be undefined
        leftPos = (target as HTMLElement).offsetLeft;
      } else {
        // In this case we'll use the current last item as our target
        // and add the width of an activity
        const activityWidth: number = 460; // 460px / 46rem
        leftPos =
          (list![list!.length - 1] as HTMLElement).offsetLeft + activityWidth;
      }
      setTimeout(() => {
        stream!.scrollTo({
          top: 0,
          left: leftPos,
          behavior: "smooth",
        });
      }, 100); // Let some time for DOM to update. Also, it looks better.
    }
  }
}

async function handleRelatedAssistant(block: ActivityBlock) {
  possibleRelated.value[block].forEach((r) => {
    relatedActivities.value.push({
      name: r.name,
      block: block,
      origin: r.origin,
    });
  });
  relatedActivitiesDestination.value = block;
  await fetchRelatedActionTemplates(relatedActivities.value);
  areRelatedTemplatesReady.value = true;
  if (relatedActivities.value) {
    openRelatedAssistant();
  }
}

async function insertActivity(id: string, to: string) {
  let index: number =
    populateType.value === "before"
      ? populateIndex.value!
      : populateIndex.value! + 1;
  await handleInsertActivity(id, to, index);
  everyActivity.value.forEach((a) => {
    (a as HTMLDetailsElement).removeAttribute("open");
  });
  openActivityForm(to, index);
  suffixCounter.value++;
}

function openActivityForm(where: string, index: number) {
  if (where === "hypothesis") {
    let details = (hypothesisWrapper.value as HTMLElement).querySelectorAll(
      "details"
    );
    if (details[index]) {
      details[index].setAttribute("open", "true");
    }
  } else if (where === "method") {
    let details = (methodWrapper.value as HTMLElement).querySelectorAll(
      "details"
    );
    if (details[index]) {
      details[index].setAttribute("open", "true");
    }
  } else if (where === "warmup") {
    let details = (warmupWrapper.value as HTMLElement).querySelectorAll(
      "details"
    );
    if (details[index]) {
      details[index].setAttribute("open", "true");
    }
  } else if (where === "rollbacks") {
    let details = (rollbacksWrapper.value as HTMLElement).querySelectorAll(
      "details"
    );
    if (details[index]) {
      details[index].setAttribute("open", "true");
    }
  } else if (where === "all") {
    openActivityForm("hypothesis", index);
    openActivityForm("method", index);
    openActivityForm("warmup", index);
    openActivityForm("rollbacks", index);
  }
}

function updateTolerance(
  index: number,
  type: string,
  value: Probe["tolerance"] | null,
  status: { index: number; status: boolean }
) {
  if (experiment.value!["steady-state-hypothesis"]!.probes![index]) {
    if (value === null) {
      delete experiment.value!["steady-state-hypothesis"]!.probes![index]
        .tolerance;
      fullModeTemplate.value.hypothesis[index].toleranceType = "string";
      fullModeTemplate.value.hypothesis[index].tolerance = "";
    } else {
      experiment.value!["steady-state-hypothesis"]!.probes![index].tolerance =
        value;
      fullModeTemplate.value.hypothesis[index].toleranceType = type;
      fullModeTemplate.value.hypothesis[index].tolerance = value;
    }
  }
  fullModeTemplate.value.hypothesis[index].fieldsStatus[status.index] =
    status.status;
}

function updateFullModeConfiguration(
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
    const suffixedKey: string = `${key}_${suffix}`;
    const target = experiment.value.configuration[suffixedKey];
    if (
      hasProp(target as object, "type") &&
      (target as EnvConfiguration).type === "env"
    ) {
      let newKey: string = (
        experiment.value.configuration[suffixedKey] as EnvConfiguration
      ).key;
      if (suffix !== undefined) {
        newKey = newKey.endsWith(suffix) ? newKey : `${newKey}_${suffix}`;
      }
      (experiment.value.configuration[suffixedKey] as EnvConfiguration).key =
        newKey;
      if (value !== null && value !== undefined) {
        (
          experiment.value.configuration[suffixedKey] as EnvConfiguration
        ).default = value;
      } else {
        const evt = (
          experiment.value.configuration[suffixedKey] as EnvConfiguration
        ).env_var_type;
        if (evt === "int" || evt === "float" || evt === "bool") {
          delete (
            experiment.value.configuration[suffixedKey] as EnvConfiguration
          ).default;
        } else if (evt === "str") {
          (
            experiment.value.configuration[suffixedKey] as EnvConfiguration
          ).default = "";
        } else if (evt === "json") {
          (
            experiment.value.configuration[suffixedKey] as EnvConfiguration
          ).default = null;
        } else {
          delete (
            experiment.value.configuration[suffixedKey] as EnvConfiguration
          ).default;
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
        experiment.value.configuration[suffixedKey] = {
          key: `RELIABLY_PARAM_${suffixedKey.toUpperCase()}`,
          type: "env",
          env_var_type: evt,
          default: value,
        };
      } else if (evt === "int" || evt === "float" || evt === "bool") {
        experiment.value.configuration[suffixedKey] = {
          key: `RELIABLY_PARAM_${suffixedKey.toUpperCase()}`,
          type: "env",
          env_var_type: evt,
        };
      } else if (evt === "str") {
        experiment.value.configuration[suffixedKey] = {
          key: `RELIABLY_PARAM_${suffixedKey.toUpperCase()}`,
          type: "env",
          env_var_type: evt,
          default: "",
        };
      } else if (evt === "json") {
        experiment.value.configuration[suffixedKey] = {
          key: `RELIABLY_PARAM_${suffixedKey.toUpperCase()}`,
          type: "env",
          env_var_type: evt,
          default: null,
        };
      } else {
        experiment.value.configuration[suffixedKey] = {
          key: `RELIABLY_PARAM_${suffixedKey.toUpperCase()}`,
          type: "env",
          env_var_type: evt,
        };
      }
    }
  }
  if (suffix) {
    let i: number | null = 0;
    i = fullModeTemplate.value.hypothesis.findIndex((entry) => {
      return entry.suffix === suffix;
    });
    if (i > -1) {
      fullModeTemplate.value.hypothesis[i].fieldsStatus[index] = newStatus;
    } else {
      i = fullModeTemplate.value.warmup.findIndex((entry) => {
        return entry.suffix === suffix;
      });
      if (i > -1) {
        fullModeTemplate.value.warmup[i].fieldsStatus[index] = newStatus;
      } else {
        i = fullModeTemplate.value.method.findIndex((entry) => {
          return entry.suffix === suffix;
        });
        if (i > -1) {
          fullModeTemplate.value.method[i].fieldsStatus[index] = newStatus;
        } else {
          i = fullModeTemplate.value.rollbacks.findIndex((entry) => {
            return entry.suffix === suffix;
          });
          if (i > -1) {
            fullModeTemplate.value.rollbacks[i].fieldsStatus[index] = newStatus;
          }
        }
      }
    }
  }

  updateState();
}

const scrollElements = ref<InstanceType<typeof ScrollSync>[]>([]);

function addScrollElementRef(element: any) {
  if (scrollElements.value.indexOf(element) === -1) {
    scrollElements.value.push(element);
  }
}

function handleScrollSync(
  emitter: string,
  group: string,
  scrollLeft: number,
  scrollWidth: number,
  clientWidth: number,
  offsetWidth: number
) {
  scrollElements.value.forEach((element) => {
    element.reactToScroll(
      emitter,
      group,
      scrollLeft,
      scrollWidth,
      clientWidth,
      offsetWidth
    );
  });
}


const state = ref<FieldsState[]>([]);
function updateState() {
  const c: Configuration | undefined = experiment.value?.configuration;
  if ((c === undefined) || (c === null)) {
    return;
  }
  
  let s: FieldsState[] = [];
  let keys = Object.keys(c);
  Object.entries(c).forEach(([key, value]) => {
    if(value!== null && (value as EnvConfiguration).default !== undefined) {
      s.push({
        val: value.default,
        key: key
      })
    }
  });

  state.value = s;
}


onMounted(async () => {
  isLoading.value = true;
  mode.value = defineMode();
  if (mode.value !== null) {
    if (mode.value.type === "build") {
      await fetchActionTemplate(mode.value.id);
      setMetaData();
      await setup();
      initializeForm();
    } else if (mode.value.type === "edit") {
      const { d, w, total } = await setExperimentFromId(mode.value.id);
      experiment.value = d;
      holdConfiguration();
      if (w) {
        fullModeTemplate.value = cloneDeep(w);
      }
      suffixCounter.value = total;
    }
  }
  isLoading.value = false;
});
</script>

<style lang="scss" scoped>
@use "../../styles/abstracts/mixins" as *;

.builder {
  &__intro {
    max-width: 70ch;

    color: var(--text-color-dim);
    font-size: 2rem;

    span {
      color: var(--text-color);
    }
  }

  > section + section {
    margin-top: var(--space-large);
  }

  &__form {
    position: relative;
  }

  &__view {
    font-size: 1.8rem;
    font-weight: 500;
  }
  .experimentSave {
    display: flex;
    justify-content: center;
  }

  .experimentWorkflow {
    display: flex;
    flex-direction: column;
    gap: var(--space-large);

    > div {
      position: relative;
    }

    h3 {
      display: flex;
      gap: 0.6rem;

      span,
      svg {
        height: 1.8rem;
      }
    }
  }

  .experimentStreamWrapper {
    position: relative;

    padding-bottom: 1rem;

    background-color: var(--section-background);
    border: 0.1rem solid var(--grey-400);
    border-radius: var(--border-radius-m);

    .experimentStreamActions {
      position: absolute;
      top: var(--space-small);
      right: var(--space-small);

      display: flex;
      gap: var(--space-small);
    }
  }

  .experimentStream {
    position: relative;

    min-height: 30rem;
    overflow-x: auto;
    padding: var(--space-large) var(--space-large) 7.2rem;
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
