<template>
  <LoadingPlaceholder size="large" v-if="isLoading" />
  <article
    class="integrationView"
    v-else-if="int !== undefined && int !== null && int.id !== undefined"
  >
    <header class="pageHeader">
      <div>
        <h1 class="pageHeader__title">
          <IntegrationVendorIcon
            v-if="int.vendor && int.vendor !== null"
            :vendor="int.vendor"
          />
          {{ int.name }}
        </h1>
        <div class="pageHeader__description">{{ int.id }}</div>
      </div>
      <div class="pageHeader__actions">
        <button
          class="button button--destructiveLight"
          @click.prevent="displayDelete"
        >
          Remove integration
        </button>
      </div>
    </header>
    <section class="integrationSection">
      <h2>Details</h2>
      <dl>
        <div>
          <dt>Created</dt>
          <dd><TimeAgo :timestamp="int.created_date" /></dd>
        </div>
        <div>
          <dt>Vendor</dt>
          <dd>{{ int.vendor }}</dd>
        </div>
        <div>
          <dt>Provider</dt>
          <dd>{{ int.provider }}</dd>
        </div>
      </dl>
    </section>
    <section v-if="integrationSettings !== null" class="integrationSection">
      <h2>Settings</h2>
      <GcpOTSettings
        v-if="displayGcpOpenTelemetry"
        :settings="(integrationSettings as Environment)"
      />
      <DynatraceOTSettings
        v-if="displayDynatraceOpenTelemetry"
        :settings="(integrationSettings as Environment)"
      />
      <HoneycombOTSettings
        v-if="displayHoneycombOpenTelemetry"
        :settings="(integrationSettings as Environment)"
      />
      <GrafanaOTSettings
        v-if="displayGrafanaOpenTelemetry"
        :settings="(integrationSettings as Environment)"
      />
      <SlackSettings
        v-if="displaySlack"
        :settings="(integrationSettings as Environment)"
      />
      <OpenAiSettings
        v-if="displayOpenAi"
        :settings="(integrationSettings as Environment)"
      />
      <AutoPauseSettings
        v-if="displayAutoPause"
        :settings="(integrationSettings as Environment)"
      />
      <PrechecksSettings
        v-if="displayPrechecks"
        :settings="(integrationSettings as Environment)"
      />
      <SafeguardsSettings
        v-if="displaySafeguards"
        :settings="(integrationSettings as Environment)"
      />
      <NotificationSettings
        v-if="displayNotifications"
        :settings="(integrationSettings as Environment)"
      />
    </section>

    <ModalWindow
      v-if="isDeleteDisplayed"
      :hasCloseButton="true"
      :hasPadding="true"
      @close="closeDelete"
    >
      <template #title>Remove integration</template>
      <template #content>
        <ConfirmDeleteIntegration
          :id="int.id"
          :to-list="true"
          @close="closeDelete"
        />
      </template>
    </ModalWindow>
  </article>
  <NoData v-else message="We couldn't find an experiment with this ID." />
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import type { Environment } from "@/types/environments";
import { useStore } from "@nanostores/vue";

import { integration, fetchIntegration } from "@/stores/integrations";
import { environment, fetchEnvironment } from "@/stores/environments";

import GcpOTSettings from "@/components/integrations/settings/GcpOTSettings.vue";
import DynatraceOTSettings from "@/components/integrations/settings/DynatraceOTSettings.vue";
import HoneycombOTSettings from "@/components/integrations/settings/HoneycombOTSettings.vue";
import GrafanaOTSettings from "@/components/integrations/settings/GrafanaOTSettings.vue";
import SlackSettings from "@/components/integrations/settings/SlackSettings.vue";
import OpenAiSettings from "@/components/integrations/settings/OpenAiSettings.vue";
import AutoPauseSettings from "@/components/integrations/settings/AutoPauseSettings.vue";
import PrechecksSettings from "@/components/integrations/settings/PrechecksSettings.vue";
import SafeguardsSettings from "@/components/integrations/settings/SafeguardsSettings.vue";
import NotificationSettings from "@/components/integrations/settings/NotificationSettings.vue";
import IntegrationVendorIcon from "@/components/integrations/IntegrationVendorIcon.vue";
import LoadingPlaceholder from "@/components/_ui/LoadingPlaceholder.vue";
import NoData from "@/components/_ui/NoData.vue";
import ModalWindow from "@/components/_ui/ModalWindow.vue";
import ConfirmDeleteIntegration from "@/components/integrations/ConfirmDeleteIntegration.vue";
import TimeAgo from "@/components/_ui/TimeAgo.vue";

const isLoading = ref(true);
const id = ref<string | undefined>(undefined);
const int = useStore(integration);

const getCurrentId = () => {
  let location = window.location;
  let params = new URLSearchParams(location.search);
  if (params.has("id")) {
    id.value = params.get("id")!;
  }
};

const getIntegration = async () => {
  await fetchIntegration(id.value!);
};

const setMetaData = () => {
  let title = "Integration · Reliably";
  if (int.value !== undefined && int.value !== null) {
    title = `${int.value.name} · Reliably`;
  }
  document.title = title;
};

const displayGcpOpenTelemetry = computed<boolean>(() => {
  return int.value?.provider === "opentelemetry" && int.value.vendor === "gcp";
});
const displayDynatraceOpenTelemetry = computed<boolean>(() => {
  return (
    int.value?.provider === "opentelemetry" && int.value.vendor === "dynatrace"
  );
});
const displayHoneycombOpenTelemetry = computed<boolean>(() => {
  return (
    int.value?.provider === "opentelemetry" && int.value.vendor === "honeycomb"
  );
});
const displayGrafanaOpenTelemetry = computed<boolean>(() => {
  return (
    int.value?.provider === "opentelemetry" && int.value.vendor === "grafana"
  );
});
const displayOpenAi = computed<boolean>(() => {
  return int.value?.provider === "chatgpt" && int.value.vendor === "openai";
});
const displaySlack = computed<boolean>(() => {
  return int.value?.provider === "slack" && int.value.vendor === "slack";
});
const displayAutoPause = computed<boolean>(() => {
  return int.value?.provider === "autopause" && int.value.vendor === "reliably";
});
const displayPrechecks = computed<boolean>(() => {
  return int.value?.provider === "prechecks" && int.value.vendor === "reliably";
});
const displaySafeguards = computed<boolean>(() => {
  return (
    int.value?.provider === "safeguards" && int.value.vendor === "reliably"
  );
});
const displayNotifications = computed<boolean>(() => {
  return (
    int.value?.provider === "notification" && int.value.vendor === "reliably"
  );
});

const integrationSettings = useStore(environment);
async function getIntegrationSettings() {
  await fetchEnvironment(int.value?.environment_id!);
}

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
  await getIntegration();
  await getIntegrationSettings();
  setMetaData();
  isLoading.value = false;
});
</script>

<style lang="scss" scoped>
.integrationView {
  > section + section {
    margin-top: var(--space-medium);
  }

  .integrationSection {
    > div,
    > dl {
      margin: 0;
      padding: var(--space-small);

      background-color: var(--section-background);
      border-radius: var(--border-radius-s);
    }

    dl {
      display: flex;
      gap: var(--space-medium);

      > div {
        flex: 1;
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
}
</style>
