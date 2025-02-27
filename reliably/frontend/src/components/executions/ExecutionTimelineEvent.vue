<template>
  <li
    class="timelineEvent"
    :class="{
      'timelineEvent--odd': isOdd,
      'timelineEvent--left': isLeftMode,
      'timelineEvent--discreet': isDiscreet,
    }"
    :data-id="event.date"
  >
    <ExecutionTimelineEventIcon
      :event="event"
      :isOdd="isOdd"
      :isLeftMode="isLeftMode"
    />
    <div class="timelineEvent__content">
      <time
        class="timelineEvent__time"
        :class="{ 'timelineEvent__time--odd': isOdd }"
        :datetime="dateWithTimeZone"
        :title="fullTime"
        >{{ preciseTime }}</time
      >
      <h3
        class="timelineEvent__title"
        :class="{ 'timelineEvent__title--hidden': isTitleHidden }"
      >
        {{ event.title }}
      </h3>
      <div v-if="event.subtitle" class="timelineEvent__subtitle">
        <span v-if="event.background" class="timelineEvent__background">
          Background
        </span>
        {{ event.subtitle }}
      </div>
      <div class="timelineEvent__icons">
        <span
          v-if="hasTracing"
          class="hasTooltip hasTooltip--bottom-center"
          aria-label="Includes Traces"
          label="Includes Traces"
        >
          <TracingIcon />
        </span>
        <span
          v-if="hasLoadTest || hasOhaLoadTest"
          class="hasTooltip hasTooltip--bottom-center"
          aria-label="Includes Load Test"
          label="Includes Load Test"
        >
          <TrendingUp />
        </span>
        <span
          v-if="hasPodsLogs"
          class="hasTooltip hasTooltip--bottom-center"
          aria-label="Includes Pod Logs"
          label="Includes Pod Logs"
        >
          <LogsIcon />
        </span>
      </div>
      <div class="timelineEvent__pills pills">
        <template v-if="event.steady_state_met !== undefined">
          <div
            class="timelineEvent__pill timelineEvent__pill--ok pill"
            v-if="event.steady_state_met"
          >
            Steady State Met
          </div>
          <div
            class="timelineEvent__pill timelineEvent__pill--ko pill"
            v-if="!event.steady_state_met"
          >
            Steady State Not Met
          </div>
        </template>
        <template v-if="event.tolerance_met !== undefined">
          <div
            class="timelineEvent__pill timelineEvent__pill--ok pill"
            v-if="event.tolerance_met"
          >
            Tolerance Met
          </div>
          <div
            class="timelineEvent__pill timelineEvent__pill--ko pill"
            v-if="!event.tolerance_met"
          >
            Tolerance Not Met
          </div>
        </template>
        <div
          class="timelineEvent__pill timelineEvent__pill--ko pill"
          v-if="event.details && event.details.status === 'failed'"
        >
          Failed
        </div>
      </div>
      <div
        v-if="event.execution_status"
        class="timelineEvent__experimentStatus"
      >
        <ExperimentStatus :status="event.execution_status" />
      </div>
      <div v-if="event.display_resume" class="timelineEvent__resume">
        <button @click.prevent="emitResume" class="button button--creative">
          Resume
        </button>
      </div>
      <div v-if="event.result_link">
        <button
          class="button button--inline"
          @click.prevent="scrollToEvent(event.result_link)"
        >
          View results
        </button>
      </div>
      <details v-if="event.details" ref="details" class="timelineEventDetail">
        <summary>
          <MaximizeIcon />
          <MinimizeIcon />
          Details
        </summary>
        <div class="timelineEventDetail__content">
          <dl>
            <div>
              <dt>Status</dt>
              <dd v-if="event.details.status !== undefined">
                {{ event.details.status }}
              </dd>
              <dd v-else>-</dd>
            </div>
            <div>
              <dt>Duration (seconds)</dt>
              <dd v-if="event.details.duration !== undefined">
                {{ event.details.duration }}
              </dd>
              <dd v-else>-</dd>
            </div>
          </dl>
          <dl v-if="hasArguments">
            <div>
              <dt>
                Arguments
                <span
                  class="hasTooltip hasTooltip--center-left"
                  label="The arguments passed by your configuration block. These arguments might be overriden at runtime, for example by environment variables on your local machine."
                  aria-label="The arguments passed by your configuration block. These arguments might be overriden at runtime, for example by environment variables on your local machine."
                  ><HelpCircle
                /></span>
              </dt>
              <dd>
                <ExecutionTimelineActivityArguments
                  :args="event.details.activity.provider.arguments"
                />
              </dd>
            </div>
          </dl>
          <dl v-if="event.details.exception">
            <div class="timelineEventDetail__exception">
              <dt>Exception</dt>
              <dd>
                <div>
                  <pre>{{ event.details.exception }}</pre>
                </div>
              </dd>
            </div>
          </dl>
          <dl v-if="hasTracing">
            <div>
              <dt>Trace</dt>
              <dd v-if="event.details.output">
                <XrayTrace :source="event.details.output" />
              </dd>
              <dd v-else>Activity output is not available yet.</dd>
            </div>
          </dl>
          <dl v-if="hasLoadTest">
            <div>
              <dt>Request Status</dt>
              <dd v-if="event.details.output && event.details.output.length">
                <LoadTestRequestStatus :source="event.details.output[0]" />
              </dd>
              <dd v-else>Activity output is not available yet.</dd>
            </div>
          </dl>
          <dl v-if="hasLoadTest">
            <div>
              <dt>Requests Timeline</dt>
              <dd v-if="event.details.output && event.details.output.length">
                <LoadTestRequestsTimeline :source="event.details.output[0]" />
              </dd>
              <dd v-else>Activity output is not available yet.</dd>
            </div>
          </dl>
          <dl v-if="hasLoadTest">
            <div>
              <dt>Response Time Distribution</dt>
              <dd v-if="event.details.output && event.details.output.length">
                <LoadTestResponseTimeDistribution
                  :source="event.details.output[0]"
                />
              </dd>
              <dd v-else>Activity output is not available yet.</dd>
            </div>
          </dl>
          <dl v-if="hasOhaLoadTest">
            <div>
              <dt>Load Test Summary</dt>
              <dd v-if="event.details.output">
                <OhaSummary
                  :source="(event.details.output as OhaOutput).summary"
                />
              </dd>
              <dd v-else>Activity output is not available yet.</dd>
            </div>
          </dl>
          <dl v-if="hasOhaLoadTest">
            <div>
              <dt>Response Time Distribution</dt>
              <dd v-if="event.details.output">
                <OhaResponseTimeHistogram
                  :source="{ all: (event.details.output as OhaOutput).responseTimeHistogram, successful:
                (event.details.output as OhaOutput).responseTimeHistogramSuccessful,
                notSuccessful: (event.details.output as OhaOutput).responseTimeHistogramNotSuccessful }"
                />
              </dd>
              <dd v-else>Activity output is not available yet.</dd>
            </div>
          </dl>
          <dl v-if="hasOhaLoadTest">
            <div>
              <dt>Latency Percentiles</dt>
              <dd v-if="event.details.output">
                <OhaLatencyPercentiles
                  :source="{ all: (event.details.output as OhaOutput).latencyPercentiles, successful:
                (event.details.output as OhaOutput).latencyPercentilesSuccessful,
                notSuccessful: (event.details.output as OhaOutput).latencyPercentilesNotSuccessful }"
                />
              </dd>
              <dd v-else>Activity output is not available yet.</dd>
            </div>
          </dl>
          <dl v-if="hasOhaLoadTest">
            <div>
              <dt>Requests per second</dt>
              <dd v-if="event.details.output">
                <OhaRps :source="(event.details.output as OhaOutput).rps" />
              </dd>
              <dd v-else>Activity output is not available yet.</dd>
            </div>
          </dl>
          <dl v-if="hasOhaLoadTest">
            <div>
              <dt>Details</dt>
              <dd v-if="event.details.output">
                <OhaDnsDetails
                  :source="(event.details.output as OhaOutput).details"
                />
              </dd>
              <dd v-else>Activity output is not available yet.</dd>
            </div>
          </dl>
          <dl v-if="hasOhaLoadTest">
            <div>
              <dt>Status Code Distribution</dt>
              <dd v-if="event.details.output">
                <OhaStatusCodeDistribution
                  :source="(event.details.output as OhaOutput).statusCodeDistribution"
                />
              </dd>
              <dd v-else>Activity output is not available yet.</dd>
            </div>
          </dl>
          <dl v-if="hasOhaLoadTest">
            <div>
              <dt>Error Distribution</dt>
              <dd v-if="event.details.output">
                <OhaErrorDistribution
                  :source="(event.details.output as OhaOutput).errorDistribution"
                />
              </dd>
              <dd v-else>Activity output is not available yet.</dd>
            </div>
          </dl>
          <dl>
            <div v-if="hasPodsLogs">
              <PodsLogs :logs="event.details.output" />
            </div>
            <div v-else>
              <dt>Output</dt>
              <dd v-if="event.details.output !== null">
                <JsonViewer
                  :json="JSON.stringify(event.details.output, null, 2)"
                  :no-padding="true"
                />
              </dd>
              <dd v-else>
                Output will be displayed when activity has completed
              </dd>
            </div>
          </dl>
          <dl>
            <div>
              <dt>Activity</dt>
              <dd>
                <JsonViewer
                  :json="JSON.stringify(event.details.activity, null, 2)"
                  :no-padding="true"
                />
              </dd>
            </div>
          </dl>
        </div>
      </details>
      <SlackMessage
        v-if="
          event.type === 'slack-message' &&
          event.slack_message_raw &&
          event.slack_message_channel
        "
        :message="event.slack_message_raw"
        :channel="event.slack_message_channel"
        :channel-index="event.slack_message_channel_index!"
        :user="
          event.slack_message_user
            ? event.slack_message_user
            : {
                id: '',
                name: 'unknown user',
                image: '/images/default-avatar.png',
                real_name: 'unknown user',
                display_name: 'unknown user',
              }
        "
        :thread="event.slack_message_thread"
      />
    </div>
  </li>
