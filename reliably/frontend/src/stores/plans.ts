
// Do not remove the (empty) line above it helps with code coverage in c8
import { atom, map } from "nanostores";

import type {
  Plan,
  PlanCreate,
  PlansApiJsonResponse,
  PlansPage,
} from "@/types/plans";
import type {
  Execution,
  ExecutionResult,
  ExecutionsApiJsonResponse,
  ExecutionsPage,
} from "@/types/executions";
import type { Notification } from "@/types/ui-types";

import { handleError403 } from "../utils/user";

import { useStore } from "@nanostores/vue";
import { organizationToken } from "../stores/user";
import { increaseLoaderCounter, decreaseLoaderCounter } from "../stores/loader";
import { addNotification } from "../stores/notifications";
import { environment, fetchEnvironment } from "../stores/environments";
import { deployment, fetchDeployment } from "../stores/deployments";

/* c8 ignore start */
const baseApiUrl: string = import.meta.env === undefined
  ? "https://62ff903e9350a1e548e1952e.mockapi.io/api"
  : import.meta.env.PUBLIC_API_URL;
const useMockApi = 
  baseApiUrl === "https://62ff903e9350a1e548e1952e.mockapi.io/api";

const apiUrlPrefix: string = useMockApi ? "&limit=10" : "";
/* c8 ignore stop */

const context = useStore(organizationToken);

// Plans List
export const plans = map<PlansPage>({
  page: 0,
  plans: [],
  total: 0,
  isReady: false,
});

export async function updatePlans(data: PlansPage) {
  plans.set(data);
  return plans.get();
};

export const fetchPlans = async (page: number, term?: string) => {
  increaseLoaderCounter();
  let url = `${baseApiUrl}/organization/${context.value}/plans?page=${page}${apiUrlPrefix}`;

  if (term) {
    url = `${baseApiUrl}/organization/${context.value}/plans/search?pattern=${term}&page=${page}${apiUrlPrefix}`;
  }
  
  try {
    const response = await fetch(url);
    if (response.status === 403) {
      handleError403(context.value);
    } else if (!response.ok) {
      throw new Error(response.statusText);
    } else {
      const p: PlansApiJsonResponse = await response.json();
      let data: PlansPage = {
        page: page,
        plans: p.items,
        total: p.count,
        isReady: true,
      };
      updatePlans(data);
    }
  } catch(e) {
    const n: Notification = {
      title: "Plans couldn't be fetched",
      message: (e as Error).message,
      type: "error",
    };
    addNotification(n);
  } finally {
    decreaseLoaderCounter();
  }
};

export const plansEnvironments = map<{
  [key: string]: {
    provider: string;
    name: string;
  }
}>({});

export async function updatePlansEnvironments(data: {
  [key: string]: {
    provider: string;
    name: string;
  }
}) {
  plansEnvironments.set(data);
  return plansEnvironments.get();
};

export async function getEnvironmentName(id: string, provider: string) {
  let knownEnvs = plansEnvironments.get();
  if (knownEnvs[id] === undefined) {
    await fetchEnvironment(id);
    const newEnv = useStore(environment);
    if (newEnv.value) {
      plansEnvironments.setKey(
        id,
        {
          provider: provider,
          name: newEnv.value!.name
        }
      );
      return {
        provider: provider,
        name: newEnv.value!.name
      }
    }
  } else {
    return knownEnvs[id];
  }
}

export const plansDeployments = map<{
  [key: string]: string;
}>({});

export async function getDeploymentName(id: string) {
  let knownDeps = plansDeployments.get();
  if (knownDeps[id] === undefined) {
    await fetchDeployment(id);
    const newDep = useStore(deployment);
    if (newDep.value) {
      plansDeployments.setKey(id, newDep.value!.name);
      return newDep.value!.name
    }
  } else {
    return knownDeps[id];
  }
}

// When getting the list of plans using an experiment 
export const relatedPlansList = atom<Plan[]>([]);

export async function updateRelatedPlansList(data: Plan[]) {
  relatedPlansList.set(data);
  return relatedPlansList.get();
};

// Fetch a list of plan IDs used by an object (an experiment or a deployment)
// and get the plans identified by these IDs
// @param id: the ID of the object, a string
// @param type: a string representing the type of the object ("deployments"
// and "experiments" being correct values)
export const fetchRelatedPlans = async (id: string, type: string, term?: string) => {
  increaseLoaderCounter();
  let plansArr: Plan[] = [];

  let url = `${baseApiUrl}/organization/${context.value}/${type}/${id}/plans`;
  if (term) {
    url = `${baseApiUrl}/organization/${context.value}/${type}/${id}/plans?pattern=${term}`;
  }

  try {
    const response = await fetch(url);
    if (response.status === 403) {
      handleError403(context.value);
    } else if (!response.ok) {
      throw new Error(response.statusText);
    } else {
      const data: string[] = await response.json();
      for (const id of data) {
        await fetchPlan(id);
        const p = useStore(plan);
        if (p.value !== null) {
          plansArr.push(p.value as any);
        }
      };
      updateRelatedPlansList(plansArr);
    }
  } catch (e) {
    const n: Notification = {
      title: "Plans couldn't be fetched",
      message: (e as Error).message,
      type: "error",
    };
    addNotification(n);
  } finally {
    decreaseLoaderCounter();
  }
}

