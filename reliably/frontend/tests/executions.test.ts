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
  execution,
  fetchExecution,
  deleteExecution,
  stopExecution,
  pauseExecution,
  resumeExecution,
  executions,
  fetchExecutions,
  experimentStatus,
  fetchExperimentStatus,
} from "../src/stores/executions";
import type {
  Execution,
  ExecutionsApiJsonResponse,
  ExecutionsPage,
} from "@/types/executions";
import type { ExperimentStatus } from "@/types/experiments";

import { notifications } from "../src/stores/notifications";
import type { Notification } from "@/types/ui-types";

import { organizationToken } from "../src/stores/user";

test.before.each(() => {
  useTestStorageEngine();
  organizationToken.set("1");
  setTestStorageKey("reliably:context", "1");
});

test.after.each(() => {
  cleanTestStorage();
  cleanStores(execution, executions);
  fetchMock.restore();
});

test("fetch one execution", async () => {
  const expected: Execution = JSON.parse(
    readFileSync(
      join(__dirname, "./data/executions/single-execution.json"),
      "utf-8"
    )
  ) as unknown as Execution;
  fetchMock.mock(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/experiments/5653c16d-1e17-44b4-9f12-2fea9b246749/executions/59b92bba-9071-48f9-a110-665b3afa790a",
    expected
  );
  await fetchExecution(
    "59b92bba-9071-48f9-a110-665b3afa790a",
    "5653c16d-1e17-44b4-9f12-2fea9b246749"
  );
  const x = execution.get();
  assert.equal(x, expected);
  fetchMock.restore();
});

test("fetch first page of executions", async () => {
  const mockResponse: ExecutionsApiJsonResponse = JSON.parse(
    readFileSync(
      join(__dirname, "./data/executions/single-execution.json"),
      "utf-8"
    )
  ) as unknown as ExecutionsApiJsonResponse;
  const expected: ExecutionsPage = {
    page: 1,
    executions: mockResponse.items,
    total: mockResponse.count,
    isReady: true,
  };
  fetchMock.mock(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/executions?page=1&limit=10",
    mockResponse
  );
  await fetchExecutions(1);
  const x = executions.get();
  assert.equal(x, expected);
  fetchMock.restore();
});

test("delete execution", async () => {
  const idToDelete = "59b92bba-9071-48f9-a110-665b3afa790a";
  const experimentId = "5653c16d-1e17-44b4-9f12-2fea9b246749";
  const mockResponseBefore: ExecutionsApiJsonResponse = JSON.parse(
    readFileSync(
      join(__dirname, "./data/executions/executions-page.json"),
      "utf-8"
    )
  );
  const mockResponseAfter: ExecutionsApiJsonResponse = JSON.parse(
    readFileSync(
      join(__dirname, "./data/executions/executions-page-after-delete.json"),
      "utf-8"
    )
  );
  fetchMock.mock(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/executions?page=1&limit=10",
    mockResponseBefore,
    { overwriteRoutes: true }
  );
  await fetchExecutions(1);
  const before: ExecutionsPage = executions.get();
  fetchMock.mock(
    `https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/experiments/${experimentId}/executions/${idToDelete}`,
    idToDelete,
    { overwriteRoutes: true }
  );
  await deleteExecution(idToDelete, experimentId);
  fetchMock.mock(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/executions?page=1&limit=10",
    mockResponseAfter,
    { overwriteRoutes: true }
  );
  await fetchExecutions(1);
  const after: ExecutionsPage = executions.get();
  const x: number = before.total - after.total;
  assert.equal(x, 1); // We have deleted something
  const expected: number = -1;
  const y = after.executions.findIndex((e: Execution) => {
    e.id === idToDelete;
  });
  assert.equal(y, expected); // Execution can't be found
});

