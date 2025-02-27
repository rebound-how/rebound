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
  plan,
  fetchPlan,
  createPlan,
  deletePlan,
  plans,
  fetchPlans,
  relatedPlansList,
  fetchRelatedPlans,
} from "../src/stores/plans";
import { organizationToken } from "../src/stores/user";
import { notifications } from "../src/stores/notifications";

import type {
  Plan,
  PlansApiJsonResponse,
  PlansPage,
  PlanCreate,
} from "@/types/plans";
import type { Notification } from "@/types/ui-types";

test.before(() => {
  const PUBLIC_API_URL: string = "https://62ff903e9350a1e548e1952e.mockapi.io";
});

test.before.each(() => {
  useTestStorageEngine();
  organizationToken.set("1");
  setTestStorageKey("reliably:context", "1");
  fetchMock.restore();
});

test.after.each(() => {
  cleanTestStorage();
  cleanStores(plan, plans, notifications);
});

test("fetch one plan", async () => {
  const expected: Plan = JSON.parse(
    readFileSync(join(__dirname, "./data/plans/single.json"), "utf-8")
  );
  fetchMock.mock(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/plans/44a4b19e-0209-4f87-8778-77d0fcb6b9a2",
    expected
  );
  await fetchPlan("44a4b19e-0209-4f87-8778-77d0fcb6b9a2");
  const x = plan.get();
  assert.equal(x, expected);
});

test("fetch first page of plans", async () => {
  const mockResponse: PlansApiJsonResponse = JSON.parse(
    readFileSync(join(__dirname, "./data/plans/first-page.json"), "utf-8")
  );
  const expected: PlansPage = {
    page: 1,
    plans: mockResponse.items,
    total: mockResponse.count,
    isReady: true,
  };
  fetchMock.mock(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/plans?page=1&limit=10",
    mockResponse
  );
  await fetchPlans(1);
  const x = plans.get();
  assert.equal(x, expected);
});

test("fetch second (and last) page of plans", async () => {
  const mockResponse: PlansApiJsonResponse = JSON.parse(
    readFileSync(join(__dirname, "./data/plans/second-page.json"), "utf-8")
  );
  const expected: PlansPage = {
    page: 2,
    plans: mockResponse.items,
    total: mockResponse.count,
    isReady: true,
  };
  fetchMock.mock(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/plans?page=2&limit=10",
    mockResponse
  );
  await fetchPlans(2);
  const x = plans.get();
  assert.equal(x, expected);
});

test("fetch plans for an experiment", async () => {
  const mockResponseList: string[] = ["ef434fff-2731-441d-8587-abd713fa8cf6"];
  const mockResponsePlan: Plan = {
    id: "ef434fff-2731-441d-8587-abd713fa8cf6",
    created_date: "2022-09-29T12:04:27.735863+00:00",
    definition: {
      environment: {
        provider: "gcp",
      },
      deployment: {
        deployment_id: "acee6165-7b88-4d9c-aa85-0c15406be726",
      },
      schedule: {
        type: "now",
      },
      experiments: ["5653c16d-1e17-44b4-9f12-2fea9b246749"],
    },
    ref: "cede5a2adc242fa79630b9040e5f9702",
    status: "creation error",
    error:
      "Failed to create GCP Cloud Run job: 401 => {'error': {'code': 401, 'message': 'Request had invalid authentication credentials. Expected OAuth 2 access token, login cookie or other valid authentication credential. See https://developers.google.com/identity/sign-in/web/devconsole-project.', 'status': 'UNAUTHENTICATED', 'details': [{'@type': 'type.googleapis.com/google.rpc.ErrorInfo', 'reason': 'ACCESS_TOKEN_TYPE_UNSUPPORTED', 'metadata': {'method': 'google.cloud.run.v1.Jobs.CreateJob', 'service': 'run.googleapis.com'}}]}}",
  };
  const expected: Plan[] = [
    {
      id: "ef434fff-2731-441d-8587-abd713fa8cf6",
      created_date: "2022-09-29T12:04:27.735863+00:00",
      definition: {
        environment: {
          provider: "gcp",
        },
        deployment: {
          deployment_id: "acee6165-7b88-4d9c-aa85-0c15406be726",
        },
        schedule: {
          type: "now",
        },
        experiments: ["5653c16d-1e17-44b4-9f12-2fea9b246749"],
      },
      ref: "cede5a2adc242fa79630b9040e5f9702",
      status: "creation error",
      error:
        "Failed to create GCP Cloud Run job: 401 => {'error': {'code': 401, 'message': 'Request had invalid authentication credentials. Expected OAuth 2 access token, login cookie or other valid authentication credential. See https://developers.google.com/identity/sign-in/web/devconsole-project.', 'status': 'UNAUTHENTICATED', 'details': [{'@type': 'type.googleapis.com/google.rpc.ErrorInfo', 'reason': 'ACCESS_TOKEN_TYPE_UNSUPPORTED', 'metadata': {'method': 'google.cloud.run.v1.Jobs.CreateJob', 'service': 'run.googleapis.com'}}]}}",
    },
  ];
  fetchMock.mock(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/experiments/7/plans",
    mockResponseList,
    { overwriteRoutes: true }
  );
  fetchMock.mock(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/plans/ef434fff-2731-441d-8587-abd713fa8cf6",
    mockResponsePlan,
    { overwriteRoutes: true }
  );
  await fetchRelatedPlans("7", "experiments");
  const x = relatedPlansList.get();
  assert.equal(x, expected);
});

