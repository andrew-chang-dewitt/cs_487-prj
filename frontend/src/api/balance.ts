import { getCurrentUserId, request } from "./client";
import { mockApi, USE_MOCK_API } from "./mock";

function requireUserId(): string {
  const id = getCurrentUserId();
  if (!id) throw new Error("Not authenticated");
  return id;
}

export const balanceApi = {
  /** Sum of all transactions across the user's open accounts. */
  async total(): Promise<string> {
    if (USE_MOCK_API) return mockApi.totalBalance(requireUserId());
    const res = await request<{ amount: string }>("/balance/total");
    return res.amount;
  },

  /** Sum of transactions for a single account. */
  async forAccount(accountId: string): Promise<string> {
    if (USE_MOCK_API) return mockApi.accountBalance(accountId);
    const res = await request<{ amount: string }>(`/balance/account/${accountId}`);
    return res.amount;
  },
};
