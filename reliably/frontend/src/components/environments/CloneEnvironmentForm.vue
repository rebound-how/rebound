<template>
  <p>Please provide a name for the new environment.</p>
  <p>
    All current environment variables and secrets will be added to the clone.
  </p>
  <form class="form">
    <div class="inputWrapper">
      <label for="newName"></label>
      <input
        type="text"
        id="newName"
        name="newName"
        :placeholder="name"
        v-model="cloneName"
      />
    </div>
    <div class="inputWrapper">
      <button @click.prevent="cancel" class="button">Cancel</button>
      <button
        @click.prevent="proceed"
        class="button button--primary"
        :disabled="cloneName === ''"
      >
        Clone environment
      </button>
    </div>
  </form>
</template>

<script setup lang="ts">
import { toRefs, ref } from "vue";
import { cloneEnvironment } from "@/stores/environments";

const props = defineProps<{
  id: string;
  name: string;
}>();
const { id, name } = toRefs(props);

const cloneName = ref<string>("");

const emit = defineEmits<{
  (e: "close"): void;
}>();
const cancel = () => {
  emit("close");
};

const proceed = async () => {
  if (id.value !== undefined && cloneName.value !== "") {
    await cloneEnvironment(id.value, cloneName.value);
  }
};
</script>

<style lang="scss" scoped>
.button + .button {
  margin-left: var(--space-small);
}
</style>
