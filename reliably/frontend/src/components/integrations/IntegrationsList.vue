<template>
  <LoadingPlaceholder size="large" v-if="isLoading" />
  <NoData
    message="You don't have any active integration yet"
    v-if="ints.total === 0"
  />
  <ul v-else class="environmentsList tableList">
    <li class="tableList__row tableList__row--header">
      <div class="tableList__cell"></div>
      <div class="tableList__cell">Name</div>
      <div class="tableList__cell">Provider</div>
      <div class="tableList__cell">
        <span class="screen-reader-text">Actions</span>
      </div>
    </li>
    <template v-for="i in ints.integrations" :key="i.id">
    <IntegrationPreview
      v-if="!(i.vendor === 'reliably' && ((i.provider === 'assistant') || (i.provider === 'snapshot')))"
      :integration="(i as Integration)"
      :page="page"
      @display-control="displayControl"
    />
    </template>
  </ul>
  <ModalWindow
    v-if="isControlDisplayed"
    :hasCloseButton="true"
    :hasPadding="true"
    @close="closeControl"
  >
    <template #title>Control for integration {{ controlName }}</template>
    <template #content>
      <IntegrationControl
        :id="controlId"
        :name="controlName"
        @close="closeControl"
      />
    </template>
  </ModalWindow>
  <Pager v-if="ints.total > 10" :page="pagerData" />
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import type { Integration } from "@/types/integrations";
import type { PagerData } from "@/types/pager";

import { integrations, fetchIntegrations } from "@/stores/integrations";
import { useStore } from "@nanostores/vue";

import NoData from "@/components/_ui/NoData.vue";
import ModalWindow from "@/components/_ui/ModalWindow.vue";
import IntegrationPreview from "@/components/integrations/IntegrationPreview.vue";
import IntegrationControl from "@/components/integrations/IntegrationControl.vue";
import LoadingPlaceholder from "@/components/_ui/LoadingPlaceholder.vue";
import Pager from "@/components/_ui/Pager.vue";

const isLoading = ref(true);
const page = ref<number | undefined>(undefined);
const pagerData = ref<PagerData>({
  currentPage: 1,
  lastPage: 1,
  urlBase: "",
});
const ints = useStore(integrations);

const getCurrentPage = () => {
  let location = window.location;
  let params = new URLSearchParams(location.search);
  if (params.has("page")) {
    page.value = parseInt(params.get("page")!);
  } else {
    page.value = 1;
  }
};

const getpagerData = () => {
  let pager: PagerData = {
    currentPage: page.value!,
    lastPage: Math.ceil(ints.value.total / 10),
    urlBase: "/integrations/?page=",
  };
  pagerData.value = pager;
};

const isControlDisplayed = ref<boolean>(false);
const controlId = ref<string>("");
const controlName = ref<string>("");
function displayControl(integration: { id: string; name: string }): void {
  controlId.value = integration.id;
  controlName.value = integration.name;
  isControlDisplayed.value = true;
}
function closeControl(): void {
  controlId.value = "";
  controlName.value = "";
  isControlDisplayed.value = false;
}

onMounted(async () => {
  isLoading.value = true;
  getCurrentPage();
  await fetchIntegrations(page.value!);
  getpagerData();
  isLoading.value = false;
});
</script>
