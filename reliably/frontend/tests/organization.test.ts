import { test } from "uvu";
import * as assert from "uvu/assert";
import fetchMock from "fetch-mock";
import { readFileSync } from "fs";
import { join } from "path";
import { JSDOM } from 'jsdom';

import { cleanStores } from "nanostores";
import {
  useTestStorageEngine,
  setTestStorageKey,
  cleanTestStorage,
} from "@nanostores/persistent";
import {
  users,
  fetchUsers,
  removeUser,
  invitationLink,
  getInvitationLink,
  generateInvitationLink,
} from "../src/stores/organization";
import { notifications } from "../src/stores/notifications";
import { organizationToken } from "../src/stores/user";

import type {
  OrganizationUser,
  OrganizationUsers,
  OrganizationUsersPage,
  OrganizationUsersPayload,
  InvitationLink,
  InvitationLinkPayload,
} from "@/types/organization";

import type { Notification } from "@/types/ui-types";

const { window } = new JSDOM('');

test.before(() => {
  const PUBLIC_API_URL: string = "https://62ff903e9350a1e548e1952e.mockapi.io";
	global.window = window;
});

test.before.each(() => {
  useTestStorageEngine();
  organizationToken.set("1");
  setTestStorageKey("reliably:context", "1");
});

test.after.each(() => {
  cleanTestStorage();
  cleanStores(users, invitationLink);
  fetchMock.restore();
});

test("fetch users", async () => {
  const mockResponse: OrganizationUsersPayload = JSON.parse(
    readFileSync(join(__dirname, "./data/organization/users.json"), "utf-8")
  );
  const expected: OrganizationUsersPage = {
    page: 1,
    users: mockResponse.items,
    total: 4,
    state: "ready",
  };
  fetchMock.mock(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/users?page=1&limit=10",
    mockResponse
  );
  await fetchUsers(1);
  const x = users.get();
  assert.equal(x, expected);
  fetchMock.restore();
});

test("catch error while fetching users", async () => {
  const notificationsBefore: Notification[] = notifications.get();
  fetchMock.mock(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/users?page=1&limit=10",
    404
  );
  await fetchUsers(1);
  const x: Notification[] = notifications.get();
  assert.equal(x.length, notificationsBefore.length + 1);
  assert.equal(x[x.length - 1].title, "Users couldn't be fetched");
  fetchMock.restore();
});

test("remove user", async () => {
  const idToRemove = "30";
  const nameToRemove = "Herbert_OHara";
  const mockResponseBefore: OrganizationUsersPayload = JSON.parse(
    readFileSync(join(__dirname, "./data/organization/users.json"), "utf-8")
  );
  const mockResponseAfter: OrganizationUsersPayload = JSON.parse(
    readFileSync(
      join(__dirname, "./data/organization/users-after-remove.json"),
      "utf-8"
    )
  );
  fetchMock.mock(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/users?page=1&limit=10",
    mockResponseBefore,
    { overwriteRoutes: true }
  );
  await fetchUsers(1);
  const before: OrganizationUsers = users.get();
  fetchMock.mock(
    `https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/users/${idToRemove}`,
    idToRemove,
    { overwriteRoutes: true }
  );
  await removeUser(idToRemove, nameToRemove);
  fetchMock.mock(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/users?page=1&limit=10",
    mockResponseAfter,
    { overwriteRoutes: true }
  );
  await fetchUsers(1);
  const after: OrganizationUsers = users.get();
  const x: number = before.users.length - after.users.length;
  assert.equal(x, 1); // We have deleted something
  const expected: number = -1;
  const y = after.users.findIndex((u: OrganizationUser) => {
    u.id === idToRemove;
  });
  assert.equal(y, expected); // User can't be found
});

test("catch error while removing user", async () => {
  const idToRemove = "30";
  const nameToRemove = "Herbert_OHara";
  const notificationsBefore: Notification[] = notifications.get();
  fetchMock.mock(
    `https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/users/${idToRemove}`,
    404
  );
  await removeUser(idToRemove, nameToRemove);
  const x: Notification[] = notifications.get();
  assert.equal(x.length, notificationsBefore.length + 1);
  assert.equal(x[x.length - 1].title, "User couldn't be removed");
});

test("get invitation link", async () => {
  const mockResponse: InvitationLinkPayload = {
    link: "46fbb0023197282319bfc9082ded6409",
  };
  const expected: InvitationLink = {
    link: "about:///join/?invite=46fbb0023197282319bfc9082ded6409",
    state: "ready",
  };
  fetchMock.mock(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/invite",
    mockResponse
  );
  await getInvitationLink();
  const x = invitationLink.get();
  assert.equal(x, expected);
  fetchMock.restore();
});

test("get invitation link before it's been created", async () => {
  const mockResponseInvite: InvitationLinkPayload = {
    link: null,
  };
  const mockResponseGenerate: InvitationLinkPayload = {
    link: "46fbb0023197282319bfc9082ded6409",
  };
  const expected: InvitationLink = {
    link: "about:///join/?invite=46fbb0023197282319bfc9082ded6409",
    state: "ready",
  };
  fetchMock.mock(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/invite",
    mockResponseInvite
  );
  fetchMock.mock(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/invite/generate",
    mockResponseGenerate
  );
  await getInvitationLink();
  const x = invitationLink.get();
  assert.equal(x, expected);
  fetchMock.restore();
});

test("get invitation link from a free plan", async () => {
  const expected: InvitationLink = {
    link: "Organizations on a Free plan can't invite additional team members",
    state: "ready",
  };
  fetchMock.mock(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/invite",
    429
  );
  await getInvitationLink();
  const x = invitationLink.get();
  assert.equal(x, expected);
  fetchMock.restore();
});

test("catch error while getting an invitation link", async () => {
  const notificationsBefore: Notification[] = notifications.get();
  fetchMock.mock(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/invite",
    500
  );
  await getInvitationLink();
  const x: Notification[] = notifications.get();
  assert.equal(x.length, notificationsBefore.length + 1);
  assert.equal(x[x.length - 1].title, "Invitation link couldn't be fetched");
  fetchMock.restore();
});

test("generate invitation link from a free plan", async () => {
  const expected: InvitationLink = {
    link: "Organizations on a Free plan can't invite additional team members",
    state: "ready",
  };
  fetchMock.mock(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/invite/generate",
    429
  );
  await generateInvitationLink();
  const x = invitationLink.get();
  assert.equal(x, expected);
  fetchMock.restore();
});

test("catch error while generating an invitation link", async () => {
  const notificationsBefore: Notification[] = notifications.get();
  fetchMock.mock(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/invite/generate",
    500
  );
  await generateInvitationLink();
  const x: Notification[] = notifications.get();
  assert.equal(x.length, notificationsBefore.length + 1);
  assert.equal(x[x.length - 1].title, "Invitation link couldn't be created");
  fetchMock.restore();
});

test.run();
