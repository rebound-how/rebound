
// Do not remove the (empty) line above it helps with code coverage in c8
import { map } from "nanostores";

import type {
  Subscription,
  CheckoutPayload,
  CheckoutResponsePayload,
  NameCandidateResponsePayload,
  NameCandidateInternalResponse,
} from "@/types/subscriptions";
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

const currentSubscriptionUrl: string = useMockApi
  ? "subscriptions-current"
  : "subscriptions/current";
/* c8 ignore stop */

const context = useStore(organizationToken);

export const currentSubscription = map<Subscription>({
  org_id: null,
  subscription: null,
  plan: {
    name: "free",
    remaining: {
      executions: 0,
      experiments: 0,
      minutes: 0,
      members: 0,
    },
  },
  state: "empty",
});

export async function updateSubscription(data: Subscription) {
  currentSubscription.set(data);
  return currentSubscription.get();
};

export async function fetchCurrentSubscription() {
  increaseLoaderCounter();
  currentSubscription.setKey("state", "loading");
  const url = `${baseApiUrl}/organization/${context.value}/${currentSubscriptionUrl}`;
  try {
    const response = await fetch(url);
    if (response.status === 403) {
      handleError403(context.value);
    } else if (!response.ok) {
      throw new Error(response.statusText);
    } else {
      const s: Subscription = await response.json();
      let current: Subscription = {
        org_id: s.org_id,
        subscription: s.subscription,
        plan: s.plan,
        state: "ready",
      };
      updateSubscription(current);
    }
  } catch (e) {
    const n: Notification = {
      title: "Your subscription couldn't be fetched",
      message: (e as Error).message,
      type: "error",
    };
    addNotification(n);
    currentSubscription.setKey("state", "error");
  } finally {
    decreaseLoaderCounter();
  }
}

export async function doCheckout(payload: CheckoutPayload) {
  increaseLoaderCounter();
  const url = `${baseApiUrl}/organization/${context.value}/subscriptions/checkout`;
  try {
    const response = await fetch(url, {
      method: "POST",
      headers: {
        Accept: "application/json, text/plain, */*",
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });
    if (response.status === 403) {
      handleError403(context.value);
    } else if (!response.ok) {
      throw new Error(response.statusText);
    } else {
      const checkoutResponse: CheckoutResponsePayload = await response.json();
      if (checkoutResponse.err !== "") {
        throw new Error(checkoutResponse.err);
      } else {
        window.location.assign(checkoutResponse.link);
      }
    }
  } catch (e) {
    const n: Notification = {
      title: "We couldn't proceed to checkout",
      message: (e as Error).message,
      type: "error",
    };
    addNotification(n);
  } finally {
    decreaseLoaderCounter();
  }
}

export async function tryNameCandidate(
  name: string
): Promise<NameCandidateInternalResponse> {
  increaseLoaderCounter();
  const url = `${baseApiUrl}/organization/${context.value}/try-name-candidate`;
  try {
    const response = await fetch(url, {
      method: "POST",
      headers: {
        Accept: "application/json, text/plain, */*",
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ name: name }),
    });
    if (response.status === 403) {
      handleError403(context.value);
      return {
        available: false,
        err: "Name availability couldn't be checked. Please try again.",
      };
    } else if (!response.ok) {
      throw new Error(response.statusText);
    } else {
      const jsonResponse: NameCandidateResponsePayload = await response.json();
      decreaseLoaderCounter();
      return {
        available: jsonResponse.available,
        err: jsonResponse.available ? "" : "This name is not available.",
      };
    }
  } catch (e) {
    decreaseLoaderCounter();
    return {
      available: false,
      err: "Name availability couldn't be checked. Please try again.",
    };
  }
}
