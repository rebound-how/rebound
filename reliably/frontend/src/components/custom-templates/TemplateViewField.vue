<template>
  <div class="templateViewField">
    <h3>{{ field.key }}</h3>
    <div>
      <div>
        <div v-if="configuration[field.key] !== undefined">
          <JsonViewer
            :json="
              JSON.stringify({ [field.key]: configuration[field.key] }, null, 2)
            "
          />
        </div>
      </div>
      <div>
        <h4>Preview</h4>
        <p>How the field will appear when using the template.</p>
        <form class="form">
          <CreateExperimentField
            :configuration="field"
            :index="1"
            :force-internal="null"
            :previewMode="true"
          />
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { toRefs } from "vue";

import type { TemplateField } from "@/types/templates";
import type { Configuration } from "@/types/experiments";

import CreateExperimentField from "@/components/custom-templates/CreateExperimentField.vue";
import JsonViewer from "@/components/_ui/JsonViewer.vue";

const props = defineProps<{
  field: TemplateField;
  index: number;
  readonly configuration: Configuration;
}>();

const { field, index, configuration } = toRefs(props);
</script>

<style lang="scss" scoped>
.templateViewField {
  h3 {
    font-family: var(--monospace-font);
  }

  > div {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: var(--space-medium);

    > div:first-child {
      padding-right: var(--space-medium);

      border-right: 0.1rem solid var(--section-separator-color);
    }

    > div:last-child {
      .form {
        margin-top: var(--space-medium);
        padding: var(--space-small);

        border: 0.1rem solid var(--section-separator-color);
        border-radius: var(--border-radius-s);
      }
    }
  }
}
</style>
