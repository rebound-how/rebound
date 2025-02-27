<template>
  <p>You are about to delete an template. This action cannot be undone.</p>
  <p>Experiments created using this template will still run as expected.</p>
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
import { deleteTemplate, fetchTemplates } from "@/stores/templates";

const props = defineProps<{
  id: string;
  inPlace?: boolean;
  page?: number;
}>();
const { id, page, inPlace } = toRefs(props);

const confirmation = ref<string>("");

const emit = defineEmits<{
  (e: "close"): void;
}>();
const cancel = () => {
  emit("close");
};

const proceed = async () => {
  if (confirmation.value === "DELETE") {
    let s: boolean = await deleteTemplate(id.value);
    if (s) {
      if (inPlace?.value === true) {
        let p: number = 1;
        if (page !== undefined && page.value) {
          p = page.value;
        }
        await fetchTemplates(p);
        emit("close");
      } else {
        window.location.replace("/experiments/custom-templates/");
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
