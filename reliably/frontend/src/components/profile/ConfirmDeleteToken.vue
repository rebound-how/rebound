<template>
  <p>You are about to delete an token. This action cannot be undone.</p>
  <p>
    Deleting an token can cause integrations and other services depending on it
    to stop functioning.
  </p>
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
import { deleteToken, fetchTokens } from "@/stores/user";

const props = defineProps<{
  id: string;
  org: string;
}>();
const { id, org } = toRefs(props);

const confirmation = ref<string>("");

const emit = defineEmits<{
  (e: "close"): void;
}>();

const cancel = () => {
  emit("close");
};

const proceed = async () => {
  if (confirmation.value === "DELETE") {
    await deleteToken(id.value, org.value);
    await fetchTokens();
    emit("close");
  }
};
</script>

<style lang="scss" scoped>
.button + .button {
  margin-left: var(--space-small);
}
</style>
