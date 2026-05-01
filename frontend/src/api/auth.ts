/**
 * Authentication endpoints.
 *
 * Today: there's no live /token endpoint. "Login" against the real backend
 * means POST /user (creating a new user) or accepting a user_id directly.
 * Once /token is wired up, swap the realApi.login implementation for the
 * OAuth2 form-urlencoded call shown in the comment block.
 */

import { request } from "./client";
import { mockApi, USE_MOCK_API } from "./mock";
import type { User, UserIn } from "@/types/api";

export const authApi = {
  async register(input: UserIn): Promise<User> {
    if (USE_MOCK_API) return mockApi.createUser(input);
    return request<User>("/user", {
      method: "POST",
      body: input,
      skipAuth: true,
    });
  },

  /**
   * Log in with handle + password.
   *
   * MOCK: validates against in-memory store, returns the User.
   * REAL: currently throws — the /token endpoint isn't registered yet.
   *
   * When /token lands, replace the real branch with:
   *
   *   const form = new URLSearchParams();
   *   form.set("username", handle);
   *   form.set("password", password);
   *   const token = await request<Token>("/token", {
   *     method: "POST",
   *     rawBody: form,
   *     contentType: "application/x-www-form-urlencoded",
   *     skipAuth: true,
   *   });
   *   // decode token.access_token to extract user_id, then fetch /user
   */
  async login(handle: string, password: string): Promise<User> {
    if (USE_MOCK_API) return mockApi.authenticate(handle, password);
    throw new Error(
      "Real /token endpoint is not yet implemented on the backend. " +
        "Set VITE_USE_MOCK_API=true to develop against mock data.",
    );
  },
};
