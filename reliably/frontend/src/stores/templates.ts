import { atom, map } from "nanostores";

import type {
  Template,
  RelatedActivity,
  RelatedTemplates,
  TemplateManifest,
  TemplateCreate,
  TemplatesPage,
  CatalogsApiResponse,
} from "@/types/templates";
import type { Notification } from "@/types/ui-types";

import { handleError403 } from "../utils/user";

import { useStore } from "@nanostores/vue";
import { organizationToken } from "./user";
import { increaseLoaderCounter, decreaseLoaderCounter } from "./loader";
import { addNotification } from "./notifications";

/* c8 ignore start */
const baseApiUrl: string =
  import.meta.env === undefined
    ? "https://62ff903e9350a1e548e1952e.mockapi.io/api"
    : import.meta.env.PUBLIC_API_URL;
const useMockApi =
  baseApiUrl === "https://62ff903e9350a1e548e1952e.mockapi.io/api";

const apiUrlPrefix: string = useMockApi ? "&limit=10" : "";

const labelsApi: string = useMockApi ? "catalogs-labels" : "catalogs/labels";
/* c8 ignore stop */

const context = useStore(organizationToken);

// Templates List
export const templates = map<TemplatesPage>({
  page: 0,
  templates: [],
  total: 0,
  isReady: false,
});

export async function updateTemplates(data: TemplatesPage) {
  templates.set(data);
  return templates.get();
};

export const fetchTemplates = async (page: number) => {
  increaseLoaderCounter();
  const url = `${baseApiUrl}/organization/${context.value}/catalogs?page=${page}${apiUrlPrefix}`;
  try {
    const response = await fetch(url);
    if (response.status === 403) {
      handleError403(context.value);
    } else if (!response.ok) {
      throw new Error(response.statusText);
    } else {
      const c: CatalogsApiResponse = await response.json();
      let data: TemplatesPage = {
        page: page,
        templates: c.items,
        total: c.count,
        isReady: true,
      };
      updateTemplates(data);
    }
  } catch (e) {
    const n: Notification = {
      title: "Templates couldn't be fetched",
      message: (e as Error).message,
      type: "error",
    };
    addNotification(n);
  } finally {
    decreaseLoaderCounter();
  }
};

export const fetchTemplatesByLabels = async (labels: string[]) => {
  increaseLoaderCounter();
  const query: string = labels.join("&labels=");
  const url = `${baseApiUrl}/organization/${context.value}/catalogs/by/labels?labels=${query}`;
  try {
    const response = await fetch(url);
    if (response.status === 403) {
      handleError403(context.value);
    } else if (!response.ok) {
      throw new Error(response.statusText);
    } else {
      const c: Template[] = await response.json();
      let data: TemplatesPage = {
        page: 1,
        templates: c,
        total: 1,
        isReady: true,
      };
      updateTemplates(data);
    }
  } catch (e) {
    const n: Notification = {
      title: "Templates couldn't be fetched",
      message: (e as Error).message,
      type: "error",
    };
    addNotification(n);
  } finally {
    decreaseLoaderCounter();
  }
};

// Single Template
export const template = atom<Template | null>(null);

export async function updateTemplate(t: Template) {
  template.set(t);
  return template.get();
};

export const fetchTemplate = async (id: string) => {
  increaseLoaderCounter();
  const url = `${baseApiUrl}/organization/${context.value}/catalogs/${id}`;
  try {
    const response = await fetch(url);
    if (response.status === 403) {
      handleError403(context.value);
    } else if (!response.ok) {
      throw new Error(response.statusText);
    } else {
      const t: Template = await response.json();
      updateTemplate(t);
    }
  } catch (e) {
    const n: Notification = {
      title: "Template couldn't be fetched",
      message: (e as Error).message,
      type: "error",
    };
    addNotification(n);
  } finally {
    decreaseLoaderCounter();
  }
};

