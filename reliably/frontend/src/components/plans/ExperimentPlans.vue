<template>
  <div class="experimentPlansList">
    <div class="experimentPlansList__heading">
      <h2>Plans</h2>
      <p>This experiment is run by the following plans.</p>
    </div>
    <EntityFilter @search="refreshList" />
    <LoadingPlaceholder v-if="isLoading" />
    <ul v-else-if="plans.length > 0" class="plansList tableList">
      <li class="tableList__row tableList__row--header">
        <div
          class="tableList__cell tableList__cell--center tableList__cell--status"
        ></div>
        <div class="tableList__cell">Plan</div>
        <div class="tableList__cell">Experiments</div>
        <div class="tableList__cell">Environment</div>
        <div class="tableList__cell tableList__cell--right">
          Total&nbsp;Runs
        </div>
        <div class="tableList__cell tableList__cell--right">Last</div>
        <div class="tableList__cell tableList__cell--right">Next</div>
        <div class="tableList__cell">Schedule</div>
        <div class="tableList__cell">
          <span class="screen-reader-text">Actions</span>
        </div>
      </li>
      <template v-for="plan in plans" :key="plan.id">
        <PlanPreview
          v-if="plan.status !== 'deleting'"
          :plan="(plan as Plan)"
          :store="{ name: 'experiments', id: experimentId }"
          :page="0"
          class="tableList__row"
        />
      </template>
    </ul>
    <p v-else>You have filtered out all your plans</p>
  </div>
</template>

<script setup lang="ts">
import { toRefs, onMounted, ref } from "vue";
import type { Plan } from "@/types/plans";

import { useStore } from "@nanostores/vue";
import { relatedPlansList, fetchRelatedPlans } from "@/stores/plans";

import PlanPreview from "@/components/plans/PlanPreview.vue";
import EntityFilter from "@/components/_ui/EntityFilter.vue";
import LoadingPlaceholder from "@/components/_ui/LoadingPlaceholder.vue";

const props = defineProps<{
  experimentId: string;
}>();
const { experimentId } = toRefs(props);

const isLoading = ref(true);
const searchTerm = ref<string>("");
const plans = useStore(relatedPlansList);

function getSearchTerm() {
  let location = window.location;
  let params = new URLSearchParams(location.search);
  if (params.has("search")) {
    searchTerm.value = params.get("search")!;
  } else {
    searchTerm.value = "";
  }
}

async function refreshList() {
  isLoading.value = true;
  getSearchTerm();
  await fetchRelatedPlans(experimentId.value, "experiments", searchTerm.value);
  isLoading.value = false;
}

onMounted(async () => {
  await refreshList();
});
</script>

<style lang="scss" scoped>
.experimentPlansList__heading {
  h2 {
    margin-bottom: 0;
  }

  p {
    margin-bottom: var(--space-small);
    color: var(--text-color-dim);
  }
}
</style>
