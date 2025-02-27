<template>
  <div
    class="executionTimeline"
    :class="{ 'executionTimeline--left': isLeftMode }"
  >
    <div class="executionTimelineToggle">
      <input
        type="checkbox"
        id="executionTimelineSwitch"
        v-model="isLeftMode"
      />
      <label for="executionTimelineSwitch">Toggle display</label>
    </div>
    <ol class="executionTimeline__events list-reset" ref="events">
      <TimelineEvent
        v-for="(event, index) in timeline"
        :key="index"
        :event="event"
        :isOdd="(index + 1) % 2 === 1"
        :isLeftMode="isLeftMode"
        :index="index"
        @scroll-to="handleEventScroll"
        @resume-execution="handleResume"
      />
    </ol>
  </div>
</template>

<script setup lang="ts">
import { toRefs, ref, watch, onMounted } from "vue";
import dayjs from "dayjs";
import utc from "dayjs/plugin/utc";
import { uuid } from "vue-uuid";

import { getReliablyUiExtension } from "@/utils/experiments";
import { dateAsId } from "@/utils/strings";

import TimelineEvent from "@/components/executions/ExecutionTimelineEvent.vue";
import type {
  Execution,
  ExecutionTimelineEvent,
  SlackMessage,
  SlackUser,
  SlackUsers,
  SlackChannel,
  SlackMessageBotProfile,
} from "@/types/executions";
import type {
  ReliablySafeguard,
  Configuration,
  ExperimentDefinition,
  Extension,
} from "@/types/experiments";
import { isArray } from "lodash-es";

const props = defineProps<{
  execution: Execution;
  probes: { type: string; probes: ReliablySafeguard[] } | null;
  conf?: Configuration | null;
}>();
const { execution, probes } = toRefs(props);

const emit = defineEmits<{
  (e: "resume-execution"): void;
}>();

const timeline = ref<ExecutionTimelineEvent[]>([]);

const isLeftMode = ref<boolean>(false);

const sortEventsByDate = (
  a: ExecutionTimelineEvent,
  b: ExecutionTimelineEvent
): number => {
  let dateA = new Date(a.date);
  let dateB = new Date(b.date);
  return dateA.valueOf() - dateB.valueOf();
};

// We need to know if the experiment was created using the builder and
// declared some of its method as warmup
const hasWarmup = ref<boolean>(false);
const reliablyUi = ref<Extension | null>(null);
function checkReliablyUi() {
  reliablyUi.value = getReliablyUiExtension(execution.value.result.experiment);
  if (reliablyUi.value !== null) {
    hasWarmup.value = true;
    // Number of warmup activities is reliablyUi.workflow.warmup.length
  }
}

let slackMessages: ExecutionTimelineEvent[] = [];
let slackUsers: SlackUsers | null = null;
let slackBots: {
  [key: string]: SlackMessageBotProfile;
} | null = null;

let prechecks: ExecutionTimelineEvent[] = [];

let ssBeforeEvents: ExecutionTimelineEvent[] = [];
const isSSHBeforeComplete = ref<boolean>(false);
function addSSHBeforeEndedEvent() {
  let end = ssBeforeEvents[ssBeforeEvents.length - 1].date;
  ssBeforeEvents.push({
    title: "Verification (Before Turbulence) Probes Ended",
    subtitle: "Info",
    date: end,
    type: "info",
    steady_state_met:
      execution.value.result.steady_states.before.steady_state_met,
  });
  isSSHBeforeComplete.value = true;
}

let ssDuringEvents: ExecutionTimelineEvent[] = [];
const isSSHDuringComplete = ref<boolean>(false);
function addSSHDuringEndedEvent() {
  let end = ssDuringEvents[ssDuringEvents.length - 1].date;
  ssDuringEvents.push({
    title: "Verification (During Turbulence) Probes Ended",
    subtitle: "Info",
    date: end,
    type: "info",
    steady_state_met:
      execution.value.result.steady_states.during.steady_state_met,
  });
  isSSHDuringComplete.value = true;
}