// Plans List
export const planExecutions = map<ExecutionsPage>({
  page: 0,
  executions: [],
  total: 0,
  isReady: false,
});

export async function updatePlanExecutions(data: ExecutionsPage) {
  planExecutions.set(data);
  return planExecutions.get();
};

export const fetchPlanExecutions = async (id: string, page: number) => {
  increaseLoaderCounter();
  // TODO try / catch
  const url = `${baseApiUrl}/organization/${context.value}/plans/${id}/executions?page=${page}${apiUrlPrefix}`;
  try {
    const response = await fetch(url);
    if (response.status === 403) {
      handleError403(context.value);
    } else if (!response.ok) {
      throw new Error(response.statusText);
    } else {
      const p: ExecutionsApiJsonResponse = await response.json();
      let data: ExecutionsPage = {
        page: page,
        executions: p.items,
        total: p.count,
        isReady: true,
      };
      updatePlanExecutions(data);
    }
  } catch(e) {
    const n: Notification = {
      title: "Plan executions couldn't be fetched",
      message: (e as Error).message,
      type: "error",
    };
    addNotification(n);
  } finally {
    decreaseLoaderCounter();
  }
};

export const createPlan = async (plan: PlanCreate, preventRedirect?: boolean) => {
  increaseLoaderCounter();
  const url = `${baseApiUrl}/organization/${context.value}/plans`;
  try {
    const response = await fetch(url, {
      method: "POST",
      headers: {
        Accept: "application/json, text/plain, */*",
        "Content-Type": "application/json",
      },
      body: JSON.stringify(plan),
    });
    if (response.status === 403) {
      handleError403(context.value);
    } else if (!response.ok) {
      throw new Error(response.statusText);
    } else {
      const newPlan: Plan = await response.json();
      if (preventRedirect && preventRedirect === true) {
        return newPlan.id;
      } else {
        window.location.assign(`/plans/view/?id=${newPlan.id}`);
      }
    }
  } catch (e) {
    const n: Notification = {
      title: "Plan couldn't be created",
      message: (e as Error).message,
      type: "error",
    };
    addNotification(n);
  } finally {
    decreaseLoaderCounter();
  }
};

export const deletePlan = async (id: string) => {
  increaseLoaderCounter();
  const url = `${baseApiUrl}/organization/${context.value}/plans/${id}`;
  try {
    const response = await fetch(url, { method: "DELETE" });
    if (response.status === 403) {
      handleError403(context.value);
    } else if (!response.ok) {
      throw new Error(response.statusText);
    }
  } catch (e) {
    const n: Notification = {
      title: "Plan couldn't be deleted",
      message: (e as Error).message,
      type: "error",
    };
    addNotification(n);
  } finally {
    decreaseLoaderCounter();
  }
};

export const pausePlan = async (id: string) => {
  increaseLoaderCounter();
  const url = `${baseApiUrl}/organization/${context.value}/plans/${id}/suspend`;
  try {
    const response = await fetch(url,{ method: "POST" });
    if (response.status === 403) {
      handleError403(context.value);
    } else if (!response.ok) {
      throw new Error(response.statusText);
    }
  } catch (e) {
    const n: Notification = {
      title: "Plan schedule couldn't be paused",
      message: (e as Error).message,
      type: "error",
    };
    addNotification(n);
  } finally {
    decreaseLoaderCounter();
  }
};

export const resumePlan = async (id: string) => {
  increaseLoaderCounter();
  const url = `${baseApiUrl}/organization/${context.value}/plans/${id}/resume`;
  try {
    const response = await fetch(url,{ method: "POST" });
    if (response.status === 403) {
      handleError403(context.value);
    } else if (!response.ok) {
      throw new Error(response.statusText);
    }
  } catch (e) {
    const n: Notification = {
      title: "Plan schedule couldn't be paused",
      message: (e as Error).message,
      type: "error",
    };
    addNotification(n);
  } finally {
    decreaseLoaderCounter();
  }
};

export const rerunPlan = async (id: string) => {
  increaseLoaderCounter();
  const url = `${baseApiUrl}/organization/${context.value}/plans/${id}/run`;
  try {
    const response = await fetch(url,{ method: "POST" });
    if (response.status === 403) {
      handleError403(context.value);
    } else if (!response.ok) {
      throw new Error(response.statusText);
    }
  } catch (e) {
    const n: Notification = {
      title: "Plan couldn't be run",
      message: (e as Error).message,
      type: "error",
    };
    addNotification(n);
  } finally {
    decreaseLoaderCounter();
  }
};

// Single Plan
export const plan = atom<Plan | null>(null);

export async function updatePlan(p: Plan) {
  plan.set(p);
  return plan.get();
};

export const fetchPlan = async (id: string) => {
  increaseLoaderCounter();
  const url = `${baseApiUrl}/organization/${context.value}/plans/${id}`;
  try {
    const response = await fetch(url);
    if (response.status === 403) {
      handleError403(context.value);
    } else if (!response.ok) {
      throw new Error(response.statusText);
    } else {
      const newPlan: Plan = await response.json();
      updatePlan(newPlan);
    }
  } catch(e) {
    const n: Notification = {
      title: "Plan couldn't be fetched",
      message: (e as Error).message,
      type: "error",
    };
    addNotification(n);
  } finally {
    decreaseLoaderCounter();
  }
};
