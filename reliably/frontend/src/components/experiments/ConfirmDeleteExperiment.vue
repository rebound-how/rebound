<template>
  <p>You are about to delete an experiment. This action cannot be undone.</p>
  <p>Deleting an experiment will also delete all associated executions.</p>
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
      <button type="button" @click.prevent="cancel" class="button">
        Cancel
      </button>
      <button
        type="button"
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
import { deleteExperiment, fetchExperiments } from "@/stores/experiments";

const props = defineProps<{
  id: string; // ID of experiment to delete
  inPlace?: boolean; // Should user stay on the same page after delete (used when deleting from a list)
  page?: number; // Current page number in the list, to re-fetch the right page of data (used when inPlace === true)
}>();
const { id, inPlace, page } = toRefs(props);

const confirmation = ref<string>("");

const emit = defineEmits<{
  (e: "close"): void;
}>();

const cancel = () => {
  emit("close");
};

const proceed = async () => {
  if (confirmation.value === "DELETE") {
    let s: boolean = await deleteExperiment(id.value);
    if (s) {
      if (inPlace?.value === true) {
        let p: number = 1;
        if (page !== undefined && page.value) {
          p = page.value;
        }
        await fetchExperiments(p);
        emit("close");
      } else {
        window.location.replace("/experiments/");
      }
    } else {
      emit("close");
    }
  }
};
</script>

<style lang="scss" scoped>
.button + .button {
  margin-left: var(--space-small);
}
</style>
