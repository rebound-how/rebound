<template>
  <div class="eventIcon" :class="classObject">
    <ActivityIcon v-if="event.type === 'experiment'" />
    <ThermometerIcon v-else-if="event.type === 'probe'" />
    <ToolIcon v-else-if="event.type === 'action'" />
    <PauseCircle v-else-if="event.type === 'pause'" />
    <AlertCircle v-else-if="event.type === 'info'" />
    <RefreshCcw v-else-if="event.type === 'rollback'" />
    <AlertTriangle v-else-if="event.type === 'safeguard-precheck'" />
    <SlackLogo v-else-if="event.type === 'slack-message'" />
  </div>
</template>

<script setup lang="ts">
import { toRefs, computed } from "vue";

import ActivityIcon from "@/components/svg/ActivityIcon.vue";
import AlertCircle from "@/components/svg/AlertCircle.vue";
import PauseCircle from "@/components/svg/PauseCircle.vue";
import ThermometerIcon from "@/components/svg/ThermometerIcon.vue";
import ToolIcon from "@/components/svg/ToolIcon.vue";
import RefreshCcw from "@/components/svg/RefreshCcw.vue";
import AlertTriangle from "@/components/svg/AlertTriangle.vue";
import SlackLogo from "@/components/svg/SlackLogo.vue";
import type { ExecutionTimelineEvent } from "@/types/executions";

const props = defineProps<{
  event: ExecutionTimelineEvent;
  isOdd?: boolean;
  isLeftMode: boolean;
}>();
const { event, isOdd, isLeftMode } = toRefs(props);

const classObject = computed(() => ({
  "eventIcon--odd": isOdd !== undefined && isOdd.value,
  "eventIcon--left": isLeftMode.value,
  "eventIcon--experiment": event.value.type === "experiment",
  "eventIcon--probe": event.value.type === "probe",
  "eventIcon--action": event.value.type === "action",
  "eventIcon--info": event.value.type === "info",
  "eventIcon--rollback": event.value.type === "rollback",
  "eventIcon--pause": event.value.type === "pause",
  "eventIcon--safeguard": event.value.type === "safeguard-precheck",
  "eventIcon--slack": event.value.type === "slack-message",
}));
</script>

<style lang="scss" scoped>
.eventIcon {
  order: 1;

  display: flex;
  align-items: center;
  justify-content: center;
  height: 4.8rem;
  width: 4.8rem;
  margin-right: 2.4rem;

  border-radius: 50%;

  svg {
    height: 2.4rem;
  }

  &--experiment {
    background-color: var(--yellow-200);

    color: var(--yellow-700);
  }

  &--action {
    background-color: var(--pink-100);

    color: var(--pink-500);
  }

  &--probe {
    background-color: var(--green-100);

    color: var(--green-500);
  }

  &--info {
    height: 1.6rem;
    width: 1.6rem;
    margin-top: 1.8rem;
    margin-right: 4rem;

    background-color: var(--grey-200);

    svg {
      display: none;
    }
  }

  &--pause {
    background-color: var(--blue-100);

    color: var(--blue-500);
  }

  &--rollback {
    background-color: var(--purple-100);

    color: var(--purple-500);
  }

  &--safeguard {
    background-color: var(--red-100);

    color: var(--red-500);
  }

  &--slack {
    background-color: white;
  }

  &--odd {
    @media (min-width: 44rem) {
      margin-left: 2.4rem;

      &.eventIcon--info {
        margin-left: 4rem;
      }
    }
  }

  &--left {
    @media (min-width: 44rem) {
      margin-left: 0;

      &.eventIcon--info {
        margin-left: 0;
      }
    }
  }
}
</style>
