<template>
  <LoadingPlaceholder v-if="isLoading" />
  <JsonViewer
    v-else
    :json="JSON.stringify(control, null, 2)"
    :no-padding="true"
  />
</template>

<script setup lang="ts">
import { toRefs, ref, onMounted } from "vue";
import {
  fetchIntegrationControl,
  integrationControl,
} from "@/stores/integrations";

import { useStore } from "@nanostores/vue";

import LoadingPlaceholder from "@/components/_ui/LoadingPlaceholder.vue";
import JsonViewer from "@/components/_ui/JsonViewer.vue";

const props = defineProps<{
  id: string;
}>();
const { id } = toRefs(props);

const isLoading = ref<boolean>(true);
const control = useStore(integrationControl);

onMounted(async () => {
  isLoading.value = true;
  await fetchIntegrationControl(id.value);
  isLoading.value = false;
});
</script>
