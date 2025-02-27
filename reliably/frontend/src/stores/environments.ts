
// Do not remove the (empty) line above it helps with code coverage in c8
import { atom, map } from "nanostores";

import type {
  Environment,
  EnvironmentsApiJsonResponse,
  EnvironmentsPage,
  Secret,
  Var,
} from "@/types/environments";
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

const apiUrlPrefix: string = useMockApi ? "&limit=10" : "";
/* c8 ignore stop */

const context = useStore(organizationToken);

// Environment List
export const environments = map<EnvironmentsPage>({
  page: 0,
  environments: [],
  total: 0,
  isReady: false,
});

export async function updateEnvironments(data: EnvironmentsPage) {
  environments.set(data);
  return environments.get();
};

export const fetchEnvironments = async (page: number, term?: string) => {
  increaseLoaderCounter();
  
  let url = `${baseApiUrl}/organization/${context.value}/environments?page=${page}${apiUrlPrefix}`;
    if (term) {
    url = `${baseApiUrl}/organization/${context.value}/environments/search?pattern=${term}&page=${page}${apiUrlPrefix}`;
  }


  try {
    const response = await fetch(url);
    if (response.status === 403) {
      handleError403(context.value);
    } else if (!response.ok) {
      throw new Error(response.statusText);
    } else {
      const e: EnvironmentsApiJsonResponse = await response.json();
      let data: EnvironmentsPage = {
        page: page,
        environments: e.items,
        total: e.count,
        isReady: true,
      };
      updateEnvironments(data);
    }
  } catch (e) {
    const n: Notification = {
      title: "Environments couldn't be fetched",
      message: (e as Error).message,
      type: "error",
    };
    addNotification(n);
  } finally {
    decreaseLoaderCounter();
  }
};

// Single Environment
export const environment = atom<Environment | null>(null);

export async function updateEnvironment(e: Environment) {
  environment.set(e);
  return environment.get();
};

export const fetchEnvironment = async (id: string) => {
  increaseLoaderCounter();
  const url = `${baseApiUrl}/organization/${context.value}/environments/${id}`;
  try {
    const response = await fetch(url);
    if (response.status === 403) {
      handleError403(context.value);
    } else if (!response.ok) {
      throw new Error(response.statusText);
    } else {
      const newEnv: Environment = await response.json();
      updateEnvironment(newEnv);
    }
  } catch (e) {
    const n: Notification = {
      title: "Environment couldn't be fetched",
      message: (e as Error).message,
      type: "error",
    };
    addNotification(n);
  }
  decreaseLoaderCounter();
};

export const deleteEnvironment = async (id: string): Promise<boolean> => {
  increaseLoaderCounter();
  let success: boolean = true;
  const url = `${baseApiUrl}/organization/${context.value}/environments/${id}`;
  try {
    const response = await fetch(url, { method: "DELETE" });
    if (response.status === 403) {
      handleError403(context.value);
    } else if (response.status === 400) {
      let r = await response.json();
      const n: Notification = {
        title: "Environment couldn't be deleted",
        message:
          "This environment is used by a plan. You must delete the plan before proceeding.",
        type: "warning",
      };
      addNotification(n);
      success = false;
    } else if (!response.ok) {
      throw new Error(response.statusText);
    }
  } catch (e) {
    const n: Notification = {
      title: "Environment couldn't be deleted",
      message: (e as Error).message,
      type: "error",
    };
    addNotification(n);
    success = false;
  } finally {
    decreaseLoaderCounter();
    return success;
  }
};

