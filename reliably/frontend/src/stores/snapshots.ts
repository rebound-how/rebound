
// Do not remove the (empty) line above it helps with code coverage in c8
import { atom, map } from "nanostores";

import type {
  NewSnapshot,
  Snapshot,
  ResourceLinksInfoPage,
  SnapshotsApiJsonResponse,
  SnapshotsPage,
  SnapshotDiscoveryResource,
  SnapshotDiscoveryLinkInfo,
  ResourceLinksInfoApiJsonResponse,
  CandidatesPage,
  SnapshotConfiguration,
  CandidatesApiJsonResponse
} from "@/types/snapshots";
import type { Notification } from "@/types/ui-types";

import { handleError403 } from "../utils/user";

import { useStore } from "@nanostores/vue";
import { organizationToken } from "./user";
import { increaseLoaderCounter, decreaseLoaderCounter } from "./loader";
import { addNotification } from "./notifications";
import type { Environment } from "@/types/environments";

/* c8 ignore start */
const baseApiUrl: string = import.meta.env.PUBLIC_API_URL;

/* c8 ignore stop */

const context = useStore(organizationToken);

// Snapshot resources List
export const resources = map<SnapshotsPage>({
  page: 0,
  resources: [],
  total: 0,
  isReady: false,
});

export async function updateResources(data: SnapshotsPage) {
  resources.set(data);
  return resources.get();
};

// Snapshot resource data List
export const resourceData = map<string[]>([]);

export async function updateResourceData(data: string[]) {
  resourceData.set(data);
  return resourceData.get();
};

export const fetchSnapshots = async (page: number, term?: string) => {
  increaseLoaderCounter();
  
  let url = `${baseApiUrl}/organization/${context.value}/snapshots?page=${page}&limit=10`;
  if (term) {
    url = `${baseApiUrl}/organization/${context.value}/snapshots/search?pattern=${term}&page=${page}&limit=10`;
  }

  try {
    const response = await fetch(url);
    if (response.status === 403) {
      handleError403(context.value);
    } else {
      const e: SnapshotsApiJsonResponse = await response.json();
      let data: SnapshotsPage = {
        page: page,
        resources: e.items,
        total: e.count,
        isReady: true,
      };
      updateResources(data);
    }
  } catch (e) {
    const n: Notification = {
      title: "Snapshots couldn't be fetched",
      message: (e as Error).message,
      type: "error",
    };
    addNotification(n);
  } finally {
    decreaseLoaderCounter();
  }
};

// Snapshot configuration
export const snapshotConfig = atom<SnapshotConfiguration | null>(null);

export async function updateSnapshotConfig(data: SnapshotConfiguration) {
  snapshotConfig.set(data);
  return snapshotConfig.get();
};

export const fetchConfig = async () => {
  increaseLoaderCounter();
  
  let url = `${baseApiUrl}/organization/${context.value}/snapshots/config`;

  try {
    const response = await fetch(url);
    if (response.status === 403) {
      handleError403(context.value);
    } else {
      const e = await response.json();
      if (e !== null) {
        updateSnapshotConfig(e);
      }
    }
  } catch (e) {
    const n: Notification = {
      title: "The current snapshot configuration couldn't be fetched",
      message: (e as Error).message,
      type: "error",
    };
    addNotification(n);
  } finally {
    decreaseLoaderCounter();
  }
};

