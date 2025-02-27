<template>
  <LoadingPlaceholder v-if="isLoading" />
  <div
    v-else-if="total !== undefined && total > 0"
    class="experimentExecutionsList"
  >
    <h2>
      Executions
      <small
        >{{ firstDisplayedExecution }} to {{ lastDisplayedExecution }} of
        {{ total }}</small
      >
    </h2>
    <ul class="executionsList tableList">
      <li class="tableList__row tableList__row--header">
        <div
          class="tableList__cell tableList__cell--center tableList__cell--status"
        >
          Status
        </div>
        <div class="tableList__cell">Execution ID</div>
        <div class="tableList__cell">Run</div>
        <div class="tableList__cell">
          <span class="screen-reader-text">Actions</span>
        </div>
      </li>
      <ExperimentExecutionPreview
        v-for="exe in execs"
        :execution="exe"
        :page="page || 1"
        :key="exe.id"
        class="tableList__row"
      />
    </ul>
    <Pager v-if="isPagerDisplayed" :page="pagerData" />
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, toRefs, computed } from "vue";
import type { Execution } from "@/types/executions";
import type { PagerData } from "@/types/pager";

import { executions, fetchExecutions } from "@/stores/executions";

import ExperimentExecutionPreview from "@/components/executions/ExperimentExecutionPreview.vue";
import Pager from "@/components/_ui/Pager.vue";
import LoadingPlaceholder from "@/components/_ui/LoadingPlaceholder.vue";

const props = defineProps<{
  experimentId: string;
}>();
const { experimentId } = toRefs(props);

const page = ref<number | undefined>(undefined);
const pagerData = ref<PagerData>({
  currentPage: 1,
  lastPage: 1,
  urlBase: "",
});
const total = ref<number | undefined>(undefined);
const execs = ref<Execution[]>([]);

const isLoading = ref<boolean>(true);
const isPagerDisplayed = computed<boolean>(() => {
  return total.value !== undefined && total.value > 10;
});

const getCurrentPage = () => {
  let location = window.location;
  let params = new URLSearchParams(location.search);
  if (params.has("executions")) {
    page.value = parseInt(params.get("executions")!);
  } else {
    page.value = 1;
  }
};

const getExecutions = async () => {
  await fetchExecutions(page.value!, experimentId.value);
  let storeData = executions.get();
  execs.value = storeData.executions;
  total.value = storeData.total;
};

const getpagerData = () => {
  let pager: PagerData = {
    currentPage: page.value!,
    lastPage: Math.ceil(total.value! / 10),
    urlBase: `/experiments/view/?id=${experimentId.value}&executions=`,
  };
  pagerData.value = pager;
};

const firstDisplayedExecution = computed<number>(() => {
  return (page.value! - 1) * 10 + 1;
});
const lastDisplayedExecution = computed<number>(() => {
  if (page.value! === Math.ceil(total.value! / 10)) {
    return total.value!;
  } else {
    return (page.value! - 1) * 10 + 9;
  }
});

onMounted(async () => {
  isLoading.value = true;
  getCurrentPage();
  await getExecutions();
  getpagerData();
  isLoading.value = false;
});
</script>

<style lang="scss" scoped>
.experimentExecutionsList {
  h2 {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;

    small {
      color: var(--font-color-dim);
      font-size: 1.4rem;
      font-weight: 400;
    }
  }
}
</style>
