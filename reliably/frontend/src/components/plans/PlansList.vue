<template>
  <EntityFilter @search="refreshList" />
  <LoadingPlaceholder size="large" v-if="isLoading" />
  <NoData message="No plans found" v-if="data.total === 0" />
  <ul v-else class="plansList tableList">
    <li class="tableList__row tableList__row--header">
      <div
        class="tableList__cell tableList__cell--center tableList__cell--status"
      ></div>
      <div class="tableList__cell">Plan</div>
      <div class="tableList__cell">Environment</div>
      <div class="tableList__cell">Deployment</div>
      <div class="tableList__cell tableList__cell--right">Total&nbsp;Runs</div>
      <div class="tableList__cell tableList__cell--right">Last</div>
      <div class="tableList__cell tableList__cell--right">Next</div>
      <div class="tableList__cell">Schedule</div>
      <div class="tableList__cell">
        <span class="screen-reader-text">Actions</span>
      </div>
    </li>
    <template v-for="plan in data.plans" :key="plan.id">
      <PlanPreview
        v-if="plan.status !== 'deleting'"
        :plan="(plan as Plan)"
        :page="page!"
        class="tableList__row"
      />
    </template>
  </ul>
  <Pager v-if="data.total > 10" :page="pagerData" />
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import type { Plan } from "@/types/plans";
import type { PagerData } from "@/types/pager";

import { useStore } from "@nanostores/vue";
import { plans, fetchPlans } from "@/stores/plans";

import NoData from "@/components/_ui/NoData.vue";
import EntityFilter from "@/components/_ui/EntityFilter.vue";
import PlanPreview from "@/components/plans/PlanPreview.vue";
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
const data = useStore(plans);

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
  let urlBase: string = "/plans/?page=";
  if (searchTerm.value !== "") {
    urlBase = `/plans/?search=${searchTerm.value}&page=`;
  }
  let pager: PagerData = {
    currentPage: page.value!,
    lastPage: Math.ceil(data.value.total / 10),
    urlBase: urlBase,
  };
  pagerData.value = pager;
};

async function refreshList() {
  isLoading.value = true;
  getParams();
  await fetchPlans(page.value!, searchTerm.value);
  getPagerData();
  isLoading.value = false;
}

onMounted(async () => {
  await refreshList();
});
</script>

<style lang="scss" scoped>
.tableList__cell--right {
  padding-right: var(--space-medium);
}
</style>
