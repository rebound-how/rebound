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
  integrations,
  fetchIntegrations,
  integration,
  createIntegration,
  deleteIntegration,
  fetchIntegration,
} from "../src/stores/integrations";
import { notifications } from "../src/stores/notifications";
import { organizationToken } from "../src/stores/user";

import type {
  Integration,
  IntegrationsApiJsonResponse,
  IntegrationsPage,
} from "@/types/integrations";

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
  cleanStores(integration, integrations);
  fetchMock.restore();
});

test("fetch first page of integrations", async () => {
  const mockResponse: IntegrationsApiJsonResponse = JSON.parse(
    readFileSync(join(__dirname, "./data/deployments/first-page.json"), "utf-8")
  ) as unknown as IntegrationsApiJsonResponse;
  const expected: IntegrationsPage = {
    page: 1,
    integrations: mockResponse.items,
    total: mockResponse.count,
    isReady: true,
  };
  fetchMock.mock(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/integrations?page=1&limit=10",
    mockResponse
  );
  await fetchIntegrations(1);
  const x = integrations.get();
  assert.equal(x, expected);
  fetchMock.restore();
});

test("catch error while fetching integrations", async () => {
  const notificationsBefore: Notification[] = notifications.get();
  fetchMock.mock(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/integrations?page=1&limit=10",
    500
  );
  await fetchIntegrations(1);
  const x: Notification[] = notifications.get();
  assert.equal(x.length, notificationsBefore.length + 1);
  assert.equal(x[x.length - 1].title, "Integrations couldn't be fetched");
});

test("catch error while fetching a single integration", async () => {
  const notificationsBefore: Notification[] = notifications.get();
  fetchMock.mock(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/integrations/8bae98b4-9b25-4e9c-afbb-457689ffb149",
    500
  );
  await fetchIntegration("8bae98b4-9b25-4e9c-afbb-457689ffb149");
  const x: Notification[] = notifications.get();
  assert.equal(x.length, notificationsBefore.length + 1);
  assert.equal(x[x.length - 1].title, "Integration couldn't be fetched");
});

test("create integration", async () => {
  const newIntegration: Integration = {
    name: "test integration",
    provider: "opentelemetry",
    vendor: "gcp",
    environment: {
      name: "otel",
      envvars: [
        {
          var_name: "OTEL_VENDOR",
          value: "gcp",
        },
      ],
      secrets: [
        {
          key: "gcp-creds",
          var_name: "CHAOSTOOLKIT_OTEL_GCP_SA",
          value: `/home/svc/.chaostoolkit/integrations/0f60df5466bd7561ed215f6673fa39c7/sa.json`,
        },
        {
          key: "service-account",
          path: `/home/svc/.chaostoolkit/integrations/0f60df5466bd7561ed215f6673fa39c7/sa.json`,
          value: "serviceAccount",
        },
      ],
    },
  };
  const expected: Integration = {
    name: "test integration",
    provider: "opentelemetry",
    vendor: "gcp",
    id: "4cc716d7-cb4b-47b3-989b-dc3eed13c1c5",
    org_id: "30cbda8e-021c-4b38-b032-b0358ceda201",
    created_date: "2023-03-01T16:00:18.080146+00:00",
    environment_id: "40274bb6-c0f9-4515-971c-318d7eda1b9c",
  };
  fetchMock.post(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/integrations",
    expected
  );
  fetchMock.mock(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/integrations/4cc716d7-cb4b-47b3-989b-dc3eed13c1c5",
    expected
  );
  await createIntegration(newIntegration);
  await fetchIntegration("4cc716d7-cb4b-47b3-989b-dc3eed13c1c5");
  const x = integration.get();
  assert.equal(x, expected);
  fetchMock.restore();
});

test("catch error when creating integration", async () => {
  const notificationsBefore: Notification[] = notifications.get();
  const newIntegration: Integration = {
    name: "test integration",
    provider: "opentelemetry",
    vendor: "gcp",
    environment: {
      name: "otel",
      envvars: [
        {
          var_name: "OTEL_VENDOR",
          value: "gcp",
        },
      ],
      secrets: [
        {
          key: "gcp-creds",
          var_name: "CHAOSTOOLKIT_OTEL_GCP_SA",
          value: `/home/svc/.chaostoolkit/integrations/0f60df5466bd7561ed215f6673fa39c7/sa.json`,
        },
        {
          key: "service-account",
          path: `/home/svc/.chaostoolkit/integrations/0f60df5466bd7561ed215f6673fa39c7/sa.json`,
          value: "serviceAccount",
        },
      ],
    },
  };
  fetchMock.post(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/integrations",
    500
  );
  await createIntegration(newIntegration);
  const x: Notification[] = notifications.get();
  assert.equal(x.length, notificationsBefore.length + 1);
  assert.equal(x[x.length - 1].title, "Integration couldn't be created");
});

test("delete integration", async () => {
  const idToDelete = "8bae98b4-9b25-4e9c-afbb-457689ffb149";
  const mockResponseBefore: IntegrationsApiJsonResponse = JSON.parse(
    readFileSync(join(__dirname, "./data/deployments/first-page.json"), "utf-8")
  );
  const mockResponseAfter: IntegrationsApiJsonResponse = JSON.parse(
    readFileSync(
      join(__dirname, "./data/deployments/first-page-after-delete.json"),
      "utf-8"
    )
  );
  fetchMock.mock(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/integrations?page=1&limit=10",
    mockResponseBefore,
    { overwriteRoutes: true }
  );
  await fetchIntegrations(1);
  const before: IntegrationsPage = integrations.get();
  fetchMock.mock(
    `https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/integrations/${idToDelete}`,
    idToDelete,
    { overwriteRoutes: true }
  );
  await deleteIntegration(idToDelete);
  fetchMock.mock(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/integrations?page=1&limit=10",
    mockResponseAfter,
    { overwriteRoutes: true }
  );
  await fetchIntegrations(1);
  const after: IntegrationsPage = integrations.get();
  const x: number = before.total - after.total;
  assert.equal(x, 1); // We have deleted something
  const expected: number = -1;
  const y = after.integrations.findIndex((i: Integration) => {
    i.id === idToDelete;
  });
  assert.equal(y, expected); // Integration can't be found
});

test("catch error while deleting integration", async () => {
  const idToDelete = "8bae98b4-9b25-4e9c-afbb-457689ffb149";
  const notificationsBefore: Notification[] = notifications.get();
  fetchMock.mock(
    `https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/integrations/${idToDelete}`,
    500
  );
  await deleteIntegration(idToDelete);
  const x: Notification[] = notifications.get();
  assert.equal(x.length, notificationsBefore.length + 1);
  assert.equal(x[x.length - 1].title, "Integration couldn't be deleted");
});

test("handle error 400 while deleting integration", async () => {
  const idToDelete = "8bae98b4-9b25-4e9c-afbb-457689ffb149";
  const notificationsBefore: Notification[] = notifications.get();
  fetchMock.mock(
    `https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/integrations/${idToDelete}`,
    {
      status: 400,
      body: {
        title: "Integration couldn't be deleted",
        detail:
          "This integration is used by a plan. You must delete the plan before proceeding.",
      },
    }
  );
  await deleteIntegration(idToDelete);
  const x: Notification[] = notifications.get();
  assert.equal(x.length, notificationsBefore.length + 1);
  assert.equal(x[x.length - 1].title, "Integration couldn't be deleted");
  assert.equal(
    x[x.length - 1].message,
    "This integration is used by a plan. You must delete the plan before proceeding."
  );
});

test.run();
