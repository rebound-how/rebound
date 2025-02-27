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
  getTestStorage,
} from "@nanostores/persistent";
import {
  user,
  isLoggedIn,
  organizationToken,
  tryLogin,
  tryLogout,
  updateUserEmail,
  changeOrganization,
  tokens,
  fetchTokens,
  token,
  fetchToken,
  createToken,
  deleteToken,
} from "../src/stores/user";
import { notifications } from "../src/stores/notifications";

import type { User, TokensApiResponse, Token } from "@/types/user";
import type { Notification } from "@/types/ui-types";

const loginApiResponse: User = JSON.parse(
  readFileSync(join(__dirname, "./data/user/user.json"), "utf-8")
) as unknown as User;
const tokensApiResponse: TokensApiResponse[] = JSON.parse(
  readFileSync(join(__dirname, "./data/user/tokens.json"), "utf-8")
);
const singleTokenApiResponse: Token = JSON.parse(
  readFileSync(join(__dirname, "./data/user/single-token.json"), "utf-8")
);
const context: string = "8f67bb6a-4944-40af-80b0-921023467cdc";
const emptyUser: User = {
  profile: {
    email: "",
    username: "",
    picture: "",
    id: "",
  },
  orgs: [],
};

const testUser: User = {
  profile: {
    username: "mperrien",
    email: "marc.perrien@gmail.com",
    id: "4323a371-68e7-4ea8-8716-ed3acfa0205d",
    picture: "https://avatars.githubusercontent.com/u/348229?v=4",
  },
  orgs: [
    {
      id: "8f67bb6a-4944-40af-80b0-921023467cdc",
      name: "Lawouach",
      created_date: "2022-09-17T21:23:18.529425+00:00",
    },
    {
      id: "fe9637b2-1507-4543-b662-fea252d1ccb5",
      name: "mperrien",
      created_date: "2022-09-19T08:40:12.206298+00:00",
    },
  ],
};

test.before.each(() => {
  useTestStorageEngine();
  cleanTestStorage();
  // setTestStorageKey("reliably:context", "");
  // setTestStorageKey("user:", JSON.stringify(emptyUser));
});

test.after.each(() => {
  cleanStores(isLoggedIn, organizationToken, user);
  fetchMock.restore();
});

// Start isLoggedIn tests
test("isLoggedIn is false by default", async () => {
  const expected: boolean = false;
  const x = isLoggedIn.get();
  assert.equal(x, expected);
});

test("isLoggedIn is true after login", async () => {
  const expected: boolean = true;
  fetchMock.mock(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/me/1/info/1",
    loginApiResponse
  );
  await tryLogin(context);
  const x = isLoggedIn.get();
  assert.equal(x, expected);
});

test("isLoggedIn is false after logout", async () => {
  const expected: boolean = false;
  fetchMock.mock(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/me/1/info/1",
    loginApiResponse
  );
  await tryLogin(context);
  await tryLogout();
  const x = isLoggedIn.get();
  assert.equal(x, expected);
});

test("isLoggedIn is false after login fails", async () => {
  const expected: boolean = false;
  fetchMock.mock(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/me/1/info/1",
    500
  );
  await tryLogin(context);
  const x = isLoggedIn.get();
  assert.equal(x, expected);
});

// context (organization) token-related tests
test("token is empty by default", async () => {
  const expected: string = "";
  const x = organizationToken.get();
  assert.equal(x, expected);
});

test("token is set after login", async () => {
  const expected: string = "8f67bb6a-4944-40af-80b0-921023467cdc";
  fetchMock.mock(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/me/1/info/1",
    loginApiResponse
  );
  await tryLogin(context);
  const x = organizationToken.get();
  assert.equal(x, expected);
});

test("token is stored locally after login", async () => {
  const expected: string = "8f67bb6a-4944-40af-80b0-921023467cdc";
  fetchMock.mock(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/me/1/info/1",
    loginApiResponse
  );
  await tryLogin(context);
  const storage = getTestStorage();
  const x = storage["reliably:context"];
  assert.equal(x, expected);
});

test("token is empty after logout", async () => {
  const expected: string = "";
  fetchMock.mock(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/me/1/info/1",
    loginApiResponse
  );
  await tryLogin(context);
  await tryLogout();
  const x = organizationToken.get();
  assert.equal(x, expected);
});

test("local token is deleted after logout", async () => {
  const expected: string = "";
  fetchMock.mock(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/me/1/info/1",
    loginApiResponse
  );
  await tryLogin(context);
  await tryLogout();
  const storage = getTestStorage();
  const x = storage["reliably:context"];
  assert.equal(x, expected);
});

test("token is empty after login fails", async () => {
  const expected: string = "";
  fetchMock.mock(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/me/1/info/1",
    500
  );
  await tryLogin(context);
  const x = organizationToken.get();
  assert.equal(x, expected);
});

//user tests
test("user is empty by default", async () => {
  const expected: User = emptyUser;
  const x: User = user.get();
  assert.equal(x, expected);
});

