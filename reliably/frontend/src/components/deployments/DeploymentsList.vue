<template>
  <EntityFilter @search="refreshList" />
  <LoadingPlaceholder size="large" v-if="isLoading" />
  <NoData message="No deployments found" v-if="deploys.total === 0"></NoData>
  <ul v-else class="experimentsList tableList">
    <li class="tableList__row tableList__row--header">
      <div
        class="tableList__cell tableList__cell--center tableList__cell--status"
      ></div>
      <div class="tableList__cell">Name</div>
      <div class="tableList__cell">Target</div>
      <div class="tableList__cell">
        <span class="screen-reader-text">Actions</span>
      </div>
    </li>
    <DeploymentPreview
      v-for="d in deploys.deployments"
      :deployment="d"
      :page="page"
      :key="d.id"
      class="tableList__row"
    />
  </ul>
  <Pager v-if="deploys.total > 10" :page="pagerData" />
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import type { Deployment } from "@/types/deployments";
import type { PagerData } from "@/types/pager";

import { deployments, fetchDeployments } from "@/stores/deployments";
import { useStore } from "@nanostores/vue";

import DeploymentPreview from "@/components/deployments/DeploymentPreview.vue";
import EntityFilter from "@/components/_ui/EntityFilter.vue";
import LoadingPlaceholder from "@/components/_ui/LoadingPlaceholder.vue";
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
const deploys = useStore(deployments);

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
  let urlBase: string = "/deployments/?page=";
  if (searchTerm.value !== "") {
    urlBase = `/deployments/?search=${searchTerm.value}&page=`;
  }
  let pager: PagerData = {
    currentPage: page.value!,
    lastPage: Math.ceil(deploys.value.total / 10),
    urlBase: urlBase,
  };
  pagerData.value = pager;
};

async function refreshList() {
  isLoading.value = true;
  getParams();
  await fetchDeployments(page.value!, searchTerm.value);
  getPagerData();
  isLoading.value = false;
}

onMounted(async () => {
  await refreshList();
});
</script>

<style lang="scss" scoped></style>
