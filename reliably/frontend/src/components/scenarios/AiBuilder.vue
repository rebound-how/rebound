<template>
  <button @click.prevent.stop="openAssistant" class="AiBuilder">
    <div class="AiBuilder__content">
      <div class="AiIcon" :class="{ 'AiIcon--small': isSmall }"></div>
      <div
        class="AiBuilder__description"
        :class="{ 'AiBuilder__description--small': isSmall }"
      >
        <h2>Builder Assistant</h2>
        <p v-if="isSmall">Let the Assistant build your experiments.</p>
        <p v-else>
          Tell the Reliably Assistant what you want to investigate, and let it
          build an experiment for you.
        </p>
      </div>
    </div>
  </button>
  <dialog
    class="AiDialog reliablyDialog reliablyDialog--transparent"
    ref="aiDialog"
    @close="handleAssistantClose"
  >
    <div
      class="AiDialog__content AiDialog__content--initial"
      ref="aiDialogContent"
    >
      <div class="AiDialogItem AiDialogItem--hidden">
        <div class="AiDialogItem__icon">
          <div class="AiIcon AiIcon--small"></div>
        </div>
        <div class="AiDialogItem__content">
          <p class="AiDialogItem__message">
            Welcome to the Reliably Assistant experiment builder.
          </p>
        </div>
      </div>
      <div
        class="AiDialogItem AiDialogItem--hidden"
        v-if="isIntegrationRequired"
      >
        <div class="AiDialogItem__icon">
          <div class="AiIcon AiIcon--small"></div>
        </div>
        <div class="AiDialogItem__content">
          <p class="AiDialogItem__message">
            You don't have an Assistant integration set up yet. Reliably
            Assistant requires an OpenAI account. Let's set up the integration
            now.
          </p>
        </div>
      </div>
      <div
        class="AiDialogItem AiDialogItem--hidden"
        v-if="isIntegrationRequired"
      >
        <div class="AiDialogItem__icon">
          <div class="AiIcon AiIcon--small"></div>
        </div>
        <div class="AiDialogItem__content">
          <form
            class="AiDialogItem__form"
            :class="{ 'AiDialogItem__form--error': isSecretInvalid }"
            @keyup.enter.prevent="submitOpenAiKey"
          >
            <div class="AiDialogItem__inputWrapper">
              <label for="aiSecretKey"> OpenAI secret key </label>
              <div class="promptWrapper">
                <textarea
                  class="AiDialogItem__input"
                  name="aiSecretKey"
                  id="aiSecretKey"
                  v-model="secretKey"
                  :style="`height: ${secretKeyHeight}px`"
                  ref="secretKeyInput"
                  data-enable-grammarly="false"
                  @keydown.enter.prevent
                />
                <button
                  class="promptButton"
                  @click.prevent.stop="submitOpenAiKey"
                  ref="secretKeyButton"
                >
                  ↵
                  <span class="screen-reader-text">Submit OpenAI key</span>
                </button>
              </div>
              <p
                v-if="isSecretStored"
                class="AiDialogItem__help AiDialogItem__help--good"
              >
                <LockIcon /> Your OpenAI key is now safely stored!
              </p>
              <p class="AiDialogItem__help">
                Reliably Assistant uses ChatGPT-4 1106 Preview ("ChatGPT-4
                Turbo"). Using the Assistant does not result in additional
                billing from Reliably but uses OpenAI tokens.
              </p>
              <p
                v-if="isSecretInvalid"
                class="AiDialogItem__help AiDialogItem__help--error"
              >
                OpenAI secret key can't be empty.
              </p>
            </div>
          </form>
        </div>
      </div>
      <div
        class="AiDialogItem AiDialogItem--hidden"
        v-if="assistantIntegrationsList.length > 1"
      >
        <div class="AiDialogItem__icon">
          <div class="AiIcon AiIcon--small"></div>
        </div>
        <div class="AiDialogItem__content">
          <form class="AiDialogItem__form">
            <div class="AiDialogItem__inputWrapper">
              <label for="aiDialogAssistantSelect">
                Select an Assistant Integration
              </label>
              <div class="promptWrapper">
                <select
                  class="AiDialogItem__input AiDialogItem__input--select"
                  name="aiDialogAssistantSelect"
                  id="aiDialogAssistantSelect"
                  v-model="assistantId"
                  @change="revealPromptWrapper"
                >
                  <option
                    v-for="int in assistantIntegrationsList"
                    :key="int.name"
                    :value="int.id"
                  >
                    {{ int.name }}
                  </option>
                </select>
              </div>
              <p class="AiDialogItem__help">
                The Assistant will use your OpenAI key declared in this
                integration.
              </p>
            </div>
          </form>
        </div>
      </div>
      <div
        class="AiDialogItem AiDialogItem--hidden"
        v-if="assistantId !== ''"
        ref="promptWrapper"
      >
        <div class="AiDialogItem__icon">
          <div class="AiIcon AiIcon--small"></div>
        </div>
        <div class="AiDialogItem__content">
          <form class="AiDialogItem__form" @keyup.enter.prevent="askQuestion()">
            <div class="AiDialogItem__inputWrapper">
              <p class="AiDialogItem__message">How can I help you?</p>
              <label class="screen-reader-text" for="aiDialogQuestion">
                Ask your question
              </label>
              <div class="promptWrapper">
                <textarea
                  class="AiDialogItem__input"
                  name="aiDialogQuestion"
                  id="aiDialogQuestion"
                  v-model="prompt"
                  :style="`height: ${promptHeight}px`"
                  ref="input"
                  data-enable-grammarly="false"
                  @keydown.enter.prevent
                />
                <button
                  class="promptButton"
                  @click.prevent.stop="askQuestion()"
                  ref="questionButton"
                >
                  ↵
                  <span class="screen-reader-text">Submit question</span>
                </button>
              </div>
              <p class="AiDialogItem__help">
                Describe an experiment idea. The more specific you are about
                your system, the more useful the results will be.<br />
                Eg. I need to verify the impact of latency on an application
                served in Google Cloud Platform Cloud Run behind a GCP Load
                Balancer
              </p>
            </div>
          </form>
        </div>
      </div>
      <div class="AiDialogItem" v-if="isTagsSelectionDisplayed">
        <div class="AiDialogItem__icon">
          <div class="AiIcon AiIcon--small"></div>
        </div>
        <div class="AiDialogItem__content">
          <form class="AiDialogItem__form" @keyup.enter.prevent="askQuestion()">
            <div class="AiDialogItem__inputWrapper">
              <p class="AiDialogItem__message">
                Tags help me build an experiment with activities that are more
                suitable to your system. Select one or more tags and press
                <span class="key">Enter&nbsp;↵</span> to continue.
              </p>
              <div class="AiDialogItem__tags">
                <div v-for="(tag, index) in tagsList" :key="tag.tag">
                  <input
                    type="checkbox"
                    :id="`aiTag-${index}`"
                    :value="tag.tag"
                    v-model="tags"
                  />
                  <label :for="`aiTag-${index}`">{{ tag.label }}</label>
                </div>
              </div>
              <p class="AiDialogItem__help">
                Keep in mind that selecting to many tags might limit the pool of
                activities the assistant can choose from. Be specific, but not
                too specific.
              </p>
            </div>
            <button
              class="promptButton promptButton--hidden"
              @click.prevent.stop="doNothing"
              ref="tagsButton"
            >
              ↵
              <span class="screen-reader-text"></span>
            </button>
          </form>
        </div>
      </div>
      <div class="AiDialogItem" v-if="isTagsWarningDisplayed">
        <div class="AiDialogItem__icon">
          <div class="AiIcon AiIcon--small"></div>
        </div>
        <div class="AiDialogItem__content">
          <form class="AiDialogItem__form">
            <p class="AiDialogItem__message">
              Are you sure you want to continue without tags? This might result
              in an experiment that is not as suited to your system. Select one
              or more tags above and press
              <span class="key">Enter&nbsp;↵</span>.<br />
              Alternatively, you can press
              <span class="key">Enter&nbsp;↵</span> to continue without tags.
            </p>
            <button
              class="promptButton promptButton--hidden"
              @click.prevent.stop="askQuestion()"
              ref="warningButton"
            >
              ↵
              <span class="screen-reader-text">Submit without tags</span>
            </button>
          </form>
        </div>
      </div>
      <div class="AiDialogItem" v-if="isQuestionAsked">
        <div class="AiDialogItem__icon">
          <div class="AiIcon AiIcon--small"></div>
        </div>
        <div class="AiDialogItem__content">
          <p class="AiDialogItem__message">
            Please wait while I create your experiment.
          </p>
        </div>
      </div>
      <div class="AiDialogItem" v-if="s && s.suggestion">
        <ol class="list-reset AiDialog__suggestions">
          <li v-for="(item, index) in s.suggestion.items" :key="item.name">
            <SuggestionItem
              :item="(item as ScenarioItem)"
              :index="index"
              :total="s.suggestion.items.length"
            />
          </li>
        </ol>
      </div>
      <div class="AiDialogItem" v-if="isAnswerComplete">
        <div class="AiDialogItem__icon">
          <div class="AiIcon AiIcon--small"></div>
        </div>
        <div class="AiDialogItem__content">
          <p class="AiDialogItem__message">
            Your experiment is almost ready. Let's fill in some required
            parameters.
          </p>
        </div>
      </div>
      <template
        v-for="(item, itemIndex) in displayedSuggestions"
        :key="item.name"
      >
        <template v-if="item.count">
          <div class="AiDialogItem">
            <div class="AiDialogItem__icon">
              <div class="AiIcon AiIcon--small"></div>
            </div>
            <div class="AiDialogItem__content">
              I need
              <strong>{{ item.count }}</strong>
              parameters for <ScenarioActivityInfo :activity="item" />.
            </div>
          </div>
          <div
            class="AiDialogItem AiDialogItem--parameter"
            v-for="(parameter, paramIndex) in item.parameters"
            :key="parameter.item_name + paramIndex"
          >
            <div class="AiDialogItem__icon">
              <div class="AiIcon AiIcon--small"></div>
            </div>
            <div class="AiDialogItem__content">
              <ScenarioParameter
                :parameter="parameter"
                :item-index="itemIndex"
                :param-index="paramIndex"
                :history="parametersHistory[parameter.parameter.key]"
                @update-parameter="handleParameter"
              />
            </div>
          </div>
        </template>
        <NoParameterPlaceholder
          v-else
          :item="item"
          @go-to-next="addNextParameter"
        />
      </template>
      <div class="AiDialogItem" v-if="isExperimentBuilding">
        <div class="AiDialogItem__icon">
          <div class="AiIcon AiIcon--small"></div>
        </div>
        <div class="AiDialogItem__content">
          <p class="AiDialogItem__message">
            Almost there! Please wait while I create your experiment.
          </p>
        </div>
      </div>
      <div class="AiDialogItem" v-if="isExperimentReady">
        <div class="AiDialogItem__icon">
          <div class="AiIcon AiIcon--small"></div>
        </div>
        <div class="AiDialogItem__content">
          <form
            class="AiDialogItem__form"
            @keyup.enter.prevent="saveExperiment"
          >
            <div class="AiDialogItem__inputWrapper">
              <p class="AiDialogItem__message">
                Your experiment is ready! What do you want to name it?
              </p>
              <label class="screen-reader-text" for="aiDialogQuestion">
                Experiment title
              </label>
              <div class="promptWrapper">
                <textarea
                  class="AiDialogItem__input"
                  name="aiDialogQuestion"
                  id="aiDialogQuestion"
                  v-model="experimentTitle"
                  :style="`height: ${titleHeight}px`"
                  ref="title"
                  data-enable-grammarly="false"
                  @keydown.enter.prevent
                />
                <button
                  class="promptButton"
                  @click.prevent.stop="saveExperiment"
                  ref="titleButton"
                >
                  ↵
                  <span class="screen-reader-text"
                    >Submit experiment title</span
                  >
                </button>
              </div>
              <p class="AiDialogItem__help">
                Use a title that will help you understand what the experiment
                does, and what was the reason for creating it.<br />
                Example: Add latency to a network link of a pod to simulate a
                high traffic on the auth service
              </p>
            </div>
          </form>
        </div>
      </div>
      <div class="AiDialogItem" v-if="isExperimentSaved">
        <div class="AiDialogItem__icon">
          <div class="AiIcon AiIcon--small"></div>
        </div>
        <div class="AiDialogItem__content">
          <p class="AiDialogItem__message">
            We're all set! What do you want to do now?
          </p>
          <ul class="AiDialogItem__options list-reset">
            <li>
              <button
                @click.prevent.stop="startCreatingPlan"
                class="button button--primary button--large"
              >
                Run experiment
              </button>
            </li>
            <li>
              <a
                :href="`/experiments/workflows/build/?edit=${returnedId}`"
                class="button button--creative button--large"
              >
                Edit experiment
              </a>
            </li>
            <li>
              <a
                :href="`/experiments/view/?id=${returnedId}`"
                class="button button--light button--large"
              >
                View experiment
              </a>
            </li>
          </ul>
        </div>
      </div>
      <div class="AiDialogItem" v-if="isDeploymentSelectDisplayed">
        <div class="AiDialogItem__icon">
          <div class="AiIcon AiIcon--small"></div>
        </div>
        <div class="AiDialogItem__content">
          <form class="AiDialogItem__form">
            <div class="AiDialogItem__inputWrapper">
              <label for="aiDialogDeploymentSelect">
                Select a deployment
              </label>
              <div class="promptWrapper">
                <select
                  class="AiDialogItem__input AiDialogItem__input--select"
                  name="aiDialogDeploymentSelect"
                  id="aiDialogDeploymentSelect"
                  v-model="deploymentId"
                  ref="deploySelect"
                  @change="displayEnvironmentSelect"
                >
                  <option v-for="d in deploys" :key="d.id" :value="d.id">
                    {{ `${formatDeploymentType(d.type)} ${d.name}` }}
                  </option>
                </select>
              </div>
              <p class="AiDialogItem__help">
                This is where your experiment will run.
              </p>
            </div>
          </form>
        </div>
      </div>
      <div class="AiDialogItem" v-if="isEnvironmentSelectDisplayed">
        <div class="AiDialogItem__icon">
          <div class="AiIcon AiIcon--small"></div>
        </div>
        <div class="AiDialogItem__content">
          <form class="AiDialogItem__form">
            <div class="AiDialogItem__inputWrapper">
              <label for="aiDialogEnironmentSelect">
                Select an environment
              </label>
              <div class="promptWrapper">
                <select
                  class="AiDialogItem__input AiDialogItem__input--select"
                  name="aiDialogEnvironmentSelect"
                  id="aiDialogEnvironmentSelect"
                  v-model="environmentId"
                  ref="envSelect"
                  @change="displayRun"
                >
                  <option
                    v-for="e in environmentsList"
                    :key="e.id"
                    :value="e.id"
                  >
                    {{ e.name }}
                  </option>
                </select>
              </div>
              <p class="AiDialogItem__help">
                This is where your environment variables and secrets are stored.
              </p>
            </div>
          </form>
        </div>
      </div>
      <div class="AiDialogItem" v-if="isRunDisplayed">
        <div class="AiDialogItem__icon">
          <div class="AiIcon AiIcon--small"></div>
        </div>
        <div class="AiDialogItem__content">
          <p class="AiDialogItem__message">Your experiment is ready to run!</p>
          <ul class="AiDialogItem__options list-reset">
            <li>
              <button
                @click.prevent.stop="savePlan"
                class="button button--primary button--large"
              >
                Run experiment now
              </button>
            </li>
            <li>
              <a
                :href="`/experiments/workflows/build/?edit=${returnedId}`"
                class="button button--creative button--large"
              >
                Edit experiment
              </a>
            </li>
            <li>
              <a
                :href="`/experiments/view/?id=${returnedId}`"
                class="button button--light button--large"
              >
                View experiment
              </a>
            </li>
          </ul>
        </div>
      </div>
      <div class="AiDialogItem" v-if="isPlanScheduled">
        <div class="AiDialogItem__content">
          <ScenarioExecution :plan-id="planId" />
        </div>
      </div>
      <div class="AiDialogItem" v-if="isLoaderDisplayed">
        <div class="AiDialogItem__loader">
          <LoaderPuff />
        </div>
      </div>
    </div>
    <button
      class="button button--icon AiDialog__close"
      @click.prevent.stop="closeAssistant"
    >
      <span class="screen-reader-text">Close Assistant</span>
      <XIcon />
    </button>
    <ScenarioNotificationHandler @place-error="placeError" />
  </dialog>
</template>

<script setup lang="ts">
import { toRefs, ref, computed, nextTick, watch } from "vue";
import { useStore } from "@nanostores/vue";
import dayjs from "dayjs";

import {
  scenario,
  createScenario,
  fetchScenario,
  setScenarioExperiment,
  resetStoredScenario,
  pushError,
} from "@/stores/scenarios";
import { template, fetchActionTemplate } from "@/stores/templates";
import { importExperiment } from "@/stores/experiments";
import {
  integrations,
  fetchIntegrations,
  createIntegration,
} from "@/stores/integrations";
import { deployments, fetchDeployments } from "@/stores/deployments";
import { environments, fetchEnvironments } from "@/stores/environments";
import { createPlan } from "@/stores/plans";

import { formatDeploymentType } from "@/utils/deployments";

import SuggestionItem from "@/components/scenarios/SuggestionItem.vue";
import ScenarioParameter from "@/components/scenarios/ScenarioParameter.vue";
import NoParameterPlaceholder from "@/components/scenarios/NoParameterPlaceholder.vue";
import ScenarioExecution from "@/components/scenarios/ScenarioExecution.vue";
import ScenarioActivityInfo from "@/components/scenarios/ScenarioActivityInfo.vue";
import ScenarioNotificationHandler from "@/components/scenarios/ScenarioNotificationHandler.vue";

import LoaderPuff from "@/components/svg/LoaderPuff.vue";
import LockIcon from "@/components/svg/LockIcon.vue";
import XIcon from "@/components/svg/XIcon.vue";
import type {
  ScenarioItem,
  ScenarioQuery,
  UiScenarioParameter,
  UiScenarioActivity,
  ParameterHistory,
  ScenarioError,
} from "@/types/scenarios";
import type {
  ExperimentDefinition,
  Action,
  Probe,
  PythonProvider,
} from "@/types/experiments";
import type { Template } from "@/types/templates";
import type { Integration } from "@/types/integrations";
import type { Deployment, DeploymentForPlanForm } from "@/types/deployments";
import type { PlanCreate } from "@/types/plans";
import type { TemplateActivity } from "@/types/ui-types";

const props = defineProps<{
  isSmall?: boolean;
}>();
const { isSmall } = toRefs(props);

const localMode = ref<boolean>(false);

const aiDialog = ref<HTMLDialogElement | null>(null);
const aiDialogContent = ref<HTMLElement | null>(null);
const promptWrapper = ref<HTMLElement | null>(null);
const questionButton = ref<HTMLElement | null>(null);
const tagsButton = ref<HTMLElement | null>(null);
const warningButton = ref<HTMLElement | null>(null);

const isLoaderDisplayed = computed<boolean>(() => {
  if (
    isIntegrationCreating.value ||
    (isQuestionAsked.value && !isAnswerComplete.value) ||
    (isExperimentBuilding.value && !isExperimentReady.value) ||
    isExperimentSaving.value ||
    isPlanDataFetching.value
  ) {
    return true;
  } else {
    return false;
  }
});

const isIntegrationRequired = ref<boolean>(false);
const assistantIntegrationsList = ref<Integration[]>([]);
const intsTotal = ref<number>(0);
const intsArray = ref<number[]>([]);
const totalPages = ref<number>(1);
const ints = useStore(integrations);
const assistantId = ref<string>("");

async function getInitialIntegrations() {
  await fetchIntegrations(1);
  intsTotal.value = ints.value.total;
  totalPages.value = Math.ceil(intsTotal.value / 10);
  ints.value.integrations.forEach((int) => {
    if (
      int.vendor &&
      int.vendor === "reliably" &&
      int.provider === "assistant"
    ) {
      assistantIntegrationsList.value.push(int as Integration);
    }
  });
  await lookForMoreAssistantIntegrations();
}
async function lookForMoreAssistantIntegrations() {
  if (totalPages.value > 1) {
    intsArray.value = Array.from(Array(totalPages.value + 1), (x, i) => i);
    // Returns [0, 1, ..., totalPages.value]
    intsArray.value.shift();
    intsArray.value.shift(); // Faster than splice!
    // Now we have [2, 3, ... totalPages.value]
  }
  for (let page of intsArray.value) {
    await fetchIntegrations(page);
    ints.value.integrations.forEach((int) => {
      if (
        int.vendor &&
        int.vendor === "reliably" &&
        int.provider === "assistant"
      ) {
        assistantIntegrationsList.value.push(int as Integration);
      }
    });
  }
  if (assistantIntegrationsList.value.length === 0) {
    isIntegrationRequired.value = true;
    nextTick(() => {
      secretKeyInput.value!.focus();
    });
  } else if (assistantIntegrationsList.value.length === 1) {
    assistantId.value = assistantIntegrationsList.value[0].id!;
    nextTick(() => {
      input.value!.focus();
    });
  }
  // assistantIntegrationsList.value.length > 1 is handled in the template
}

function revealPromptWrapper() {
  nextTick(() => {
    promptWrapper.value!.classList.remove("AiDialogItem--hidden");
  });
}

const secretKeyInput = ref<HTMLElement | null>(null);
const secretKey = ref<string>("");
const isSecretInvalid = ref<boolean>(false);
const isIntegrationCreating = ref<boolean>(false);
const isSecretStored = ref<boolean>(false);
async function submitOpenAiKey() {
  if (secretKey.value !== "") {
    isSecretInvalid.value = false;
    isIntegrationCreating.value = true;
    const d: string = dayjs().format("YYYY-MM-DDTHH:mm:ssZ");
    const int: Integration = {
      name: "Assistant integration - " + d,
      provider: "assistant",
      vendor: "reliably",
      environment: {
        name: "openai",
        envvars: [
          {
            var_name: "OPENAI_MODEL",
            value: "gpt-4-1106-preview",
          },
        ],
        secrets: [
          {
            key: "openai-key",
            var_name: "OPENAI_API_KEY",
            value: secretKey.value,
          },
        ],
      },
    };
    const newIntegration = await createIntegration(int, true);
    if (localMode.value) {
      assistantId.value = "azerty";
      revealPromptWrapper();
    } else if (newIntegration) {
      assistantId.value = newIntegration.id!;
      revealPromptWrapper();
    }
    secretKey.value = secretKey.value.replace(/./g, "•");
    secretKeyInput.value!.setAttribute("disabled", "");
    isSecretStored.value = true;
    isIntegrationCreating.value = false;
  } else {
    isSecretInvalid.value = true;
  }
}

const s = useStore(scenario);

const prompt = ref<string>("");

const tagsList: { tag: string; label: string }[] = [
  { tag: "aws", label: "AWS" },
  { tag: "google cloud", label: "Google Cloud" },
  { tag: "kubernetes", label: "Kubernetes" },
  { tag: "on-premise", label: "On-Premise" },
];
const tags = ref<string[]>([]);
const isTagsSelectionDisplayed = ref<boolean>(false);
const isTagsWarningDisplayed = ref<boolean>(false);

async function openAssistant() {
  if (aiDialog.value !== null) {
    aiDialog.value.showModal();

    document.body.classList.add("no-scroll");

    await getInitialIntegrations();

    setTimeout(() => {
      aiDialog.value!.classList.remove("reliablyDialog--transparent");
    }, 100);

    setTimeout(() => {
      aiDialog.value!.classList.remove("AiDialog__content--hidden");
    }, 400);

    startAssistant();
  }
}

function closeAssistant() {
  if (aiDialog.value !== null) {
    aiDialog.value.close();

    handleAssistantClose();
  }
}

function startAssistant() {
  const items = aiDialogContent.value?.querySelectorAll(".AiDialogItem");
  if (items && items.length) {
    let index: number = 0;
    items.forEach((item) => {
      setTimeout(() => {
        item.classList.remove("AiDialogItem--hidden");
      }, index * 800);
      index++;
    });
  }
}

const isQuestionAsked = ref<boolean>(false);
const isAnswerComplete = ref<boolean>(false);
function doNothing() {}
function askQuestion(str?: string) {
  if (prompt.value !== "") {
    input.value?.setAttribute("disabled", "");
    aiDialogContent.value?.classList.remove("AiDialog__content--initial");
    if (!isTagsSelectionDisplayed.value) {
      isTagsSelectionDisplayed.value = true;
      nextTick(() => {
        tagsButton.value?.focus();
      });
    } else if (tags.value.length) {
      isQuestionAsked.value = true;
      sendQuery();
    } else if (!isTagsWarningDisplayed.value) {
      isTagsWarningDisplayed.value = true;
      nextTick(() => {
        warningButton.value?.focus();
      });
    } else {
      isQuestionAsked.value = true;
      experimentDescription.value += prompt.value;
      sendQuery();
    }
    nextTick(() => {
      scrollToBottom();
    });
  }
}

async function sendQuery() {
  const query: ScenarioQuery = {
    question: prompt.value,
    tags: tags.value,
    integration_id: assistantId.value,
  };
  if (localMode.value) {
    await fetchScenario("1", true);
  } else {
    await createScenario(query);
  }
  if (s.value !== null) {
    if (s.value.suggestion === undefined) {
      pushError({
        title: "Something went wrong when creating your experiment",
        message: "Improper server response.",
      });
    } else {
      refreshInterval = setInterval(refreshScenario, 3000);
    }
  }
  nextTick(() => {
    scrollToBottom();
  });
}

var refreshInterval: ReturnType<typeof setInterval>;
async function refreshScenario(): Promise<void> {
  if (s.value !== null) {
    if (localMode.value) {
      const newId: string = (parseInt(s.value.id) + 1).toString();
      await fetchScenario(newId, true);
    }
    await fetchScenario(s.value.id, true);
    if (s.value.completed) {
      clearInterval(refreshInterval);
      populateParametersArray();
      addNextParameter();
      isAnswerComplete.value = true;
    }
  }
  nextTick(() => {
    scrollToBottom();
  });
}

const parametersArray = ref<UiScenarioActivity[]>([]);
const currentSuggestion = ref<UiScenarioActivity | null>(null);
const displayedSuggestions = ref<UiScenarioActivity[]>([]);
const displayedParameters = ref<UiScenarioParameter[]>([]);
const parametersHistory = ref<ParameterHistory>({});

function populateParametersArray() {
  let activityCounter: number = 0;
  s.value!.suggestion.items.forEach((item) => {
    parametersArray.value.push({
      name: item.name,
      type: item.type,
      count: item.parameters.length,
      parameters: [],
    });
    if (item.parameters.length) {
      item.parameters.forEach((parameter) => {
        parametersArray.value[activityCounter].parameters.push({
          item_name: item.name,
          item_ref: item.ref,
          item_type: item.type,
          parameter: parameter,
          user_value: null,
        });
      });
    }
    activityCounter++;
    // Use this oppportunity to update the experiment description
    experimentDescription.value += ` ${activityCounter}. ${item.purpose}`;
  });
}

const isExperimentBuilding = ref<boolean>(false);
const isExperimentReady = ref<boolean>(false);
const isExperimentSaving = ref<boolean>(false);
const isExperimentSaved = ref<boolean>(false);

function addNextParameter() {
  let shouldProceed: boolean = false;
  if (
    currentSuggestion.value === null ||
    currentSuggestion.value.parameters.length === 0
  ) {
    // Try adding a suggestion
    const nextItem = parametersArray.value.shift();
    if (nextItem) {
      // A new suggestion exists
      currentSuggestion.value = nextItem;
      displayedSuggestions.value.push({
        name: currentSuggestion.value.name,
        type: currentSuggestion.value.type,
        count: currentSuggestion.value.count,
        parameters: [],
      });
      shouldProceed = true;
      // Suggestion added: proceed
    } else {
      // No more suggestions: build
      isExperimentBuilding.value = true;
      buildExperiment();
    }
  } else {
    shouldProceed = true;
  }
  if (shouldProceed) {
    // Let's get next parameter in current suggestion
    const next = currentSuggestion.value!.parameters.shift();
    // Next is undefined if suggestion requires no parameters
    if (next !== undefined) {
      displayedSuggestions.value[
        displayedSuggestions.value.length - 1
      ].parameters.push(next!);
    }
  }
  nextTick(() => {
    scrollToBottom();
  });
}

function handleParameter(
  value: string | number | boolean | object,
  key: string,
  itemIndex: number,
  paramIndex: number,
  reactivated?: boolean
) {
  displayedSuggestions.value[itemIndex].parameters[paramIndex].user_value =
    value;
  if (parametersHistory.value[key]) {
    const index = parametersHistory.value[key].findIndex((el) => {
      return el.value === value;
    });
    if (index === -1) {
      parametersHistory.value[key].push({
        value: value,
        type: displayedSuggestions.value[itemIndex].parameters[paramIndex]
          .parameter.type,
      });
    }
  } else {
    parametersHistory.value[key] = [
      {
        value: value,
        type: displayedSuggestions.value[itemIndex].parameters[paramIndex]
          .parameter.type,
      },
    ];
  }
  if (reactivated) {
    nextTick(() => {
      scrollToBottom();
    });
    const last = aiDialogContent.value!.lastElementChild;
    if (last!.classList.contains("AiDialogItem--parameter")) {
      (
        last!.querySelector(".scenarioParameter__input")! as HTMLTextAreaElement
      ).focus();
    }
  } else {
    addNextParameter();
  }
}

const e = ref<ExperimentDefinition>({
  version: "1.0.0",
  title: "",
  description: "",
  contributions: {
    availability: "none",
    latency: "none",
    security: "none",
    errors: "none",
  },
  tags: [],
  configuration: {},
  extensions: [
    {
      name: "reliablyui",
      workflow: {
        hypothesis: [],
        warmup: [],
        method: [],
        rollbacks: [],
      },
      builder: {
        question: "",
      },
    },
  ],
  method: [],
  "steady-state-hypothesis": {
    title: "Verification",
    probes: [],
  },
  rollbacks: [],
  runtime: {
    hypothesis: {
      strategy: "default",
      frequency: 1,
      fail_fast: false,
    },
    rollbacks: {
      strategy: "default",
    },
  },
});
const t = useStore(template);
const experimentTitle = ref<string>("");
const experimentDescription = ref<string>("");

const counter = ref<number>(1);

async function buildExperiment() {
  e.value.description = experimentDescription.value;

  await buildMethod();

  isExperimentReady.value = true;

  nextTick(() => {
    title.value!.focus();
    scrollToBottom();
  });
}

async function buildMethod() {
  // We start by resetting, because if the user edits a value in a parameter
  // field, it calls buildExperiment() again, thus resulting in all activities
  // being added another time
  // Resetting prevents this behavior
  e.value.method = [];
  e.value.extensions![0].workflow.method = [];
  for (const [index, item] of s.value!.suggestion.items.entries()) {
    await fetchActionTemplate(item.ref);
    if (t.value) {
      const temp = t.value.manifest.spec.template;
      const suffix = `M${counter.value.toString().padStart(3, "0")}`;
      let activity: Action | Probe | null = null;
      if (temp.method && temp.method.length > 0) {
        activity = JSON.parse(JSON.stringify(temp.method[0])) as Action | Probe;
      } else if (
        temp["steady-state-hypothesis"] &&
        temp["steady-state-hypothesis"].probes &&
        temp["steady-state-hypothesis"].probes.length > 0
      ) {
        activity = JSON.parse(
          JSON.stringify(temp["steady-state-hypothesis"].probes[0])
        ) as Action | Probe;
      } else if (temp.rollbacks && temp.rollbacks.length > 0) {
        activity = JSON.parse(JSON.stringify(temp.rollbacks[0])) as
          | Action
          | Probe;
      }
      if (activity !== null) {
        let workflowTemplate: TemplateActivity = {
          template: t.value as Template,
          suffix: suffix,
          background: false,
          fieldsStatus: [],
        };
        activity!.name = item.name;
        const args = Object.keys(activity!.provider.arguments!);
        if (args.length) {
          args.forEach((arg) => {
            let param = undefined;
            if (displayedSuggestions.value[index].parameters.length) {
              param = displayedSuggestions.value[index].parameters.find((p) => {
                if (p.item_name === undefined) {
                  return false;
                } else {
                  return p.item_name === item.name && p.parameter.key === arg;
                }
              });
            }
            if (param) {
              const suffixedParam = `${arg}_${suffix}`;

              e.value.configuration![suffixedParam] = {
                type: "env",
                key: `RELIABLY_${suffixedParam.toUpperCase()}`,
                default: param.user_value,
                env_var_type: param.parameter.type,
              };

              (
                (activity!.provider as PythonProvider).arguments as {
                  [key: string]: string;
                }
              )[arg] = "${" + suffixedParam + "}";

              workflowTemplate.fieldsStatus.push(true);
            } else {
              delete (
                (activity!.provider as PythonProvider).arguments as {
                  [key: string]: string;
                }
              )[arg];

              workflowTemplate.fieldsStatus.push(false);
            }
          });
        }
        e.value.method!.push(activity!);
        e.value.extensions![0].workflow.method.push(workflowTemplate);
      }
    }
    counter.value++;
  }
}

const returnedId = ref<string>("");

async function saveExperiment() {
  isExperimentSaving.value = true;
  title.value!.setAttribute("disabled", "");
  let t = `Experiment - ${dayjs().format()}`;
  if (experimentTitle.value !== "") {
    t = experimentTitle.value;
  }
  e.value.title = t;
  let experimentId: string | undefined = undefined;
  if (localMode.value) {
    experimentId = "7";
  } else {
    experimentId = await importExperiment(
      { experiment: JSON.stringify(e.value) },
      false,
      true
    );
  }
  if (experimentId) {
    returnedId.value = experimentId;
    await setScenarioExperiment(s.value!.id, experimentId);
    isExperimentSaving.value = false;
    isExperimentSaved.value = true;
  }

  nextTick(() => {
    scrollToBottom();
  });
}

// When creating plan
const isPlanDataFetching = ref<boolean>(false);
const isDeploymentSelectDisplayed = ref<boolean>(false);
const isEnvironmentSelectDisplayed = ref<boolean>(false);
const isRunDisplayed = ref<boolean>(false);
const deploymentId = ref<string>("");
const environmentId = ref<string>("");

const deploySelect = ref<HTMLElement | null>(null);
const envSelect = ref<HTMLElement | null>(null);

const deploys = ref<DeploymentForPlanForm[]>([]);
const totalDeploys = ref<number>(0);
const deploysPage = ref<number>(1);
const getDeployments = async () => {
  await fetchDeployments(deploysPage.value);
  let latestDeploys = useStore(deployments);
  totalDeploys.value = latestDeploys.value.total;
  latestDeploys.value.deployments.forEach((d: Deployment) => {
    if (d.definition.type !== "github") {
      deploys.value.push({
        name: d.name,
        id: d.id!,
        type: d.definition.type,
      });
    }
  });
  deploysPage.value++;
};
const getMoreDeployments = async () => {
  for (let i: number = 1; 10 * i < totalDeploys.value; i++) {
    await getDeployments();
  }
};

const environmentsList = ref<{ name: string; id: string }[]>([]);

async function getEnvironments() {
  let fetched: { name: string; id: string }[] = [];
  await fetchEnvironments(1);
  let stored = useStore(environments);
  stored.value.environments.forEach((e) => {
    fetched.push({ name: e.name, id: e.id! });
  });
  if (stored.value.total > 10) {
    let rounds = Math.floor(stored.value.total / 10);
    if (stored.value.total % 10 > 0) {
      rounds++;
    }
    let pages: number[] = [];
    for (var i = 2; i <= rounds; i++) {
      pages.push(i);
    }
    for (const page of pages) {
      await fetchEnvironments(page);
      let stored = useStore(environments);
      stored.value.environments.forEach((e) => {
        fetched.push({ name: e.name, id: e.id! });
      });
    }
  }
  environmentsList.value = [...fetched];
}

async function startCreatingPlan() {
  isPlanDataFetching.value = true;
  await getDeployments();
  await getMoreDeployments();
  await getEnvironments();
  isPlanDataFetching.value = false;
  isDeploymentSelectDisplayed.value = true;
  nextTick(() => {
    deploySelect.value!.focus();
    scrollToBottom();
  });
}

function displayEnvironmentSelect() {
  if (isEnvironmentSelectDisplayed.value === false) {
    isEnvironmentSelectDisplayed.value = true;
    nextTick(() => {
      envSelect.value!.focus();
      scrollToBottom();
    });
  }
}

function displayRun() {
  if (isRunDisplayed.value === false) {
    isRunDisplayed.value = true;
    nextTick(() => {
      deploySelect.value!.focus();
      scrollToBottom();
    });
  }
}

const planId = ref<string>("");
const isPlanScheduled = ref<boolean>(false);

async function savePlan() {
  let newPlan: PlanCreate = {
    title: e.value.title,
    environment: {
      provider: "reliably_cloud",
      id: environmentId.value,
    },
    deployment: {
      deployment_id: deploymentId.value,
    },
    schedule: {
      type: "now",
    },
    experiments: [returnedId.value],
    integrations: [],
  };
  const p = await createPlan(newPlan, true);
  if (p) {
    planId.value = p;
    isPlanScheduled.value = true;
    nextTick(() => {
      scrollToBottom();
    });
  }
}

// Utils
const input = ref<HTMLElement | null>(null);
const promptHeight = ref<number>(0);
function updatePromptHeight() {
  if (input.value) {
    input.value.style.height = "5px";
    input.value.style.height = input.value.scrollHeight + "px";
  }
}
watch(prompt, () => {
  updatePromptHeight();
});

const secretKeyHeight = ref<number>(0);
function updateSecretKeyHeight() {
  if (secretKeyInput.value) {
    secretKeyInput.value.style.height = "5px";
    secretKeyInput.value.style.height =
      secretKeyInput.value.scrollHeight + "px";
  }
}
watch(secretKey, () => {
  updateSecretKeyHeight();
});

const title = ref<HTMLElement | null>(null);
const titleHeight = ref<number>(0);
function updateTitleHeight() {
  if (title.value) {
    title.value.style.height = "5px";
    title.value.style.height = title.value.scrollHeight + "px";
  }
}
watch(experimentTitle, () => {
  updateTitleHeight();
});

function scrollToBottom(str?: string) {
  if (aiDialogContent.value!.scrollHeight > window.innerHeight) {
    const top = Math.max(
      aiDialogContent.value!.getBoundingClientRect().bottom,
      aiDialogContent.value!.scrollHeight
    );
    aiDialog.value!.scrollTo({
      top: top,
      left: 0,
      behavior: "smooth",
    });
  }
}

function handleAssistantClose() {
  document.body.classList.remove("no-scroll");

  // Integration
  isIntegrationRequired.value = false;
  assistantIntegrationsList.value = [];
  intsTotal.value = 0;
  intsArray.value = [];
  totalPages.value = 1;
  assistantId.value = "";

  secretKey.value = "";
  isSecretInvalid.value = false;
  isIntegrationCreating.value = false;
  isSecretStored.value = false;

  // Reset values
  prompt.value = "";
  tags.value = [];

  parametersArray.value = [];
  currentSuggestion.value = null;
  displayedSuggestions.value = [];
  displayedParameters.value = [];
  parametersHistory.value = {};

  e.value = {
    version: "1.0.0",
    title: "",
    description: "",
    contributions: {
      availability: "none",
      latency: "none",
      security: "none",
      errors: "none",
    },
    tags: [],
    configuration: {},
    extensions: [
      {
        name: "reliablyui",
        workflow: {
          hypothesis: [],
          warmup: [],
          method: [],
          rollbacks: [],
        },
        builder: {
          question: "",
        },
      },
    ],
    method: [],
    "steady-state-hypothesis": {
      title: "Verification",
      probes: [],
    },
    rollbacks: [],
    runtime: {
      hypothesis: {
        strategy: "default",
        frequency: 1,
        fail_fast: false,
      },
      rollbacks: {
        strategy: "default",
      },
    },
  };

  // Reset states
  isTagsSelectionDisplayed.value = false;
  isTagsWarningDisplayed.value = false;
  isQuestionAsked.value = false;

  isExperimentBuilding.value = false;
  isExperimentReady.value = false;
  isExperimentSaving.value = false;
  isExperimentSaved.value = false;

  experimentTitle.value = "";
  counter.value = 1;
  returnedId.value = "";

  // Plan
  isPlanDataFetching.value = false;
  isDeploymentSelectDisplayed.value = false;
  isEnvironmentSelectDisplayed.value = false;
  isRunDisplayed.value = false;
  deploymentId.value = "";
  environmentId.value = "";

  deploys.value = [];
  totalDeploys.value = 0;
  deploysPage.value = 1;

  environmentsList.value = [];

  // Reset store
  resetStoredScenario();
}

function placeError(e: ScenarioError) {
  const errorAsString: string = `<div class="AiDialogItem AiDialogItem--error">
    <div class="AiDialogItem__content">
      <p>
        <strong>${e.title}</strong><br/>
        ${e.message}<br/>
        Please try again later.
      </p>
    </div>
  </div>`;
  const lastItem: Element | null = aiDialogContent.value!.lastElementChild;
  if (lastItem === null) {
    aiDialogContent.value!.insertAdjacentHTML("beforeend", errorAsString);
  } else if (lastItem.querySelector(".AiDialogItem__loader") !== null) {
    // lastItem is a loader: insert before
    lastItem.insertAdjacentHTML("beforebegin", errorAsString);
  } else {
    // No loader: insert after current lastItem
    lastItem.insertAdjacentHTML("afterend", errorAsString);
  }
  // Stop builder resfresh, as we probably won't recover
  clearInterval(refreshInterval);
}
</script>

<style lang="scss">
.AiBuilder {
  position: relative;

  height: 100%;
  overflow: hidden;
  padding: 0.5rem;

  background-color: var(--pink-100);
  border: none;
  border-radius: var(--border-radius-s);
  cursor: pointer;

  text-align: left;

  &::before {
    content: "";

    position: absolute;
    top: 0;
    left: 0;
    z-index: 2;

    display: block;
    height: 100%;
    width: 100%;

    background: var(--pink-500) url("/images/assistant-button.webp") no-repeat
      top left / 100% auto;
    border-radius: var(--border-radius-s);

    transform: translate(-100%, -100%);
    transition: transform 0.3s ease-in-out;
  }

  &:hover {
    &::before {
      transform: translate(0, 0);
    }

    .AiIcon {
      animation: 10s infinite animateIcon ease-in-out;
    }
  }

  &__content {
    position: relative;
    z-index: 3;

    display: flex;
    gap: var(--space-small);
    align-items: center;
    height: 100%;
    padding: var(--space-small);

    background-color: var(--pink-100);
    border: 0.3rem solid transparent;
    border-radius: calc(var(--border-radius-s) - 0.3rem);
  }

  &__description {
    h2 {
      margin-bottom: 0.6rem;

      color: var(--pink-800);
    }

    p {
      color: var(--pink-700);
      font-size: 1.4rem;
    }
  }
}

.AiDialog {
  padding: var(--space-small);

  color: var(--text-color);

  &__content {
    width: 100%;
    max-width: 80rem;
    margin-right: auto;
    margin-left: auto;

    transform: translateY(0);
    transition: transform 0.5s ease-in-out;

    &--initial {
      transform: translateY(calc(50vh - 50%));
    }

    .AiDialogItem {
      display: flex;
      gap: var(--space-small);
      margin-bottom: var(--space-large);

      opacity: 1;

      font-size: 2.4rem;

      transform: translateY(0);
      transition: all 0.3s ease-in-out 0.7s;

      &--hidden {
        opacity: 0;

        transform: translateY(10rem);
      }

      &--error {
        padding: var(--space-small);

        background-color: var(--red-100);
        border-radius: var(--border-radius-m);

        color: var(--red-600);

        strong {
          color: var(--statusColor-ko-bright);
        }
      }

      &__content {
        width: 100%;
      }

      &__icon {
        padding-top: 0.3rem;
      }

      &__form {
        position: relative;

        .promptWrapper {
          position: relative;

          display: flex;
        }

        .promptButton {
          all: unset;

          position: absolute;
          right: 0.7rem;
          bottom: 0.8rem;

          box-sizing: border-box;
          display: block;
          height: 3.4rem;
          width: 3.4rem;
          padding: 0.6rem 0.6rem 0.3rem;

          border: 0.1rem solid var(--grey-400);
          border-radius: var(--border-radius-s);
          background-color: var(--grey-200);
          cursor: pointer;

          color: var(--text-color);
          font-size: 1.6rem;
          text-align: center;

          &:hover {
            background-color: var(--green-400);
            border-color: var(--green-500);

            color: var(--green-900);
          }

          &--hidden {
            position: absolute;

            height: 0;
            width: 0;

            opacity: 0;
          }

          &:focus {
            outline: 0.2rem solid red;
          }
        }

        &--error {
          textarea {
            outline: 0.3rem solid var(--statusColor-ko);
            outline-offset: 0.2rem;
          }
        }
      }

      &__input {
        overflow: hidden;
        padding: 0.6rem 4.6rem 0.6rem 1rem;
        min-height: 4.8rem;
        width: 100%;

        background-color: var(--grey-100);
        border: 0.1rem solid var(--grey-400);
        border-radius: var(--border-radius-s);
        resize: none;

        font-family: var(--body-font);
        font-size: 2.4rem;
        line-height: 1.5;
      }

      &__tags {
        position: relative;
        display: flex;
        flex-wrap: wrap;
        gap: 0.6rem var(--space-small);

        label {
          padding: 0.3rem 0.6rem;

          background-color: var(--grey-100);
          border: 0.1rem solid var(--grey-400);
          border-radius: var(--border-radius-s);

          font-size: 2rem;
        }

        input {
          position: absolute;

          height: 0;
          width: 0;

          opacity: 0;

          &:checked + label {
            background-color: var(--pink-100);
            border-color: var(--pink-400);

            color: var(--pink-800);
          }
        }

        button {
          visibility: hidden;
          outline: 0.2rem solid red;
        }

        &:hover {
          button {
            visibility: visible;
            outline: 0.2rem solid red;
          }
        }
      }

      &__help {
        color: var(--text-color-dim);
        font-size: 1.6rem;

        &--error {
          color: var(--statusColor-ko);
        }

        &--good {
          color: var(--statusColor-ok);

          svg {
            height: 1.6rem;
            margin-top: 0.2rem;
          }
        }
      }

      &__options {
        display: flex;
        gap: var(--space-small);
        margin-top: var(--space-small);
      }

      &__loader {
        display: grid;
        place-items: center;
        width: 100%;

        svg {
          height: 4.4rem;

          stroke: var(--grey-700);
        }
      }
    }
  }

  &__suggestions {
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: var(--space-large);
    margin-right: auto !important;
    margin-left: auto !important;

    > li + li {
      position: relative;

      &::before {
        content: "";

        position: absolute;
        top: 0;
        left: 50%;

        display: block;
        height: var(--space-large);
        width: 0.2rem;

        background-color: var(--grey-400);

        transform: translate(-50%, -100%);
      }
    }
  }

  .AiDialog__close {
    position: fixed;
    top: var(--space-small);
    right: var(--space-small);
  }
}

.key {
  padding: 0.1em 0.2em;

  background-color: var(--blue-100);
  border: 0.1rem solid var(--blue-400);
  border-radius: var(--border-radius-s);

  color: var(--blue-600);
  font-size: 0.8em;
}

@keyframes animateIcon {
  0% {
    transform: rotate(0) scale(1);
  }

  2% {
    transform: rotate(360deg) scale(1);
  }

  4% {
    transform: rotate(360deg) scale(1.1);
  }

  6% {
    transform: rotate(360deg) scale(0.9);
  }

  8% {
    transform: rotate(360deg) scale(1);
  }

  100% {
    transform: rotate(360deg) scale(1);
  }
}
</style>