test("user is set after login", async () => {
  const expected: User = testUser;
  fetchMock.mock(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/me/1/info/1",
    loginApiResponse
  );
  await tryLogin(context);
  const x: User = user.get();
  assert.equal(x, expected);
});

test("user is stored locally after login", async () => {
  const expected: User = testUser;
  fetchMock.mock(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/me/1/info/1",
    loginApiResponse
  );
  await tryLogin(context);
  const storage = getTestStorage();
  const x: User = JSON.parse(storage["reliably:user"]);
  assert.equal(x, expected);
});

test("user is empty after logout", async () => {
  const expected: User = emptyUser;
  fetchMock.mock(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/me/1/info/1",
    loginApiResponse
  );
  await tryLogin(context);
  await tryLogout();
  const x = user.get();
  assert.equal(x, expected);
});

test("local user is deleted after logout", async () => {
  const expected: User = emptyUser;
  fetchMock.mock(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/me/1/info/1",
    loginApiResponse
  );
  await tryLogin(context);
  await tryLogout();
  const storage = getTestStorage();
  const x: User = JSON.parse(storage["reliably:user"]);
  assert.equal(x, expected);
});

test("user is empty after login fails", async () => {
  const expected: User = emptyUser;
  fetchMock.mock(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/me/1/info/1",
    500
  );
  await tryLogin(context);
  const x = user.get();
  assert.equal(x, expected);
});

test("user email is updated", async () => {
  const expected: string = "marc.perrien@gmail.com";
  fetchMock.mock(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/me/1/info/1",
    loginApiResponse
  );
  await tryLogin(context);
  await updateUserEmail("marc.perrien@gmail.com");
  const storage = getTestStorage();
  const u: User = JSON.parse(storage["reliably:user"]);
  const x: string = u.profile.email;
  assert.equal(x, expected);
});

// organization tests
test("changing organization updates token", async () => {
  const loginId: string = "8f67bb6a-4944-40af-80b0-921023467cdc";
  const newOrganizationId: string = "3047418c-85ca-42a2-a975-ac7d26355b14";
  const expected: string = newOrganizationId;
  fetchMock.mock(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/me/1/info/1",
    loginApiResponse
  );
  await tryLogin(context);
  changeOrganization(newOrganizationId);
  const x = organizationToken.get();
  assert.equal(x, expected);
});

test("changing organization stores token locally", async () => {
  const loginId: string = "8f67bb6a-4944-40af-80b0-921023467cdc";
  const newOrganizationId: string = "3047418c-85ca-42a2-a975-ac7d26355b14";
  const expected: string = newOrganizationId;
  fetchMock.mock(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/me/1/info/1",
    loginApiResponse
  );
  await tryLogin(context);
  changeOrganization(newOrganizationId);
  const storage = getTestStorage();
  const x = storage["reliably:context"];
  assert.equal(x, expected);
});

// User-generated tokens tests
test("tokens are fetched", async () => {
  const expected: TokensApiResponse[] = [
    {
      org: {
        id: "8f67bb6a-4944-40af-80b0-921023467cdc",
        name: "Lawouach",
        created_date: "2022-09-17T21:23:18.529425+00:00",
      },
      tokens: [
        {
          id: "69a05159-3ca5-42b8-9470-a5e25472f799",
          name: "My first token",
          created_date: "2022-09-17T21:25:18.529425+00:00",
        },
        {
          id: "06aaa09b-3a82-4709-8623-b8ac70383e59",
          name: "Another token",
          created_date: "2022-09-17T21:27:18.529425+00:00",
        },
      ],
    },
    {
      org: {
        id: "fe9637b2-1507-4543-b662-fea252d1ccb5",
        name: "mperrien",
        created_date: "2022-09-19T08:40:12.206298+00:00",
      },
      tokens: [
        {
          id: "59f5cbe1-efc4-434b-8c58-5176b0b605cf",
          name: "Token in my org",
          created_date: "2022-09-17T21:29:18.529425+00:00",
        },
        {
          id: "49804a51-069f-479e-ac8f-70935e14eb94",
          name: "A test token",
          created_date: "2022-09-17T21:31:18.529425+00:00",
        },
        {
          id: "97976c19-ccdb-4297-9815-d9e278e7d0c2",
          name: "Forgotten what this was for",
          created_date: "2022-09-17T21:33:18.529425+00:00",
        },
      ],
    },
  ];
  fetchMock.mock(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/me/1/tokens",
    tokensApiResponse
  );
  await fetchTokens();
  const x = tokens.get();
  assert.equal(x, expected);
});

test("catch error while fetching tokens", async () => {
  const notificationsBefore: Notification[] = notifications.get();
  fetchMock.mock(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/me/1/tokens",
    500
  );
  await fetchTokens();
  const x: Notification[] = notifications.get();
  assert.equal(x.length, notificationsBefore.length + 1);
  assert.equal(x[x.length - 1].title, "Tokens couldn't be fetched");
});