test("fetch plans for an deployment", async () => {
  const mockResponseList: string[] = ["ef434fff-2731-441d-8587-abd713fa8cf6"];
  const mockResponsePlan: Plan = {
    id: "ef434fff-2731-441d-8587-abd713fa8cf6",
    created_date: "2022-09-29T12:04:27.735863+00:00",
    definition: {
      environment: {
        provider: "gcp",
      },
      deployment: {
        deployment_id: "acee6165-7b88-4d9c-aa85-0c15406be726",
      },
      schedule: {
        type: "now",
      },
      experiments: ["5653c16d-1e17-44b4-9f12-2fea9b246749"],
    },
    ref: "cede5a2adc242fa79630b9040e5f9702",
    status: "creation error",
    error:
      "Failed to create GCP Cloud Run job: 401 => {'error': {'code': 401, 'message': 'Request had invalid authentication credentials. Expected OAuth 2 access token, login cookie or other valid authentication credential. See https://developers.google.com/identity/sign-in/web/devconsole-project.', 'status': 'UNAUTHENTICATED', 'details': [{'@type': 'type.googleapis.com/google.rpc.ErrorInfo', 'reason': 'ACCESS_TOKEN_TYPE_UNSUPPORTED', 'metadata': {'method': 'google.cloud.run.v1.Jobs.CreateJob', 'service': 'run.googleapis.com'}}]}}",
  };
  const expected: Plan[] = [
    {
      id: "ef434fff-2731-441d-8587-abd713fa8cf6",
      created_date: "2022-09-29T12:04:27.735863+00:00",
      definition: {
        environment: {
          provider: "gcp",
        },
        deployment: {
          deployment_id: "acee6165-7b88-4d9c-aa85-0c15406be726",
        },
        schedule: {
          type: "now",
        },
        experiments: ["5653c16d-1e17-44b4-9f12-2fea9b246749"],
      },
      ref: "cede5a2adc242fa79630b9040e5f9702",
      status: "creation error",
      error:
        "Failed to create GCP Cloud Run job: 401 => {'error': {'code': 401, 'message': 'Request had invalid authentication credentials. Expected OAuth 2 access token, login cookie or other valid authentication credential. See https://developers.google.com/identity/sign-in/web/devconsole-project.', 'status': 'UNAUTHENTICATED', 'details': [{'@type': 'type.googleapis.com/google.rpc.ErrorInfo', 'reason': 'ACCESS_TOKEN_TYPE_UNSUPPORTED', 'metadata': {'method': 'google.cloud.run.v1.Jobs.CreateJob', 'service': 'run.googleapis.com'}}]}}",
    },
  ];
  fetchMock.mock(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/deployments/7/plans",
    mockResponseList,
    { overwriteRoutes: true }
  );
  fetchMock.mock(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/plans/ef434fff-2731-441d-8587-abd713fa8cf6",
    mockResponsePlan,
    { overwriteRoutes: true }
  );
  await fetchRelatedPlans("7", "deployments");
  const x = relatedPlansList.get();
  assert.equal(x, expected);
});