export const setupSnapshot = async (snapshot: NewSnapshot) => {
  increaseLoaderCounter();
  const url = `${baseApiUrl}/organization/${context.value}/snapshots`;
  try {
    const response = await fetch(url, {
      method: "POST",
      headers: {
        Accept: "application/json, text/plain, */*",
        "Content-Type": "application/json",
      },
      body: JSON.stringify(snapshot),
    });
    if (response.status === 403) {
      handleError403(context.value);
    } else if (response.status === 409) {
      let r = await response.json();
      const n: Notification = {
        title: "Resource discovery couldn't be configured",
        message:
          "A snapshot with the same name already exists",
        type: "error",
      };
      addNotification(n);
    } else if (!response.ok) {
      throw new Error(response.statusText);
    } else {
      const refreshUrl = `${baseApiUrl}/organization/${context.value}/snapshots/refresh`;
      const response = await fetch(refreshUrl);
      if (response.status === 403) {
        handleError403(context.value);
      } else if (!response.ok) {
        let r = await response.json();
        const n: Notification = {
          title: "Resources couldn't be discovered",
          message:
            "An internal error prevented resources to be discovered. This could be an issue with Reliably or a misconfigured system",
          type: "error",
        };
        addNotification(n);
      } else {
        window.location.assign("/resources/");
      }
    }
  } catch (e) {
    const n: Notification = {
      title: "Snapshot couldn't be created",
      message: (e as Error).message,
      type: "error",
    };
    addNotification(n);
  } finally {
    decreaseLoaderCounter();
  }
};

export const updateSnapshotConfiguration = async (integration_id: string, environment: Environment) => {
  increaseLoaderCounter();
  const url = `${baseApiUrl}/organization/${context.value}/snapshots/${integration_id}`;
  try {
    const response = await fetch(url, {
      method: "PUT",
      headers: {
        Accept: "application/json, text/plain, */*",
        "Content-Type": "application/json",
      },
      body: JSON.stringify(environment),
    });
    if (response.status === 403) {
      handleError403(context.value);
    } else if (!response.ok) {
      throw new Error(response.statusText);
    } else {
      const refreshUrl = `${baseApiUrl}/organization/${context.value}/snapshots/refresh`;
      const response = await fetch(refreshUrl);
      if (response.status === 403) {
        handleError403(context.value);
      } else if (!response.ok) {
        let r = await response.json();
        const n: Notification = {
          title: "Resources couldn't be discovered",
          message:
            "An internal error prevented resources to be discovered. This could be an issue with Reliably or a misconfigured system",
          type: "error",
        };
        addNotification(n);
      } else {
        window.location.assign("/resources/");
      }
    }
  } catch (e) {
    const n: Notification = {
      title: "Snapshot couldn't be updated",
      message: (e as Error).message,
      type: "error",
    };
    addNotification(n);
  } finally {
    decreaseLoaderCounter();
  }
};

export const refreshSnapshot = async () => {
  increaseLoaderCounter();
  const url = `${baseApiUrl}/organization/${context.value}/snapshots/refresh`;
  try {
    const response = await fetch(url);
    if (response.status === 403) {
      handleError403(context.value);
    } else if (!response.ok) {
      let r = await response.json();
      const n: Notification = {
        title: "Resources couldn't be discovered",
        message:
          "An internal error prevented resources to be discovered. This could be an issue with Reliably or a misconfigured system",
        type: "error",
      };
      addNotification(n);
    } else {
      window.location.assign("/resources/");
    }
  } finally {
    decreaseLoaderCounter();
  }
};

// Snapshot resource data List
export const candidates = map<CandidatesPage>({
  page: 0,
  candidates: [],
  total: 0,
  isReady: false,
});

export async function updateCandidates(data: CandidatesPage) {
  candidates.set(data);
  return candidates.get();
};

export const fetchCandidateValues = async (query: string) => {
  increaseLoaderCounter();
  const params = new URLSearchParams({
    query: query,
  });
  const url = `${baseApiUrl}/organization/${context.value}/snapshots/resources/data?${params}`;
  try {
    const response = await fetch(url);
    if (response.status === 403) {
      handleError403(context.value);
    } else if (!response.ok) {
      let r = await response.json();
      const n: Notification = {
        title: "Resource candidates couldn't be retrieved",
        message: "",
        type: "error",
      };
      addNotification(n);
    } else {
      let e: CandidatesApiJsonResponse = await response.json();
      let data: CandidatesPage = {
        page: 1,
        candidates: e.items,
        total: e.count,
        isReady: true,
      };
      updateCandidates(data);
    }
  } finally {
    decreaseLoaderCounter();
  }
};

