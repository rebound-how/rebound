<template>
  <li class="environmentPreview tableList__row">
    <div class="tableList__cell environmentPreview__name">
      <a :href="`/environments/view?id=${environment.id}`">
        <span>{{ environment.name }}</span>
      </a>
      <small>Created <TimeAgo :timestamp="environment.created_date" /></small>
    </div>
    <div class="tableList__cell environmentPreview__vars">
      {{ environmentVars }}
    </div>
    <div class="tableList__cell environmentPreview__secrets">
      {{ environmentSecrets }}
    </div>
    <div class="tableList__cell tableList__cell--small">
      <DeleteButton @click.prevent="displayDelete" />
    </div>
    <ModalWindow
      v-if="isDeleteDisplayed"
      :hasCloseButton="true"
      :hasPadding="true"
      @close="closeDelete"
    >
      <template #title>Delete Environment</template>
      <template #content>
        <ConfirmDeleteEnvironment
          :id="environment.id!"
          :page="page"
          :in-place="true"
          @close="closeDelete"
        />
      </template>
    </ModalWindow>
  </li>
</template>

<script setup lang="ts">
import { toRefs, computed, ref } from "vue";
import type { Environment } from "@/types/environments";
import { hasProp } from "@/utils/objects";

import TimeAgo from "@/components/_ui/TimeAgo.vue";
import DeleteButton from "@/components/_ui/DeleteButton.vue";
import ModalWindow from "@/components/_ui/ModalWindow.vue";
import ConfirmDeleteEnvironment from "@/components/environments/ConfirmDeleteEnvironment.vue";

const props = defineProps<{
  environment: Environment;
  page?: number;
}>();
const { environment, page } = toRefs(props);

const environmentVars = computed<string>(() => {
  let varsStr = "";
  if (environment !== undefined) {
    environment.value.envvars.forEach((v) => {
      varsStr += `${v.var_name}, `;
    });
    varsStr = varsStr.slice(0, varsStr.length - 2);
  }
  return varsStr;
});

const environmentSecrets = computed<string>(() => {
  let secretsStr = "";
  if (environment !== undefined) {
    environment.value.secrets.forEach((s) => {
      if (hasProp(s, "var_name")) {
        secretsStr += `${s.var_name}, `;
      } else if (hasProp(s, "path")) {
        secretsStr += `${s.path}, `;
      }
    });
    secretsStr = secretsStr.slice(0, secretsStr.length - 2);
  }
  return secretsStr;
});

const isDeleteDisplayed = ref<boolean>(false);

const displayDelete = () => {
  isDeleteDisplayed.value = true;
};
const closeDelete = () => {
  isDeleteDisplayed.value = false;
};
</script>

<style lang="scss" scoped>
.environmentPreview {
  > .tableList__cell {
    small {
      display: block;

      color: var(--text-color-dim);
      font-size: 1.4rem;
      white-space: nowrap;
    }
  }

  &__name {
    span {
      font-size: 1.8rem;
      font-weight: 700;
    }
  }

  &__vars,
  &__secrets {
    color: var(--green-500);
    font-family: var(--monospace-font);
    font-size: 1.4rem;
  }

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
