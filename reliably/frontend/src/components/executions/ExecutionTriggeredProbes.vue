<template>
  <section class="executionSection triggeredProbes">
    <p>Execution was interrupted by the <span class="triggeredProbes__type">{{ probes.type }}</span> integration <TimeAgo :timestamp="`${(probes.probes[0] as any).end}+00:00`" />. View probes result in the timeline below.</p>
  </section>
</template>

<script setup lang="ts">
import { toRefs } from "vue";
import TimeAgo from "@/components/_ui/TimeAgo.vue";

const props = defineProps<{
  probes: { type: string; probes: Object[] };
}>();
const { probes } = toRefs(props);
</script>

<style lang="scss" scoped>
.triggeredProbes {
  padding: var(--space-small);

  background-color: var(--red-100);
  border-radius: var(--border-radius-s);

  color: var(--red-800);

  &__type {
    font-weight: 500;
    text-transform: capitalize;
  }
}
</style>
