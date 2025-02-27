<template>
  <ul class="dependenciesList">
    <li v-for="d in dependencies" :key="d.name">
      <a
        v-if="Object.keys(knownExtenstions).includes(d.name)"
        :href="knownExtenstions[d.name]"
        target="_blank"
        rel="noopener noreferer"
      >
        {{ d.name }}&nbsp;<span>{{ d.version }}</span>
      </a>
      <template v-else>
        {{ d.name }}&nbsp;<span>{{ d.version }}</span>
      </template>
    </li>
  </ul>
</template>

<script setup lang="ts">
import { toRefs } from "vue";

import type { ExecutionDependency } from "@/types/executions";

const props = defineProps<{
  dependencies: ExecutionDependency[];
}>();

const { dependencies } = toRefs(props);

const knownExtenstions: { [key: string]: string } = {
  "chaostoolkit-reliably": "https://chaostoolkit.org/drivers/reliably/",
  "chaostoolkit-aws": "https://chaostoolkit.org/drivers/aws/",
  "chaostoolkit-kubernetes": "https://chaostoolkit.org/drivers/kubernetes/",
  "chaostoolkit-google-cloud-platform": "https://chaostoolkit.org/drivers/gcp/",
  "chaostoolkit-cloud-foundry":
    "https://chaostoolkit.org/drivers/cloudfoundry/",
  "chaostoolkit-azure": "https://chaostoolkit.org/drivers/azure/",
  "chaostoolkit-prometheus": "https://chaostoolkit.org/drivers/prometheus/",
  "chaostoolkit-humio": "https://chaostoolkit.org/drivers/humio/",
  "chaostoolkit-spring": "https://chaostoolkit.org/drivers/spring/",
  "chaostoolkit-toxiproxy": "https://chaostoolkit.org/drivers/toxiproxy/",
  "chaostoolkit-opentracing": "https://chaostoolkit.org/drivers/opentracing/",
  "chaostoolkit-service-fabric":
    "https://chaostoolkit.org/drivers/service-fabric/",
  "chaostoolkit-istio": "https://chaostoolkit.org/drivers/istio/",
  "chaostoolkit-wiremock": "https://chaostoolkit.org/drivers/wiremock/",
  "chaostoolkit-gandi": "https://chaostoolkit.org/drivers/gandi/",
  "chaostoolkit-dynatrace": "https://chaostoolkit.org/drivers/dynatrace/",
  "chaostoolkit-addons": "https://chaostoolkit.org/drivers/addons/",
  "chaostoolkit-grafana": "https://chaostoolkit.org/drivers/grafana/",
  "chaostoolkit-slack": "https://chaostoolkit.org/drivers/slack/",
  "chaostoolkit-pixie": "https://chaostoolkit.org/drivers/pixie/",
  "chaostoolkit-datadog": "https://chaostoolkit.org/drivers/datadog/",
};
</script>

<style lang="scss">
.dependenciesList {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-small);
  padding: var(--space-small);

  background-color: var(--section-background);
  border-radius: var(--border-radius-s);
  list-style: none;

  @media print {
    display: block;
    list-style: disc;
  }

  li {
    padding-right: var(--space-medium);

    a {
      color: var(--text-color);
    }

    span {
      color: var(--text-color-dim);
    }
  }
}
</style>
