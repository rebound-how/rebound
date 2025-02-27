
// Do not remove the (empty) line above it helps with code coverage in c8
import { atom, map } from "nanostores";

import type {
  Deployment,
  NewDeploymentName,
  DeploymentsApiJsonResponse,
  DeploymentsPage,
} from "@/types/deployments";
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

// Deployments List
export const deployments = map<DeploymentsPage>({
  page: 0,
  deployments: [],
  total: 0,
  isReady: false,
});

export async function updateDeployments(data: DeploymentsPage) {
  deployments.set(data);
  return deployments.get();
};

export const fetchDeployments = async (page: number, term?: string) => {
  increaseLoaderCounter();
  
  let url = `${baseApiUrl}/organization/${context.value}/deployments?page=${page}${apiUrlPrefix}`;
  if (term) {
    url = `${baseApiUrl}/organization/${context.value}/deployments/search?pattern=${term}&page=${page}${apiUrlPrefix}`;
  }

  try {
    const response = await fetch(url);
    if (response.status === 403) {
      handleError403(context.value);
    } else {
      const e: DeploymentsApiJsonResponse = await response.json();
      let data: DeploymentsPage = {
        page: page,
        deployments: e.items,
        total: e.count,
        isReady: true,
      };
      updateDeployments(data);
    }
  } catch (e) {
    const n: Notification = {
      title: "Deployments couldn't be fetched",
      message: (e as Error).message,
      type: "error",
    };
    addNotification(n);
  } finally {
    decreaseLoaderCounter();
  }
};

export const createDeployment = async (deployment: Deployment) => {
  increaseLoaderCounter();
  const url = `${baseApiUrl}/organization/${context.value}/deployments`;
  try {
    const response = await fetch(url, {
      method: "POST",
      headers: {
        Accept: "application/json, text/plain, */*",
        "Content-Type": "application/json",
      },
      body: JSON.stringify(deployment),
    });
    if (response.status === 403) {
      handleError403(context.value);
    } else if (response.status === 409) {
      let r = await response.json();
      const n: Notification = {
        title: "Deployment couldn't be created",
        message:
          "A deployment with the same name already exists",
        type: "error",
      };
      addNotification(n);
    } else if (!response.ok) {
      throw new Error(response.statusText);
    } else {
      const newDeployment: Deployment = await response.json();
      window.location.assign(`/deployments/view/?id=${newDeployment.id}`);
    }
  } catch (e) {
    const n: Notification = {
      title: "Deployment couldn't be created",
      message: (e as Error).message,
      type: "error",
    };
    addNotification(n);
  } finally {
    decreaseLoaderCounter();
  }
};

export const editDeployment = async (id: string, deployment: Deployment) => {
  increaseLoaderCounter();
  const url = `${baseApiUrl}/organization/${context.value}/deployments/${id}`;
  try {
    const response = await fetch(url, {
      method: "PUT",
      headers: {
        Accept: "application/json, text/plain, */*",
        "Content-Type": "application/json",
      },
      body: JSON.stringify(deployment),
    });
    if (response.status === 403) {
      handleError403(context.value);
    } else if (response.status === 409) {
      let r = await response.json();
      const n: Notification = {
        title: "Deployment couldn't be edited",
        message:
          "A deployment with the same name already exists",
        type: "error",
      };
      addNotification(n);
    } else if (!response.ok) {
      throw new Error(response.statusText);
    }
  } catch (e) {
    const n: Notification = {
      title: "Deployment couldn't be created",
      message: (e as Error).message,
      type: "error",
    };
    addNotification(n);
  } finally {
    decreaseLoaderCounter();
  }
};

export const cloneDeployment = async (id: string, name: NewDeploymentName) => {
  increaseLoaderCounter();
  const url = `${baseApiUrl}/organization/${context.value}/deployments/${id}/clone`;
  try {
    const response = await fetch(url, {
      method: "POST",
      headers: {
        Accept: "application/json, text/plain, */*",
        "Content-Type": "application/json",
      },
      body: JSON.stringify(name),
    });
    if (response.status === 403) {
      handleError403(context.value);
    } else if (response.status === 409) {
      let r = await response.json();
      const n: Notification = {
        title: "Deployment couldn't be cloned",
        message:
          "A deployment with the same name already exists",
        type: "error",
      };
      addNotification(n);
    } else if (!response.ok) {
      throw new Error(response.statusText);
    } else {
      const newDeployment: Deployment = await response.json();
      window.location.assign(`/deployments/view/?id=${newDeployment.id}`);
    }
  } catch (e) {
    const n: Notification = {
      title: "Deployment couldn't be cloned",
      message: (e as Error).message,
      type: "error",
    };
    addNotification(n);
  } finally {
    decreaseLoaderCounter();
  }
};

// Single Deployment
export const deployment = atom<Deployment | null>(null);

export async function updateDeployment(d: Deployment) {
  deployment.set(d);
  return deployment.get();
};

export const fetchDeployment = async (id: string) => {
  increaseLoaderCounter();
  const url = `${baseApiUrl}/organization/${context.value}/deployments/${id}`;
  try {
    const response = await fetch(url);
    if (response.status === 403) {
      handleError403(context.value);
    } else if (!response.ok) {
      throw new Error(response.statusText);
    } else {
      const newDeploy: Deployment = await response.json();
      updateDeployment(newDeploy);
    }
  } catch (e) {
    const n: Notification = {
      title: "Deployment couldn't be fetched",
      message: (e as Error).message,
      type: "error",
    };
    addNotification(n);
  }
  decreaseLoaderCounter();
};

export const deleteDeployment = async (id: string): Promise<boolean> => {
  increaseLoaderCounter();
  let success: boolean = true;
  const url = `${baseApiUrl}/organization/${context.value}/deployments/${id}`;
  try {
    const response = await fetch(url, { method: "DELETE" });
    if (response.status === 403) {
      handleError403(context.value);
    } else if (response.status === 400) {
      let r = await response.json();
      const n: Notification = {
        title: "Deployment couldn't be deleted",
        message:
          "This deployment is used by a plan. You must delete the plan before proceeding.",
        type: "error",
      };
      addNotification(n);
      success = false;
    } else if (!response.ok) {
      throw new Error(response.statusText);
    }
  } catch (e) {
    const n: Notification = {
      title: "Deployment couldn't be deleted",
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
