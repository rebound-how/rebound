<template>
  <li class="templatePreview tableList__row">
    <div class="templatePreview__meta tableList__cell">
      <div class="templatePreview__name">
        <a :href="`/experiments/custom-templates/create/?id=${template.id}`">
          {{ template.manifest.metadata.name }}
        </a>
      </div>
      <div class="templatePreview__info">
        #{{ template.id }} created
        <TimeAgo :timestamp="template.created_date" />
      </div>
    </div>

    <div class="templatePreview__labels tableList__cell">
      <TagList :tags="template.manifest.metadata.labels" />
    </div>
    <div
      class="templatePreview__actions tableList__cell tableList__cell--small"
    >
      <a
        :href="`/experiments/custom-templates/view/?id=${template.id}`"
        class="button button--icon hasTooltip hasTooltip--bottom-center"
        aria-label="View details"
        label="View details"
      >
        <EyeIcon />
      </a>
      <a
        :href="`/experiments/custom-templates/new/?duplicate=${template.id}`"
        class="button button--icon hasTooltip hasTooltip--bottom-center"
        aria-label="Duplicate"
        label="Duplicate"
      >
        <CopyIcon />
      </a>
      <DeleteButton @click.prevent="displayDelete" />
    </div>
    <ModalWindow
      v-if="isDeleteDisplayed"
      :hasCloseButton="true"
      :hasPadding="true"
      @close="closeDelete"
    >
      <template #title>Delete Template</template>
      <template #content>
        <ConfirmDeleteTemplate
          :id="template.id"
          :in-place="true"
          :page="page"
          @close="closeDelete"
        />
      </template>
    </ModalWindow>
  </li>
</template>

<script setup lang="ts">
import { toRefs, ref, computed } from "vue";
import type { Template } from "@/types/templates";

import ConfirmDeleteTemplate from "@/components/custom-templates/ConfirmDeleteTemplate.vue";
import TimeAgo from "@/components/_ui/TimeAgo.vue";
import TagList from "@/components/_ui/TagList.vue";
import ModalWindow from "@/components/_ui/ModalWindow.vue";
import DeleteButton from "@/components/_ui/DeleteButton.vue";
import EyeIcon from "@/components/svg/EyeIcon.vue";
import CopyIcon from "@/components/svg/CopyIcon.vue";

const props = defineProps<{
  template: Template;
  page: number;
}>();
const { template, page } = toRefs(props);

const isDeleteDisplayed = ref<boolean>(false);

const displayDelete = () => {
  isDeleteDisplayed.value = true;
};
const closeDelete = () => {
  isDeleteDisplayed.value = false;
};
</script>

<style lang="scss" scoped>
.templatePreview {
  &__name {
    a {
      font-size: 1.8rem;
      font-weight: 700;

      text-decoration: none;

      &:hover {
        color: var(--accentColorSecondary);
      }
    }
  }

  &__info {
    color: var(--text-color-dim);
    font-size: 1.2rem;
  }

  &__trend {
    vertical-align: bottom;
  }

  &__last,
  &__actions {
    vertical-align: middle;
  }

  &__actions {
    > * {
      visibility: hidden;
    }

    > * + * {
      margin-left: 0.6rem;
    }
  }

  &:hover {
    .templatePreview__actions {
      > * {
        visibility: visible;
      }
    }
  }
}
</style>
