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
  environment,
  fetchEnvironment,
  environments,
  fetchEnvironments,
  deleteEnvironment,
  createEnvironment,
} from "../src/stores/environments";
import { notifications } from "../src/stores/notifications";
import { organizationToken } from "../src/stores/user";

import type {
  Environment,
  EnvironmentsApiJsonResponse,
  EnvironmentsPage,
} from "@/types/environments";
import type { Notification } from "@/types/ui-types";

test.before.each(() => {
  useTestStorageEngine();
  organizationToken.set("1");
  setTestStorageKey("reliably:context", "1");
});

test.after.each(() => {
  cleanTestStorage();
  cleanStores(environment, environments);
  fetchMock.restore();
});

test("fetch one environment", async () => {
  const expected: Environment = JSON.parse(
    readFileSync(join(__dirname, "./data/environments/single.json"), "utf-8")
  ) as unknown as Environment;
  fetchMock.mock(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/environments/1",
    expected
  );
  await fetchEnvironment("1");
  const x = environment.get();
  assert.equal(x, expected);
  fetchMock.restore();
});

test("catch error while fetching one environment", async () => {
  const notificationsBefore: Notification[] = notifications.get();
  fetchMock.mock(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/environments/1",
    500
  );
  await fetchEnvironment("1");
  const x: Notification[] = notifications.get();
  assert.equal(x.length, notificationsBefore.length + 1);
  assert.equal(x[x.length - 1].title, "Environment couldn't be fetched");
});

test("fetch page of environments", async () => {
  const mockResponse: EnvironmentsApiJsonResponse = JSON.parse(
    readFileSync(join(__dirname, "./data/environments/page.json"), "utf-8")
  );
  const expected: EnvironmentsPage = {
    page: 1,
    environments: mockResponse.items,
    total: mockResponse.count,
    isReady: true,
  };
  fetchMock.mock(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/environments?page=1&limit=10",
    mockResponse
  );
  await fetchEnvironments(1);
  const x = environments.get();
  assert.equal(x, expected);
  fetchMock.restore();
});

test("catch error while fetching environments", async () => {
  const notificationsBefore: Notification[] = notifications.get();
  fetchMock.mock(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/environments?page=1&limit=10",
    500
  );
  await fetchEnvironments(1);
  const x: Notification[] = notifications.get();
  assert.equal(x.length, notificationsBefore.length + 1);
  assert.equal(x[x.length - 1].title, "Environments couldn't be fetched");
});

test("delete environment", async () => {
  const idToDelete = "c4c0e3d5-445e-48de-b727-950c6b605336";
  const mockResponseBefore: EnvironmentsApiJsonResponse = JSON.parse(
    readFileSync(join(__dirname, "./data/environments/page.json"), "utf-8")
  );
  const mockResponseAfter: EnvironmentsApiJsonResponse = {
    count: 1,
    items: [
      {
        org_id: "1",
        id: "c4c0e3d5-445e-48de-b727-950c6b605339",
        name: "myenv95",
        created_date: "2023-01-09T16:02:40.282192+00:00",
        envvars: [
          { var_name: "DEMO_VAR2", value: "hello" },
          { var_name: "GH_REPO", value: "reliablyhq/reliably" },
        ],
        secrets: [
          {
            var_name: "GITHUB_TOKEN",
            value: "**********",
            key: "gh_token",
          },
          {
            key: "kubeconfig",
            value: "**********",
            path: "/home/svc/.kube/config",
          },
        ],
      },
    ],
  };
  fetchMock.mock(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/environments?page=1&limit=10",
    mockResponseBefore,
    { overwriteRoutes: true }
  );
  await fetchEnvironments(1);
  const before: EnvironmentsPage = environments.get();
  fetchMock.mock(
    `https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/experiments/${idToDelete}`,
    idToDelete,
    { overwriteRoutes: true }
  );
  await deleteEnvironment(idToDelete);
  fetchMock.mock(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/environments?page=1&limit=10",
    mockResponseAfter,
    { overwriteRoutes: true }
  );
  await fetchEnvironments(1);
  const after: EnvironmentsPage = environments.get();
  const x: number = before.total - after.total;
  assert.equal(x, 1); // We have deleted something
  const expected: number = -1;
  const y = after.environments.findIndex((e: Environment) => {
    e.id === idToDelete;
  });
  assert.equal(y, expected); // Experiment can't be found
});

