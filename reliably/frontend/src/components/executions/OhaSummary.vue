<template>
  <div class="ohaSummary">
    <table class="ohaSummary__table">
      <tr class="ohaSummary__row ohaSummary__row--successRate">
        <th scope="row">Success rate</th>
        <td>{{ toFixedIfNecessary(source.successRate * 100, 2) }}%</td>
      </tr>
      <tr class="ohaSummary__row ohaSummary__row--total">
        <th scope="row">Total</th>
        <td>{{ toFixedIfNecessary(source.total, 4) }} s</td>
      </tr>
      <tr class="ohaSummary__row ohaSummary__row--slow">
        <th scope="row">Slowest</th>
        <td>{{ toFixedIfNecessary(source.slowest, 4) }} s</td>
      </tr>
      <tr class="ohaSummary__row ohaSummary__row--fast">
        <th scope="row">Fastest</th>
        <td>{{ toFixedIfNecessary(source.fastest, 4) }} s</td>
      </tr>
      <tr class="ohaSummary__row ohaSummary__row--average">
        <th scope="row">Average</th>
        <td>{{ toFixedIfNecessary(source.average, 4) }} s</td>
      </tr>
      <tr class="ohaSummary__row ohaSummary__row--request">
        <th scope="row">Requests/sec</th>
        <td>{{ toFixedIfNecessary(source.requestsPerSec, 4) }}</td>
      </tr>
      <tr class="ohaSummary__row" role="presentation">
        <td></td>
        <td></td>
      </tr>
      <tr class="ohaSummary__row">
        <th scope="row">Total data</th>
        <td>{{ formatBytes(source.totalData) }}</td>
      </tr>
      <tr class="ohaSummary__row">
        <th scope="row">Size/request</th>
        <td>{{ formatBytes(source.sizePerRequest) }}</td>
      </tr>
      <tr class="ohaSummary__row">
        <th scope="row">Size/sec</th>
        <td>{{ formatBytes(source.sizePerSec) }}</td>
      </tr>
    </table>
  </div>
</template>

<script setup lang="ts">
import { toRefs } from "vue";

import { toFixedIfNecessary, formatBytes } from "@/utils/numbers";

import type { OhaSummary } from "@/types/oha";

const props = defineProps<{
  source: OhaSummary;
}>();
const { source } = toRefs(props);
</script>

<style lang="scss" scoped>
.ohaSummary {
  &__table {
    margin-top: var(--space-small);

    th {
      &[scope="row"] {
        padding-left: 0;

        font-weight: 500;
      }
    }

    td {
      padding-left: var(--space-small);

      font-variant-numeric: tabular-nums;
    }
  }

  &__row {
    &--slow {
      color: var(--sand-500);
    }

    &--fast {
      color: var(--green-500);
    }

    &--average {
      color: var(--blue-500);
    }

    &[role="presentation"] {
      td {
        height: 2.4rem;
      }
    }
  }
}
</style>