export const createEnvironment = async (environment: Environment) => {
  if (environment.envvars.length + environment.secrets.length === 0) {
    const n: Notification = {
      title: "Environment couldn't be created",
      message: "You must provide at least one environment variable or secret",
      type: "error",
    };
    addNotification(n);
  } else {
    increaseLoaderCounter();
    const url = `${baseApiUrl}/organization/${context.value}/environments`;
    try {
      const response = await fetch(url, {
        method: "POST",
        headers: {
          Accept: "application/json, text/plain, */*",
          "Content-Type": "application/json",
        },
        body: JSON.stringify(environment),
      });
      if (response.status === 403) {
        handleError403(context.value);
      } else if (response.status === 422) {
        let msg: string = "";
        const details: any[] = await response.json();
        details.forEach(d => {
          if (d.type === "value_error") {
            msg += `${d.msg}. `;
          }
        });
        if (msg !== "") {
          throw new Error(`${response.statusText}: ${msg}`);  
        } else {
          throw new Error(response.statusText);
        }
      } else if (!response.ok) {
        throw new Error(response.statusText);
      } else {
        const newEnvironment: Environment = await response.json();
        window.location.assign(`/environments/view/?id=${newEnvironment.id}`);
      }
    } catch (e) {
      const n: Notification = {
        title: "Environment couldn't be created",
        message: (e as Error).message,
        type: "error",
      };
      addNotification(n);
    } finally {
      decreaseLoaderCounter();
    }
  }
};

export const cloneEnvironment = async (envId: string, newName: string) => {
  increaseLoaderCounter();
  const url = `${baseApiUrl}/organization/${context.value}/environments/${envId}/clone`;
  try {
    const response = await fetch(url, {
        method: "POST",
        headers: {
          Accept: "application/json, text/plain, */*",
          "Content-Type": "application/json",
        },
        body: JSON.stringify({name: newName}),
      });
    if (response.status === 403) {
        handleError403(context.value);
      } else if (!response.ok) {
        throw new Error(response.statusText);
      } else {
        const newEnvironment: Environment = await response.json();
        window.location.assign(`/environments/view/?id=${newEnvironment.id}`);
      }
  } catch (e) {
      const n: Notification = {
        title: "Environment couldn't be cloned",
        message: (e as Error).message,
        type: "error",
      };
      addNotification(n);
    } finally {
      decreaseLoaderCounter();
    }
}

export const deleteEnvironmentSecretVar = async (key: string, type: "secret" | "variable", envId: string): Promise<boolean> => {
  increaseLoaderCounter();
  let success: boolean = true;
  const url = `${baseApiUrl}/organization/${context.value}/environments/${envId}/remove/${key}`;
  try {
    const response = await fetch(url, { method: "DELETE" });
    const n: Notification = {
      title: `Environment ${type} deleted`,
      message: `Environment ${type} ${key} was successfully deleted`,
      type: "success",
    };
    addNotification(n);
    if (response.status === 403) {
      handleError403(context.value);
    } else if (!response.ok) {
      throw new Error(response.statusText);
    }
  } catch (e) {
    const n: Notification = {
      title: `Environment ${type} couldn't be deleted`,
      message: (e as Error).message,
      type: "error",
    };
    addNotification(n);
    success = false;
  } finally {
    decreaseLoaderCounter();
    return success;
  }
};

export const updateEnvironmentSecretVar = async (payload: Secret | Var, type: "secret" | "variable", envId: string): Promise<boolean> => {
  increaseLoaderCounter();
  let success: boolean = true;
  const url = `${baseApiUrl}/organization/${context.value}/environments/${envId}/set`;
  try {
    const response = await fetch(url, { 
      method: "PUT",
        headers: {
          Accept: "application/json, text/plain, */*",
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
     });
    const n: Notification = {
      title: `Environment ${type} updated`,
      message: `Environment ${type} was successfully updated`,
      type: "success",
    };
    addNotification(n);
    if (response.status === 403) {
      handleError403(context.value);
    } else if (!response.ok) {
      throw new Error(response.statusText);
    }
  } catch (e) {
    const n: Notification = {
      title: `Environment ${type} couldn't be updated`,
      message: (e as Error).message,
      type: "error",
    };
    addNotification(n);
    success = false;
  } finally {
    decreaseLoaderCounter();
    return success;
  }
};
