<template>
  <p>This will create a clone of the current deployment under an new name.</p>
  <form class="form">
    <div class="inputWrapper">
      <label for="cloneName">Name</label>
      <input type="text" id="cloneName" name="cloneName" v-model="name" />
    </div>
    <div class="inputWrapper">
      <button @click.prevent="cancel" class="button button--destructiveLight">
        Cancel
      </button>
      <button
        @click.prevent="proceed"
        class="button button--creative"
        :disabled="name === ''"
      >
        Clone deployment
      </button>
    </div>
  </form>
</template>

<script setup lang="ts">
import { toRefs, ref } from "vue";
import { cloneDeployment } from "@/stores/deployments";

const props = defineProps<{
  id: string;
}>();
const { id } = toRefs(props);

const name = ref<string>("");

const emit = defineEmits<{
  (e: "close"): void;
}>();
const cancel = () => {
  emit("close");
};

const proceed = async () => {
  await cloneDeployment(id.value, { name: name.value });
  emit("close");
};
</script>
