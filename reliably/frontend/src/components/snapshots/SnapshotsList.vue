<template>
  <header class="pageHeader">
    <div>
      <h1 class="pageHeader__title">
        <span>
          Resources
        </span>
      </h1>
      <p>
        Known resources from your system.
      </p>
    </div>
    <div class="pageHeader__actions">
      <MultiButton
        title="Manage"
        :options="manageActions"
        @emit-action="handleMultiButtonAction"
      />
    </div>
  </header>
  <EntityFilter @search="refreshList" />
  <LoadingPlaceholder size="large" v-if="isLoading" />
  <NoData message="No resources found" v-if="res.total === 0"></NoData>
  <ul v-else class="snapshotsList tableList">
    <li class="tableList__row tableList__row--header">
      <div
        class="tableList__cell tableList__cell--center tableList__cell--status"
      ></div>
      <div class="tableList__cell">Name</div>
      <div class="tableList__cell">Type</div>
      <div class="tableList__cell">Usage</div>
      <div class="tableList__cell"># Relations</div>
      <div class="tableList__cell">Tags</div>
      <div class="tableList__cell">
        <span class="screen-reader-text">Actions</span>
      </div>
    </li>
    <ResourcePreview
      v-for="r in res.resources"
      :resource="r"
      :page="page"
      :key="r.id"
      class="tableList__row"
    />
  </ul>
  <Pager v-if="res.total > 10" :page="pagerData" />
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import type { PagerData } from "@/types/pager";
import type { MultiButtonOption } from "@/types/ui-types";
import MultiButton from "@/components/_ui/MultiButton.vue";

import { resources, fetchSnapshots, refreshSnapshot } from "@/stores/snapshots";
import { useStore } from "@nanostores/vue";

import EntityFilter from "@/components/_ui/EntityFilter.vue";
import LoadingPlaceholder from "@/components/_ui/LoadingPlaceholder.vue";
import ResourcePreview from "@/components/snapshots/ResourcePreview.vue";
import Pager from "@/components/_ui/Pager.vue";
import NoData from "@/components/_ui/NoData.vue";

const isLoading = ref(true);
const page = ref<number | undefined>(undefined);
const searchTerm = ref<string>("");
const pagerData = ref<PagerData>({
  currentPage: 1,
  lastPage: 1,
  urlBase: "",
});
const res = useStore(resources);

const manageActions = ref<MultiButtonOption[]>([
  {
    label: "Refresh",
    action: "refresh",
    icon: "refresh",
  },
  {
    label: "Configure",
    action: "setup",
    icon: "edit",
  },
]);

async function handleMultiButtonAction(action: string) {
  if (action == "setup") {
    window.location.assign("/resources/configure");
  } else if (action == "refresh") {
    await refreshSnapshot();
  }
}

const getParams = () => {
  let location = window.location;
  let params = new URLSearchParams(location.search);
  if (params.has("page")) {
    page.value = parseInt(params.get("page")!);
  } else {
    page.value = 1;
  }
  if (params.has("search")) {
    searchTerm.value = params.get("search")!;
  } else {
    searchTerm.value = "";
  }
};

const getPagerData = () => {
  let urlBase: string = "/resources/?page=";
  if (searchTerm.value !== "") {
    urlBase = `/resources/?search=${searchTerm.value}&page=`;
  }
  let pager: PagerData = {
    currentPage: page.value!,
    lastPage: Math.ceil(res.value.total / 10),
    urlBase: urlBase,
  };
  pagerData.value = pager;
};

async function refreshList() {
  isLoading.value = true;
  getParams();
  await fetchSnapshots(page.value!, searchTerm.value);
  getPagerData();
  isLoading.value = false;
}

onMounted(async () => {
  await refreshList();
});
</script>

<style lang="scss" scoped></style>