test("catch error while deleting execution", async () => {
  const idToDelete = "ef434fff-2731-441d-8587-abd713fa8cf6";
  const experimentId = "5653c16d-1e17-44b4-9f12-2fea9b246749";
  const notificationsBefore: Notification[] = notifications.get();
  fetchMock.mock(
    `https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/experiments/${experimentId}/executions/${idToDelete}`,
    500
  );
  await deleteExecution(idToDelete, experimentId);
  const x: Notification[] = notifications.get();
  assert.equal(x.length, notificationsBefore.length + 1);
  assert.equal(x[x.length - 1].title, "Execution couldn't be deleted");
});

test("fetch executions list for one experiment", async () => {
  const mockResponse: ExecutionsApiJsonResponse = JSON.parse(
    readFileSync(
      join(__dirname, "./data/executions/experiment-executions-page.json"),
      "utf-8"
    )
  ) as unknown as ExecutionsApiJsonResponse;
  const expected: ExecutionsPage = {
    page: 1,
    executions: mockResponse.items,
    total: mockResponse.count,
    isReady: true,
  };
  fetchMock.mock(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/experiments/1/executions?page=1&limit=10",
    mockResponse
  );
  await fetchExecutions(1, "1");
  const x = executions.get();
  assert.equal(x, expected);
  fetchMock.restore();
});

test("initial experiment status is empty", async () => {
  const expected: ExperimentStatus = {
    experimentId: null,
    lastExecution: null,
    lastStatuses: [],
  };
  const x = experimentStatus.get();
  assert.equal(x, expected);
});

test("fetching an experiment status updates the store", async () => {
  const experimentId = "5653c16d-1e17-44b4-9f12-2fea9b246749";
  const mockResponse: ExecutionsApiJsonResponse = JSON.parse(
    readFileSync(
      join(__dirname, "./data/executions/experiment-executions-page.json"),
      "utf-8"
    )
  );

  const expected: ExperimentStatus = {
    experimentId: experimentId,
    lastExecution: "2022-09-22T11:45:49.054927+00:00",
    lastStatuses: ["completed", "deviated", "deviated"],
  };

  fetchMock.mock(
    `https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/experiments/${experimentId}/executions?limit=5`,
    mockResponse
  );
  await fetchExperimentStatus(experimentId);
  const x: ExperimentStatus = experimentStatus.get();
  assert.equal(x, expected);
});

test("illegal status in execution is returned as empty string", async () => {
  const experimentId = "5653c16d-1e17-44b4-9f12-2fea9b246749";
  const mockResponse: ExecutionsApiJsonResponse = JSON.parse(
    readFileSync(
      join(
        __dirname,
        "./data/executions/experiment-executions-with-illegal-status-page.json"
      ),
      "utf-8"
    )
  );

  const expected: ExperimentStatus = {
    experimentId: experimentId,
    lastExecution: "2022-09-22T11:45:49.054927+00:00",
    lastStatuses: ["", "deviated", "deviated"],
  };

  fetchMock.mock(
    `https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/experiments/${experimentId}/executions?limit=5`,
    mockResponse
  );
  await fetchExperimentStatus(experimentId);
  const x: ExperimentStatus = experimentStatus.get();
  assert.equal(x, expected);
});

test("catch error while getting experiment status", async () => {
  const experimentId = "5653c16d-1e17-44b4-9f12-2fea9b246749";
  const notificationsBefore: Notification[] = notifications.get();
  fetchMock.mock(
    `https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/experiments/${experimentId}/executions?limit=5`,
    500
  );
  await fetchExperimentStatus(experimentId);
  const x: Notification[] = notifications.get();
  assert.equal(x.length, notificationsBefore.length + 1);
  assert.equal(
    x[x.length - 1].title,
    "Experiment Status couldn't be retrieved"
  );
});

