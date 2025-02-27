export interface Subscription {
  org_id: string | null;
  subscription: SubscriptionDetail | null;
  plan: SubscriptionPlan;
  state?: string;
}

interface SubscriptionDetail {
  id: string;
}

interface SubscriptionPlan {
  name: string;
  remaining: {
    [key: string]: number;
  };
}

export interface RemainingForUi {
  [key: string]: string;
}

export interface CheckoutPayload {
  org_name: string;
  plan_name: string;
}

export interface CheckoutResponsePayload {
  link: string;
  err: string;
}

export interface NameCandidatePayload {
  name: string;
}

export interface NameCandidateResponsePayload {
  available: boolean;
}

export interface NameCandidateInternalResponse {
  available: boolean;
  err:
    | "This name is not available."
    | "Name availability couldn't be checked. Please try again."
    | "";
}
