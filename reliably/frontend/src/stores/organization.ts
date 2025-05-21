
// Do not remove the (empty) line above it helps with code coverage in c8
import { atom, map } from "nanostores";
import type {
  OrganizationUser,
  OrganizationUsersPayload,
  OrganizationUsers,
  OrganizationUsersPage,
  InvitationLinkPayload,
  InvitationLink,
} from "@/types/organization";
import type { Notification } from "@/types/ui-types";
import { handleError403 } from "../utils/user";
import { useStore } from "@nanostores/vue";
import { organizationToken } from "./user";
import { increaseLoaderCounter, decreaseLoaderCounter } from "./loader";
import { addNotification } from "./notifications";

/* c8 ignore start */
const baseApiUrl: string =
  import.meta.env === undefined
    ? "https://62ff903e9350a1e548e1952e.mockapi.io/api"
    : import.meta.env.PUBLIC_API_URL;

const useMockApi =
  baseApiUrl === "https://62ff903e9350a1e548e1952e.mockapi.io/api";

const apiUrlPrefix: string = useMockApi ? "&limit=10" : "";
/* c8 ignore stop */

const context = useStore(organizationToken);

export const users = map<OrganizationUsersPage>({
  page: 0,
  users: [],
  total: 0,
  state: "empty",
});

export async function updateUsers(data: OrganizationUsersPage) {
  users.set(data);
  return users.get();
};

export const fetchUsers = async (page: number) => {
  increaseLoaderCounter();
  const url = `${baseApiUrl}/organization/${context.value}/users?page=${page}${apiUrlPrefix}`;
  try {
    const response = await fetch(url);
    if (response.status === 403) {
      handleError403(context.value);
    } else if (!response.ok) {
      throw new Error(response.statusText);
    } else {
      const e: OrganizationUsersPayload = await response.json();
      let data: OrganizationUsersPage = {
        page: page,
        users: e.items,
        total: e.count,
        state: "ready",
      };
      updateUsers(data);
    }
  } catch (e) {
    const n: Notification = {
      title: "Users couldn't be fetched",
      message: (e as Error).message,
      type: "error",
    };
    addNotification(n);
    users.setKey("state", "error");
  } finally {
    decreaseLoaderCounter();
  }
};

export const removeUser = async (id: string, username: string) => {
  increaseLoaderCounter();
  const url = `${baseApiUrl}/organization/${context.value}/users/${id}`;
  try {
    const response = await fetch(url, { method: "DELETE" });
    if (response.status === 403) {
      handleError403(context.value);
    } else if (!response.ok) {
      throw new Error(response.statusText);
    } else {
      const n: Notification = {
        title: "User was successfully removed",
        message: `${username} is not a member of your organization anymore.`,
        type: "success",
      };
      addNotification(n);
    }
  } catch (e) {
    const n: Notification = {
      title: "User couldn't be removed",
      message: (e as Error).message,
      type: "error",
    };
    addNotification(n);
  } finally {
    decreaseLoaderCounter();
  }
};

export const invitationLink = atom<InvitationLink>({
  link: null,
  state: "empty",
});

export async function updateInvitationLink(data: InvitationLink) {
  invitationLink.set(data);
  return invitationLink.get();
};

export const getInvitationLink = async () => {
  increaseLoaderCounter();
  const url = `${baseApiUrl}/organization/${context.value}/invite`;
  try {
    const response = await fetch(url);
    if (response.status === 403) {
      handleError403(context.value);
    } else if (response.status === 429) {
      let data: InvitationLink = {
        link: "Organizations on a Free plan can't invite additional team members",
        state: "ready",
      };
      updateInvitationLink(data);
    } else if (!response.ok) {
      throw new Error(response.statusText);
    } else {
      const link: InvitationLinkPayload = await response.json();
      if (link.link !== null) {
        const scheme = window.location.protocol;
        const loc =  window.location.host;
        let data: InvitationLink = {
          link: `${scheme}//${loc}/join/?invite=${link.link}`,
          state: "ready",
        };
        updateInvitationLink(data);
      } else {
        generateInvitationLink();
      }
    }
  } catch (e) {
    const n: Notification = {
      title: "Invitation link couldn't be fetched",
      message: (e as Error).message,
      type: "error",
    };
    addNotification(n);
    users.setKey("state", "error");
  } finally {
    decreaseLoaderCounter();
  }
};

export const generateInvitationLink = async () => {
  increaseLoaderCounter();
  const url = `${baseApiUrl}/organization/${context.value}/invite/generate`;
  try {
    const response = await fetch(url);
    if (response.status === 403) {
      handleError403(context.value);
    } else if (response.status === 429) {
      let data: InvitationLink = {
        link: "Organizations on a Free plan can't invite additional team members",
        state: "ready",
      };
      updateInvitationLink(data);
    } else if (!response.ok) {
      throw new Error(response.statusText);
    } else {
      const link: InvitationLinkPayload = await response.json();
      const scheme = window.location.protocol;
      const loc =  window.location.host;
      let data: InvitationLink = {
        link: `${scheme}//${loc}/join/?invite=${link.link}`,
        state: "ready",
      };
      updateInvitationLink(data);
    }
  } catch (e) {
    const n: Notification = {
      title: "Invitation link couldn't be created",
      message: (e as Error).message,
      type: "error",
    };
    addNotification(n);
    users.setKey("state", "error");
  } finally {
    decreaseLoaderCounter();
  }
};
