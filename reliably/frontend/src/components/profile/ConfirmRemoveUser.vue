<template>
  <p>
    You are about to remove user {{ user.username }} from your organization.
  </p>
  <p>Type '{{ user.username }}' to proceed.</p>
  <form class="form">
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
        :disabled="confirmation !== user.username"
      >
        Remove
      </button>
    </div>
  </form>
</template>

<script setup lang="ts">
import { toRefs, ref } from "vue";
import { removeUser, fetchUsers } from "@/stores/organization";

import type { OrganizationUser } from "@/types/organization";

const props = defineProps<{
  user: OrganizationUser;
}>();
const { user } = toRefs(props);

const confirmation = ref<string>("");

const emit = defineEmits<{
  (e: "close"): void;
}>();
const cancel = () => {
  emit("close");
};

const proceed = async () => {
  await removeUser(user.value.id, user.value.username);
  await fetchUsers();
  emit("close");
};
</script>

<style lang="scss" scoped>
.button + .button {
  margin-left: var(--space-small);
}
</style>