</template>

<script setup lang="ts">
import { toRefs, computed, ref, onMounted, onBeforeUnmount } from "vue";
import dayjs from "dayjs";
import { dateAsId } from "@/utils/strings";

import ExecutionTimelineEventIcon from "@/components/executions/ExecutionTimelineEventIcon.vue";
import ExperimentStatus from "@/components/experiments/ExperimentStatus.vue";
import ExecutionTimelineActivityArguments from "@/components/executions/ExecutionTimelineActivityArguments.vue";
import PodsLogs from "@/components/executions/ChaosK8sPodsLogs.vue";
import XrayTrace from "@/components/executions/XrayTrace.vue";
import LoadTestRequestStatus from "@/components/executions/LoadTestRequestStatus.vue";
import LoadTestRequestsTimeline from "@/components/executions/LoadTestRequestsTimeline.vue";
import LoadTestResponseTimeDistribution from "@/components/executions/LoadTestResponseTimeDistribution.vue";
import OhaSummary from "@/components/executions/OhaSummary.vue";
import OhaResponseTimeHistogram from "@/components/executions/OhaResponseTimeHistogram.vue";
import OhaLatencyPercentiles from "@/components/executions/OhaLatencyPercentiles.vue";
import OhaStatusCodeDistribution from "@/components/executions/OhaStatusCodeDistribution.vue";
import OhaErrorDistribution from "@/components/executions/OhaErrorDistribution.vue";
import OhaDnsDetails from "@/components/executions/OhaDnsDetails.vue";
import OhaRps from "@/components/executions/OhaRps.vue";
import SlackMessage from "@/components/executions/SlackMessage.vue";
import JsonViewer from "@/components/_ui/JsonViewer.vue";
import MaximizeIcon from "@/components/svg/MaximizeIcon.vue";
import MinimizeIcon from "@/components/svg/MinimizeIcon.vue";
import LogsIcon from "@/components/svg/FileText.vue";
import TracingIcon from "@/components/svg/TracingIcon.vue";
import TrendingUp from "@/components/svg/TrendingUp.vue";
import HelpCircle from "@/components/svg/HelpCircle.vue";