export const fetchActionTemplate = async (action: string) => {
  increaseLoaderCounter();
  const url = `/templates/experiments/${action}.json`;
  try {
    const response = await fetch(url);
    if (response.status === 403) {
      handleError403(context.value);
    } else if (!response.ok) {
      throw new Error(response.statusText);
    } else {
      const m: TemplateManifest = await response.json();
      updateTemplate({
        id: action,
        manifest: m,
      });
    }
  } catch (e) {
    const n: Notification = {
      title: "Template couldn't be fetched",
      message: (e as Error).message,
      type: "error",
    };
    addNotification(n);
  } finally {
    decreaseLoaderCounter();
  }
};

// Related templates
export const relatedTemplates = map<RelatedTemplates>();

export async function updateRelatedTemplates(t: Template) {
  relatedTemplates.setKey(t.id, t);
  return relatedTemplates.get();
};

export async function resetRelatedTemplates() {
  relatedTemplates.set({});
  return relatedTemplates.get();
};

export const fetchRelatedActionTemplates = async (
  actions: RelatedActivity[]
) => {
  increaseLoaderCounter();
  resetRelatedTemplates();
  try {
    for (const action of actions) {
      const url = `/templates/experiments/${action.name}.json`;
      const response = await fetch(url);
      if (response.status === 403) {
        handleError403(context.value);
      } else if (!response.ok) {
        throw new Error(response.statusText);
      } else {
        const m: TemplateManifest = await response.json();
        updateRelatedTemplates({
          id: action.name,
          manifest: m,
        });
      }
    }
  } catch (e) {
    const n: Notification = {
      title: "Some related templates couldn't be fetched",
      message: (e as Error).message,
      type: "error",
    };
    addNotification(n);
  } finally {
    decreaseLoaderCounter();
  }
};

// Create
export const createTemplate = async (template: TemplateCreate) => {
  increaseLoaderCounter();
  const url = `${baseApiUrl}/organization/${context.value}/catalogs`;
  try {
    const response = await fetch(url, {
      method: "POST",
      headers: {
        Accept: "application/json, text/plain, */*",
        "Content-Type": "application/json",
      },
      body: JSON.stringify(template),
    });
    if (response.status === 403) {
      handleError403(context.value);
    } else if (!response.ok) {
      throw new Error(response.statusText);
    } else {
      const newTemplate: Template = await response.json();
      window.location.assign(
        `/experiments/custom-templates/view/?id=${newTemplate.id}`
      );
    }
  } catch (e) {
    const n: Notification = {
      title: "Template couldn't be created",
      message: (e as Error).message,
      type: "error",
    };
    addNotification(n);
  } finally {
    decreaseLoaderCounter();
  }
};

export const deleteTemplate = async (id: string) => {
  increaseLoaderCounter();
  let success: boolean = true;
  const url = `${baseApiUrl}/organization/${context.value}/catalogs/${id}`;
  try {
    const response = await fetch(url, { method: "DELETE" });
    if (response.status === 403) {
      handleError403(context.value);
    } else if (!response.ok) {
      throw new Error(response.statusText);
    }
  } catch (e) {
    const n: Notification = {
      title: "Template couldn't be deleted",
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

// Labels
export const labels = atom<string[] | null>(null);

export async function updateLabels(l: string[]) {
  labels.set(l);
  return labels.get();
};

export const fetchLabels = async () => {
  increaseLoaderCounter();
  const url = `${baseApiUrl}/organization/${context.value}/${labelsApi}`;
  try {
    const response = await fetch(url);
    if (response.status === 403) {
      handleError403(context.value);
    } else if (!response.ok) {
      throw new Error(response.statusText);
    } else {
      const l: string[] = await response.json();
      updateLabels(l);
    }
  } catch (e) {
    const n: Notification = {
      title: "Labels couldn't be fetched",
      message: (e as Error).message,
      type: "error",
    };
    addNotification(n);
  } finally {
    decreaseLoaderCounter();
  }
};
