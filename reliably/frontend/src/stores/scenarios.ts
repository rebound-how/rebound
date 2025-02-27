
// Do not remove the (empty) line above it helps with code coverage in c8
import { atom } from "nanostores";
import { uuid } from "vue-uuid";
import  dayjs  from "dayjs";

import type { Scenario, ScenarioQuery, ScenarioError } from "@/types/scenarios";
import type { Notification } from "@/types/ui-types";

import { handleError403 } from "../utils/user";

import { useStore } from "@nanostores/vue";
import { organizationToken } from "../stores/user";
import { increaseLoaderCounter, decreaseLoaderCounter } from "../stores/loader";
import { addNotification } from "../stores/notifications";

/* c8 ignore start */
const baseApiUrl: string = import.meta.env === undefined
  ? "https://62ff903e9350a1e548e1952e.mockapi.io/api"
  : import.meta.env.PUBLIC_API_URL;

const useMockApi = 
  baseApiUrl === "https://62ff903e9350a1e548e1952e.mockapi.io/api";

const endpoint: string = useMockApi
  ? "assistant_scenario"
  : "assistant/scenario"
/* c8 ignore stop */

const context = useStore(organizationToken);

export const scenario = atom<Scenario | null>(null);

export async function updateScenario(data: Scenario | null) {
  scenario.set(data);
  return scenario.get();
};

export const createScenario = async (query: ScenarioQuery) => {
  const url = `${baseApiUrl}/organization/${context.value}/${endpoint}`;
  try {
    const response = await fetch(url,
      { method: "POST",
      headers: {
        Accept: "application/json, text/plain, */*",
        "Content-Type": "application/json",
      },
      body: JSON.stringify(query),
    });
    if (response.status === 403) {
      handleError403(context.value);
    } else if (!response.ok) {
      throw new Error(response.statusText);
    } else {
      const newScenario: Scenario = await response.json();
      updateScenario(newScenario);
    }
  } catch (e) {
    pushError(
      {
        title: "Something went wrong when creating your experiment",
        message: (e as Error).message,
      }
    );
  }
}

export const fetchScenario = async (id: string, dialog: boolean) => {
  if (!dialog) {
    increaseLoaderCounter();
  }
  const url = `${baseApiUrl}/organization/${context.value}/${endpoint}/${id}`;
  try {
    const response = await fetch(url);
    if (response.status === 403) {
      handleError403(context.value);
    } else if (!response.ok) {
      throw new Error(response.statusText);
    } else {
      const s: Scenario = await response.json();
      updateScenario(s);
    }
  } catch (e) {
    if (dialog) {
      pushError(
        {
          title: "Something went wrong when retrieving a scenario",
          message: (e as Error).message,
        }
      );
    } else {
      const n: Notification = {
        title: "Something went wrong when retrieving a scenario",
        message: (e as Error).message,
        type: "error",
      }
      addNotification(n);
    }
  } finally {
    decreaseLoaderCounter();
  }
};

export const fetchScenarioByExperiment = async (id: string, dialog: boolean, silent: boolean) => {
  if (!dialog) {
    increaseLoaderCounter();
  }
  const url = `${baseApiUrl}/organization/${context.value}/${endpoint}/by/experiment/${id}`;
  try {
    const response = await fetch(url);
    if (response.status === 403) {
      handleError403(context.value);
    } else if (!response.ok) {
      throw new Error(response.statusText);
    } else {
      const s: Scenario = await response.json();
      updateScenario(s);
    }
  } catch (e) {
    if (dialog) {
      pushError(
        {
          title: "Something went wrong when retrieving a scenario",
          message: (e as Error).message,
        }
      );
    } else {
      if (!silent) {
        const n: Notification = {
          title: "Something went wrong when retrieving a scenario",
          message: (e as Error).message,
          type: "error",
        }
        addNotification(n);
      }
    }
  } finally {
    decreaseLoaderCounter();
  }
};

export const setScenarioExperiment = async (id: string, experimentId: string) => {
  const url = `${baseApiUrl}/organization/${context.value}/${endpoint}/${id}/experiment/${experimentId}`;
  try {
    const response = await fetch(url, {
      method: "PUT"
    });
    if (response.status === 403) {
      handleError403(context.value);
    } else if (!response.ok) {
      throw new Error(response.statusText);
    } else {
      const s: Scenario = await response.json();
      updateScenario(s);
    }
  } catch(e) {
    // Handle error
  }
}

export const resetStoredScenario = () => {
  updateScenario(null);
}

// Errors
export const errors = atom<ScenarioError[]>([]);

export async function pushError(e: ScenarioError) {
    const error: ScenarioError = {
      title: e.title,
      message: e.message,
      created_at: dayjs().format(),
      id: uuid.v4(),
    };
    errors.set([...errors.get(), error]);
    return errors.get();
  };

export function  shiftError() {
  let arr: ScenarioError[] = errors.get();
  if (arr.length > 1) {
    arr.splice(0, 1);
    errors.set([...arr]);
    return errors.get();
  }
};
