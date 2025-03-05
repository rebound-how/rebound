
// Do not remove the (empty) line above it helps with code coverage in c8
import { atom, map } from "nanostores";

import type {
  Experiment,
  ExperimentScore,
  ExperimentsPage,
  SimpleExperimentsApiJsonResponse,
  ExperimentShortForm,
  AllExperimentsApiResponse,
  ExperimentImportPayload
} from "@/types/experiments";
import type { Notification } from "@/types/ui-types";

import { handleError403 } from "../utils/user";
import { getReliablyUiExtension } from "../utils/experiments";

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

const apiUrlPrefix: string = useMockApi
  ? "&limit=10"
  : "";

const simpleExperimentsEndpoint: string = useMockApi
  ? "experiments_summary"
  : "experiments/summary"

const allExperimentsEndpoint: string = useMockApi
  ? "experiments_all"
  : "experiments/all";

const experimentScoreEndpoint: string = useMockApi
  ? "series-score-experiment"
  : "series/scores/experiment";
/* c8 ignore stop */

const context = useStore(organizationToken);

// Experiments List
export const experiments = map<ExperimentsPage>({
  page: 0,
  experiments: [],
  total: 0,
  isReady: false,
});

export async function updateExperiments(data: ExperimentsPage) {
  experiments.set(data);
  return experiments.get();
};

export const fetchExperiments = async (page: number, term?: string) => {
  increaseLoaderCounter();
  let url = `${baseApiUrl}/organization/${context.value}/${simpleExperimentsEndpoint}?page=${page}${apiUrlPrefix}`;

  if (term) {
    url = `${baseApiUrl}/organization/${context.value}/${simpleExperimentsEndpoint}?pattern=${term}&page=${page}${apiUrlPrefix}`;
  }

  try {
    const response = await fetch(url);
    if (response.status === 403) {
      handleError403(context.value);
    } else if (!response.ok) {
      throw new Error(response.statusText);
    } else {
      const e: SimpleExperimentsApiJsonResponse = await response.json();
      let data: ExperimentsPage = {
        page: page,
        experiments: e.items,
        total: e.count,
        isReady: true,
      };
      updateExperiments(data);
    }
  } catch (e) {
    const n: Notification = {
      title: "Experiments couldn't be fetched",
      message: (e as Error).message,
      type: "error",
    }
    addNotification(n);
  } finally {
    decreaseLoaderCounter();
  }
};

// Single Experiment
export const experiment = atom<Experiment | null>(null);

export async function updateExperiment(e: Experiment) {
  experiment.set(e);
  return experiment.get();
};

export const fetchExperiment = async (id: string) => {
  increaseLoaderCounter();
  const url = `${baseApiUrl}/organization/${context.value}/experiments/${id}`;
  try {
    const response = await fetch(url);
    if (response.status === 403) {
      handleError403(context.value);
    } else if (!response.ok) {
      throw new Error(response.statusText);
    } else {
      const e: Experiment = await response.json();
      const scoreUrl = `${baseApiUrl}/organization/${context.value}/${experimentScoreEndpoint}/${id}`
      try {
        const scoreResponse = await fetch(scoreUrl);
        if (!scoreResponse.ok) {
          throw new Error(scoreResponse.statusText);
        } else {
          const score: ExperimentScore = await scoreResponse.json();
          e.score = score;
        }
      } catch(e) {
        const n: Notification = {
          title: "Experiment score couldn't be fetched",
          message: (e as Error).message,
          type: "error",
        }
        addNotification(n);
      }
      updateExperiment(e);
    }
  } catch (e) {
    const n: Notification = {
      title: "Experiment couldn't be fetched",
      message: (e as Error).message,
      type: "error",
    }
    addNotification(n);
  } finally {
    decreaseLoaderCounter();
  }
};

export const deleteExperiment = async (id: string) => {
  increaseLoaderCounter();
  let success: boolean = true;
  const url = `${baseApiUrl}/organization/${context.value}/experiments/${id}`;
  try {
    const response = await fetch(url, { method: "DELETE" });
    if (response.status === 403) {
      handleError403(context.value);
    } else if (response.status === 400) {
      let r = await response.json();
      const n: Notification = {
        title: "Experiment couldn't be deleted",
        message: "This experiment is used by a plan. You must delete the plan before proceeding.",
        type: "warning",
      };
      addNotification(n);
      success = false;
    } else if (!response.ok) {
      throw new Error(response.statusText);
    }
  } catch (e) {
    const n: Notification = {
      title: "Experiment couldn't be deleted",
      message: (e as Error).message,
      type: "error",
    }
    addNotification(n);
    success = false;
  } finally {
    decreaseLoaderCounter();
    return success;
  }
};