let runEvents: ExecutionTimelineEvent[] = [];
let execEvents: ExecutionTimelineEvent[] = [];
const isMethodComplete = ref<boolean>(false);
function addMethodEndedEvent() {
  if (execEvents.length) {
    let methodEnd = execEvents[execEvents.length - 1].date;
    execEvents.push({
      title: "Turbulence Ended",
      subtitle: "Info",
      date: methodEnd,
      type: "info",
    });
  }
  isMethodComplete.value = true;
}

let ssAfterEvents: ExecutionTimelineEvent[] = [];
const isSSHAfterComplete = ref<boolean>(false);
function addSSHAfterEndedEvent() {
  let end = ssAfterEvents[ssAfterEvents.length - 1].date;
  ssAfterEvents.push({
    title: "Verification (After Turbulence) Probes Ended",
    subtitle: "Info",
    date: end,
    type: "info",
    steady_state_met:
      execution.value.result.steady_states.after.steady_state_met,
  });
  isSSHAfterComplete.value = true;
}

let beforeRollbacksSafeguards: ExecutionTimelineEvent[] = [];

let rollbacksEvents: ExecutionTimelineEvent[] = [];
const isRollbacksComplete = ref<boolean>(false);
function addRollbacksEndedEvent() {
  let end = rollbacksEvents[rollbacksEvents.length - 1].date;
  rollbacksEvents.push({
    title: "Rollbacks Ended",
    subtitle: "Info",
    date: end,
    type: "info",
  });
}

function isPause(event: any): boolean {
  return event.activity.provider.module === "chaosreliably.activities.pauses";
}

function pauseTriggeredBy(event: any): string {
  if (isPause(event) && event.activity.provider.arguments.username) {
    if (event.activity.provider.arguments.username !== "") {
      return `by ${event.activity.provider.arguments.username}`;
    } else {
      return "";
    }
  } else {
    return "";
  }
}

function getSlackMessages() {
  if (execution.value.result.experiment.extensions) {
    const extensions = execution.value.result.experiment.extensions;
    const re = extensions.filter((e) => {
      return e.name === "reliably";
    });
    if (re[0].captures && re[0].captures.slack) {
      const slack = re[0].captures.slack;
      if (slack.users) {
        slackUsers = slack.users as SlackUsers;
      }

      if (slack.channels) {
        slack.channels.forEach((channel: SlackChannel, chIndex: number) => {
          if (channel.conversation) {
            channel.conversation.forEach((m: SlackMessage) => {
              if (m.reply_count === undefined || m.reply_count === 0) {
                // If message has replies, it will be present in the thread
                storeBotProfile(m);
                addBotProfileIfUndefined(m);
                const slackEvent: ExecutionTimelineEvent = {
                  title: m.text,
                  subtitle: "Slack",
                  type: "slack-message",
                  date: formatSlackTimestamp(m.ts),
                  slack_message_raw: m,
                  slack_message_channel: channel.name,
                  slack_message_channel_index: chIndex,
                  slack_message_user:
                    slackUsers === null
                      ? {
                          id: "",
                          name: "unknown user",
                          image: "/images/default-avatar.png",
                          real_name: "unknown user",
                          display_name: "unknown user",
                        }
                      : slackUsers[m.user],
                };
                slackMessages.push(slackEvent);
              }
            });
          }

          if (channel.threads) {
            const threads = Object.keys(channel.threads);
            threads.forEach((thread, index) => {
              channel.threads[thread].forEach((m: SlackMessage) => {
                storeBotProfile(m);
                addBotProfileIfUndefined(m);
                const slackEvent: ExecutionTimelineEvent = {
                  title: m.text,
                  subtitle: "Slack",
                  type: "slack-message",
                  date: formatSlackTimestamp(m.ts),
                  slack_message_raw: m,
                  slack_message_channel: channel.name,
                  slack_message_user:
                    slackUsers === null
                      ? {
                          id: "",
                          name: "unknown user",
                          image: "/images/default-avatar.png",
                          real_name: "unknown user",
                          display_name: "unknown user",
                        }
                      : slackUsers[m.user],
                  slack_message_thread: index + 1,
                };
                slackMessages.push(slackEvent);
              });
            });
          }
        });
      }
    }
  }
}

