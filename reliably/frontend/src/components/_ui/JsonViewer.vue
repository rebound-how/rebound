<template>
  <div
    class="jsonViewer"
    :class="{
      'jsonViewer--noPadding': noPadding,
      'jsonViewer--wrap': forceWrap,
    }"
  >
    <div class="jsonViewer__switcher">
      <button
        class="jsonViewerSwitch"
        :class="{ 'jsonViewerSwitch--active': displayedLang === 'json' }"
        @click.prevent="switchLangTo('json')"
      >
        JSON
      </button>
      <button
        class="jsonViewerSwitch"
        :class="{ 'jsonViewerSwitch--active': displayedLang === 'yaml ' }"
        @click.prevent="switchLangTo('yaml')"
      >
        YAML
      </button>
    </div>
    <div
      class="jsonViewer__content"
      :class="{ displayed: displayedLang === 'json' }"
      v-html="highlightedJson"
    ></div>
    <div
      class="jsonViewer__content jsonViewer__content--yaml"
      :class="{ displayed: displayedLang === 'yaml' }"
      v-html="highlightedYaml"
    ></div>
    <div class="jsonViewer__clipboard" v-if="isSupported">
      <button
        v-if="displayedLang === 'json'"
        @click="copy(json)"
        class="button button--icon clipboard"
        :class="{ 'clipboard--success': copied }"
      >
        <ClipboardIcon />
      </button>
      <button
        v-if="displayedLang === 'yaml'"
        @click="copy(rawYaml)"
        class="button button--icon clipboard"
        :class="{ 'clipboard--success': copied }"
      >
        <ClipboardIcon />
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { toRefs, ref, onMounted } from "vue";
import { createHighlighter } from "shiki";
import * as yaml from "js-yaml";
import { useClipboard } from "@vueuse/core";
import ClipboardIcon from "@/components/svg/ClipboardIcon.vue";

const props = defineProps<{
  json: string;
  noPadding?: boolean;
  forceWrap?: boolean;
}>();
const { json } = toRefs(props);

const rawYaml = ref<string>("");

const displayedLang = ref<string>("json");
function switchLangTo(l: string): void {
  if (l === "json" || l === "yaml") {
    displayedLang.value = l;
  }
}

const highlightedJson = ref<string>("");
const highlightedYaml = ref<string>("");

const highlightJson = async () => {
  const highlighter = await createHighlighter({
    themes: ["min-light"],
    langs: ["json"],
  });

  highlightedJson.value = highlighter.codeToHtml(json.value, { lang: "json", theme: "min-light" });
};

const dumpYaml = () => {
  rawYaml.value = yaml.dump(JSON.parse(json.value));
};

const highlightYaml = async () => {
  const highlighter = await createHighlighter({
    themes: ["min-light"],
    langs: ["yaml"],
  });

  highlightedYaml.value = highlighter.codeToHtml(rawYaml.value, {
    lang: "yaml",
    theme: "min-light"
  });
};

const { copy, copied, isSupported } = useClipboard();

onMounted(async () => {
  await highlightJson();
  dumpYaml();
  await highlightYaml();
});
</script>

<style lang="scss">
.jsonViewer {
  position: relative;

  padding: var(--space-small);

  &--noPadding {
    padding: 0;
  }

  &__switcher {
    display: flex;
    gap: 0.6rem;

    @media print {
      display: none;
    }

    .jsonViewerSwitch {
      padding: 0.4rem;

      background-color: var(--lang-switcher-label);
      border: none;
      border-radius: var(--border-radius-s);
      cursor: pointer;

      color: var(--text-color-dim);
      font-size: 1.4rem;

      &:hover {
        background-color: var(--lang-switcher-label-hover);

        color: var(--text-color-bright);
      }

      &--active {
        background-color: var(--lang-switcher-label-active);
        cursor: default;

        color: var(--text-color);
      }
    }
  }

  &__content {
    height: 0;
    visibility: hidden;

    &.displayed {
      height: auto;
      visibility: visible;
    }
  }

  .clipboard {
    position: absolute;
    top: var(--space-small);
    right: var(--space-small);

    visibility: hidden;

    &--success {
      background-color: var(--statusColor-ok);

      color: white;
    }
  }

  .shiki {
    margin-bottom: 0;
    overflow-x: auto;
  }

  &:hover {
    .clipboard {
      visibility: visible;
    }
  }

  &--wrap {
    .shiki {
      white-space: pre-wrap;
    }
  }
}
</style>
