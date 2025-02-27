
// Do not remove the (empty) line above it helps with code coverage in c8
import { atom, map } from "nanostores";
import type {
  Execution,
  ExecutionResult,
  ExecutionsApiJsonResponse,
  ExecutionsPage,
} from "@/types/executions";
import type { ExperimentStatus } from "@/types/experiments";
import type { Notification } from "@/types/ui-types";

import { handleError403 } from "../utils/user";

import { useStore } from "@nanostores/vue";
import { organizationToken } from "../stores/user";
import { increaseLoaderCounter, decreaseLoaderCounter } from "../stores/loader";
import { addNotification } from "../stores/notifications";
import { update } from "lodash-es";

const context = useStore(organizationToken);

/* c8 ignore start */
const baseApiUrl: string = import.meta.env === undefined
  ? "https://62ff903e9350a1e548e1952e.mockapi.io/api"
  : import.meta.env.PUBLIC_API_URL;
const useMockApi = 
  baseApiUrl === "https://62ff903e9350a1e548e1952e.mockapi.io/api";

const apiUrlPrefix: string = useMockApi
  ? "&limit=10"
  : "";
/* c8 ignore stop */

// Executions Lists
export const executions = map<ExecutionsPage>({
  page: 0,
  executions: [],
  total: 0,
  isReady: false,
});

export async function updateExecutions(data: ExecutionsPage) {
  executions.set(data);
  return executions.get();
};

export const fetchExecutions = async (page: number, experimentId?: string) => {
  increaseLoaderCounter();
  let url = `${baseApiUrl}/organization/${context.value}/executions?page=${page}${apiUrlPrefix}`;
  if (experimentId) {
    url = `${baseApiUrl}/organization/${context.value}/experiments/${experimentId}/executions?page=${page}${apiUrlPrefix}`;
  }
  try {
    const response = await fetch(url);
    if (response.status === 403) {
      handleError403(context.value);
    } else if (!response.ok) {
      throw new Error(response.statusText)
    } else {
      const e: ExecutionsApiJsonResponse = await response.json();
      let data: ExecutionsPage = {
        page: page,
        executions: e.items,
        total: e.count,
        isReady: true,
      };
      updateExecutions(data);
    }
  } catch(e) {
    const n: Notification = {
      title: "Executions couldn't be fetched",
      message: (e as Error).message,
      type: "error",
    };
    addNotification(n);
  } finally {
    decreaseLoaderCounter();
  }
};

// Single Execution
export const execution = atom<Execution | null>(null);

export async function updateExecution(e: Execution) {
  execution.set(e);
  return execution.get();
};

export const fetchExecution = async (id: string, exp: string) => {
  increaseLoaderCounter();
  const url = `${baseApiUrl}/organization/${context.value}/experiments/${exp}/executions/${id}`;
  try {
    const response = await fetch(url);
    if (response.status === 403) {
      handleError403(context.value);
    } else if (!response.ok) {
      throw new Error(response.statusText)
    } else {
      const e: Execution = await response.json();
      updateExecution(e);
    }
  } catch(e) {
    const n: Notification = {
      title: "Execution couldn't be fetched",
      message: (e as Error).message,
      type: "error",
    };
    addNotification(n);
  } finally {
    decreaseLoaderCounter();
  }
};

export const deleteExecution = async (id: string, exp: string) => {
  increaseLoaderCounter();
  const url = `${baseApiUrl}/organization/${context.value}/experiments/${exp}/executions/${id}`;
  try {
    const response = await fetch(url, { method: "DELETE" });
    if (response.status === 403) {
      handleError403(context.value);
    } else if (!response.ok) {
      throw new Error(response.statusText);
    }
  } catch (e) {
    const n: Notification = {
      title: "Execution couldn't be deleted",
      message: (e as Error).message,
      type: "error",
    }
    addNotification(n);
  } finally {
    decreaseLoaderCounter();
  }
};

export const stopExecution = async (id: string, exp: string, skip_rollbacks: boolean) => {
  increaseLoaderCounter();
  const url = `${baseApiUrl}/organization/${context.value}/experiments/${exp}/executions/${id}/state`;
  try {
    const response = await fetch(
      url,
      { 
        method: "PUT",
        headers: {
          Accept: "application/json, text/plain, */*",
          "Content-Type": "application/json",
        },
        body: JSON.stringify(
          {
            current: "terminate",
            skip_rollbacks: skip_rollbacks
          }
        )
      }
    );
    if (response.status === 403) {
      handleError403(context.value);
    } else if (!response.ok) {
      throw new Error(response.statusText);
    } else {
      let exec = execution.get();
      exec!.user_state.current = "terminated";
      updateExecution(exec!);
      const n: Notification = {
        title: "Execution successfully stopped",
        message: `Termination can take a few seconds to proceed.${ skip_rollbacks ? " Rollbacks will not be played." : ""}`,
        type: "success",
      }
      addNotification(n);
    }
  } catch (e) {
    const n: Notification = {
      title: "Execution couldn't be stopped",
      message: (e as Error).message,
      type: "error",
    };
    addNotification(n);
  } finally {
    decreaseLoaderCounter();
  }
};

