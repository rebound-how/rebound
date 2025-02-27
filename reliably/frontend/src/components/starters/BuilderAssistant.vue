<template>
  <section class="builderAssistant">
    <h3>
      Reliably Assistant
      <span
        class="hasTooltip hasTooltip--center-right"
        aria-label="Reliably Assistant questions require the OpenAI integration to be added to the plan that will run your experiment."
      >
        <HelpCircle />
      </span>
    </h3>
    <div class="builderAssistant__wrapper">
      <draggable
        class="builderAssistant__list list-reset"
        tag="ul"
        :list="questions.messages"
        handle=".assistantQuestion__handle"
        item-key="name"
        @end="updateAssistant"
      >
        <template #header v-if="questions.messages.length === 0">
          You don't have Assistant questions yet.
        </template>
        <template #item="{ element, index }">
          <li class="assistantQuestion">
            <span class="assistantQuestion__handle"></span>
            <p class="assistantQuestion__content">{{ element.content }}</p>
            <DeleteButton
              @click.prevent="deleteQuestion(index)"
              class="assistantQuestion__delete"
            />
          </li>
        </template>
      </draggable>
      <div class="builderAssistant__form">
        <form v-if="isFormDisplayed" class="form">
          <div class="inputWrapper">
            <label for="newAssistantQuestion">
              Your question to Reliably Assistant
            </label>
            <textarea
              v-model="newQuestion"
              ref="field"
              name="newAssistantQuestion"
              @keyup.enter="addQuestion"
            ></textarea>
            <p class="inputWrapper__help">
              Reliably Assistant questions require the OpenAI integration to be
              added to the plan that will run your experiment.
              <a
                href="https://reliably.com/docs/features/assistant/"
                target="_blank"
                rel="noopener noreferer"
                >Read more</a
              >
            </p>
          </div>
          <div class="inputWrapper">
            <button
              @click.prevent="closeForm"
              class="button button--destructive"
            >
              Cancel
            </button>
            <button
              @click.prevent="addQuestion"
              class="button button--creative"
            >
              Add question
            </button>
          </div>
        </form>
        <div v-else>
          <button class="button button--primary" @click.prevent="askQuestion">
            Ask another question
          </button>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { toRefs, ref, onUpdated, onMounted } from "vue";
import draggable from "vuedraggable";

import DeleteButton from "@/components/_ui/DeleteButton.vue";
import HelpCircle from "@/components/svg/HelpCircle.vue";

import type { ExperimentDefinition, Extension } from "@/types/experiments";
import type { ChatGptExtension, ChatGptMessage } from "@/types/ui-types";

const props = defineProps<{
  experiment: ExperimentDefinition | null;
}>();

const emit = defineEmits<{
  (e: "update-assistant", assistant: ChatGptExtension): void;
}>();

const { experiment } = toRefs(props);

const questions = ref<ChatGptExtension>({
  name: "chatgpt",
  messages: [],
  results: [],
});

const field = ref(null);
const newQuestion = ref<string>("");
const isFormDisplayed = ref<boolean>(false);

function askQuestion() {
  isFormDisplayed.value = true;
}

function addQuestion() {
  if (newQuestion.value !== "") {
    questions.value.messages.push({
      role: "user",
      content: newQuestion.value,
    });
  }
  updateAssistant();
  closeForm();
}

function closeForm() {
  newQuestion.value = "";
  isFormDisplayed.value = false;
}

function deleteQuestion(index: number) {
  questions.value.messages.splice(index, 1);
}

function updateAssistant() {
  emit("update-assistant", questions.value);
}

onUpdated(() => {
  if (isFormDisplayed.value) {
    if (field.value) {
      (field.value! as HTMLTextAreaElement).focus();
    }
  }
});

onMounted(() => {
  if (experiment.value) {
    if (experiment.value.extensions) {
      const chatgpt: Extension | undefined = experiment.value.extensions.find(
        (e: Extension) => {
          return e.name === "chatgpt";
        }
      );
      if (chatgpt) {
        questions.value = chatgpt as ChatGptExtension;
      }
    }
  }
});
</script>

<style lang="scss">
.builderAssistant {
  margin-bottom: var(--space-medium);

  h3 {
    display: flex;
    gap: 0.6rem;

    span,
    svg {
      height: 1.8rem;
    }
  }

  &__wrapper {
    padding: var(--space-small);

    background-color: var(--grey-100);
    border-radius: var(--border-radius-m);
  }

  &__form {
    margin-top: var(--space-medium);

    .inputWrapper {
      max-width: 60rem;

      textarea {
        height: 16rem;
      }
    }
  }

  .assistantQuestion {
    display: flex;
    // align-items: ;
    gap: var(--space-small);
    margin-bottom: var(--space-small);

    &__handle {
      position: relative;

      flex: 0 0 auto;
      height: 3rem;
      width: 3rem;

      cursor: grab;

      &::before,
      &::after {
        content: "";

        position: absolute;
        top: 50%;
        left: 20%;

        display: block;
        height: 0.2rem;
        width: 60%;

        background-color: var(--grey-400);
      }

      &:before {
        transform: translateY(-0.3rem);
      }

      &:after {
        transform: translateY(0.3rem);
      }
    }

    &__content {
      flex: 1 1 auto;
      margin-top: 0.3rem;
    }

    &__delete {
      flex: 0 0 auto;
      height: 3.6rem;
      width: 3.6rem;

      opacity: 0;

      transition: all 0.3s ease-in-out;
    }

    &:hover {
      .assistantQuestion__delete {
        opacity: 1;
      }
    }
  }
}
</style>
