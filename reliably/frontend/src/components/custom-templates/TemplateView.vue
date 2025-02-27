<template>
  <LoadingPlaceholder size="large" v-if="isLoading" />
  <article
    class="templateView"
    v-else-if="temp !== undefined && temp !== null && temp.id !== undefined"
  >
    <header class="pageHeader">
      <div>
        <h1 class="pageHeader__title">
          <span>
            {{ temp.manifest.metadata.name }}
            <small>{{ shortenUuid(temp.id) }}</small>
          </span>
        </h1>
        <p>Created <TimeAgo :timestamp="temp.created_date" /></p>
      </div>
      <div class="pageHeader__actions">
        <button
          class="button button--destructiveLight"
          @click.prevent="displayDelete"
        >
          Delete template
        </button>
        <a
          :href="`/experiments/custom-templates/new/?duplicate=${temp.id}`"
          class="button button--primary"
        >
          Duplicate template
        </a>
        <a
          :href="`/experiments/custom-templates/create/?id=${temp.id}`"
          class="button button--creative"
        >
          Create an experiment from this template
        </a>
      </div>
    </header>
    <section class="templateInfo">
      <dl>
        <div>
          <dt>Labels</dt>
          <dd>
            <div v-if="hasLabels" class="templateView__labels">
              <TagList :tags="(temp.manifest.metadata.labels as string[])" />
            </div>
          </dd>
        </div>
        <div>
          <dt>Experiment</dt>
          <dd>{{ temp.manifest.spec.template.title }}</dd>
        </div>
        <div>
          <dt>Description</dt>
          <dd>{{ temp.manifest.spec.template.description }}</dd>
        </div>
        <div>
          <dt>Usage</dt>
          <dd>
            Use this template to create an experiment by overriding a set
            predefined values.
          </dd>
        </div>
      </dl>
    </section>
    <section class="templateConfiguration">
      <div class="templateConfiguration__header">
        <div>
          <h2>Configuration</h2>
          <p>
            These configuration values can be edited when using the template to
            create an experiment.
          </p>
        </div>
        <div>
          <button
            @click="displayExperimentDefinition"
            class="button button--light"
          >
            View experiment
          </button>
          <button @click="displayTemplate" class="button button--primary">
            View template
          </button>
        </div>
      </div>
      <ul class="templateFields list-reset">
        <li
          v-for="(conf, index) in temp.manifest.spec.schema.configuration"
          class="templateField"
          :key="index"
        >
          <TemplateViewField
            :field="conf"
            :index="index"
            :configuration="(temp.manifest.spec.template.configuration! as Configuration)"
          />
        </li>
      </ul>
    </section>
    <ModalWindow
      v-if="isDeleteDisplayed"
      :hasCloseButton="true"
      :hasPadding="true"
      @close="closeDelete"
    >
      <template #title>Delete Template</template>
      <template #content>
        <ConfirmDeleteTemplate :id="temp.id" @close="closeDelete" />
      </template>
    </ModalWindow>
    <ModalWindow
      v-if="isTemplateDisplayed"
      :isUnlimited="true"
      :hasCloseButton="true"
      @close="closeTemplate"
    >
      <template #title>Template</template>
      <template #content>
        <JsonViewer
          :json="JSON.stringify(templateExport, null, 2)"
          :force-wrap="true"
        />
      </template>
    </ModalWindow>
    <ModalWindow
      v-if="isDefinitionDisplayed"
      :isUnlimited="true"
      :hasCloseButton="true"
      @close="closeExperimentDefinition"
    >
      <template #title>Experiment Definition</template>
      <template #content>
        <JsonViewer
          :json="JSON.stringify(temp.manifest.spec.template, null, 2)"
          :force-wrap="true"
        />
      </template>
    </ModalWindow>
  </article>
  <NoData v-else message="We couldn't find an experiment with this ID." />
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { shortenUuid } from "@/utils/strings";
import { useStore } from "@nanostores/vue";

import { template, fetchTemplate } from "@/stores/templates";

