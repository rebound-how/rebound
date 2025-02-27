<template>
  <li class="tableList__row userPreview">
    <div class="tableList__cell">{{ user.username }}</div>
    <div class="tableList__cell tableList__cell--small">
      <DeleteButton
        v-if="isRemovable"
        type="user"
        @click.prevent="displayRemoveModal"
      />
    </div>
    <ModalWindow
      v-if="isRemoveDisplayed"
      :hasCloseButton="true"
      :hasPadding="true"
      @close="closeRemoveModal"
    >
      <template #title>Remove User</template>
      <template #content>
        <ConfirmRemoveUser :user="user" @close="closeRemoveModal" />
      </template>
    </ModalWindow>
  </li>
</template>

<script setup lang="ts">
import { toRefs, ref } from "vue";

import ConfirmRemoveUser from "@/components/profile/ConfirmRemoveUser.vue";
import ModalWindow from "@/components/_ui/ModalWindow.vue";
import DeleteButton from "@/components/_ui/DeleteButton.vue";

import type { OrganizationUser } from "@/types/organization";

const props = defineProps<{
  user: OrganizationUser;
  isRemovable?: boolean;
}>();
const { user } = toRefs(props);

const isRemoveDisplayed = ref<boolean>(false);
function displayRemoveModal() {
  isRemoveDisplayed.value = true;
}
function closeRemoveModal() {
  isRemoveDisplayed.value = false;
}
</script>

<style lang="scss" scoped>
.userPreview {
  .deleteButton {
    visibility: hidden;
  }

  &:hover {
    .deleteButton {
      visibility: visible;
    }
  }
}
</style>
