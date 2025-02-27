<template>
  <p>You are about to delete a {{ type }}. This action cannot be undone.</p>
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
import type { Secret, Var } from "@/types/environments";
import {
  deleteEnvironmentSecretVar,
  fetchEnvironment,
} from "@/stores/environments";

const props = defineProps<{
  target: Secret | Var;
  type: "secret" | "variable";
  env: string;
}>();
const { target, type, env } = toRefs(props);

const confirmation = ref<string>("");

const emit = defineEmits<{
  (e: "close"): void;
  (e: "refresh-environment"): void;
}>();
const cancel = () => {
  emit("close");
};

const proceed = async () => {
  if (confirmation.value === "DELETE") {
    let key: string = "";
    if (type.value === "secret") {
      key = (target.value as Secret).key;
    } else if (type.value === "variable") {
      key = (target.value as Var).var_name;
    }
    let s: boolean = await deleteEnvironmentSecretVar(
      key,
      type.value,
      env.value
    );
    if (s) {
      emit("refresh-environment");
      emit("close");
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
