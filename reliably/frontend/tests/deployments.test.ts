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
  deployment,
  fetchDeployment,
  createDeployment,
  deployments,
  fetchDeployments,
  deleteDeployment,
} from "../src/stores/deployments";
import { notifications } from "../src/stores/notifications";
import { organizationToken } from "../src/stores/user";

import type {
  Deployment,
  DeploymentsApiJsonResponse,
  DeploymentsPage,
} from "@/types/deployments";

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
  cleanStores(deployment, deployments);
  fetchMock.restore();
});

test("fetch one deployment", async () => {
  const expected: Deployment = JSON.parse(
    readFileSync(join(__dirname, "./data/deployments/single.json"), "utf-8")
  ) as unknown as Deployment;
  fetchMock.mock(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/deployments/2",
    expected
  );
  await fetchDeployment("2");
  const x = deployment.get();
  assert.equal(x, expected);
  fetchMock.restore();
});

test("catch error while fetching a single deployment", async () => {
  const notificationsBefore: Notification[] = notifications.get();
  fetchMock.mock(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/deployments/2",
    500
  );
  await fetchDeployment("2");
  const x: Notification[] = notifications.get();
  assert.equal(x.length, notificationsBefore.length + 1);
  assert.equal(x[x.length - 1].title, "Deployment couldn't be fetched");
});

test("fetch first page of deployments", async () => {
  const mockResponse: DeploymentsApiJsonResponse = JSON.parse(
    readFileSync(join(__dirname, "./data/deployments/first-page.json"), "utf-8")
  ) as unknown as DeploymentsApiJsonResponse;
  const expected: DeploymentsPage = {
    page: 1,
    deployments: mockResponse.items,
    total: mockResponse.count,
    isReady: true,
  };
  fetchMock.mock(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/deployments?page=1&limit=10",
    mockResponse
  );
  await fetchDeployments(1);
  const x = deployments.get();
  assert.equal(x, expected);
  fetchMock.restore();
});

test("fetch second (and last) page of deployments", async () => {
  const mockResponse: DeploymentsApiJsonResponse = JSON.parse(
    readFileSync(
      join(__dirname, "./data/deployments/second-page.json"),
      "utf-8"
    )
  ) as unknown as DeploymentsApiJsonResponse;
  const expected: DeploymentsPage = {
    page: 2,
    deployments: mockResponse.items,
    total: mockResponse.count,
    isReady: true,
  };
  fetchMock.mock(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/deployments?page=2&limit=10",
    mockResponse
  );
  await fetchDeployments(2);
  const x = deployments.get();
  assert.equal(x, expected);
  fetchMock.restore();
});

test("catch error while fetching deployments", async () => {
  const notificationsBefore: Notification[] = notifications.get();
  fetchMock.mock(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/deployments?page=1&limit=10",
    500
  );
  await fetchDeployments(1);
  const x: Notification[] = notifications.get();
  assert.equal(x.length, notificationsBefore.length + 1);
  assert.equal(x[x.length - 1].title, "Deployments couldn't be fetched");
});

test("create deployment", async () => {
  const newDeployment: Deployment = {
    name: "test deployment",
    definition: {
      type: "github",
      repo: "https://github.com/reliablyhq/reliably",
      name: "staging",
      token: "abc",
    },
  };
  const expected: Deployment = {
    name: "test deployment",
    definition: {
      type: "github",
      repo: "https://github.com/reliablyhq/reliably",
      name: "staging",
      token: "abc",
    },
    id: "9348424d-ece9-4a43-9cbf-753a425c74d9",
    org_id: "ce4e266e-652c-43f4-95cf-167599f11c97",
    created_date: "2022-09-14T16:19:17.227Z",
  };
  fetchMock.post(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/deployments",
    expected
  );
  fetchMock.mock(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/deployments/9348424d-ece9-4a43-9cbf-753a425c74d9",
    expected
  );
  await createDeployment(newDeployment);
  await fetchDeployment("9348424d-ece9-4a43-9cbf-753a425c74d9");
  const x = deployment.get();
  assert.equal(x, expected);
  fetchMock.restore();
});

test("catch error while creating deployments", async () => {
  const newDeployment: Deployment = {
    name: "test deployment",
    definition: {
      type: "github",
      repo: "https://github.com/reliablyhq/reliably",
      name: "staging",
      token: "abc",
    },
  };
  const notificationsBefore: Notification[] = notifications.get();
  fetchMock.mock(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/deployments",
    500
  );
  await createDeployment(newDeployment);
  const x: Notification[] = notifications.get();
  assert.equal(x.length, notificationsBefore.length + 1);
  assert.equal(x[x.length - 1].title, "Deployment couldn't be created");
});

test("delete deployment", async () => {
  const idToDelete = "2";
  const mockResponseBefore: DeploymentsApiJsonResponse = JSON.parse(
    readFileSync(join(__dirname, "./data/deployments/first-page.json"), "utf-8")
  );
  const mockResponseAfter: DeploymentsApiJsonResponse = JSON.parse(
    readFileSync(
      join(__dirname, "./data/deployments/first-page-after-delete.json"),
      "utf-8"
    )
  );
  fetchMock.mock(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/deployments?page=1&limit=10",
    mockResponseBefore,
    { overwriteRoutes: true }
  );
  await fetchDeployments(1);
  const before: DeploymentsPage = deployments.get();
  fetchMock.mock(
    `https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/deployments/${idToDelete}`,
    idToDelete,
    { overwriteRoutes: true }
  );
  await deleteDeployment(idToDelete);
  fetchMock.mock(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/deployments?page=1&limit=10",
    mockResponseAfter,
    { overwriteRoutes: true }
  );
  await fetchDeployments(1);
  const after: DeploymentsPage = deployments.get();
  const x: number = before.total - after.total;
  assert.equal(x, 1); // We have deleted something
  const expected: number = -1;
  const y = after.deployments.findIndex((d: Deployment) => {
    d.id === idToDelete;
  });
  assert.equal(y, expected); // Deployment can't be found
});

test("catch error while deleting deployment", async () => {
  const idToDelete = "2";
  const notificationsBefore: Notification[] = notifications.get();
  fetchMock.mock(
    `https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/deployments/${idToDelete}`,
    500
  );
  await deleteDeployment(idToDelete);
  const x: Notification[] = notifications.get();
  assert.equal(x.length, notificationsBefore.length + 1);
  assert.equal(x[x.length - 1].title, "Deployment couldn't be deleted");
});

test("handle error 400 while deleting deployment", async () => {
  const idToDelete = "2";
  const notificationsBefore: Notification[] = notifications.get();
  fetchMock.mock(
    `https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/deployments/${idToDelete}`,
    {
      status: 400,
      body: {
        title: "Deployment couldn't be deleted",
        detail:
          "This deployment is used by a plan. You must delete the plan before proceeding.",
      },
    }
  );
  await deleteDeployment(idToDelete);
  const x: Notification[] = notifications.get();
  assert.equal(x.length, notificationsBefore.length + 1);
  assert.equal(x[x.length - 1].title, "Deployment couldn't be deleted");
  assert.equal(
    x[x.length - 1].message,
    "This deployment is used by a plan. You must delete the plan before proceeding."
  );
});

test.run();
