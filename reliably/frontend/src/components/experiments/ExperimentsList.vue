<template>
  <EntityFilter @search="refreshList" />
  <LoadingPlaceholder size="large" v-if="isLoading" />
  <NoData message="No experiments found" v-else-if="exps.total === 0"></NoData>
  <ul v-else class="experimentsList tableList">
    <li class="tableList__row tableList__row--header">
      <div class="tableList__cell"></div>
      <div class="tableList__cell">Name</div>
      <div class="tableList__cell">Freshness</div>
      <div class="tableList__cell">Trend</div>
      <div class="tableList__cell">Last Execution</div>
      <div class="tableList__cell">
        <span class="screen-reader-text">Actions</span>
      </div>
    </li>
    <ExperimentPreview
      v-for="experiment in exps.experiments"
      :experiment="(experiment as SimpleExperiment)"
      :page="page!"
      :key="experiment.id"
      class="tableList__row"
    />
  </ul>
  <Pager v-if="exps.total > 10" :page="pagerData" />
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import type { SimpleExperiment } from "@/types/experiments";
import type { PagerData } from "@/types/pager";

import { experiments, fetchExperiments } from "@/stores/experiments";
import { useStore } from "@nanostores/vue";

import EntityFilter from "@/components/_ui/EntityFilter.vue";
import NoData from "@/components/_ui/NoData.vue";
import ExperimentPreview from "@/components/experiments/ExperimentPreview.vue";
import LoadingPlaceholder from "@/components/_ui/LoadingPlaceholder.vue";
import Pager from "@/components/_ui/Pager.vue";

const isLoading = ref(true);
const page = ref<number | undefined>(undefined);
const searchTerm = ref<string>("");
const pagerData = ref<PagerData>({
  currentPage: 1,
  lastPage: 1,
  urlBase: "",
});
const exps = useStore(experiments);

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
  let urlBase: string = "/experiments/?page=";
  if (searchTerm.value !== "") {
    urlBase = `/experiments/?search=${searchTerm.value}&page=`;
  }
  let pager: PagerData = {
    currentPage: page.value!,
    lastPage: Math.ceil(exps.value.total / 10),
    urlBase: urlBase,
  };
  pagerData.value = pager;
};

async function refreshList() {
  isLoading.value = true;
  getParams();
  await fetchExperiments(page.value!, searchTerm.value);
  getPagerData();
  isLoading.value = false;
}

onMounted(async () => {
  await refreshList();
});
</script>

<style lang="scss" scoped></style>