export const importExperiment = async (experiment: ExperimentImportPayload, run?: boolean, assistant?: boolean): Promise<string | undefined> => {
  increaseLoaderCounter();
  const url = `${baseApiUrl}/organization/${context.value}/experiments/import`;
  try {
    const response = await fetch(url,
      { method: "POST",
      headers: {
        Accept: "application/json, text/plain, */*",
        "Content-Type": "application/json",
      },
      body: JSON.stringify(experiment),
    });
    if (response.status === 403) {
      handleError403(context.value);
    } else if (response.status === 429) {
      throw new Error ("You've reached the limit of custom experiments allowed by your plan.")
    } else if (!response.ok) {
      throw new Error(response.statusText);
    } else {
      const newExperiment: Experiment = await response.json();
      if (run === true) {
        window.location.assign(`/plans/new/?exp=${newExperiment.id}`);
      } else if (assistant === true) {
        return newExperiment.id;
      }
      else {
        window.location.assign(`/experiments/view/?id=${newExperiment.id}`);
      }
    }
  } catch (e) {
    const n: Notification = {
      title: "Experiment couldn't be imported",
      message: (e as Error).message,
      type: "error",
    }
    addNotification(n);
  } finally {
    decreaseLoaderCounter();
  }
}

export const overwriteExperiment = async (id: string, experiment: ExperimentImportPayload, preventReload?: boolean) => {
  increaseLoaderCounter();
  const url = `${baseApiUrl}/organization/${context.value}/experiments/${id}`;
  try {
    const response = await fetch(url,
      { method: "PUT",
      headers: {
        Accept: "application/json, text/plain, */*",
        "Content-Type": "application/json",
      },
      body: JSON.stringify(experiment),
    });
    if (response.status === 403) {
      handleError403(context.value);
    } else if (response.status === 404) {
      throw new Error ("This experiment doesn't exist anymore")
    } else if (!response.ok) {
      throw new Error(response.statusText);
    } else {
      const newExperiment: Experiment = await response.json();
      if (!preventReload) {
        window.location.assign(`/experiments/view/?id=${newExperiment.id}`);
      }
    }
  } catch (e) {
    const n: Notification = {
      title: "Experiment couldn't be edited",
      message: (e as Error).message,
      type: "error",
    }
    addNotification(n);
  } finally {
    decreaseLoaderCounter();
  }
}

// All Experiments (in short form)
// Experiments List
export const allExperiments = atom<ExperimentShortForm[]>([]);

export async function updateAllExperiments(data: AllExperimentsApiResponse) {
  allExperiments.set(data.items);
  return allExperiments.get();
};

export const fetchAllExperiments = async () => {
  increaseLoaderCounter();
  const url = `${baseApiUrl}/organization/${context.value}/${allExperimentsEndpoint}`;
  try {
    const response = await fetch(url);
    if (response.status === 403) {
      handleError403(context.value);
    } else if (!response.ok) {
      throw new Error(response.statusText);
    } else {
      const e: AllExperimentsApiResponse = await response.json();
      updateAllExperiments(e);
    }
  } catch (e) {
    const n: Notification = {
      title: "Experiments couldn't be fetched",
      message: (e as Error).message,
      type: "error",
    }
    addNotification(n);
  } finally {
    decreaseLoaderCounter();
  }
};

// Activity

/*
 * Retrieve an activity actual title to display it in the builder
*/
export function getActivityActualTitle(block: string, index: number): string | null {
  const exp = experiment.get();
  if (exp) {
    let actualTitle: string = "";
    if (block === "warmup") {
      actualTitle = exp.definition.method![index].name;
    } else if (block === "turbulence" || block === "method") {
      let numberOfWarmupActivities: number = 0;
      const reliablyui = getReliablyUiExtension(exp.definition);
      if (reliablyui) {
        numberOfWarmupActivities = reliablyui.workflow.warmup.length;
      }
      actualTitle =
        exp.definition.method![index + numberOfWarmupActivities].name;
    } else if (block === "verification" || block === "hypothesis") {
      actualTitle =
        exp.definition["steady-state-hypothesis"]!.probes![index].name;
    } else if (block === "rollbacks") {
      actualTitle = exp.definition.rollbacks![index].name;
    }

    if (actualTitle !== "") {
      return actualTitle;
    }
  }
  return null;
}