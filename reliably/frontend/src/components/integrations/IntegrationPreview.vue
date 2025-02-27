<template>
  <li class="integrationPreview tableList__row">
    <div
      class="tableList__cell tableList__cell--center integrationPreview__icon"
    >
      <IntegrationVendorIcon
        v-if="integration.vendor && integration.vendor !== null"
        :vendor="integration.vendor"
      />
    </div>
    <div class="tableList__cell integrationPreview__meta">
      <a
        :href="`/integrations/view/?id=${integration.id}`"
        class="integrationPreview__name"
      >
        {{ integration.name }}
      </a>
      <div class="integrationPreview__info">
        Created <TimeAgo :timestamp="integration.created_date" />
      </div>
    </div>
    <div class="tableList__cell">
      {{ readableProvider }}
    </div>
    <div v-if="!hideActions" class="tableList__cell tableList__cell--small">
      <div class="integrationPreview__actions">
        <button
          class="controlButton button button--icon hasTooltip hasTooltip--bottom-center"
          aria-label="Display control"
          label="Display control"
          @click.prevent="displayControl"
          v-if="canShowControlButton"
        >
          {&nbsp;}
        </button>
        <DeleteButton @click.prevent="displayDelete" />
      </div>
    </div>
    <ModalWindow
      v-if="isDeleteDisplayed"
      :hasCloseButton="true"
      :hasPadding="true"
      @close="closeDelete"
    >
      <template #title>Delete Integration</template>
      <template #content>
        <ConfirmDeleteIntegration
          :id="integration.id!"
          :page="page"
          :in-place="true"
          @close="closeDelete"
        />
      </template>
    </ModalWindow>
  </li>
</template>

<script setup lang="ts">
import { toRefs, computed, ref } from "vue";
import type { Integration } from "@/types/integrations";

import TimeAgo from "@/components/_ui/TimeAgo.vue";
import DeleteButton from "@/components/_ui/DeleteButton.vue";
import ModalWindow from "@/components/_ui/ModalWindow.vue";
import ConfirmDeleteIntegration from "@/components/integrations/ConfirmDeleteIntegration.vue";
import IntegrationVendorIcon from "@/components/integrations/IntegrationVendorIcon.vue";

const props = defineProps<{
  integration: Integration;
  page?: number;
  hideActions?: boolean;
}>();
const { integration, page, hideActions } = toRefs(props);

const emit = defineEmits<{
  (e: "display-control", integration: { id: string; name: string }): void;
}>();

const readableProvider = computed<string>(() => {
  if (integration.value.vendor === "slack") {
    return "Slack";
  } else if (integration.value.provider === "opentelemetry") {
    if (integration.value.vendor === "honeycomb") {
      return "OpenTelemetry (Honeycomb)";
    } else if (integration.value.vendor === "dynatrace") {
      return "OpenTelemetry (Dynatrace)";
    } else if (integration.value.vendor === "gcp") {
      return "OpenTelemetry (Google Cloud)";
    } else if (integration.value.vendor === "grafana") {
      return "OpenTelemetry (Grafana Tempo)";
    } else {
      return "";
    }
  } else if (integration.value.vendor === "reliably") {
    if (integration.value.provider == "notification") {
      return "Notification";
    } else if (integration.value.provider == "snapshot") {
      return "Resources";
    } else if (integration.value.provider == "assistant") {
      return "Assistant";
    } else if (integration.value.provider == "autopause") {
      return "Auto-Pause";
    } else if (integration.value.provider == "prechecks") {
      return "Pre-checks";
    } else if (integration.value.provider == "chatgpt") {
      return "AI Questions";
    }
  } else if (integration.value.vendor === "openai") {
    return "OpenAI";
  } else {
    return integration.value.vendor || "";
  }
});

const isDeleteDisplayed = ref<boolean>(false);

const canShowControlButton = computed<boolean>(() => {
  return integration.value.provider != "notification";
});

const displayDelete = () => {
  isDeleteDisplayed.value = true;
};
const closeDelete = () => {
  isDeleteDisplayed.value = false;
};

function displayControl() {
  emit("display-control", {
    id: integration.value.id!,
    name: integration.value.name,
  });
}
</script>

<style lang="scss" scoped>
.integrationPreview {
  > .tableList__cell {
    small {
      display: block;

      color: var(--text-color-dim);
      font-size: 1.4rem;
    }
  }

  &__icon {
    width: 3.2rem;

    svg {
      height: 2.4rem;
    }
  }

  &__name {
    font-size: 1.8rem;
    font-weight: 700;

    &:hover {
      color: var(--pink-500);
    }
  }

  &__info {
    color: var(--text-color-dim);
    font-size: 1.2rem;
  }

  &__actions {
    display: flex;
    gap: var(--space-small);
  }

  .deleteButton,
  .controlButton {
    visibility: hidden;
  }

  .controlButton {
    background-color: transparent;

    color: var(--text-color-bright);
    font-weight: 700;

    &:hover {
      background-color: var(--grey-300);
    }
  }

  &:hover {
    .deleteButton,
    .controlButton {
      visibility: visible;
    }
  }
}
</style>