export const pauseExecution = async (id: string, exp: string) => {
  increaseLoaderCounter();
  const url = `${baseApiUrl}/organization/${context.value}/experiments/${exp}/executions/${id}/state`;
  try {
    const response = await fetch(
      url,
      { 
        method: "PUT",
        headers: {
          Accept: "application/json, text/plain, */*",
          "Content-Type": "application/json",
        },
        body: JSON.stringify(
          {
            current: "pause",
            duration: 300
          }
        )
      }
    );
    if (response.status === 403) {
      handleError403(context.value);
    } else if (!response.ok) {
      throw new Error(response.statusText);
    } else {
      let exec = execution.get();
      exec!.user_state.current = "pause";
      updateExecution(exec!);
      const n: Notification = {
        title: "Execution successfully paused",
        message: "It will be paused after the current activity is over.",
        type: "success",
      }
      addNotification(n);
    }
  } catch (e) {
    const n: Notification = {
      title: "Execution couldn't be paused",
      message: (e as Error).message,
      type: "error",
    }
    addNotification(n);
  } finally {
    decreaseLoaderCounter();
  }
};

export const resumeExecution = async (id: string, exp: string) => {
  increaseLoaderCounter();
  const url = `${baseApiUrl}/organization/${context.value}/experiments/${exp}/executions/${id}/state`;
  try {
    const response = await fetch(
      url,
      { 
        method: "PUT",
        headers: {
          Accept: "application/json, text/plain, */*",
          "Content-Type": "application/json",
        },
        body: JSON.stringify(
          {
            current: "resume",
          }
        )
      }
    );
    if (response.status === 403) {
      handleError403(context.value);
    } else if (!response.ok) {
      throw new Error(response.statusText);
    } else {
      let exec = execution.get();
      exec!.user_state.current = "running";
      updateExecution(exec!);
      const n: Notification = {
        title: "Execution successfully resumed",
        message: "The next queued activity will start in a few seconds.",
        type: "success",
      }
      addNotification(n);
    }
  } catch (e) {
    const n: Notification = {
      title: "Execution couldn't be resumed",
      message: (e as Error).message,
      type: "error",
    }
    addNotification(n);
  } finally {
    decreaseLoaderCounter();
  }
};

// Experiment Status (from Executions)
export const experimentStatus = atom<ExperimentStatus>({
  experimentId: null,
  lastExecution: null,
  lastStatuses: [],
});

export async function updateExperimentStatus(s: ExperimentStatus) {
  experimentStatus.set(s);
  return experimentStatus.get();
};

export const fetchExperimentStatus = async (id: string) => {
  increaseLoaderCounter();
  try {
    const url = `${baseApiUrl}/organization/${context.value}/experiments/${id}/executions?limit=5`;
    const response = await fetch(url);
    if (response.status === 403) {
      handleError403(context.value);
    } else if (!response.ok) {
      throw new Error(response.statusText);
    } else {
      const lastExecs: ExecutionsApiJsonResponse = await response.json();
      var statuses: ("deviated" | "completed" | "interrupted" | "aborted" | "")[] = [];
      var limit = Math.min(5, lastExecs.items.length);
      if (limit > 0) {
        for (var i: number = 0; i < limit; i++) {
          let r: ExecutionResult = lastExecs.items[i].result;
          let d: boolean = r.deviated;
          let s: string = r.status;
          if (d) {
            statuses.push("deviated");
          } else if (["completed","interrupted","aborted"].includes(s)) {
            statuses.push(s as ("completed" | "interrupted" | "aborted"));
          } else {
            statuses.push("");
          }
        }
        let status: ExperimentStatus = {
          experimentId: id,
          lastExecution: lastExecs.items[0].created_date,
          lastStatuses: statuses,
        };
        updateExperimentStatus(status);
      } else {
        let status: ExperimentStatus = {
          experimentId: id,
          lastExecution: null,
          lastStatuses: [],
        };
        updateExperimentStatus(status);
      }
      
    }
  } catch (e) {
    const n: Notification = {
      title: "Experiment Status couldn't be retrieved",
      message: (e as Error).message,
      type: "error",
    }
    addNotification(n);
  } finally {
    decreaseLoaderCounter();
  }
};

// // Execution Journal
// export const journal = atom<string | null>(null);

// export const updateJournal = action(
//   journal,
//   "updateJournal",
//   async (store, j: string) => {
//     store.set(j);
//     return store.get();
//   }
// );

// export const fetchExecution = async (id: string, exp: string) => {
//   increaseLoaderCounter();
//   const url = `${baseApiUrl}/organization/${context.value}/experiments/${exp}/executions/${id}`;
//   const response = await fetch(url);
//   const e: Execution = await response.json();
//   updateExecution(e);
//   decreaseLoaderCounter();
// };