import TemplateViewField from "@/components/custom-templates/TemplateViewField.vue";
import ConfirmDeleteTemplate from "@/components/custom-templates/ConfirmDeleteTemplate.vue";
import LoadingPlaceholder from "@/components/_ui/LoadingPlaceholder.vue";
import NoData from "@/components/_ui/NoData.vue";
import ModalWindow from "@/components/_ui/ModalWindow.vue";
import TagList from "@/components/_ui/TagList.vue";
import TimeAgo from "@/components/_ui/TimeAgo.vue";
import JsonViewer from "@/components/_ui/JsonViewer.vue";

import type { Configuration, ExperimentDefinition } from "@/types/experiments";
import type { TemplateExport, TemplateField } from "@/types/templates";

const isLoading = ref(true);
const id = ref<string | undefined>(undefined);
const temp = useStore(template);
const templateExport = ref<TemplateExport | null>(null);

function getCurrentId() {
  let location = window.location;
  let params = new URLSearchParams(location.search);
  if (params.has("id")) {
    id.value = params.get("id")!;
  }
}

async function getTemplate() {
  await fetchTemplate(id.value!);
  if (temp.value !== null) {
    templateExport.value = {
      metadata: {
        id: temp.value.id,
        org_id: temp.value.org_id || "",
        name: temp.value.manifest.metadata.name,
        labels: temp.value.manifest.metadata.labels as string[],
        annotations: temp.value.manifest.metadata.annotations as
          | string[]
          | null,
      },
      spec: {
        provider: "chaostoolkit",
        type: "experiment",
        schema: {
          configuration: temp.value.manifest.spec.schema
            .configuration as TemplateField[],
        },
        template: temp.value.manifest.spec.template as ExperimentDefinition,
      },
    };
  }
}

const setMetaData = () => {
  let title = "Template · Reliably";
  if (temp.value !== undefined && temp.value !== null) {
    title = `${temp.value.manifest.metadata.name} · Reliably`;
  }
  document.title = title;
};

const hasLabels = computed<boolean>(() => {
  if (
    temp.value === undefined ||
    temp.value === null ||
    temp.value.manifest.metadata.labels === undefined
  ) {
    return false;
  }
  return temp.value.manifest.metadata.labels.length > 0;
});

const isDefinitionDisplayed = ref<boolean>(false);
const displayExperimentDefinition = () => {
  isDefinitionDisplayed.value = true;
};
const closeExperimentDefinition = () => {
  isDefinitionDisplayed.value = false;
};

const isTemplateDisplayed = ref<boolean>(false);
const displayTemplate = () => {
  isTemplateDisplayed.value = true;
};
const closeTemplate = () => {
  isTemplateDisplayed.value = false;
};

const isDeleteDisplayed = ref<boolean>(false);

const displayDelete = () => {
  isDeleteDisplayed.value = true;
};
const closeDelete = () => {
  isDeleteDisplayed.value = false;
};

onMounted(async () => {
  isLoading.value = true;
  getCurrentId();
  await getTemplate();
  setMetaData();
  isLoading.value = false;
});
</script>

<style lang="scss" scoped>
.templateView {
  > section + section {
    margin-top: var(--space-large);
  }

  .templateInfo {
    dl {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      margin: 0;
      padding: var(--space-small);

      background-color: var(--section-background);
      border-radius: var(--border-radius-m);

      > div {
        padding-right: var(--space-small);
      }

      > div + div {
        padding-left: var(--space-small);

        border-left: 1px solid var(--section-separator-color);
      }

      dt {
        color: var(--text-color-dim);
        font-size: 1.4rem;
        text-transform: uppercase;
      }
    }
  }

  .templateConfiguration {
    &__header {
      display: flex;

      > div:last-child {
        display: flex;
        align-items: flex-start;
        gap: var(--space-small);
        margin-left: auto;
      }
    }
    .templateFields {
      margin-top: var(--space-medium);

      .templateField + .templateField {
        margin-top: var(--space-medium);
      }

      .templateField {
        padding: var(--space-small);

        background-color: var(--section-background);
        border-radius: var(--border-radius-m);
      }
    }
  }
}
</style>
