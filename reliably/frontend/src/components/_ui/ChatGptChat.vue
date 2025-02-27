<template>
  <ul class="chatGpt list-reset" ref="messages">
    <template v-for="(entry, index) in content.messages" :key="index">
      <li v-if="content.results.length > index">
        <details class="chatGpt__entry">
          <summary class="chatGpt__question">
            <div class="chatGpt__iconWrapper">
              <div class="chatGpt__icon chatGpt__icon--user">
                {{ initial }}
              </div>
            </div>
            <p>{{ entry.content }}</p>
            <div class="chatGpt__chevron">
              <ChevronDown />
            </div>
          </summary>
          <div class="chatGpt__answer">
            <div class="chatGpt__iconWrapper">
              <div class="chatGpt__icon chatGpt__icon--assistant">
                <OpenAi />
              </div>
            </div>
            <MarkdownRenderer
              :src="content.results[index].choices[0].message.content"
            />
          </div>
          <div class="chatGpt__disclaimer">
            <p>
              Generated
              <TimeAgo
                :timestamp="content.results[index].created"
                :epoch="true"
              />
              by
              <a
                href="https://reliably.com/docs/features/reliably-gpt"
                target="_blank"
                rel="noopener noreferer"
                >Reliably GPT <span class="alpha">Alpha</span></a
              >
              using {{ gptModel(content.results[index].model) }}.
            </p>
          </div>
        </details>
      </li>
    </template>
  </ul>
</template>

<script setup lang="ts">
import { toRefs, computed, ref, onMounted, onBeforeUnmount } from "vue";
import type { ChatGptExtension } from "@/types/ui-types";

import { useStore } from "@nanostores/vue";
import { organizationName } from "@/stores/user";

import MarkdownRenderer from "@/components/_ui/MarkdownRenderer.vue";
import TimeAgo from "@/components/_ui/TimeAgo.vue";
import OpenAi from "@/components/svg/OpenAi.vue";
import ChevronDown from "@/components/svg/ChevronDown.vue";

const props = defineProps<{
  content: ChatGptExtension;
}>();

const { content } = toRefs(props);

const currentOrganizationName = useStore(organizationName);
const initial = computed<string>(() => {
  return currentOrganizationName.value.charAt(0);
});

function gptModel(model: string): string {
  if (model.startsWith("o1-mini")) {
    return "o1-mini";
  } else if (model.startsWith("o1")) {
    return "o1";
  } else if (model.startsWith("gpt-4o")) {
    return "GPT-4o";
  } else {
    return model;
  }
}

const messages = ref<HTMLInputElement | null>(null);
const wereDetailsClosed = ref<boolean[]>([]);
function handleBeforePrint() {
  let details = messages.value!.querySelectorAll("li details");
  details.forEach((d) => {
    if (!d.hasAttribute("open")) {
      d.setAttribute("open", "");
      wereDetailsClosed.value.push(true);
    } else {
      wereDetailsClosed.value.push(false);
    }
  });
}
function handleAfterPrint() {
  let details = messages.value!.querySelectorAll("li details");
  details.forEach((d, index) => {
    if (wereDetailsClosed.value[index]) {
      d.removeAttribute("open");
    }
  });
  wereDetailsClosed.value = [];
}

onMounted(() => {
  window.addEventListener("beforeprint", handleBeforePrint);
  window.addEventListener("afterprint", handleAfterPrint);
});

onBeforeUnmount(() => {
  window.removeEventListener("beforeprint", handleBeforePrint);
  window.removeEventListener("afterprint", handleAfterPrint);
});
</script>

<style lang="scss">
.chatGpt {
  padding: var(--space-small) !important;

  background-color: var(--section-background);
  border-radius: var(--border-radius-s);

  > li + li {
    margin-top: var(--space-medium);
    padding-top: var(--space-medium);

    border-top: 0.1rem solid var(--grey-400);
  }

  &__entry {
    &[open] {
      .chatGpt__chevron {
        svg {
          transform: rotate(0);
        }
      }
    }
  }

  &__question,
  &__answer,
  &__disclaimer {
    display: grid;
    grid-template-columns: 3.6rem 70ch 1fr;
    gap: var(--space-medium);
  }

  &__question {
    cursor: pointer;

    font-weight: 700;
  }

  &__chevron {
    display: flex;
    justify-content: flex-end;

    color: var(--text-color-bright);

    svg {
      height: 2.4rem;

      transform: rotate(-90deg);
      transition: transform 0.2s ease-in-out;
    }
  }

  &__answer {
    margin-top: var(--space-medium);
  }

  &__icon {
    display: grid;
    place-content: center;
    height: 3.6rem;
    width: 3.6rem;

    border-radius: var(--border-radius-s);

    &--user {
      background-color: var(--pink-100);

      color: var(--pink-700);
      text-transform: uppercase;
    }

    &--assistant {
      background-color: #000;

      svg {
        height: 2.4rem;
      }

      path {
        fill: #fff;
      }
    }
  }

  &__disclaimer {
    margin-top: var(--space-medium);

    p {
      grid-column-start: 2;

      color: var(--text-color-dim);
      font-size: 1.4rem;

      time {
        text-decoration: underline dashed;
      }

      a {
        color: var(--text-color);

        .alpha {
          padding: 0.2rem 0.4rem;
          background-color: var(--red-100);
          border-radius: var(--border-radius-s);

          color: var(--red-700);
          font-size: 1rem;
          font-weight: 500;
          text-transform: uppercase;
        }
      }
    }
  }
}
</style>