test("handle error 400 while deleting environment", async () => {
  const idToDelete = "c4c0e3d5-445e-48de-b727-950c6b605336";
  const notificationsBefore: Notification[] = notifications.get();
  fetchMock.mock(
    `https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/environments/${idToDelete}`,
    {
      status: 400,
      body: {
        title: "Environment couldn't be deleted",
        detail:
          "This environment is used by a plan. You must delete the plan before proceeding.",
      },
    }
  );
  await deleteEnvironment(idToDelete);
  const x: Notification[] = notifications.get();
  assert.equal(x.length, notificationsBefore.length + 1);
  assert.equal(x[x.length - 1].title, "Environment couldn't be deleted");
  assert.equal(
    x[x.length - 1].message,
    "This environment is used by a plan. You must delete the plan before proceeding."
  );
});

test("catch error while deleting environment", async () => {
  const idToDelete = "c4c0e3d5-445e-48de-b727-950c6b605336";
  const notificationsBefore: Notification[] = notifications.get();
  fetchMock.mock(
    `https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/environments/${idToDelete}`,
    500
  );
  await deleteEnvironment(idToDelete);
  const x: Notification[] = notifications.get();
  assert.equal(x.length, notificationsBefore.length + 1);
  assert.equal(x[x.length - 1].title, "Environment couldn't be deleted");
});

test("create environment", async () => {
  const mockUserInput: string = readFileSync(
    join(__dirname, "./data/environments/import-user-input.json"),
    "utf-8"
  );
  const mockPayload: { environment: Environment } = {
    environment: mockUserInput as unknown as Environment,
  };
  const expected: Environment = JSON.parse(
    readFileSync(
      join(__dirname, "./data/experiments/import-success.json"),
      "utf-8"
    )
  );
  fetchMock.post(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/environments",
    mockPayload,
    { overwriteRoutes: true }
  );
  fetchMock.mock(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/environments/c4c0e3d5-445e-48de-b727-950c6b605342",
    expected,
    { overwriteRoutes: true }
  );
  await createEnvironment(JSON.parse(mockUserInput) as unknown as Environment);
  await fetchEnvironment("c4c0e3d5-445e-48de-b727-950c6b605342");
  const x = environment.get();
  assert.equal(x, expected);
  fetchMock.restore();
});

test("catch error while creating environment", async () => {
  const mockUserInput: string = readFileSync(
    join(__dirname, "./data/environments/import-user-input.json"),
    "utf-8"
  );
  const notificationsBefore: Notification[] = notifications.get();
  fetchMock.post(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/environments",
    500,
    { overwriteRoutes: true }
  );
  await createEnvironment(JSON.parse(mockUserInput) as unknown as Environment);
  const x: Notification[] = notifications.get();
  assert.equal(x.length, notificationsBefore.length + 1);
  assert.equal(x[x.length - 1].title, "Environment couldn't be created");
  fetchMock.restore();
});

test("don't allow creation of emprt environment", async () => {
  const mockUserInput: Environment = {
    name: "TestEnv",
    envvars: [],
    secrets: [],
  };
  const notificationsBefore: Notification[] = notifications.get();
  await createEnvironment(mockUserInput);
  const x: Notification[] = notifications.get();
  assert.equal(x.length, notificationsBefore.length + 1);
  assert.equal(x[x.length - 1].title, "Environment couldn't be created");
  assert.equal(
    x[x.length - 1].message,
    "You must provide at least one environment variable or secret"
  );
  fetchMock.restore();
});

test.run();
