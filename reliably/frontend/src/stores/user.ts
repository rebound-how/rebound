
// Do not remove the (empty) line above it helps with code coverage in c8
import { atom, map, task } from "nanostores";
// Since we need to use "localStorage", we need nanostores persistent
import { persistentAtom } from "@nanostores/persistent";
import type { 
  User,
  UserApiJson,
  UserProfile,
  Token,
  TokensApiResponse,
  LoginInfo,
  LoginApiResponse,
  LoginAppResponse,
} from "@/types/user";
import type { Notification } from "@/types/ui-types";
import { increaseLoaderCounter, decreaseLoaderCounter } from "../stores/loader";
import { addNotification } from "./notifications";

/* c8 ignore start */
const baseApiUrl: string = import.meta.env === undefined
  ? "https://62ff903e9350a1e548e1952e.mockapi.io/api"
  : import.meta.env.PUBLIC_API_URL;
const useMockApi = 
  baseApiUrl === "https://62ff903e9350a1e548e1952e.mockapi.io/api";

const profileEndpoint: string = useMockApi
  ? "1/info/1"
  : "info";

const tokensEndpoint: string = useMockApi
  ? "1/tokens"
  : "tokens";
/* c8 ignore stop */

export const isLoggedIn = atom<boolean>(false);
export const organizationToken = persistentAtom<string>("reliably:context", "");
export const organizationName = atom<string>("");
export const user = persistentAtom<User>(
  "reliably:user",
  {
    profile: {
      email: "",
      username: "",
      id: "",
      picture: "",
    },
    orgs: [],
  },
  {
    encode: JSON.stringify,
    decode: JSON.parse,
  }
);

export function mutateIsLoggedIn(loggedIn: boolean) {
    isLoggedIn.set(loggedIn);
    return isLoggedIn.get();
};

export function mutateContext(newContext: string) {
    organizationToken.set(newContext);
    return organizationToken.get();
};

export async function updateOrganizationName(data: string) {
  organizationName.set(data);
  return organizationName.get();
};

export async function setOrganizationName() {
  let u = user.get();
  await u.orgs.forEach((o) => {
    if (o.id === organizationToken.get()) {
      updateOrganizationName(o.name);
    }
  });
}

export async function updateUserEmail(newEmail: string) {
    // TODO update in backend
    const currentUser: User = user.get();
    currentUser.profile.email = newEmail;
    user.set(currentUser);
};

export const loginWithEmail = async (loginInfo: LoginInfo, join: boolean, hash: string): Promise<LoginAppResponse> => {
  let url = `/login/with/email`;
  if (join) {
    url = `${url}?join=${hash}`
  }
  let response: Response | null = null;
  try {
    response = await fetch(url,
      { method: "POST",
      headers: {
        Accept: "application/json, text/plain, */*",
        "Content-Type": "application/json",
      },
      body: JSON.stringify(loginInfo),
    });
    if (!response.ok) {
      throw new Error(response.statusText);
    } else {
      const apiResponse: LoginApiResponse = await response.json();
      return {
        status: response.status,
        message: "",
        api_response: apiResponse,
      }
    }
  } catch (e) {
    let messageBase: string = loginInfo.register
      ? "Registration failed"
      : "Login failed";
    let appResponse: LoginAppResponse = {
      status: response === null ? 520 : response.status,
      message: `${messageBase}: ${(e as Error).message}`,
    }
    return appResponse;
  }
}

export const tryLogin = async (context: string) => {
  user.set({
    profile: {
      username: "",
      email: "",
      id: "",
      picture: "",
    },
    orgs: [],
  });
  await task(async () => {
    try {
      const response = await fetch(`${baseApiUrl}/me/${profileEndpoint}`);
      if (!response.ok) {
        /* c8 ignore start */
        if (response.status === 401) {
          window.location.replace("/login/");
        } else {
          /* c8 ignore stop */
          throw new Error(response.statusText);
        }
      }

      const userJson: UserApiJson = await response.json();
      organizationToken.set(context);
      let p: UserProfile = {
        id: userJson.profile.id,
        username: userJson.profile.username,
        email: userJson.profile.email,
        picture: userJson.profile.openid_profile.picture,
      };
      let u: User = {
        profile: p,
        orgs: userJson.orgs
      };
      user.set(u);
      mutateIsLoggedIn(true);
    } catch (e) {
      const n: Notification = {
        title: "We couldn't log you in",
        message: (e as Error).message,
        type: "error",
      }
      addNotification(n);
    }
  });
};