test("pausing an execution changes its state", async () => {
  const expected: string = "pause";
  const idToPause = "59b92bba-9071-48f9-a110-665b3afa790a";
  const experimentId = "5653c16d-1e17-44b4-9f12-2fea9b246749";
  const url = `https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/experiments/${experimentId}/executions/${idToPause}`;
  const currentExecution: Execution = JSON.parse(
    readFileSync(
      join(__dirname, "./data/executions/single-execution.json"),
      "utf-8"
    )
  ) as unknown as Execution;
  fetchMock.mock(url, currentExecution, { overwriteRoutes: true });
  await fetchExecution(
    "59b92bba-9071-48f9-a110-665b3afa790a",
    "5653c16d-1e17-44b4-9f12-2fea9b246749"
  );
  fetchMock.put(
    `${url}/state`,
    { current: "pause", duration: 300 },
    { overwriteRoutes: true }
  );
  await pauseExecution(idToPause, experimentId);
  fetchMock.mock(
    url,
    { status: 200, body: { current: "pause" } },
    { overwriteRoutes: true }
  );
  let response = await fetch(url);
  let state = await response.json();
  assert.equal(expected, state.current);
});

test("pausing an execution displays the correct notification", async () => {
  const idToPause = "59b92bba-9071-48f9-a110-665b3afa790a";
  const experimentId = "5653c16d-1e17-44b4-9f12-2fea9b246749";
  const notificationsBefore: Notification[] = notifications.get();
  fetchMock.put(
    `https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/experiments/${experimentId}/executions/${idToPause}/state`,
    { current: "pause", duration: 300 },
    { overwriteRoutes: true }
  );
  await pauseExecution(idToPause, experimentId);
  const x: Notification[] = notifications.get();
  assert.equal(x.length, notificationsBefore.length + 1);
  assert.equal(x[x.length - 1].title, "Execution successfully paused");
});

test("error while pausing an execution displays the correct notification", async () => {
  const idToPause = "59b92bba-9071-48f9-a110-665b3afa790a";
  const experimentId = "5653c16d-1e17-44b4-9f12-2fea9b246749";
  const notificationsBefore: Notification[] = notifications.get();
  fetchMock.put(
    `https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/experiments/${experimentId}/executions/${idToPause}/state`,
    404,
    { overwriteRoutes: true }
  );
  await pauseExecution(idToPause, experimentId);
  const x: Notification[] = notifications.get();
  assert.equal(x.length, notificationsBefore.length + 1);
  assert.equal(x[x.length - 1].title, "Execution couldn't be paused");
});

test("resuming an execution changes its state", async () => {
  const expected: string = "running";
  const idToResume = "59b92bba-9071-48f9-a110-665b3afa790a";
  const experimentId = "5653c16d-1e17-44b4-9f12-2fea9b246749";
  const url = `https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/experiments/${experimentId}/executions/${idToResume}`;
  const currentExecution: Execution = JSON.parse(
    readFileSync(
      join(__dirname, "./data/executions/single-execution-paused.json"),
      "utf-8"
    )
  ) as unknown as Execution;
  fetchMock.mock(url, currentExecution, { overwriteRoutes: true });
  await fetchExecution(
    "59b92bba-9071-48f9-a110-665b3afa790a",
    "5653c16d-1e17-44b4-9f12-2fea9b246749"
  );
  fetchMock.put(
    `${url}/state`,
    { current: "resume" },
    { overwriteRoutes: true }
  );
  await resumeExecution(idToResume, experimentId);
  fetchMock.mock(
    url,
    { status: 200, body: { current: "running" } },
    { overwriteRoutes: true }
  );
  let response = await fetch(url);
  let state = await response.json();
  assert.equal(expected, state.current);
});

test("resuming an execution displays the correct notification", async () => {
  const idToPause = "59b92bba-9071-48f9-a110-665b3afa790a";
  const experimentId = "5653c16d-1e17-44b4-9f12-2fea9b246749";
  const notificationsBefore: Notification[] = notifications.get();
  fetchMock.put(
    `https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/experiments/${experimentId}/executions/${idToPause}/state`,
    { current: "resume" },
    { overwriteRoutes: true }
  );
  await resumeExecution(idToPause, experimentId);
  const x: Notification[] = notifications.get();
  assert.equal(x.length, notificationsBefore.length + 1);
  assert.equal(x[x.length - 1].title, "Execution successfully resumed");
});

