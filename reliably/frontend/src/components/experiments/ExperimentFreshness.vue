<template>
  <div
    class="freshnessScore hasTooltip hasTooltip--bottom-center"
    :class="freshnessObject"
    aria-label="Freshness represents how long
ago an experiment was last run"
    label="Freshness represents how long
ago an experiment was last run"
  >
    <span class="freshnessScore__score">
      {{ f }}<small v-if="f !== '-' && !mini">%</small>
    </span>
    <span v-if="!mini" class="freshnessScore__days">{{ days }}</span>
  </div>
</template>

<script setup lang="ts">
import { toRefs, ref, computed } from "vue";
import dayjs from "dayjs";

const props = defineProps<{
  last: string | Date | null;
  mini?: boolean;
}>();

const { last, mini } = toRefs(props);

const d = computed<number | null>(() => {
  if (last.value === null || last.value === "") {
    return null;
  } else {
    const now = dayjs();
    return now.diff(last.value, "day");
  }
});

const days = computed<string>(() => {
  if (d.value === null) {
    return "Not run yet";
  } else if (d.value > 28) {
    return "28+ days";
  } else if (d.value === 1) {
    return "1 day";
  } else {
    return `${d.value.toString()} days`;
  }
});

const f = computed<string>(() => {
  if (d.value !== null) {
    if (d.value > 28) {
      return "0";
    } else if (d.value === 0) {
      return "100";
    } else {
      // A function that roughly fits this rule and fills the voids:
      // f(1) = 100
      // f(7) = 50
      // f(14) = 25
      // f(21) = 12.5
      // f(28) = 0
      return Math.round(
        0.14656 * d.value * d.value - 7.7048 * d.value + 103.79
      ).toString();
    }
  } else {
    return "-";
  }
});

const freshnessObject = computed(() => ({
  "freshnessScore--fresh": f.value !== "-" && parseInt(f.value) > 75,
  "freshnessScore--good":
    f.value !== "-" && parseInt(f.value) <= 75 && parseInt(f.value) > 50,
  "freshnessScore--ok":
    f.value !== "-" && parseInt(f.value) <= 50 && parseInt(f.value) > 25,
  "freshnessScore--bad": f.value !== "-" && parseInt(f.value) <= 25,
  "freshnessScore--mini": mini !== undefined && mini.value === true,
}));
</script>

<style lang="scss" scoped>
.freshnessScore {
  --scoreBackground: var(--grey-200);
  --scoreText: var(--text-color);

  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 10rem;
  width: auto;
  padding: var(--space-small) var(--space-medium);

  background-color: var(--scoreBackground);
  border-radius: var(--border-radius-s);

  color: var(--scoreText);

  &__score {
    font-size: 4.8rem;
    font-weight: 700;
    line-height: 0.9;

    small {
      font-size: 1.6rem;
      font-weight: 400;
    }
  }

  &__days {
    font-size: 1.4rem;
    text-align: center;
    text-transform: uppercase;
    white-space: nowrap;
  }

  &--fresh {
    --scoreBackground: var(--green-200);
    --scoreText: var(--green-800);
  }

  &--good {
    --scoreBackground: var(--yellow-300);
    --scoreText: var(--yellow-800);
  }

  &--ok {
    --scoreBackground: rgb(255, 202, 104);
    --scoreText: var(--sand-800);
  }

  &--bad {
    --scoreBackground: var(--red-200);
    --scoreText: var(--red-900);
  }

  &--mini {
    height: 3.4rem;
    width: auto;
    margin-top: 0.7rem;
    margin-right: 0;
    padding: 0.6rem;

    .freshnessScore__score {
      font-size: 2.4rem;

      small {
        display: none;
      }
    }
  }
}
</style>
