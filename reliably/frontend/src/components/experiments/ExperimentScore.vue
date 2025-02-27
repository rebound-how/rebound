<template>
  <div
    class="experimentScore hasTooltip hasTooltip--bottom-center"
    :class="classObject"
    aria-label="Experiment Score, based 
on the last 10 executions"
    label="Experiment Score, based 
on the last 10 executions"
  >
    <div class="experimentScore__grade text-center">
      <span class="screen-reader-text">Experiment Grade</span>
      {{ scoreGrade }}
    </div>
    <div v-if="!mini" class="experimentScore__score text-center">
      <span class="screen-reader-text">Experiment Score</span>
      {{ scorePercent }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { toRefs, computed } from "vue";

const props = defineProps<{
  score: number | null;
  mini?: boolean;
}>();

const { score, mini } = toRefs(props);

const scoreGrade = computed<string>(() => {
  if (score.value === null) {
    return "-";
  } else if (score.value >= 0.9) {
    return "A";
  } else if (score.value >= 0.7) {
    return "B";
  } else if (score.value >= 0.5) {
    return "C";
  } else {
    return "D";
  }
});

const scorePercent = computed<string>(() => {
  if (score.value === null) {
    return "-";
  } else {
    return Math.round(score.value * 100).toString();
  }
});

const classObject = computed(() => ({
  "experimentScore--mini": mini !== undefined && mini.value === true,
  "experimentScore--null": score.value === null,
  "experimentScore--A": score.value !== null && score.value >= 0.9,
  "experimentScore--B":
    score.value !== null && score.value >= 0.7 && score.value < 0.9,
  "experimentScore--C":
    score.value !== null && score.value >= 0.5 && score.value < 0.7,
  "experimentScore--D": score.value !== null && score.value < 0.5,
}));
</script>

<style lang="scss">
.experimentScore {
  height: 10rem;
  width: 10rem;
  padding: var(--space-small) var(--space-medium);

  background-color: var(--scoreBackground);
  border-radius: var(--border-radius-s);

  color: var(--scoreText);

  &__grade {
    font-size: 4.8rem;
    font-weight: 700;
    line-height: 0.9;
  }

  &--null {
    pointer-events: none;

    opacity: 0;

    --scoreBackground: var(--grey-300);
    --scoreText: var(--text-color);
  }

  &--A {
    --scoreBackground: var(--green-400);
    --scoreText: var(--green-900);
  }

  &--B {
    --scoreBackground: var(--yellow-500);
    --scoreText: var(--yellow-900);
  }

  &--C {
    --scoreBackground: orange;
    --scoreText: var(--sand-900);
  }

  &--D {
    --scoreBackground: rgb(255, 60, 88);
    --scoreText: var(--red-900);
  }

  &--mini {
    height: 3.4rem;
    width: 3rem;
    margin-top: 0.7rem;
    margin-right: 0;
    padding: 0.6rem;

    .experimentScore__grade {
      font-size: 2.4rem;
    }
  }
}
</style>
