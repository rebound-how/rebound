<template>
  <div class="builderMeta">
    <div class="builderMeta__description">
      <h2>Description</h2>
      <div v-if="!isDescriptionEditable">
        <p>{{ experimentDescription }}</p>
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
    <div class="builderMeta__tags">
      <h2>Tags</h2>
      <form class="form">
        <ExperimentTags v-if="isMounted" v-model="tags" :hideLabel="true" />
      </form>
    </div>
    <div class="builderMeta__contributions">
      <h2>Contributions</h2>
      <form class="form">
        <ExperimentContributions
          v-model="contributions"
          :hideLabel="true"
          :key="contributionsKey"
        />
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { toRefs, ref, watch, onMounted } from "vue";
import type { ExperimentDefinition, Contributions } from "@/types/experiments";

import ExperimentTags from "@/components/experiments/ExperimentTags.vue";
import ExperimentContributions from "@/components/experiments/ExperimentContributions.vue";

const props = defineProps<{
  experiment: ExperimentDefinition | null;
}>();

const isMounted = ref<boolean>(false);
const { experiment } = toRefs(props);

const emit = defineEmits<{
  (e: "update-description", description: string): void;
  (e: "update-tags", tags: string[]): void;
  (e: "update-contributions", contributions: Contributions): void;
}>();

// Description
const experimentDescription = ref<string>("");
const isDescriptionEditable = ref<boolean>(false);

function toggleEditDescription() {
  isDescriptionEditable.value = !isDescriptionEditable.value;
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
// End description

// Tags
const tags = ref<string[]>([]);

function getExperimentTags() {
  const t: string[] | undefined = experiment.value?.tags;
  if (t !== undefined) {
    tags.value = t;
  }
}

watch(tags, () => {
  emit("update-tags", tags.value);
});
// End tags

// Contributions
const contributionsKey = ref<number>(0);

const contributions = ref<Contributions>({
  availability: "none",
  latency: "none",
  security: "none",
  errors: "none",
});

function getExperimentContributions() {
  const c: Contributions | undefined = experiment.value?.contributions;
  if (c !== undefined && Object.keys(c).length) {
    contributions.value = c;
  }
  contributionsKey.value++;
  emit("update-contributions", contributions.value);
}
watch(contributions, () => {
  emit("update-contributions", contributions.value);
});
//End contributions

onMounted(() => {
  isMounted.value = false;
  getExperimentDescription();
  getExperimentTags();
  getExperimentContributions();
  isMounted.value = true;
});
</script>

<style lang="scss">
.builderMeta {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-medium);
  margin: var(--space-medium) 0;
  padding: var(--space-small);

  background-color: var(--section-background);
  border-radius: var(--border-radius-m);

  &__description {
    button {
      margin-top: var(--space-small);
    }

    textarea {
      height: 16rem;
    }
  }
}
</style>