function storeBotProfile(m: SlackMessage) {
  const botProfile: SlackMessageBotProfile | undefined = m.bot_profile;
  if (botProfile !== undefined) {
    const id = botProfile.id;
    if (slackBots === null) {
      slackBots = {
        [id]: botProfile,
      };
    } else {
      slackBots[id] = botProfile;
    }
  }
}

function addBotProfileIfUndefined(m: SlackMessage): SlackMessage {
  const unknownBot: SlackMessageBotProfile = {
    id: "",
    name: "unknown bot",
    icons: {
      image_36: "/images/default-bot-36.webp",
      image_48: "/images/default-bot-48.webp",
      image_72: "/images/default-bot-72.webp",
    },
    app_id: "",
    deleted: false,
    team_id: "",
    updated: 0,
  };
  if (m.bot_profile !== undefined) {
    return m;
  } else if (m.bot_id === undefined) {
    return m;
  } else {
    if (slackBots === null) {
      m.bot_profile = unknownBot;
    } else {
      const found: boolean = slackBots[m.bot_id] !== undefined;
      if (found) {
        m.bot_profile = slackBots[m.bot_id];
      } else {
        m.bot_profile = unknownBot;
      }
    }
    return m;
  }
}

function formatSlackTimestamp(ts: string): string {
  dayjs.extend(utc);
  const microseconds = ts.split(".")[1];
  const formattedTs = dayjs.unix(Number(ts)).utc().format().slice(0, -1);
  return `${formattedTs}.${microseconds}`;
}

