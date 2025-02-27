<template>
  <LoadingPlaceholder v-if="isLoading" />
  <div v-else class="tokensLists">
    <div v-for="(org, index) in t" :key="index">
      <h2>{{ org.org.name }}</h2>
      <ul v-if="org.tokens.length > 0" class="tokensList tableList">
        <li class="tableList__row tableList__row--header">
          <div class="tableList__cell">Name</div>
          <div class="tableList__cell">Value</div>
          <div class="tableList__cell">Creation Date</div>
          <div class="tableList__cell">
            <span class="screen-reader-text">Actions</span>
          </div>
        </li>
        <TokenPreview
          v-for="t in org.tokens"
          :key="t.id"
          :t="t"
          :org="org.org.id"
        />
      </ul>
      <ul v-else class="tokensList tableList">
        <li class="tableList__row tableList__row--header">
          <div class="tableList__cell">Name</div>
          <div class="tableList__cell">Value</div>
          <div class="tableList__cell">Creation Date</div>
          <div class="tableList__cell">
            <span class="screen-reader-text">Actions</span>
          </div>
        </li>
        <li class="tableList__cell">
          You don't have any token for organization
          <strong>{{ org.org.name }}</strong>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import type { TokensApiResponse } from "@/types/user";
import { useStore } from "@nanostores/vue";

import { tokens, fetchTokens } from "@/stores/user";

import TokenPreview from "@/components/profile/TokenPreview.vue";
import LoadingPlaceholder from "@/components/_ui/LoadingPlaceholder.vue";

const isLoading = ref(true);
const t = useStore(tokens);

onMounted(async () => {
  isLoading.value = true;
  await fetchTokens();
  isLoading.value = false;
});
</script>

<style lang="scss" scoped></style>