test("fetch a single token", async () => {
  const expected: Token = {
    id: "06aaa09b-3a82-4709-8623-b8ac70383e59",
    name: "Another token",
    created_date: "2022-09-17T21:27:18.529425+00:00",
    token: "24955849d71156ef989696dc9f732c6d",
  };
  organizationToken.set("1");
  fetchMock.mock(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/tokens/06aaa09b-3a82-4709-8623-b8ac70383e59",
    singleTokenApiResponse
  );
  await fetchToken("06aaa09b-3a82-4709-8623-b8ac70383e59");
  const x = token.get();
  assert.equal(x, expected);
});

test("catch error while fetching single token", async () => {
  const notificationsBefore: Notification[] = notifications.get();
  fetchMock.mock(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/tokens/06aaa09b-3a82-4709-8623-b8ac70383e59",
    404
  );
  organizationToken.set("1");
  await fetchToken("06aaa09b-3a82-4709-8623-b8ac70383e59");
  const x: Notification[] = notifications.get();
  assert.equal(x.length, notificationsBefore.length + 1);
  assert.equal(x[x.length - 1].title, "Token couldn't be fetched");
});

test("create token", async () => {
  const expected: Token = {
    id: "06aaa09b-3a82-4709-8623-b8ac70383e59",
    name: "Another token",
    created_date: "2022-09-17T21:27:18.529425+00:00",
    token: "24955849d71156ef989696dc9f732c6d",
  };
  organizationToken.set("1");
  fetchMock.mock(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/tokens",
    singleTokenApiResponse
  );
  await createToken("Another token");
  fetchMock.mock(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/tokens/06aaa09b-3a82-4709-8623-b8ac70383e59",
    singleTokenApiResponse
  );
  await fetchToken("06aaa09b-3a82-4709-8623-b8ac70383e59");
  const x = token.get();
  assert.equal(x, expected);
});

test("catch error while creating token", async () => {
  organizationToken.set("1");
  const notificationsBefore: Notification[] = notifications.get();
  fetchMock.mock(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/1/tokens",
    409
  );
  await createToken("Another token");
  const x: Notification[] = notifications.get();
  assert.equal(x.length, notificationsBefore.length + 1);
  assert.equal(x[x.length - 1].title, "Token couldn't be created");
});

test("delete token", async () => {
  const orgId: string = "fe9637b2-1507-4543-b662-fea252d1ccb5";
  organizationToken.set(orgId);
  const idToDelete = "49804a51-069f-479e-ac8f-70935e14eb94";
  const mockResponseBefore: TokensApiResponse[] = JSON.parse(
    readFileSync(join(__dirname, "./data/user/tokens.json"), "utf-8")
  );
  const mockResponseAfter: TokensApiResponse[] = JSON.parse(
    readFileSync(
      join(__dirname, "./data/user/tokens-after-delete.json"),
      "utf-8"
    )
  );
  fetchMock.mock(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/me/1/tokens",
    mockResponseBefore,
    { overwriteRoutes: true }
  );
  await fetchTokens();
  const before: TokensApiResponse[] = tokens.get();
  fetchMock.mock(
    `https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/${orgId}/tokens/${idToDelete}`,
    idToDelete,
    { overwriteRoutes: true }
  );
  await deleteToken(idToDelete, orgId);
  fetchMock.mock(
    "https://62ff903e9350a1e548e1952e.mockapi.io/api/me/1/tokens",
    mockResponseAfter,
    { overwriteRoutes: true }
  );
  await fetchTokens();
  const after: TokensApiResponse[] = tokens.get();
  const i = before.findIndex((o) => o.org.id === orgId);
  const x: number = before[i].tokens.length - after[i].tokens.length;
  assert.equal(x, 1); // We have deleted something
  const expected: number = -1;
  const y = after[i].tokens.findIndex((t: Token) => {
    t.id === idToDelete;
  });
  assert.equal(y, expected); // Plan can't be found
});

test("catch error while deleting token", async () => {
  const orgId: string = "fe9637b2-1507-4543-b662-fea252d1ccb5";
  organizationToken.set(orgId);
  const idToDelete = "49804a51-069f-479e-ac8f-70935e14eb94";
  const notificationsBefore: Notification[] = notifications.get();
  fetchMock.mock(
    `https://62ff903e9350a1e548e1952e.mockapi.io/api/organization/${orgId}/tokens/${idToDelete}`,
    500
  );
  await deleteToken(idToDelete, orgId);
  const x: Notification[] = notifications.get();
  assert.equal(x.length, notificationsBefore.length + 1);
  assert.equal(x[x.length - 1].title, "Token couldn't be deleted");
});

// ================= WARNING

// test("unauthorized user is redirected to login", async () => {
//   const expected: string = "/login";
//   fetchMock.mock("https://62ff903e9350a1e548e1952e.mockapi.io/api/me/1/info", 401);
//   await tryLogin(context);
//   // const url = "/login";
//   // Object.defineProperty(window, "location", {
//   //   value: new URL(url),
//   // });
//   // window.location.href = url;
//   const x = window.location.href;
//   console.log(x);
//   assert.equal(x, expected);
// });

test.run();