const buildTimeline = () => {
  // Experiment Start
  let start: ExecutionTimelineEvent = {
    title: "Experiment Starts",
    date: `${execution.value.result.start}+00:00`,
    type: "experiment",
  };
  timeline.value.push(start);
  if (probes.value !== null && probes.value.type === "prechecks") {
    const p: ReliablySafeguard = probes.value.probes[0];
    const event: ExecutionTimelineEvent = {
      title: "Execution Interrupted",
      subtitle: "Precheck integration",
      type: "safeguard-precheck",
      date: `${p.end}`,
      details: p,
    };
    prechecks.push(event);
  }
  if (execution.value.result.steady_states.before !== null) {
    let ssBefore = execution.value.result.steady_states.before.probes;
    if (ssBefore !== undefined && ssBefore.length) {
      ssBefore.forEach((probe: any) => {
        if (isPause(probe)) {
          if (probe.end === undefined) {
            ssBeforeEvents.push({
              title: probe.activity.name,
              subtitle: `Experiment paused ${pauseTriggeredBy(probe)}`,
              type: "pause",
              date: probe.start,
            });
          } else {
            ssBeforeEvents.push({
              title: probe.activity.name,
              subtitle: `Experiment paused ${pauseTriggeredBy(
                probe
              )} and resumed after ${Math.floor(probe.duration)} seconds`,
              type: "pause",
              date: probe.start,
              details: probe,
              details_type: "pause",
            });
          }
        } else {
          if (probe.end === undefined) {
            ssBeforeEvents.push({
              title: probe.activity.name,
              subtitle: "Probe starts",
              type: "probe",
              date: probe.start,
            });
          } else {
            if (probe.background !== undefined && probe.background === true) {
              ssBeforeEvents.push({
                title: probe.activity.name,
                subtitle: "Probe starts",
                type: "probe",
                date: probe.start,
              });
              ssBeforeEvents.push({
                title: probe.activity.name,
                subtitle: "Probe ends",
                type: "probe",
                date: probe.end,
                tolerance_met: probe.tolerance_met,
                status: probe.status,
                details: probe,
                details_type: "probe",
              });
            } else {
              ssBeforeEvents.push({
                title: probe.activity.name,
                subtitle: "Probe",
                type: "probe",
                date: probe.end,
                tolerance_met: probe.tolerance_met,
                status: probe.status,
                details: probe,
                details_type: "probe",
              });
            }
          }
        }
      });
      ssBeforeEvents.sort((a, b) => {
        return sortEventsByDate(a, b);
      });
      let start = ssBeforeEvents[0].date;
      ssBeforeEvents.unshift({
        title: "Starting Verification (Before Turbulence) Probes",
        subtitle: "Info",
        date: start,
        type: "info",
      });
    }
  } else {
    isSSHBeforeComplete.value = true;
  }
  let run = execution.value.result.run;
  if (run.length) {
    if (!isSSHBeforeComplete.value) {
      addSSHBeforeEndedEvent();
    }

    run.forEach((r: any) => {
      if (isPause(r)) {
        if (r.end === undefined) {
          runEvents.push({
            title: r.activity.name,
            subtitle: `Experiment paused ${pauseTriggeredBy(r)}`,
            type: "pause",
            date: r.start,
            display_resume: true,
          });
        } else {
          runEvents.push({
            title: r.activity.name,
            subtitle: `Experiment paused ${pauseTriggeredBy(
              r
            )} and resumed after ${Math.floor(r.duration)} seconds`,
            type: "pause",
            date: r.end,
            details: r,
            details_type: "pause",
          });
        }
      } else {
        let type: string = r.activity.type;
        if (r.end === undefined) {
          runEvents.push({
            title: r.activity.name,
            subtitle: `${type} starts`,
            type: type,
            details: r,
            date: r.start,
          });
        } else {
          if (
            r.activity.background !== undefined &&
            r.activity.background === true
          ) {
            runEvents.push({
              title: r.activity.name,
              subtitle: `${type} starts`,
              type: type,
              date: r.start,
              result_link: r.end,
              background: true,
            });
            runEvents.push({
              title: r.activity.name,
              subtitle: `${type} ends`,
              type: type,
              date: r.end,
              details: r,
              details_type: "run",
              background: true,
            });
          } else {
            runEvents.push({
              title: r.activity.name,
              subtitle: `${type}`,
              type: type,
              date: r.end,
              details: r,
              details_type: "run",
            });
          }
        }
      }
    });
  }
  let ssDuring = execution.value.result.steady_states.during;
  if (ssDuring !== undefined && ssDuring.length) {
    if (!isSSHBeforeComplete.value) {
      addSSHBeforeEndedEvent();
    }
    ssDuring.forEach(
      (probesArray: { probes: any[]; steady_state_met: boolean }) => {
        probesArray.probes.forEach((probe: any) => {
          if (isPause(probe)) {
            if (probe.end === undefined) {
              ssDuringEvents.push({
                title: probe.activity.name,
                subtitle: `Experiment paused ${pauseTriggeredBy(probe)}`,
                type: "pause",
                date: probe.start,
              });
            } else {
              ssDuringEvents.push({
                title: probe.activity.name,
                subtitle: `Experiment paused ${pauseTriggeredBy(
                  probe
                )} and resumed after ${Math.floor(probe.duration)} seconds`,
                type: "pause",
                date: probe.end,
                details: probe,
                details_type: "pause",
              });
            }
          } else {
            if (probe.end === undefined) {
              ssDuringEvents.push({
                title: probe.activity.name,
                subtitle: "Probe starts",
                type: "probe",
                date: probe.start,
              });
            } else {
              if (probe.background !== undefined && probe.background === true) {
                ssDuringEvents.push({
                  title: probe.activity.name,
                  subtitle: "Probe starts",
                  type: "probe",
                  date: probe.start,
                });
                ssDuringEvents.push({
                  title: probe.activity.name,
                  subtitle: "Probe ends",
                  type: "probe",
                  date: probe.end,
                  tolerance_met: probe.tolerance_met,
                  status: probe.status,
                  details: probe,
                  details_type: "probe",
                });
              } else {
                ssDuringEvents.push({
                  title: probe.activity.name,
                  subtitle: "Probe",
                  type: "probe",
                  date: probe.end,
                  tolerance_met: probe.tolerance_met,
                  status: probe.status,
                  details: probe,
                  details_type: "probe",
                });
              }
            }
          }
        });
      }
    );
    ssDuringEvents.sort((a, b) => {
      return sortEventsByDate(a, b);
    });
    let start = ssDuringEvents[0].date;
    ssDuringEvents.unshift({
      title: "Starting Warm-up and Turbulence Verification Probes",
      subtitle: "Info",
      date: start,
      type: "info",
    });
  } else {
    isSSHDuringComplete.value = true;
  }
  let tmpExecEvents = runEvents.concat(ssDuringEvents);
  if (tmpExecEvents.length) {
    tmpExecEvents.sort((a, b) => {
      return sortEventsByDate(a, b);
    });
    let start = tmpExecEvents[0].date;
    const title = hasWarmup.value ? "Starting Warm-up" : "Starting Turbulence";
    execEvents.push({
      title: title,
      subtitle: "Info",
      date: start,
      type: "info",
    });
    execEvents.push(...tmpExecEvents);
  }
  if (execution.value.result.steady_states.after !== null) {
    if (!isSSHBeforeComplete.value) {
      addSSHBeforeEndedEvent();
    }
    if (!isSSHDuringComplete.value) {
      addSSHDuringEndedEvent();
    }
    if (!isMethodComplete.value) {
      addMethodEndedEvent();
    }

    let ssAfter = execution.value.result.steady_states.after.probes;
    if (ssAfter !== undefined && ssAfter.length) {
      ssAfter.forEach((probe: any) => {
        if (isPause(probe)) {
          if (probe.end === undefined) {
            ssAfterEvents.push({
              title: probe.activity.name,
              subtitle: `Experiment paused ${pauseTriggeredBy(probe)}`,
              type: "pause",
              date: probe.start,
            });
          } else {
            ssAfterEvents.push({
              title: probe.activity.name,
              subtitle: `Experiment paused ${pauseTriggeredBy(
                probe
              )} and resumed after ${Math.floor(probe.duration)} seconds`,
              type: "pause",
              date: probe.end,
              details: probe,
              details_type: "pause",
            });
          }
        } else {
          if (probe.end === undefined) {
            ssAfterEvents.push({
              title: probe.activity.name,
              subtitle: "Probe starts",
              type: "probe",
              date: probe.start,
            });
          } else {
            if (probe.background !== undefined && probe.background === true) {
              ssAfterEvents.push({
                title: probe.activity.name,
                subtitle: "Probe starts",
                type: "probe",
                date: probe.start,
              });
              ssAfterEvents.push({
                title: probe.activity.name,
                subtitle: "Probe ends",
                type: "probe",
                date: probe.end,
                tolerance_met: probe.tolerance_met,
                status: probe.status,
                details: probe,
                details_type: "probe",
              });
            } else {
              ssAfterEvents.push({
                title: probe.activity.name,
                subtitle: "Probe",
                type: "probe",
                date: probe.end,
                tolerance_met: probe.tolerance_met,
                status: probe.status,
                details: probe,
                details_type: "probe",
              });
            }
          }
        }
      });
      ssAfterEvents.sort((a, b) => {
        return sortEventsByDate(a, b);
      });
      let start = ssAfterEvents[0].date;
      ssAfterEvents.unshift({
        title: "Starting Verification (After Turbulence) Probes",
        subtitle: "Info",
        date: start,
        type: "info",
      });
    }
  } else {
    isSSHAfterComplete.value = true;
  }
  if (probes.value !== null && probes.value.type === "safeguards") {
    const p: ReliablySafeguard = probes.value.probes[0];
    const event: ExecutionTimelineEvent = {
      title: "Execution Interrupted",
      subtitle: "Safeguards integration",
      type: "safeguard-precheck",
      date: `${p.end}`,
      details: p,
    };
    beforeRollbacksSafeguards.push(event);
  }
  let rollbacks = execution.value.result.rollbacks;
  if (rollbacks !== undefined && rollbacks.length) {
    if (!isSSHBeforeComplete.value) {
      addSSHBeforeEndedEvent();
    }
    if (!isSSHBeforeComplete.value) {
      addSSHBeforeEndedEvent();
    }
    if (!isMethodComplete.value) {
      addMethodEndedEvent();
    }
    if (!isSSHAfterComplete.value) {
      addSSHAfterEndedEvent();
    }

    rollbacks.forEach((rollback: any) => {
      if (isPause(rollback)) {
        if (rollback.end === undefined) {
          rollbacksEvents.push({
            title: rollback.activity.name,
            subtitle: `Experiment paused ${pauseTriggeredBy(rollback)}`,
            type: "pause",
            date: rollback.start,
          });
        } else {
          rollbacksEvents.push({
            title: rollback.activity.name,
            subtitle: `Experiment paused ${pauseTriggeredBy(
              rollback
            )} and resumed after ${Math.floor(rollback.duration)}s`,
            type: "pause",
            date: rollback.end,
            details: rollback,
            details_type: "pause",
          });
        }
      } else {
        if (rollback.end === undefined) {
          rollbacksEvents.push({
            title: rollback.activity.name,
            subtitle: "Rollback starts",
            type: "rollback",
            date: rollback.start,
          });
        } else {
          if (
            rollback.background !== undefined &&
            rollback.background === true
          ) {
            rollbacksEvents.push({
              title: rollback.activity.name,
              subtitle: "Rollback starts",
              type: "rollback",
              date: rollback.start,
            });
            rollbacksEvents.push({
              title: rollback.activity.name,
              subtitle: "Rollback ends",
              type: "rollback",
              date: rollback.end,
              status: rollback.status,
              details: rollback,
              details_type: "rollback",
            });
          } else {
            rollbacksEvents.push({
              title: rollback.activity.name,
              subtitle: "Rollback",
              type: "rollback",
              date: rollback.end,
              status: rollback.status,
              details: rollback,
              details_type: "rollback",
            });
          }
        }
      }
    });
    rollbacksEvents.sort((a, b) => {
      return sortEventsByDate(a, b);
    });
    let start = rollbacksEvents[0].date;
    rollbacksEvents.unshift({
      title: "Starting Rollbacks",
      subtitle: "Info",
      date: start,
      type: "info",
    });
  } else {
    isRollbacksComplete.value = true;
  }

  // Experiment Ends
  if (execution.value.user_state!.current === "finished") {
    // Wrap up
    if (!isSSHBeforeComplete.value) {
      addSSHBeforeEndedEvent();
    }
    if (!isSSHBeforeComplete.value) {
      addSSHBeforeEndedEvent();
    }
    if (!isMethodComplete.value) {
      addMethodEndedEvent();
    }
    if (!isSSHAfterComplete.value) {
      addSSHAfterEndedEvent();
    }
    if (!isRollbacksComplete.value) {
      addRollbacksEndedEvent();
    }

    timeline.value.push(...prechecks);
    timeline.value.push(...ssBeforeEvents);
    timeline.value.push(...execEvents);
    timeline.value.push(...ssAfterEvents);
    timeline.value.push(...beforeRollbacksSafeguards);
    timeline.value.push(...rollbacksEvents);

    let status: "deviated" | "completed" | "interrupted" | "aborted" | "" = "";
    if (execution.value.result.deviated) {
      status = "deviated";
    } else if (
      ["aborted", "interrupted", "completed"].includes(
        execution.value.result.status
      )
    ) {
      status = execution.value.result.status as unknown as
        | "completed"
        | "interrupted"
        | "aborted"
        | "";
    }
    let end: ExecutionTimelineEvent = {
      title: "Experiment Ends",
      date: execution.value.result.end,
      type: "experiment",
      execution_status: status,
    };
    timeline.value.push(end);
  } else {
    // Wrap up
    timeline.value.push(...prechecks);
    timeline.value.push(...ssBeforeEvents);
    timeline.value.push(...execEvents);
    timeline.value.push(...ssAfterEvents);
    timeline.value.push(...beforeRollbacksSafeguards);
    timeline.value.push(...rollbacksEvents);

    let running: ExecutionTimelineEvent = {
      title: "Running",
      date: "",
      type: "experiment",
      execution_status: "running",
    };
    timeline.value.push(running);
  }

  // Add Slack messages
  getSlackMessages();
  timeline.value.push(...slackMessages);
  timeline.value.sort((a, b) => {
    return sortEventsByDate(a, b);
  });
};

