<template>
  <div class="activityLogo" :title="target">
    <AwsLogo v-if="target === 'AWS'" />
    <AwsAzLogo v-else-if="target === 'AWS AZ'" />
    <AzureLogo v-else-if="target === 'Azure'" />
    <DynatraceLogo v-else-if="target === 'Dynatrace'" />
    <GandiLogo v-else-if="target === 'Gandi'" />
    <GoogleCloudLogo v-else-if="target === 'Google Cloud'" />
    <K6Logo v-else-if="target === 'k6'" />
    <IstioLogo v-else-if="target === 'Istio'" />
    <HoneycombMark v-else-if="target === 'Honeycomb'" />
    <KubernetesLogo v-else-if="target === 'Kubernetes'" />
    <PrometheusLogo v-else-if="target === 'Prometheus'" />
    <ReliablyLogo v-else-if="target === 'reliability'" />
    <ServiceFabricLogo v-else-if="target === 'Service Fabric'" />
    <SpringLogo v-else-if="target === 'Spring'" />
    <ToxiProxyLogo v-else-if="target === 'ToxiProxy'" />
    <WireMockLogo v-else-if="target === 'WireMock'" />
    <BoxIcon v-else />
    <span class="screen-reader-text">{{ target }}</span>
  </div>
</template>

<script setup lang="ts">
import { toRefs } from "vue";
import AwsLogo from "@/components/svg/AwsLogo.vue";
import AwsAzLogo from "@/components/svg/AwsAzLogo.vue";
import AzureLogo from "@/components/svg/AzureLogo.vue";
import DynatraceLogo from "@/components/svg/DynatraceLogo.vue";
import GandiLogo from "@/components/svg/GandiLogo.vue";
import GoogleCloudLogo from "@/components/svg/GoogleCloudLogo.vue";
import IstioLogo from "@/components/svg/IstioLogo.vue";
import HoneycombMark from "@/components/svg/HoneycombMark.vue";
import K6Logo from "@/components/svg/K6Logo.vue";
import KubernetesLogo from "@/components/svg/KubernetesLogoBlue.vue";
import PrometheusLogo from "@/components/svg/PrometheusLogo.vue";
import ReliablyLogo from "@/components/svg/ReliablyRLogo.vue";
import ServiceFabricLogo from "@/components/svg/ServiceFabricLogo.vue";
import SpringLogo from "@/components/svg/SpringLogo.vue";
import ToxiProxyLogo from "@/components/svg/ToxiProxyLogo.vue";
import WireMockLogo from "@/components/svg/WireMockLogo.vue";
import BoxIcon from "@/components/svg/BoxIcon.vue";

const props = defineProps<{
  target: string;
}>();
const { target } = toRefs(props);
</script>

<style lang="scss">
.activityLogo {
  padding-top: 0.6rem;

  svg {
    max-height: 3.6rem;
    width: 3.6rem;
  }

  &--large {
    svg {
      max-height: unset;
      width: 7.2rem;
    }
  }
}
</style>
