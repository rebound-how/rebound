<template>
  <p>You are about to stop an execution. This action cannot be undone.</p>
  <p>
    You can choose to skip rollbacks, but be aware that even running them might
    leave your system in an unknown state.
  </p>
  <form class="form">
    <div class="inputWrapper inputWrapper--tick">
      <div>
        <input
          type="checkbox"
          id="skipRollbacks"
          name="skipRollbacks"
          v-model="areRollbacksSkipped"
        />
        <label for="skipRollbacks">Terminate ungracefully</label>
      </div>
    </div>
    <div class="inputWrapper">
      <button @click.prevent="cancel" class="button">Cancel</button>
      <button @click.prevent="proceed" class="button button--destructive">
        Stop execution
      </button>
    </div>
  </form>
</template>

<script setup lang="ts">
import { toRefs, ref } from "vue";
import { stopExecution, fetchExecutions } from "@/stores/executions";

const props = defineProps<{
  id: string; // ID of execution to stop
  exp: string; // ID of experiment
  inPlace?: boolean; // Should user stay on the same page after delete
  page?: number; // Page number, to re-fetch data after delete
  toExp?: boolean; // Should user be redirected to the experiment after delete
}>();
const { id, exp, inPlace, toExp, page } = toRefs(props);

const areRollbacksSkipped = ref<boolean>(false);

const emit = defineEmits<{
  (e: "close", isStopping: boolean): void;
}>();
const cancel = () => {
  emit("close", false);
};

const proceed = async () => {
  await stopExecution(id.value, exp.value, areRollbacksSkipped.value);
  emit("close", true);
};
</script>

<style lang="scss" scoped>
form {
  margin-top: var(--space-small);
}
.button + .button {
  margin-left: var(--space-small);
}
</style>
