<template>
  <SlackLogo v-if="vendor === 'slack'" />
  <HoneycombMark v-else-if="vendor === 'honeycomb'" />
  <DynatraceLogo v-else-if="vendor === 'dynatrace'" />
  <GoogleCloudLogo v-else-if="vendor === 'gcp'" />
  <GrafanaTempoLogo v-else-if="vendor === 'grafana'" />
  <ReliablyRLogo v-else-if="vendor === 'reliably'" />
  <OpenAiLogo v-else-if="vendor === 'openai'" />
</template>

<script setup lang="ts">
import { toRefs } from "vue";

import SlackLogo from "@/components/svg/SlackLogo.vue";
import HoneycombMark from "@/components/svg/HoneycombMark.vue";
import DynatraceLogo from "@/components/svg/DynatraceLogo.vue";
import GoogleCloudLogo from "@/components/svg/GoogleCloudLogo.vue";
import GrafanaTempoLogo from "@/components/svg/GrafanaTempoLogo.vue";
import ReliablyRLogo from "@/components/svg/ReliablyRLogo.vue";
import OpenAiLogo from "@/components/svg/OpenAi.vue";

const props = defineProps<{
  vendor: string;
}>();
const { vendor } = toRefs(props);
</script>