import type { ExecutionTimelineEvent } from "@/types/executions";
import type { OhaOutput } from "@/types/oha";

const props = defineProps<{
  event: ExecutionTimelineEvent;
  isOdd?: boolean;
  isLeftMode: boolean;
}>();
const { event, isOdd, isLeftMode } = toRefs(props);

const emit = defineEmits<{
  (e: "scroll-to", id: string): void;
  (e: "resume-execution"): void;
}>();

const isTitleHidden = computed<boolean>(() => {
  return event.value.type === "slack-message";
});

const isDiscreet = computed<boolean>(() => {
  return event.value.type === "info";
});

const hasArguments = computed<boolean>(() => {
  // console.log(event.value.details.activity.provider.arguments);
  return (
    event.value.details.activity.provider.arguments &&
    typeof event.value.details.activity.provider.arguments === "object" &&
    Object.keys(event.value.details.activity.provider.arguments).length > 0
  );
});

const hasTracing = computed<boolean>(() => {
  if (event.value.details === undefined) {
    return false;
  } else {
    return (
      event.value.details.activity.provider.module === "chaosaws.xray.probes" &&
      event.value.details.activity.provider.func === "get_most_recent_trace"
    );
  }
});

const hasLoadTest = computed<boolean>(() => {
  if (event.value.details === undefined) {
    return false;
  } else {
    return (
      event.value.details.activity.provider.module ===
        "chaosreliably.activities.load.actions" &&
      event.value.details.activity.provider.func ===
        "inject_gradual_traffic_into_endpoint"
    );
  }
});

