<template>
  <LoadingPlaceholder v-if="isLoading" />
  <div v-else-if="plans.length > 0" class="deploymentPlansList">
    <div class="deploymentPlansList__heading">
      <h2>Plans</h2>
      <p>This deployment is used by the following plans.</p>
    </div>
    <ul class="plansList tableList">
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
          :page="0"
          class="tableList__row"
        />
      </template>
    </ul>
  </div>
</template>

<script setup lang="ts">
import { toRefs, onMounted, ref } from "vue";
import type { Plan } from "@/types/plans";

import { useStore } from "@nanostores/vue";
import { relatedPlansList, fetchRelatedPlans } from "@/stores/plans";

import PlanPreview from "@/components/plans/PlanPreview.vue";
import LoadingPlaceholder from "@/components/_ui/LoadingPlaceholder.vue";

const props = defineProps<{
  deploymentId: string;
}>();
const { deploymentId } = toRefs(props);

const isLoading = ref(true);
const plans = useStore(relatedPlansList);

onMounted(async () => {
  isLoading.value = true;
  await fetchRelatedPlans(deploymentId.value, "deployments");
  isLoading.value = false;
});
</script>

<style lang="scss" scoped>
.deploymentPlansList__heading {
  h2 {
    margin-bottom: 0;
  }

  p {
    margin-bottom: var(--space-small);
    color: var(--text-color-dim);
  }
}
</style>