test("error while resuming an execution displays the correct notification", async () => {
  const idToPause = "59b92bba-9071-48f9-a110-665b3afa790a";
  const experimentId = "5653c16d-1e17-44b4-9f12-2fea9b246749";
  const notificationsBefore: Notification[] = notifications.get();
  fetchMock.put(
    `https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/experiments/${experimentId}/executions/${idToPause}/state`,
    500,
    { overwriteRoutes: true }
  );
  await resumeExecution(idToPause, experimentId);
  const x: Notification[] = notifications.get();
  assert.equal(x.length, notificationsBefore.length + 1);
  assert.equal(x[x.length - 1].title, "Execution couldn't be resumed");
});

test("stopping an execution changes its state", async () => {
  const expected: string = "terminate";
  const idToStop = "59b92bba-9071-48f9-a110-665b3afa790a";
  const experimentId = "5653c16d-1e17-44b4-9f12-2fea9b246749";
  const url = `https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/experiments/${experimentId}/executions/${idToStop}`;
  const currentExecution: Execution = JSON.parse(
    readFileSync(
      join(__dirname, "./data/executions/single-execution.json"),
      "utf-8"
    )
  ) as unknown as Execution;
  fetchMock.mock(url, currentExecution, { overwriteRoutes: true });
  await fetchExecution(
    "59b92bba-9071-48f9-a110-665b3afa790a",
    "5653c16d-1e17-44b4-9f12-2fea9b246749"
  );
  fetchMock.put(
    `${url}/state`,
    { current: "terminate" },
    { overwriteRoutes: true }
  );
  await stopExecution(idToStop, experimentId, true);
  fetchMock.mock(
    url,
    { status: 200, body: { current: "terminate" } },
    { overwriteRoutes: true }
  );
  let response = await fetch(url);
  let state = await response.json();
  assert.equal(expected, state.current);
});

test("stopping an execution displays the correct notification", async () => {
  const idToStop = "59b92bba-9071-48f9-a110-665b3afa790a";
  const experimentId = "5653c16d-1e17-44b4-9f12-2fea9b246749";
  const notificationsBefore: Notification[] = notifications.get();
  fetchMock.put(
    `https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/experiments/${experimentId}/executions/${idToStop}/state`,
    { current: "terminate", skip_rollbacks: false },
    { overwriteRoutes: true }
  );
  await stopExecution(idToStop, experimentId, false);
  const x: Notification[] = notifications.get();
  assert.equal(x.length, notificationsBefore.length + 1);
  assert.equal(x[x.length - 1].title, "Execution successfully stopped");
  assert.equal(
    x[x.length - 1].message,
    "Termination can take a few seconds to proceed."
  );
});

test("stopping and skipping rollbacks displays the correct notification", async () => {
  const idToStop = "59b92bba-9071-48f9-a110-665b3afa790a";
  const experimentId = "5653c16d-1e17-44b4-9f12-2fea9b246749";
  const notificationsBefore: Notification[] = notifications.get();
  fetchMock.put(
    `https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/experiments/${experimentId}/executions/${idToStop}/state`,
    { current: "terminate", skip_rollbacks: true },
    { overwriteRoutes: true }
  );
  await stopExecution(idToStop, experimentId, true);
  const x: Notification[] = notifications.get();
  assert.equal(x.length, notificationsBefore.length + 1);
  assert.equal(x[x.length - 1].title, "Execution successfully stopped");
  assert.equal(
    x[x.length - 1].message,
    "Termination can take a few seconds to proceed. Rollbacks will not be played."
  );
});

test("error while stopping an execution displays the correct notification", async () => {
  const idToStop = "59b92bba-9071-48f9-a110-665b3afa790a";
  const experimentId = "5653c16d-1e17-44b4-9f12-2fea9b246749";
  const notificationsBefore: Notification[] = notifications.get();
  fetchMock.put(
    `https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/experiments/${experimentId}/executions/${idToStop}/state`,
    500,
    { overwriteRoutes: true }
  );
  await stopExecution(idToStop, experimentId, false);
  const x: Notification[] = notifications.get();
  assert.equal(x.length, notificationsBefore.length + 1);
  assert.equal(x[x.length - 1].title, "Execution couldn't be stopped");
});

test.run();
