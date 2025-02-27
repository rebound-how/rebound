import type { Plan } from "@/types/plans";

import { Cron } from "croner";
import { humanReadableTime } from "@/utils/strings";

export function getPlanLastRun(plan: Plan): string | null {
  if (
    plan.last_executions_info === undefined ||
    plan.last_executions_info === null
  ) {
    return null;
  } else {
    const i = plan.last_executions_info!;
    if (i.running !== null) {
      return humanReadableTime(i.running.timestamp, "shortest");
    } else if (i.terminated !== null) {
      return humanReadableTime(i.terminated.timestamp, "shortest");
    } else {
      return null;
    }
  }
}

/************************************
 * Params
 * schedule: A plan schedule
 * prev: not used at the moment
 * returnType: "string" (default, for display) or "date" (for further use)
 */
export function getPlanNextRun(
  schedule:
    | {
        type: string;
        pattern?: string;
        via_agent?: boolean;
      }
    | undefined,
  prev: string | null,
  returnType?: string
): string | null {
  if (schedule === undefined || schedule.type === "now") {
    return null;
  } else if (schedule.type === "cron") {
    const pattern = schedule.pattern;
    if (pattern === undefined) {
      return null;
    } else {
      const next = Cron(schedule.pattern!).nextRun();
      if (next === null) {
        return null;
      } else if (returnType !== undefined) {
        if (returnType === "date") {
          return next.toISOString();
        } else if (returnType === "string") {
          return humanReadableTime(next, "shortest");
        }
      } else {
        return humanReadableTime(next, "shortest");
      }
    }
  } else {
    return null;
  }
  return null;
}
