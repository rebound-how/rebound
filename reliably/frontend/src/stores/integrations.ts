
// Do not remove the (empty) line above it helps with code coverage in c8
import { atom, map } from "nanostores";

import type {
  Integration,
  IntegrationsPage,
  IntegrationsApiJsonResponse,
  IntegrationControl,
} from "@/types/integrations";
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

export const integrations = map<IntegrationsPage>({
  page: 0,
  integrations: [],
  total: 0,
  isReady: false,
});

export async function updateIntegrations(data: IntegrationsPage) {
  integrations.set(data);
  return integrations.get();
};

export const fetchIntegrations = async (page: number) => {
  increaseLoaderCounter();
  const url = `${baseApiUrl}/organization/${context.value}/integrations?page=${page}${apiUrlPrefix}`;
  try {
    const response = await fetch(url);
    if (response.status === 403) {
      handleError403(context.value);
    } else if (!response.ok) {
      throw new Error(response.statusText);
    } else {
      const e: IntegrationsApiJsonResponse = await response.json();
      let data: IntegrationsPage = {
        page: page,
        integrations: e.items,
        total: e.count,
        isReady: true,
      };
      updateIntegrations(data);
    }
  } catch (e) {
    const n: Notification = {
      title: "Integrations couldn't be fetched",
      message: (e as Error).message,
      type: "error",
    };
    addNotification(n);
  } finally {
    decreaseLoaderCounter();
  }
};

export const createIntegration = async (integration: Integration, inPlace?: boolean) => {
  increaseLoaderCounter();
  const url = `${baseApiUrl}/organization/${context.value}/integrations`;
  try {
    const response = await fetch(url, {
      method: "POST",
      headers: {
        Accept: "application/json, text/plain, */*",
        "Content-Type": "application/json",
      },
      body: JSON.stringify(integration),
    });
    if (response.status === 403) {
      handleError403(context.value);
    } else if (!response.ok) {
      throw new Error(response.statusText);
    } else {
      const newIntegration: Integration = await response.json();
      if (inPlace !== undefined && inPlace === true) {
        return newIntegration;
      } else {
        // window.location.assign(`/environments/view/?id=${newEnvironment.id`);
        window.location.assign("/integrations/");
      }
    }
  } catch (e) {
    const n: Notification = {
      title: "Integration couldn't be created",
      message: (e as Error).message,
      type: "error",
    };
    addNotification(n);
  } finally {
    decreaseLoaderCounter();
  }
};

export const deleteIntegration = async (id: string): Promise<boolean> => {
  increaseLoaderCounter();
  let success: boolean = true;
  const url = `${baseApiUrl}/organization/${context.value}/integrations/${id}`;
  try {
    const response = await fetch(url, { method: "DELETE" });
    if (response.status === 403) {
      handleError403(context.value);
    } else if (response.status === 400) {
      let r = await response.json();
      const n: Notification = {
        title: "Integration couldn't be deleted",
        message:
          "This integration is used by a plan. You must delete the plan before proceeding.",
        type: "error",
      };
      addNotification(n);
      success = false;
    } else if (!response.ok) {
      throw new Error(response.statusText);
    }
  } catch (e) {
    const n: Notification = {
      title: "Integration couldn't be deleted",
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

export const integration = atom<Integration | null>(null);

export async function updateIntegration(i: Integration) {
  integration.set(i);
  return integration.get();
};

export const fetchIntegration = async (id: string) => {
  increaseLoaderCounter();
  const url = `${baseApiUrl}/organization/${context.value}/integrations/${id}`;
  try {
    const response = await fetch(url);
    if (response.status === 403) {
      handleError403(context.value);
    } else if (!response.ok) {
      throw new Error(response.statusText);
    } else {
      const i: Integration = await response.json();
      updateIntegration(i);
    }
  } catch (e) {
    const n: Notification = {
      title: "Integration couldn't be fetched",
      message: (e as Error).message,
      type: "error",
    };
    addNotification(n);
  } finally {
    decreaseLoaderCounter();
  }
};

export const integrationControl = atom<IntegrationControl | null>(null);

export async function updateIntegrationControl(c: IntegrationControl) {
  integrationControl.set(c);
  return integrationControl.get();
};

export const fetchIntegrationControl = async (id: string) => {
  increaseLoaderCounter();
  const url = `${baseApiUrl}/organization/${context.value}/integrations/${id}/control`;
  try {
    const response = await fetch(url);
    if (response.status === 403) {
      handleError403(context.value);
    } else if (!response.ok) {
      throw new Error(response.statusText);
    } else {
      const c: IntegrationControl = await response.json();
      updateIntegrationControl(c);
    }
  } catch (e) {
    const n: Notification = {
      title: "Control couldn't be fetched",
      message: (e as Error).message,
      type: "error",
    };
    addNotification(n);
  } finally {
    decreaseLoaderCounter();
  }
};