export const updateUserInfo = async () => {
  await task(async () => {
    try {
      const response = await fetch(`${baseApiUrl}/me/${profileEndpoint}`);
      if (!response.ok) {
        /* c8 ignore start */
        if (response.status === 401) {
          window.location.replace("/login/");
        } else {
          /* c8 ignore stop */
          throw new Error(response.statusText);
        }
      }

      const userJson: UserApiJson = await response.json();
      organizationToken.set(userJson.orgs[0].id);
      let p: UserProfile = {
        id: userJson.profile.id,
        username: userJson.profile.username,
        email: userJson.profile.email,
        picture: userJson.profile.openid_profile.picture,
      };
      let u: User = {
        profile: p,
        orgs: userJson.orgs
      };
      user.set(u);
      mutateIsLoggedIn(true);
    } catch (e) {
      const n: Notification = {
        title: "We couldn't log you in",
        message: (e as Error).message,
        type: "error",
      }
      addNotification(n);
    }
  });
}

export const tryLogout = async () => {
  await task(async () => {
    // clear the organizationToken and user
    organizationToken.set("");
    user.set({
      profile: {
        username: "",
        email: "",
        id: "",
        picture: "",
      },
      orgs: [],
    });
    // set the state of isLoggedIn to false
    mutateIsLoggedIn(false);
  });
};

export const changeOrganization = async (id: string) => {
  mutateContext(id);
}

/********************************
 *          TOKENS              *
 ********************************/

export const tokens = map<TokensApiResponse[]>([]);

export async function updateTokens(data: TokensApiResponse[]) {
  tokens.set(data);
  return tokens.get();
};

export const fetchTokens = async () => {
  increaseLoaderCounter();
  const url = `${baseApiUrl}/me/${tokensEndpoint}`;
  try {
    const response = await fetch(url);
    const data: TokensApiResponse[] = await response.json();
    updateTokens(data);
  } catch (e) {
    const n: Notification = {
      title: "Tokens couldn't be fetched",
      message: (e as Error).message,
      type: "error",
    }
    addNotification(n);
  } finally {
    decreaseLoaderCounter();
  }
};

export const token = atom<Token>({
  id: "",
  name: "",
  created_date: "",
  token: "",
});

export async function updateToken(data: Token) {
  token.set(data);
  return token.get();
};

export const fetchToken = async (tokenId: string) => {
  increaseLoaderCounter();
  const url = `${baseApiUrl}/organization/${organizationToken.get()}/tokens/${tokenId}`;
  try {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(response.statusText);
    }
    const data: Token = await response.json();
    updateToken(data);
  } catch (e) {
    const n: Notification = {
      title: "Token couldn't be fetched",
      message: (e as Error).message,
      type: "error",
    }
    addNotification(n);
  } finally {
    decreaseLoaderCounter();
  }
};

export const createToken = async (tokenName: string): Promise<void | Token> => {
  increaseLoaderCounter();
  const url = `${baseApiUrl}/organization/${organizationToken.get()}/tokens`;
  try {
    const response = await fetch(url, {
      method: "POST",
      headers: {
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({name: tokenName}),
    });
    if (!response.ok) {
      throw new Error(response.statusText);
    }
    const newToken: Token = await response.json();
    return newToken;
  } catch (e) {
    // TODO: handle special error cases
    // Error 409: a token with this name already exists
    const n: Notification = {
      title: "Token couldn't be created",
      message: (e as Error).message,
      type: "error",
    }
    addNotification(n);
  } finally {
    decreaseLoaderCounter();
  }
}

export const deleteToken = async (id: string, orgId: string) => {
  increaseLoaderCounter();
  const url = `${baseApiUrl}/organization/${orgId}/tokens/${id}`;
  try {
    const response = await fetch(url, { method: "DELETE" });
    if (!response.ok) {
      throw new Error(response.statusText);
    }
  } catch (e) {
    const n: Notification = {
      title: "Token couldn't be deleted",
      message: (e as Error).message,
      type: "error",
    }
    addNotification(n);
  } finally {
    decreaseLoaderCounter();
  }
};