const hasOhaLoadTest = computed<boolean>(() => {
  if (event.value.details === undefined) {
    return false;
  } else {
    return (
      event.value.details.activity.provider.module ===
        "chaosreliably.activities.load.actions" &&
      event.value.details.activity.provider.func === "run_load_test"
    );
  }
});

const hasPodsLogs = computed<boolean>(() => {
  if (event.value.details === undefined) {
    return false;
  } else {
    return (
      event.value.details.activity.provider.module === "chaosk8s.pod.probes"
    );
  }
});

const dateWithTimeZone = computed<string>(() => {
  return event.value.date;
});

const fullTime = computed<string>(() => {
  return dayjs(dateWithTimeZone.value).format("D MMMM YYYY, H:mm:ss");
});

const preciseTime = computed<string>(() => {
  if (dateWithTimeZone.value !== "") {
    return dayjs(dateWithTimeZone.value).format("H:mm:ss.SSS");
  } else {
    return "";
  }
});

function scrollToEvent(id: string) {
  emit("scroll-to", id);
}

function emitResume() {
  emit("resume-execution");
}

const details = ref<HTMLInputElement | null>(null);
const wereDetailsClosed = ref<boolean>(true);
function handleBeforePrint() {
  if (details.value && !details.value.hasAttribute("open")) {
    details.value.setAttribute("open", "");
    wereDetailsClosed.value = false;
  }
}
function handleAfterPrint() {
  if (wereDetailsClosed) {
    details.value?.removeAttribute("open");
  }
}

onMounted(() => {
  window.addEventListener("beforeprint", handleBeforePrint);
  window.addEventListener("afterprint", handleAfterPrint);
});

onBeforeUnmount(() => {
  window.removeEventListener("beforeprint", handleBeforePrint);
  window.removeEventListener("afterprint", handleAfterPrint);
});
</script>

