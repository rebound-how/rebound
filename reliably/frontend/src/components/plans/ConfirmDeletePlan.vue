<template>
  <p>You are about to delete a plan. This action cannot be undone.</p>
  <p>Type 'DELETE' to proceed.</p>
  <form class="form" @submit.prevent="proceed">
    <div class="inputWrapper">
      <label for="confirmDelete"></label>
      <input
        type="text"
        id="confirmDelete"
        name="confirmDelete"
        v-model="confirmation"
      />
    </div>
    <div class="inputWrapper">
      <button @click.prevent="cancel" class="button">Cancel</button>
      <button
        @click.prevent="proceed"
        class="button button--destructive"
        :disabled="confirmation !== 'DELETE'"
      >
        Delete
      </button>
    </div>
  </form>
</template>

<script setup lang="ts">
import { toRefs, ref } from "vue";
import { deletePlan, fetchPlans, fetchRelatedPlans } from "@/stores/plans";

const props = defineProps<{
  id: string; // Plan to delete
  inPlace?: boolean; // Should user stay on the same page after delete (used when deleting from a list)
  page?: number; // Current page number in the list, to re-fetch the right page of data (used when inPlace === true)
  store?: { name: string; id: string }; // Which store should be refreshed after plan has been deleted
}>();
const { id, inPlace, page, store } = toRefs(props);

const confirmation = ref<string>("");

const emit = defineEmits<{
  (e: "close"): void;
}>();
const cancel = () => {
  emit("close");
};

const proceed = async () => {
  if (confirmation.value === "DELETE") {
    await deletePlan(id.value);
    if (store !== undefined && store.value !== undefined) {
      await fetchRelatedPlans(store.value.id, store.value.name);
      emit("close");
    } else if (inPlace?.value === true) {
      let p: number = 1;
      if (page !== undefined && page.value) {
        p = page.value;
      }
      await fetchPlans(p);
      emit("close");
    } else {
      window.location.replace("/plans/");
    }
  }
};
</script>

<style lang="scss" scoped>
.button + .button {
  margin-left: var(--space-small);
}
</style>
