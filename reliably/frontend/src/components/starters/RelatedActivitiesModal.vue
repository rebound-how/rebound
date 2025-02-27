<template>
  <div class="relatedActivities">
    <p v-if="destination">
      We found some activities that could be used in your
      {{ formattedDestination }}.
    </p>
    <p v-else>
      Experiments using <strong>{{ origin }}</strong> often use the following
      related activities.
    </p>
    <p v-if="destination">
      Select the ones you want to add to your experiment.
    </p>
    <p v-else>Do you want to add them to your experiment?</p>
    <form v-if="destination" class="form">
      <ul class="list-reset">
        <li v-for="id in templateIds" :key="id">
          <input
            type="checkbox"
            :name="id"
            :id="id"
            :value="id"
            v-model="selectedIds"
          />
          <label :for="id">
            <ActivityHeader :activity="getTemplateMeta(related[id])" />
            <div class="relatedActivities__checked">
              <CheckIcon />
            </div>
          </label>
        </li>
      </ul>
    </form>
    <ul v-else class="list-reset">
      <li v-for="id in templateIds" :key="id">
        <ActivityHeader :activity="getTemplateMeta(related[id])" />
      </li>
    </ul>
    <div v-if="destination" class="relatedActivities__actions">
      <button class="button button--destructiveLight" @click.prevent="discard">
        Discard all
      </button>
      <button
        class="button button--primary"
        @click.prevent="add"
        :disabled="isAddMultipleDisabled"
      >
        Add
        <span v-if="selectedIds.length">
          {{
            selectedIds.length > 1
              ? `${selectedIds.length} activities`
              : `1 activity`
          }}
        </span>
      </button>
    </div>
    <div v-else class="relatedActivities__actions">
      <button class="button button--destructiveLight" @click.prevent="discard">
        Discard
      </button>
      <button class="button button--primary" @click.prevent="add">
        Add activities
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { toRefs, ref, computed, onMounted } from "vue";

import type { Template, RelatedTemplates } from "@/types/templates";
import type { Activity, ActivityBlock } from "@/types/ui-types";

import ActivityHeader from "@/components/starters/ActivityHeader.vue";
import CheckIcon from "@/components/svg/CheckIcon.vue";

const props = defineProps<{
  origin?: string;
  destination?: ActivityBlock | null;
  related: RelatedTemplates;
}>();
const { origin, destination, related } = toRefs(props);

const emit = defineEmits<{
  // (e: "addActivities", block?: ActivityBlock): void;
  (e: "addActivities", activities?: string[], block?: ActivityBlock): void;
  (e: "discard", block?: ActivityBlock): void;
}>();

const templateIds = ref<string[]>([]);
const formattedDestination = computed<string>(() => {
  if (destination && destination.value) {
    switch (destination.value) {
      case "warmup":
        return "Warm Up";
      case "hypothesis":
        return "Hypothesis";
      case "method":
        return "Turbulence";
      case "rollbacks":
        return "Rollbacks";
      default:
        break;
    }
  }
  return "";
});

const selectedIds = ref<string[]>([]);
const isAddMultipleDisabled = computed<boolean>(() => {
  return selectedIds.value.length === 0;
});

function getTemplateMeta(t: Template): Activity {
  const metadata = t.manifest.metadata;
  const template = t.manifest.spec.template;

  const id = metadata.name;
  const name = metadata.name;
  const target = metadata.labels[0];
  const category = metadata.labels[metadata.labels.length - 1];
  let type = "";
  const description = template.title;
  let module = "";

  if (template.method && template.method.length) {
    type = template.method[0].type;
  } else if (
    template["steady-state-hypothesis"] &&
    template["steady-state-hypothesis"].probes &&
    template["steady-state-hypothesis"].probes.length
  ) {
    type = template["steady-state-hypothesis"].probes[0].type;
  } else if (template.rollbacks && template.rollbacks.length) {
    type = template.rollbacks[0].type;
  }
  module = type;

  return {
    id: id,
    name: name,
    target: target,
    category: category,
    type: type,
    description: description,
    module: module,
  };
}

function add() {
  if (destination?.value) {
    emit("addActivities", selectedIds.value, destination.value);
  } else {
    emit("addActivities");
  }
}

function discard() {
  if (destination?.value) {
    emit("discard", destination.value);
  } else {
    emit("discard");
  }
}

onMounted(() => {
  templateIds.value = Object.keys(related.value);
});
</script>

<style lang="scss" scoped>
.relatedActivities {
  min-height: 33rem;
  min-width: 40rem;
  padding: var(--space-small);

  > ul,
  > form > ul {
    display: flex;
    flex-wrap: wrap;
    gap: var(--space-small);
    margin-top: var(--space-medium);
    max-width: 90rem;

    > li {
      position: relative;

      flex: 0 1 auto;
      padding: var(--space-small);
      width: 40rem;

      background-color: var(--section-background);
      border-radius: var(--border-radius-m);

      input {
        position: absolute;

        height: 0;
        width: 0;

        opacity: 0;
      }

      label {
        cursor: pointer;
        opacity: 0.5;

        transition: all 0.2s ease-in-out;

        &:hover {
          opacity: 0.8;
        }
      }

      .relatedActivities__checked {
        position: absolute;
        top: var(--space-small);
        right: var(--space-small);
        z-index: 3;

        display: none;
        place-items: center;
        height: 2rem;
        width: 2rem;

        background-color: var(--green-500);
        border-radius: 50%;

        color: var(--grey-100);

        transform: translateY(0.2rem);

        svg {
          height: 1.4rem;

          stroke-width: 3;
        }
      }

      input:checked + label {
        opacity: 1;

        .relatedActivities__checked {
          display: grid;
        }
      }
    }
  }

  &__actions {
    display: flex;
    justify-content: flex-end;
    gap: var(--space-small);
    margin-top: var(--space-medium);
  }
}
</style>
