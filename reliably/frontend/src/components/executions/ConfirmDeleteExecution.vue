<template>
  <p>You are about to delete an execution. This action cannot be undone.</p>
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
import { deleteExecution, fetchExecutions } from "@/stores/executions";

const props = defineProps<{
  id: string; // ID of execution to delete
  exp: string; // ID of experiment
  inPlace?: boolean; // Should user stay on the same page after delete
  onExp?: boolean; // Deleting from an experiment. Stay on page. Refecth data
  page?: number; // Page number, to re-fetch data after delete
  toExp?: boolean; // Should user be redirected to the experiment after delete
}>();
const { id, exp, inPlace, onExp, toExp, page } = toRefs(props);

const confirmation = ref<string>("");

const emit = defineEmits<{
  (e: "close"): void;
}>();
const cancel = () => {
  emit("close");
};

const proceed = async () => {
  if (confirmation.value === "DELETE") {
    await deleteExecution(id.value, exp.value);
    if (inPlace?.value === true) {
      let p: number = 1;
      if (page !== undefined && page.value) {
        p = page.value;
      }
      await fetchExecutions(p);
      emit("close");
    } else if (onExp !== undefined && onExp.value === true) {
      let p: number = 1;
      if (page !== undefined && page.value) {
        p = page.value;
      }
      await fetchExecutions(p, exp.value);
      emit("close");
    } else if (toExp?.value === true) {
      window.location.replace(`/experiments/?view=${exp}`);
    } else {
      window.location.replace("/executions/");
    }
  }
};
</script>

<style lang="scss" scoped>
.button + .button {
  margin-left: var(--space-small);
}
</style>