test("catch error while fetching plans for an experiment", async () => {
  const notificationsBefore: Notification[] = notifications.get();
  fetchMock.mock(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/experiments/7/plans",
    404
  );
  await fetchRelatedPlans("7", "experiments");
  const x: Notification[] = notifications.get();
  assert.equal(x.length, notificationsBefore.length + 1);
  assert.equal(x[x.length - 1].title, "Plans couldn't be fetched");
});

test("create plan", async () => {
  const newPlan: PlanCreate = {
    environment: {
      provider: "gcp",
    },
    deployment: {
      deployment_id: "acee6165-7b88-4d9c-aa85-0c15406be726",
    },
    schedule: {
      type: "now",
    },
    experiments: ["5653c16d-1e17-44b4-9f12-2fea9b246749"],
  };
  const expected: Plan = {
    id: "44a4b19e-0209-4f87-8778-77d0fcb6b9a2",
    created_date: "2022-09-29T10:59:19.528904+00:00",
    definition: {
      environment: {
        provider: "gcp",
      },
      deployment: {
        deployment_id: "acee6165-7b88-4d9c-aa85-0c15406be726",
      },
      schedule: {
        type: "now",
      },
      experiments: ["5653c16d-1e17-44b4-9f12-2fea9b246749"],
    },
    ref: "5fea8ac986f549b7c68ce1c80cb0c73a",
    status: "creating",
    error: null,
  };
  fetchMock.post(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/plans",
    expected
  );
  fetchMock.mock(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/plans/44a4b19e-0209-4f87-8778-77d0fcb6b9a2",
    expected
  );
  await createPlan(newPlan);
  await fetchPlan("44a4b19e-0209-4f87-8778-77d0fcb6b9a2");
  const x = plan.get();
  assert.equal(x, expected);
});

test("catch error while creating plan", async () => {
  const notificationsBefore: Notification[] = notifications.get();
  const newPlan: PlanCreate = {
    environment: {
      provider: "gcp",
    },
    deployment: {
      deployment_id: "acee6165-7b88-4d9c-aa85-0c15406be726",
    },
    schedule: {
      type: "now",
    },
    experiments: ["5653c16d-1e17-44b4-9f12-2fea9b246749"],
  };
  fetchMock.post(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/plans",
    500
  );
  await createPlan(newPlan);
  const x: Notification[] = notifications.get();
  assert.equal(x.length, notificationsBefore.length + 1);
  assert.equal(x[x.length - 1].title, "Plan couldn't be created");
});

test("delete plan", async () => {
  const idToDelete = "ef434fff-2731-441d-8587-abd713fa8cf6";
  const mockResponseBefore: PlansApiJsonResponse = JSON.parse(
    readFileSync(join(__dirname, "./data/plans/first-page.json"), "utf-8")
  );
  const mockResponseAfter: PlansApiJsonResponse = JSON.parse(
    readFileSync(
      join(__dirname, "./data/plans/first-page-after-delete.json"),
      "utf-8"
    )
  );
  fetchMock.mock(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/plans?page=1&limit=10",
    mockResponseBefore,
    { overwriteRoutes: true }
  );
  await fetchPlans(1);
  const before: PlansPage = plans.get();
  fetchMock.mock(
    `https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/plans/${idToDelete}`,
    idToDelete,
    { overwriteRoutes: true }
  );
  await deletePlan(idToDelete);
  fetchMock.mock(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/plans?page=1&limit=10",
    mockResponseAfter,
    { overwriteRoutes: true }
  );
  await fetchPlans(1);
  const after: PlansPage = plans.get();
  const x: number = before.total - after.total;
  assert.equal(x, 1); // We have deleted something
  const expected: number = -1;
  const y = after.plans.findIndex((p: Plan) => {
    p.id === idToDelete;
  });
  assert.equal(y, expected); // Plan can't be found
});

test("catch error while deleting plan", async () => {
  const idToDelete = "ef434fff-2731-441d-8587-abd713fa8cf6";
  const notificationsBefore: Notification[] = notifications.get();
  fetchMock.mock(
    `https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/plans/${idToDelete}`,
    500
  );
  await deletePlan(idToDelete);
  const x: Notification[] = notifications.get();
  assert.equal(x.length, notificationsBefore.length + 1);
  assert.equal(x[x.length - 1].title, "Plan couldn't be deleted");
});

test.run();
