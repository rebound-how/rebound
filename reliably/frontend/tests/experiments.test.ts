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
  experiment,
  fetchExperiment,
  experiments,
  fetchExperiments,
  deleteExperiment,
  allExperiments,
  fetchAllExperiments,
  importExperiment,
} from "../src/stores/experiments";
import { notifications } from "../src/stores/notifications";
import { organizationToken } from "../src/stores/user";

import type {
  Experiment,
  ExperimentsApiJsonResponse,
  SimpleExperiment,
  SimpleExperimentsApiJsonResponse,
  AllExperimentsApiResponse,
  ExperimentsPage,
  ExperimentShortForm,
  ExperimentImportPayload,
} from "@/types/experiments";

import type { Notification } from "@/types/ui-types";

test.before.each(() => {
  useTestStorageEngine();
  organizationToken.set("1");
  setTestStorageKey("reliably:context", "1");
});

test.after.each(() => {
  cleanTestStorage();
  cleanStores(experiment, experiments);
  fetchMock.restore();
});

test("fetch one experiment", async () => {
  const expected: Experiment = JSON.parse(
    readFileSync(join(__dirname, "./data/experiments/single.json"), "utf-8")
  ) as unknown as Experiment;
  fetchMock.mock(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/experiments/1",
    expected
  );
  await fetchExperiment("1");
  const x = experiment.get();
  assert.equal(x, expected);
  fetchMock.restore();
});

test("catch error while fetching experiment", async () => {
  const notificationsBefore: Notification[] = notifications.get();
  fetchMock.mock(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/experiments/1",
    500
  );
  await fetchExperiment("1");
  const x: Notification[] = notifications.get();
  assert.equal(x.length, notificationsBefore.length + 1);
  assert.equal(x[x.length - 1].title, "Experiment couldn't be fetched");
});

test("fetch first page of experiments", async () => {
  const mockResponse: SimpleExperimentsApiJsonResponse = JSON.parse(
    readFileSync(join(__dirname, "./data/experiments/first-page.json"), "utf-8")
  );
  const expected: ExperimentsPage = {
    page: 1,
    experiments: mockResponse.items,
    total: mockResponse.count,
    isReady: true,
  };
  fetchMock.mock(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/experiments_summary?page=1&limit=10",
    mockResponse
  );
  await fetchExperiments(1);
  const x = experiments.get();
  assert.equal(x, expected);
  fetchMock.restore();
});

test("catch error while fetching experiments", async () => {
  const notificationsBefore: Notification[] = notifications.get();
  fetchMock.mock(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/experiments_summary?page=1&limit=10",
    500
  );
  await fetchExperiments(1);
  const x: Notification[] = notifications.get();
  assert.equal(x.length, notificationsBefore.length + 1);
  assert.equal(x[x.length - 1].title, "Experiments couldn't be fetched");
});

test("import experiment", async () => {
  const mockUserInput: string = readFileSync(
    join(__dirname, "./data/experiments/import-user-input.txt"),
    "utf-8"
  );
  const mockPayload: ExperimentImportPayload = {
    experiment: mockUserInput,
  };
  const expected: Experiment = JSON.parse(
    readFileSync(
      join(__dirname, "./data/experiments/import-success.json"),
      "utf-8"
    )
  );
  fetchMock.post(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/experiments/import",
    mockPayload,
    { overwriteRoutes: true }
  );
  fetchMock.mock(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/experiments/f9d4cf86-c36c-48a0-9614-94af887204bd",
    expected,
    { overwriteRoutes: true }
  );
  await importExperiment(mockPayload);
  await fetchExperiment("f9d4cf86-c36c-48a0-9614-94af887204bd");
  const x = experiment.get();
  assert.equal(x, expected);
  fetchMock.restore();
});

test("import and experiment", async () => {
  const mockUserInput: string = readFileSync(
    join(__dirname, "./data/experiments/import-user-input.txt"),
    "utf-8"
  );
  const mockPayload: ExperimentImportPayload = {
    experiment: mockUserInput,
  };
  const expected: Experiment = JSON.parse(
    readFileSync(
      join(__dirname, "./data/experiments/import-success.json"),
      "utf-8"
    )
  );
  fetchMock.post(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/experiments/import",
    mockPayload,
    { overwriteRoutes: true }
  );
  fetchMock.mock(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/experiments/f9d4cf86-c36c-48a0-9614-94af887204bd",
    expected,
    { overwriteRoutes: true }
  );
  await importExperiment(mockPayload, true);
  await fetchExperiment("f9d4cf86-c36c-48a0-9614-94af887204bd");
  const x = experiment.get();
  assert.equal(x, expected);
  fetchMock.restore();
});

