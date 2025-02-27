export interface OrganizationUser {
  username: string;
  email: string | null;
  id: string;
  created_date: string;
}

export interface OrganizationUsersPayload {
  count: number;
  items: OrganizationUser[];
}

export interface OrganizationUsersPage {
  page: number;
  users: OrganizationUser[];
  total: number;
  state: string;
}

export interface OrganizationUsers {
  users: OrganizationUser[];
  state: string;
}

export interface InvitationLinkPayload {
  link: string | null;
}

export interface InvitationLink {
  link: string | null;
  state: string;
}