function resetTimeline() {
  timeline.value = [];
  slackMessages = [];
  slackUsers = null;
  prechecks = [];
  ssBeforeEvents = [];
  isSSHBeforeComplete.value = false;
  ssDuringEvents = [];
  isSSHDuringComplete.value = false;
  runEvents = [];
  execEvents = [];
  isMethodComplete.value = false;
  ssAfterEvents = [];
  isSSHAfterComplete.value = false;
  beforeRollbacksSafeguards = [];
  rollbacksEvents = [];
  isRollbacksComplete.value = false;
}

const events = ref<HTMLElement | null>(null);
function handleEventScroll(id: string) {
  if (events.value) {
    const item = (events.value as HTMLElement).querySelector(
      `[data-id="${id}"]`
    );
    if (item) {
      const content = item.querySelector(".timelineEvent__content")!;
      content!.classList.add("timelineEvent__content--highlight");
      setTimeout(() => {
        content!.classList.remove("timelineEvent__content--highlight");
      }, 5000);
      const details = content.querySelector("details");
      details!.open = true;

      window.scrollTo({
        top:
          item.getBoundingClientRect().top -
          document.body.getBoundingClientRect().top -
          16,
        left: 0,
        behavior: "smooth",
      });
    }
  }
}

function handleResume() {
  emit("resume-execution");
}