test("catch error while importing experiment", async () => {
  const mockUserInput: string = readFileSync(
    join(__dirname, "./data/experiments/import-user-input.txt"),
    "utf-8"
  );
  const mockPayload: ExperimentImportPayload = {
    experiment: mockUserInput,
  };
  const notificationsBefore: Notification[] = notifications.get();
  fetchMock.post(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/experiments/import",
    500,
    { overwriteRoutes: true }
  );
  await importExperiment(mockPayload);
  const x: Notification[] = notifications.get();
  assert.equal(x.length, notificationsBefore.length + 1);
  assert.equal(x[x.length - 1].title, "Experiment couldn't be imported");
  fetchMock.restore();
});

test("delete experiment", async () => {
  const idToDelete = "5653c16d-1e17-44b4-9f12-2fea9b246749";
  const mockResponseBefore: ExperimentsApiJsonResponse = JSON.parse(
    readFileSync(join(__dirname, "./data/experiments/first-page.json"), "utf-8")
  );
  const mockResponseAfter: ExperimentsApiJsonResponse = {
    count: 0,
    items: [],
  };
  fetchMock.mock(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/experiments_summary?page=1&limit=10",
    mockResponseBefore,
    { overwriteRoutes: true }
  );
  await fetchExperiments(1);
  const before: ExperimentsPage = experiments.get();
  fetchMock.mock(
    `https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/experiments/${idToDelete}`,
    idToDelete,
    { overwriteRoutes: true }
  );
  await deleteExperiment(idToDelete);
  fetchMock.mock(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/experiments_summary?page=1&limit=10",
    mockResponseAfter,
    { overwriteRoutes: true }
  );
  await fetchExperiments(1);
  const after: ExperimentsPage = experiments.get();
  const x: number = before.total - after.total;
  assert.equal(x, 1); // We have deleted something
  const expected: number = -1;
  const y = after.experiments.findIndex((e: SimpleExperiment) => {
    e.id === idToDelete;
  });
  assert.equal(y, expected); // Experiment can't be found
});

test("handle error 400 while deleting experiment", async () => {
  const idToDelete = "5653c16d-1e17-44b4-9f12-2fea9b246749";
  const notificationsBefore: Notification[] = notifications.get();
  fetchMock.mock(
    `https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/experiments/${idToDelete}`,
    {
      status: 400,
      body: {
        title: "Experiment couldn't be deleted",
        detail:
          "This experiment is used by a plan. You must delete the plan before proceeding.",
      },
    }
  );
  await deleteExperiment(idToDelete);
  const x: Notification[] = notifications.get();
  assert.equal(x.length, notificationsBefore.length + 1);
  assert.equal(x[x.length - 1].title, "Experiment couldn't be deleted");
  assert.equal(
    x[x.length - 1].message,
    "This experiment is used by a plan. You must delete the plan before proceeding."
  );
});

test("catch error while deleting experiment", async () => {
  const idToDelete = "5653c16d-1e17-44b4-9f12-2fea9b246749";
  const notificationsBefore: Notification[] = notifications.get();
  fetchMock.mock(
    `https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/experiments/${idToDelete}`,
    500
  );
  await deleteExperiment(idToDelete);
  const x: Notification[] = notifications.get();
  assert.equal(x.length, notificationsBefore.length + 1);
  assert.equal(x[x.length - 1].title, "Experiment couldn't be deleted");
});

test("fetch full list of experiments", async () => {
  const mockResponse: AllExperimentsApiResponse = JSON.parse(
    readFileSync(join(__dirname, "./data/experiments/all.json"), "utf-8")
  );
  const expected: ExperimentShortForm[] = mockResponse.items;
  fetchMock.mock(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/experiments_all",
    mockResponse
  );
  await fetchAllExperiments();
  const x = allExperiments.get();
  assert.equal(x, expected);
  fetchMock.restore();
});

test("catch error while fetching full list of experiments", async () => {
  const notificationsBefore: Notification[] = notifications.get();
  fetchMock.mock(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/experiments_all",
    500
  );
  await fetchAllExperiments();
  const x: Notification[] = notifications.get();
  assert.equal(x.length, notificationsBefore.length + 1);
  assert.equal(x[x.length - 1].title, "Experiments couldn't be fetched");
});

test.run();
