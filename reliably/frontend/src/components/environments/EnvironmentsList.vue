<template>
  <EntityFilter @search="refreshList" />
  <LoadingPlaceholder size="large" v-if="isLoading" />
  <NoData message="No environments found" v-if="envs.total === 0"></NoData>
  <ul v-else class="environmentsList tableList">
    <li class="tableList__row tableList__row--header">
      <div class="tableList__cell">Name</div>
      <div class="tableList__cell">Vars</div>
      <div class="tableList__cell">Secrets</div>
      <div class="tableList__cell">
        <span class="screen-reader-text">Actions</span>
      </div>
    </li>
    <template v-for="e in envs.environments">
      <EnvironmentPreview
        v-if="e.used_for !== 'notification' && e.used_for !== 'snapshot'"
        :environment="(e as Environment)"
        :page="page"
        :key="e.id"
        class="tableList__row"
      />
    </template>
  </ul>
  <Pager v-if="envs.total > 10" :page="pagerData" />
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import type { Environment } from "@/types/environments";
import type { PagerData } from "@/types/pager";

import { environments, fetchEnvironments } from "@/stores/environments";
import { useStore } from "@nanostores/vue";

import EntityFilter from "@/components/_ui/EntityFilter.vue";
import NoData from "@/components/_ui/NoData.vue";
import EnvironmentPreview from "@/components/environments/EnvironmentPreview.vue";
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
const envs = useStore(environments);

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
  let urlBase: string = "/environments/?page=";
  if (searchTerm.value !== "") {
    urlBase = `/environments/?search=${searchTerm.value}&page=`;
  }
  let pager: PagerData = {
    currentPage: page.value!,
    lastPage: Math.ceil(envs.value.total / 10),
    urlBase: urlBase,
  };
  pagerData.value = pager;
};

async function refreshList() {
  isLoading.value = true;
  getParams();
  await fetchEnvironments(page.value!, searchTerm.value);
  getPagerData();
  isLoading.value = false;
}

onMounted(async () => {
  await refreshList();
});
</script>

<style lang="scss" scoped></style>