// Single Snapshot resource
export const resource = atom<SnapshotDiscoveryResource | null>(null);

// Single Snapshot previous resource
export const previous = atom<SnapshotDiscoveryResource | null>(null);

// Current Resource links info
export const resourceLinks = map<ResourceLinksInfoPage>({
  page: 0,
  links: [],
  total: 0,
  isReady: false,
});

export async function updateResource(s: SnapshotDiscoveryResource) {
  resource.set(s);
  return resource.get();
};

export async function updatePreviousResource(s: SnapshotDiscoveryResource) {
  previous.set(s);
  return previous.get();
};

export async function updateResourceLinksInfo(s: ResourceLinksInfoPage) {
  resourceLinks.set(s);
  return resourceLinks.get();
};

export const fetchResource = async (id: string) => {
  increaseLoaderCounter();
  const url = `${baseApiUrl}/organization/${context.value}/snapshots/resources/${id}`;
  try {
    const response = await fetch(url);
    if (response.status === 403) {
      handleError403(context.value);
    } else if (!response.ok) {
      throw new Error(response.statusText);
    } else {
      const newResource: SnapshotDiscoveryResource = await response.json();
      updateResource(newResource);
    }
  } catch (e) {
    const n: Notification = {
      title: "Resource couldn't be fetched",
      message: (e as Error).message,
      type: "error",
    };
    addNotification(n);
  }
  decreaseLoaderCounter();
};

export const fetchResourceLinksInfo = async (id: string, page: number) => {
  increaseLoaderCounter();
  const url = `${baseApiUrl}/organization/${context.value}/snapshots/resources/${id}/links?page=${page}&limit=30`;
  try {
    const response = await fetch(url);
    if (response.status === 403) {
      handleError403(context.value);
    } else if (!response.ok) {
      throw new Error(response.statusText);
    } else {
      const linksInfo: ResourceLinksInfoApiJsonResponse = await response.json();
      let data: ResourceLinksInfoPage = {
        page: page,
        links: linksInfo.items,
        total: linksInfo.count,
        isReady: true,
      };
      updateResourceLinksInfo(data);
    }
  } catch (e) {
    const n: Notification = {
      title: "Resource links couldn't be fetched",
      message: (e as Error).message,
      type: "error",
    };
    addNotification(n);
  }
  decreaseLoaderCounter();
};

export const fetchPreviousResource = async (id: string) => {
  increaseLoaderCounter();
  const url = `${baseApiUrl}/organization/${context.value}/snapshots/resources/${id}/previous`;
  try {
    const response = await fetch(url);
    if (response.status === 403) {
      handleError403(context.value);
    } else if (!response.ok) {
    } else {
      const newResource: SnapshotDiscoveryResource = await response.json();
      updatePreviousResource(newResource);
    }
  } catch (e) {
    const n: Notification = {
      title: "Resource couldn't be fetched",
      message: (e as Error).message,
      type: "error",
    };
    addNotification(n);
  }
  decreaseLoaderCounter();
};

export const deleteSnapshot = async (id: string): Promise<boolean> => {
  increaseLoaderCounter();
  let success: boolean = true;
  const url = `${baseApiUrl}/organization/${context.value}/snapshots/${id}`;
  try {
    const response = await fetch(url, { method: "DELETE" });
    if (response.status === 403) {
      handleError403(context.value);
    } else if (response.status === 400) {
      let r = await response.json();
      const n: Notification = {
        title: "Snapshot couldn't be deleted",
        message:
          "This snapshot is used by a plan. You must delete the plan before proceeding.",
        type: "error",
      };
      addNotification(n);
      success = false;
    } else if (!response.ok) {
      throw new Error(response.statusText);
    }
  } catch (e) {
    const n: Notification = {
      title: "Snapshot couldn't be deleted",
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
