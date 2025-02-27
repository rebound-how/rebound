<template>
  <ul class="tableList">
    <li class="tableList__row tableList__row--header">
      <div class="tableList__cell">Name</div>
      <div class="tableList__cell">Variable</div>
      <div class="tableList__cell">Value</div>
    </li>
    <li v-if="areSshPausesEnabled && sshPausesDuration" class="tableList__row">
      <div class="tableList__cell">Steady-State Hypothesis Pauses Duration</div>
      <div class="tableList__cell jsonString jsonString--envvar">
        {{ sshPausesDuration.var_name }}
      </div>
      <div class="tableList__cell jsonString jsonString--number">
        {{ sshPausesDuration.value }}
      </div>
    </li>
    <li v-else-if="!areSshPausesEnabled" class="tableList__row">
      <div class="tableList__cell">Steady-State Hypothesis Pauses Duration</div>
      <div class="tableList__cell"></div>
      <div class="tableList__cell jsonString jsonString--boolean">disabled</div>
    </li>
    <li
      v-if="areMethodActionPausesEnabled && methodActionPausesDuration"
      class="tableList__row"
    >
      <div class="tableList__cell">Method Action Pauses Duration</div>
      <div class="tableList__cell jsonString jsonString--envvar">
        {{ methodActionPausesDuration.var_name }}
      </div>
      <div class="tableList__cell jsonString jsonString--number">
        {{ methodActionPausesDuration.value }}
      </div>
    </li>
    <li v-else-if="!areMethodActionPausesEnabled" class="tableList__row">
      <div class="tableList__cell">Method Action Pauses Duration</div>
      <div class="tableList__cell"></div>
      <div class="tableList__cell jsonString jsonString--boolean">disabled</div>
    </li>
    <li
      v-if="areMethodProbePausesEnabled && methodProbePausesDuration"
      class="tableList__row"
    >
      <div class="tableList__cell">Method Probe Pauses Duration</div>
      <div class="tableList__cell jsonString jsonString--envvar">
        {{ methodProbePausesDuration.var_name }}
      </div>
      <div class="tableList__cell jsonString jsonString--number">
        {{ methodProbePausesDuration.value }}
      </div>
    </li>
    <li v-else-if="!areMethodProbePausesEnabled" class="tableList__row">
      <div class="tableList__cell">Method Probe Pauses Duration</div>
      <div class="tableList__cell"></div>
      <div class="tableList__cell jsonString jsonString--boolean">disabled</div>
    </li>
    <li
      v-if="areRollbacksPausesEnabled && rollbacksPausesDuration"
      class="tableList__row"
    >
      <div class="tableList__cell">Rollbacks Pauses Duration</div>
      <div class="tableList__cell jsonString jsonString--envvar">
        {{ rollbacksPausesDuration.var_name }}
      </div>
      <div class="tableList__cell jsonString jsonString--number">
        {{ rollbacksPausesDuration.value }}
      </div>
    </li>
    <li v-else-if="!areRollbacksPausesEnabled" class="tableList__row">
      <div class="tableList__cell">Rollbacks Pauses Duration</div>
      <div class="tableList__cell"></div>
      <div class="tableList__cell jsonString jsonString--boolean">
        disabled
      </div>
    </li>
  </ul>
</template>

<script setup lang="ts">
import { toRefs, computed } from "vue";

import type { Environment, Var } from "@/types/environments";

const props = defineProps<{
  settings: Environment;
}>();

const { settings } = toRefs(props);

const areSshPausesEnabled = computed<boolean>(() => {
  const e = settings.value.envvars.find(
    (v) => v.var_name === "RELIABLY_AUTOPAUSE_SSH_ENABLED"
  );
  if (e === undefined) {
    return false;
  } else {
    return e.value === "1";
  }
});
const sshPausesDuration = computed<Var | undefined>(() => {
  return settings.value.envvars.find(
    (v) => v.var_name === "RELIABLY_AUTOPAUSE_SSH_DURATION"
  );
});

const areMethodActionPausesEnabled = computed<boolean>(() => {
  const e = settings.value.envvars.find(
    (v) => v.var_name === "RELIABLY_AUTOPAUSE_METHOD_ACTION_ENABLED"
  );
  if (e === undefined) {
    return false;
  } else {
    return e.value === "1";
  }
});
const methodActionPausesDuration = computed<Var | undefined>(() => {
  return settings.value.envvars.find(
    (v) => v.var_name === "RELIABLY_AUTOPAUSE_METHOD_ACTION_DURATION"
  );
});

const areMethodProbePausesEnabled = computed<boolean>(() => {
  const e = settings.value.envvars.find(
    (v) => v.var_name === "RELIABLY_AUTOPAUSE_METHOD_ACTION_ENABLED"
  );
  if (e === undefined) {
    return false;
  } else {
    return e.value === "1";
  }
});
const methodProbePausesDuration = computed<Var | undefined>(() => {
  return settings.value.envvars.find(
    (v) => v.var_name === "RELIABLY_AUTOPAUSE_METHOD_PROBE_DURATION"
  );
});

const areRollbacksPausesEnabled = computed<boolean>(() => {
  const e = settings.value.envvars.find(
    (v) => v.var_name === "RELIABLY_AUTOPAUSE_ROLLBACKS_ENABLED"
  );
  if (e === undefined) {
    return false;
  } else {
    return e.value === "1";
  }
});
const rollbacksPausesDuration = computed<Var | undefined>(() => {
  return settings.value.envvars.find(
    (v) => v.var_name === "RELIABLY_AUTOPAUSE_ROLLBACKS_DURATION"
  );
});
</script>
