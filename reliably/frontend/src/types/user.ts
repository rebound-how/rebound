export interface User {
  profile: UserProfile;
  orgs: Organization[];
}

export interface UserApiJson {
  profile: UserApiProfile;
  orgs: Organization[];
}

export type UserApiProfile = {
  email: string;
  username: string;
  openid_profile: OpenIdProfile;
  id: string;
};

export type OpenIdProfile = {
  sub: string;
  name: string;
  email: string;
  picture: string;
  profile: string;
  website: string;
  preferred_username: string;
};

export type UserProfile = {
  email: string;
  username: string;
  picture: string;
  id: string;
};

export interface Organization {
  id: string;
  name: string;
  created_date: Date | string;
}

export interface Token {
  id: string;
  name: string;
  created_date: Date | string;
  token?: string;
}

export interface TokensApiResponse {
  org: Organization;
  tokens: Token[];
}

export interface LoginInfo {
  email: string;
  password: string;
  register: boolean;
}

export interface LoginApiResponse {
  context?: string;
  redirect_to?: string;
  org?: string;
  org_id?: string;
  join?: string;
  plan?: string;
  message?: string;
}

// export interface LoginApiResponseRegister {
//   redirect_to?: string;
//   org?: string;
//   org_id?: string;
//   join?: string;
//   plan?: string;
//   message?: string;
//   status: number;
// }

// export interface LoginApiResponseLogin {
//   context: string;
// }

export interface LoginAppResponse {
  status: number;
  message: string;
  api_response?: LoginApiResponse;
}