<style lang="scss" scoped>
.timelineEvent {
  position: relative;
  z-index: 2;

  display: flex;
  flex-direction: row-reverse;
  padding-top: var(--space-medium);

  @media (min-width: 44rem) {
    padding-top: 0;
  }

  @media print {
    flex-direction: column;
  }

  & + & {
    margin-top: var(--space-large);

    @media print {
      margin-top: var(--space-small);

      border-top: 0.1rem solid var(--grey-500);
    }
  }

  &__content {
    position: relative;

    display: flex;
    flex-direction: column;
    padding: var(--space-small);
    width: calc(100% - 7.2rem);

    background-color: white;
    border-radius: var(--border-radius-m);

    outline: 0.2rem solid transparent;

    transition: outline-color 1s ease-in-out;

    &--highlight {
      outline-color: var(--pink-500);

      transition: outline-color 0.3s ease-in-out;
    }

    @media (min-width: 44rem) {
      width: calc(50% - 4.8rem);
    }

    @media print {
      order: 2;

      padding-left: 0;
      width: 100%;
    }

    &::after {
      content: "";

      position: absolute;
      top: 1.2rem;
      left: -0.8rem;
      z-index: -1;

      display: block;
      height: 0;
      width: 0;

      border-top: 1.2rem solid transparent;
      border-right: 1.2rem solid white;
      border-bottom: 1.2rem solid transparent;
      border-left: 0;
    }
  }

  &__time {
    position: absolute;
    top: -2.4rem;
    left: 0;

    color: var(--text-color-dim);
    font-size: 1.2rem;
    text-align: right;

    @media (min-width: 44rem) {
      top: 2.4rem;
      left: -9.6rem;

      font-size: 1.4rem;

      transform: translate(-100%, -50%);
    }

    @media print {
      top: 0;
      left: 0;

      font-size: 12px;
    }
  }

  &__title {
    margin-top: 0;
    margin-bottom: 0;
    font-size: 1.6rem;

    &--hidden {
      display: none;
    }

    @media (print) {
      font-size: 14px;
    }
  }

  &__subtitle {
    order: -1;

    color: var(--text-color-dim);
    font-size: 1.2rem;
    text-transform: uppercase;
  }

  &__background {
    margin-right: 0.6rem;
    padding: 0.1rem 0.3rem;

    background-color: var(--blue-100);
    border-radius: var(--border-radius-s);

    color: var(--blue-500);
    font-size: 1.2rem;
    font-weight: 700;
    text-transform: uppercase;
  }

  &__icons {
    position: absolute;
    top: var(--space-small);
    right: var(--space-small);

    color: var(--text-color-dim);

    span {
      display: grid;
      align-items: center;
      padding: 0.6rem;

      border-radius: 50%;

      &:hover {
        background-color: var(--grey-200);

        color: var(--text-color);
      }

      svg {
        height: 2.4rem;
      }
    }
  }

  &__pills {
    &:not(:empty) {
      margin-top: var(--space-small);
    }
  }

  &__pill {
    color: white;
    font-size: 1.4rem;

    @media (print) {
      font-size: 12px;
    }

    &--ok {
      background-color: var(--statusColor-ok);
    }

    &--ko {
      background-color: var(--statusColor-ko);
    }
  }

  &__resume,
  &__experimentStatus {
    margin-top: var(--space-small);
  }

  .timelineEventDetail {
    padding-top: var(--space-small);

    summary {
      display: inline-flex;
      gap: 0.6rem;
      padding: 0.4rem;

      border-radius: var(--border-radius-s);
      cursor: pointer;
      list-style: none;

      color: var(--text-color-dim);
      font-size: 1.2rem;
      text-transform: uppercase;

      svg {
        height: 1.6rem;

        &:nth-child(2) {
          display: none;
        }
      }

      &:hover {
        background-color: var(--grey-200);
      }

      @media print {
        display: none;
      }
    }

    &[open] {
      summary {
        svg {
          &:first-child {
            display: none;
          }
          &:nth-child(2) {
            display: inline-block;
          }
        }
      }
    }

    &__content {
      padding-top: var(--space-small);

      > div,
      > dl {
        padding: var(--space-small);

        background-color: var(--section-background);
        border-radius: var(--border-radius-s);
      }

      dl {
        display: flex;
        gap: var(--space-medium);

        > div {
          flex: 1;
          max-width: 100%;
        }

        > div + div {
          padding-left: var(--space-small);

          border-left: 1px solid var(--section-separator-color);
        }

        dt {
          position: relative;

          color: var(--text-color-dim);
          font-size: 1.4rem;
          text-transform: uppercase;

          @media (print) {
            font-size: 10px;
          }

          span {
            position: absolute;
            top: 0;
            right: 0;

            svg {
              height: 1.6rem;
            }
          }
        }
      }

      dl + dl {
        margin-top: var(--space-small);
      }
    }

    &__exception {
      width: 100%;

      pre {
        margin-bottom: 0;
        overflow-x: auto;

        background-color: white;

        &::-webkit-scrollbar {
          height: 1rem;
          width: 1rem;

          background-color: transparent;
        }

        &::-webkit-scrollbar-corner {
          background-color: transparent;
        }

        &::-webkit-scrollbar-track {
          padding: 0.1rem;
        }

        &::-webkit-scrollbar-thumb {
          height: 0.6rem;
          width: 0.6rem;

          background-color: var(--grey-500);
          border-radius: 0.3rem;
          border: 0.1rem solid transparent;
        }

        scrollbar-color: var(--grey-500) transparent;
        scrollbar-width: thin;
      }
    }
  }

  &--odd {
    @media screen and (min-width: 44rem) {
      flex-direction: row;
    }

    .timelineEvent__time {
      @media screen and (min-width: 44rem) {
        right: auto;
        left: calc(100% + 9.6rem);

        text-align: left;
        transform: translate(0, -50%);
      }
    }

    .timelineEvent__content {
      @media screen and (min-width: 44rem) {
        &::after {
          right: -0.8rem;
          left: auto;

          border-right: 0;
          border-left: 1.2rem solid white;
        }
      }
    }
  }

  &--left {
    flex-direction: row-reverse;
    padding-top: var(--space-medium);

    .timelineEvent__content {
      width: calc(100% - 7.2rem);

      &::after {
        right: auto;
        left: -0.8rem;

        border-right: 1.2rem solid white;
        border-left: 0;
      }
    }

    .timelineEvent__time {
      right: auto;
      left: 0;

      text-align: left;
      transform: translate(0, -5.4rem);
    }
  }

  &--discreet {
    &.timelineEvent--odd {
      text-align: right;
    }
    .timelineEvent__content {
      padding-right: 0;
      padding-left: 0;

      background-color: transparent;

      &::after {
        display: none;
      }
    }

    .timelineEvent__title {
      color: var(--text-color-dim);
      font-size: 1.4rem;
      font-weight: 400;
      text-transform: uppercase;
    }

    .timelineEvent__subtitle {
      display: none;
    }

    .timelineEvent__time {
      top: 2.6rem;
    }
  }

  &--discreet.timelineEvent--left {
    &.timelineEvent--odd {
      text-align: left;
    }
  }
}
</style>
