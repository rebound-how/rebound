import { test } from "uvu";
import * as assert from "uvu/assert";
import fetchMock from "fetch-mock";
import { readFileSync } from "fs";
import { join } from "path";

import { cleanStores } from "nanostores";
import {
  useTestStorageEngine,
  setTestStorageKey,
  cleanTestStorage,
} from "@nanostores/persistent";
import {
  currentSubscription,
  fetchCurrentSubscription,
  doCheckout,
  tryNameCandidate,
} from "../src/stores/subscriptions";
import { notifications } from "../src/stores/notifications";
import { organizationToken } from "../src/stores/user";

import type {
  CheckoutResponsePayload,
  Subscription,
  NameCandidateResponsePayload,
  NameCandidateInternalResponse,
} from "@/types/subscriptions";

import type { Notification } from "@/types/ui-types";

test.before(() => {
  const PUBLIC_API_URL: string = "https://62ff903e9350a1e548e1952e.mockapi.io";
});

test.before.each(() => {
  useTestStorageEngine();
  organizationToken.set("1");
  setTestStorageKey("reliably:context", "1");
});

test.after.each(() => {
  cleanTestStorage();
  cleanStores(currentSubscription);
  fetchMock.restore();
});

test("fetch current (free) subscription", async () => {
  const mockResponse: Subscription = JSON.parse(
    readFileSync(join(__dirname, "./data/subscriptions/free.json"), "utf-8")
  );
  const expected: Subscription = {
    org_id: "30cbda8e-021c-4b38-b032-b0358ceda201",
    subscription: null,
    plan: {
      name: "free",
      remaining: {
        executions: 1,
        experiments: 5,
        minutes: 180,
        members: 0,
      },
    },
    state: "ready",
  };
  fetchMock.mock(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/subscriptions-current",
    mockResponse
  );
  await fetchCurrentSubscription();
  const x = currentSubscription.get();
  assert.equal(x, expected);
  fetchMock.restore();
});

test("fetch current (start) subscription", async () => {
  const mockResponse: Subscription = JSON.parse(
    readFileSync(join(__dirname, "./data/subscriptions/start.json"), "utf-8")
  );
  const expected: Subscription = {
    org_id: "cb7bf21c-f591-4c37-8e0e-2a56080cfd11",
    subscription: {
      id: "ddba24d2-8121-4f51-b647-768bb7f98df6",
    },
    plan: {
      name: "start",
      remaining: {
        executions: 5,
        experiments: -1,
        minutes: 300,
        members: 1,
      },
    },
    state: "ready",
  };
  fetchMock.mock(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/subscriptions-current",
    mockResponse
  );
  await fetchCurrentSubscription();
  const x = currentSubscription.get();
  assert.equal(x, expected);
  fetchMock.restore();
});

test("notification is sent when fetching subscription fails", async () => {
  const notificationsBefore: Notification[] = notifications.get();
  fetchMock.mock(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/subscriptions-current",
    500
  );
  await fetchCurrentSubscription();
  const x: Notification[] = notifications.get();
  assert.equal(x.length, notificationsBefore.length + 1);
  assert.equal(x[x.length - 1].title, "Your subscription couldn't be fetched");
  fetchMock.restore();
});

test("subscription state is 'error' when fetching subscription fails", async () => {
  const expected: string = "error";
  fetchMock.mock(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/subscriptions-current",
    500
  );
  await fetchCurrentSubscription();
  const x: string | undefined = currentSubscription.get().state;
  assert.equal(x, expected);
  fetchMock.restore();
});

test("catch error in checkout", async () => {
  const notificationsBefore: Notification[] = notifications.get();
  fetchMock.mock(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/subscriptions/checkout",
    500
  );
  await doCheckout({ org_name: "Reliably", plan_name: "Start" });
  const x: Notification[] = notifications.get();
  assert.equal(x.length, notificationsBefore.length + 1);
  assert.equal(x[x.length - 1].title, "We couldn't proceed to checkout");
  fetchMock.restore();
});

test("catch error in checkout response payload", async () => {
  const mockResponse: CheckoutResponsePayload = {
    link: "",
    err: "Checkout Response Error",
  };
  const notificationsBefore: Notification[] = notifications.get();
  fetchMock.mock(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/subscriptions/checkout",
    mockResponse
  );
  await doCheckout({ org_name: "Reliably", plan_name: "Start" });
  const x: Notification[] = notifications.get();
  assert.equal(x.length, notificationsBefore.length + 1);
  assert.equal(x[x.length - 1].title, "We couldn't proceed to checkout");
  assert.equal(x[x.length - 1].message, "Checkout Response Error");
  fetchMock.restore();
});

/*
test("successful checkout", async () => {
  const mockResponse: CheckoutResponsePayload = {
    link: "https://checkout.stripe.com/c/pay/cs_test_a197MJKgTqfH8NWGBVbeLdmkP9KBQcFPyEB9WQT0XZ2WTCaxKKocGuK4uU#fidkdWxOYHwnPyd1blpxYHZxWjA0T05sQFNPTDNiYmp3XUk0Yn10QzN%2FQ1BQM3BmdmtqbWxXTj1hSXVoV05HTlExSE1HdE9Jd11oMERMTGJ9cnZwdUZsSDV9dEc9dElRX3ZncWZ9S0RTRk1RNTV3SjdUVlwxfycpJ2N3amhWYHdzYHcnP3F3cGApJ2lkfGpwcVF8dWAnPyd2bGtiaWBabHFgaCcpJ2BrZGdpYFVpZGZgbWppYWB3dic%2FcXdwYHgl",
    err: "",
  };
  const notificationsBefore: Notification[] = notifications.get();
  fetchMock.mock(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/subscriptions/checkout",
    mockResponse
  );
  await doCheckout({ org_name: "Reliably", plan_name: "Start" });
  const x: Notification[] = notifications.get();
  assert.equal(x.length, notificationsBefore.length + 1);
  assert.equal(x[x.length - 1].message, "window is not defined");
  // Will have to do better
  fetchMock.restore();
});
*/
test("organization name is available", async () => {
  const expected: NameCandidateInternalResponse = {
    available: true,
    err: "",
  };
  const mockResponse: NameCandidateResponsePayload = {
    available: true,
  };
  fetchMock.mock(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/try-name-candidate",
    mockResponse
  );
  const x = await tryNameCandidate("Reliably");
  assert.equal(x, expected);
  fetchMock.restore();
});

test("organization name is not available", async () => {
  const expected: NameCandidateInternalResponse = {
    available: false,
    err: "This name is not available.",
  };
  const mockResponse: NameCandidateResponsePayload = {
    available: false,
  };
  fetchMock.mock(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/try-name-candidate",
    mockResponse
  );
  const x = await tryNameCandidate("Reliably");
  assert.equal(x, expected);
  fetchMock.restore();
});

test("catch name availability API error", async () => {
  const expected: NameCandidateInternalResponse = {
    available: false,
    err: "Name availability couldn't be checked. Please try again.",
  };
  fetchMock.mock(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/try-name-candidate",
    500
  );
  const x = await tryNameCandidate("Reliably");
  assert.equal(x, expected);
  fetchMock.restore();
});

test.run();
