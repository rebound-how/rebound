<template>
  <div class="experimentStrategy">
    <div>
      <h3>Verification</h3>
      <dl>
        <div>
          <dt>
            Strategy
            <span
              class="hasTooltip hasTooltip--top-center"
              label="When the verification probes will run"
              aria-label="When the verification probes will run"
            >
              <HelpCircle />
            </span>
          </dt>
          <dd>{{ strategyObject.hypothesis.strategy }}</dd>
        </div>
        <div>
          <dt>
            Frequency
            <span
              class="hasTooltip hasTooltip--top-center"
              label="Number of seconds between two verification runs"
              aria-label="Number of seconds between two verification runs"
            >
              <HelpCircle />
            </span>
          </dt>
          <dd>{{ strategyObject.hypothesis.frequency }}</dd>
        </div>
        <div>
          <dt>
            Fail fast
            <span
              class="hasTooltip hasTooltip--top-center"
              label="Should the experiment stop after a failed verification"
              aria-label="Should the experiment stop after a failed verification"
            >
              <HelpCircle />
            </span>
          </dt>
          <dd>{{ strategyObject.hypothesis.fail_fast }}</dd>
        </div>
      </dl>
    </div>
    <div>
      <h3>Rollbacks</h3>
      <dl>
        <div>
          <dt>
            Strategy
            <span
              class="hasTooltip hasTooltip--top-center"
              label="When the rollbacks will run"
              aria-label="When the rollbacks will run"
            >
              <HelpCircle />
            </span>
          </dt>
          <dd>{{ strategyObject.rollbacks.strategy }}</dd>
        </div>
      </dl>
    </div>
  </div>
</template>

<script setup lang="ts">
import { toRefs, ref, onMounted } from "vue";

import type { Runtime } from "@/types/experiments";

import HelpCircle from "@/components/svg/HelpCircle.vue";

const props = defineProps<{
  strategy: Runtime | undefined;
}>();

const { strategy } = toRefs(props);

const strategyObject = ref<{
  hypothesis: {
    strategy: string;
    frequency: string;
    fail_fast: string;
  };
  rollbacks: {
    strategy: string;
  };
}>({
  hypothesis: {
    strategy: "Before and after turbulence (default)",
    frequency: "-",
    fail_fast: "No",
  },
  rollbacks: {
    strategy: "If experiment didn't deviate (default)",
  },
});

function updateStrategyObject() {
  if (strategy.value) {
    if (strategy.value.hypothesis) {
      if (strategy.value.hypothesis.strategy === "before-method-only") {
        strategyObject.value.hypothesis.strategy = "Before turbulence";
      } else if (strategy.value.hypothesis.strategy === "after-method-only") {
        strategyObject.value.hypothesis.strategy = "After turbulence";
      } else if (strategy.value.hypothesis.strategy === "continuously") {
        strategyObject.value.hypothesis.strategy = "Continuously";
      } else if (strategy.value.hypothesis.strategy === "during-method-only") {
        strategyObject.value.hypothesis.strategy =
          "Continuously during turbulence";
      }
      if (
        strategy.value.hypothesis.strategy === "during-method-only" ||
        strategy.value.hypothesis.strategy === "continuously"
      ) {
        if (strategy.value.hypothesis.frequency) {
          if (strategy.value.hypothesis.frequency > 1) {
            strategyObject.value.hypothesis.frequency = `Every ${strategy.value.hypothesis.frequency} seconds`;
          } else {
            strategyObject.value.hypothesis.frequency = `Every ${strategy.value.hypothesis.frequency} second`;
          }
          if (strategy.value.hypothesis.fail_fast) {
            strategyObject.value.hypothesis.fail_fast = "Yes";
          }
        }
      }
    }
    if (strategy.value.rollbacks) {
      if (strategy.value.rollbacks.strategy === "always") {
        strategyObject.value.rollbacks.strategy = "Always";
      } else if (strategy.value.rollbacks.strategy === "never") {
        strategyObject.value.rollbacks.strategy = "Never";
      } else if (strategy.value.rollbacks.strategy === "deviated") {
        strategyObject.value.rollbacks.strategy = "Only if experiment deviated";
      }
    }
  }
}

onMounted(() => {
  updateStrategyObject();
});
</script>

<style lang="scss">
.experimentStrategy {
  display: flex;

  > div {
    flex: 1 0 auto;

    &:first-child {
      padding-right: var(--space-small);
    }

    &:last-child {
      padding-left: var(--space-small);

      border-left: 1px solid var(--section-separator-color);
    }
  }

  dl {
    display: flex;
    margin: 0;

    > div {
      padding-right: var(--space-small);
    }

    > div + div {
      padding-left: var(--space-small);

      border-left: 1px solid var(--section-separator-color);
    }

    dt {
      display: flex;
      justify-content: space-between;

      color: var(--text-color-dim);
      font-size: 1.4rem;
      text-transform: uppercase;

      svg {
        height: 1.8rem;
        margin-left: var(--space-small);
      }
    }
  }
}
</style>
