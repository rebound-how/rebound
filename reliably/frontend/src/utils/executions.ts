import type { Execution, ExecutionRollback } from "@/types/executions";
import type { ExecutionUiStatus } from "@/types/ui-types";

export function getExecutionStatusObject(
  execution: Execution
): ExecutionUiStatus {
  const state = execution.user_state;
  if (state === null) {
    return { label: "Not run yet", type: "unknown" };
  } else if (state.current === "finished") {
    if (state.status === "completed") {
      if (state.deviated) {
        return { label: "Deviated", type: "ko" };
      } else if (
        execution.result["steady_states"].before &&
        execution.result["steady_states"].before["steady_state_met"] === false
      ) {
        return { label: "Initial system condition not met", type: "ko" };
      } else if (execution.result.rollbacks.length) {
        const didRollbacksSucceed: boolean = (
          execution.result.rollbacks as ExecutionRollback[]
        ).every((r) => {
          return r.status === "succeeded";
        });
        if (didRollbacksSucceed) {
          return { label: "Completed", type: "ok" };
        } else {
          return { label: "Rollbacks failed", type: "ko" };
        }
      } else {
        return { label: "Completed", type: "ok" };
      }
    } else {
      if (state.status) {
        if (state.status === "failed") {
          return { label: "Failed", type: "ko" };
        } else {
          return { label: state.status, type: "warning" };
        }
      } else {
        return { label: "Unknown", type: "unknown" };
      }
    }
  } else if (state.current === "pause") {
    return { label: "pausing...", type: "warning" };
  } else if (state.current === "terminate") {
    return { label: "stopping...", type: "warning" };
  } else {
    return { label: state.current, type: null };
  }
}
