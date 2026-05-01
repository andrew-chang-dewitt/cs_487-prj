import { getCurrentUserId, request } from "./client";
import { mockApi, USE_MOCK_API } from "./mock";
import type { Account, AccountChanges, AccountIn } from "@/types/api";

function requireUserId(): string {
  const id = getCurrentUserId();
  if (!id) throw new Error("Not authenticated");
  return id;
}

export const accountsApi = {
  async list(includeClosed = false): Promise<Account[]> {
    if (USE_MOCK_API) return mockApi.listAccounts(requireUserId(), includeClosed);
    return request<Account[]>(includeClosed ? "/account/closed" : "/account");
  },

  async create(input: AccountIn): Promise<Account> {
    if (USE_MOCK_API) return mockApi.createAccount(requireUserId(), input);
    return request<Account>("/account", { method: "POST", body: input });
  },

  async update(accountId: string, changes: AccountChanges): Promise<Account> {
    if (USE_MOCK_API) return mockApi.updateAccount(accountId, changes);
    return request<Account>(`/account/${accountId}`, {
      method: "PUT",
      body: changes,
    });
  },

  async close(accountId: string): Promise<Account> {
    if (USE_MOCK_API) return mockApi.updateAccount(accountId, { closed: true });
    return request<Account>(`/account/${accountId}/closed`, { method: "PUT" });
  },
};