watch(execution, async () => {
  checkReliablyUi();
  await resetTimeline();
  await buildTimeline();
});

onMounted(async () => {
  await buildTimeline();
});
</script>

<style lang="scss" scoped>
.executionTimeline {
  position: relative;

  &__events {
    position: relative;

    &::before {
      content: "";

      position: absolute;
      top: 0;
      left: 2.2rem;

      display: block;
      height: 100%;
      width: 0.2rem;

      background-color: var(--grey-200);

      @media (min-width: 44rem) {
        left: calc(50% - 0.1rem);
      }
    }
  }

  &--left {
    .executionTimeline__events {
      &::before {
        left: 2.2rem;
      }
    }
  }

  .executionTimelineToggle {
    position: absolute;
    top: calc(-5rem - var(--space-small));
    right: 0;

    display: none;

    @media (min-width: 44rem) {
      display: block;
    }

    input {
      height: 0;
      width: 0;
      visibility: hidden;
    }

    label {
      position: relative;

      display: block;
      height: 2.5rem;
      width: 5rem;
      padding-top: 0.2rem;

      background-color: var(--grey-400);
      border-radius: 2.5rem;
      cursor: pointer;

      color: var(--text-color-dim);
      font-size: 1.4rem;
      text-indent: -10rem;

      &::after {
        content: "";

        position: absolute;
        top: 0.25rem;
        left: 0.25rem;

        width: 2rem;
        height: 2rem;

        background-color: white;
        border-radius: 50%;
        transition: 0.3s;
      }
    }

    input:checked + label {
      background: var(--pink-500);

      &::after {
        left: calc(100% - 0.25rem);
        transform: translateX(-100%);
      }
    }

    label:active:after {
      width: 3rem;
    }
  }
}
</style>
