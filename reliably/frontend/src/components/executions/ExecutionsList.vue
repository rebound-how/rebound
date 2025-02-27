<template>
  <LoadingPlaceholder size="large" v-if="isLoading" />
  <NoData
    message="No executions found"
    v-if="execs.executions.length === 0"
  ></NoData>
  <ul v-else class="executionsList tableList">
    <li class="tableList__row tableList__row--header">
      <div class="tableList__cell tableList__cell tableList__cell--status">
        Status
      </div>
      <div class="tableList__cell"></div>
      <div class="tableList__cell">Run</div>
      <div class="tableList__cell">
        <span class="screen-reader-text">Actions</span>
      </div>
    </li>
    <ExecutionPreview
      v-for="exe in execs.executions"
      :execution="(exe as Execution)"
      :page="page"
      :key="exe.id"
      class="tableList__row"
    />
  </ul>
  <Pager v-if="execs.total > 10" :page="pagerData" />
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import type { Execution } from "@/types/executions";
import type { PagerData } from "@/types/pager";

import { executions, fetchExecutions } from "@/stores/executions";
import { useStore } from "@nanostores/vue";

import NoData from "@/components/_ui/NoData.vue";
import ExecutionPreview from "@/components/executions/ExecutionPreview.vue";
import Pager from "@/components/_ui/Pager.vue";
import LoadingPlaceholder from "@/components/_ui/LoadingPlaceholder.vue";

const page = ref<number | undefined>(undefined);
const pagerData = ref<PagerData>({
  currentPage: 1,
  lastPage: 1,
  urlBase: "",
});
const execs = useStore(executions);
const isLoading = ref(true);

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
    lastPage: Math.ceil(execs.value.total / 10),
    urlBase: "/executions/?page=",
  };
  pagerData.value = pager;
};

onMounted(async () => {
  isLoading.value = true;
  getCurrentPage();
  await fetchExecutions(page.value!);
  getpagerData();
  isLoading.value = false;
});
</script>

<style lang="scss" scoped></style>
