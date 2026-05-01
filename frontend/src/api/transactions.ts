import { getCurrentUserId, request } from "./client";
import { mockApi, USE_MOCK_API } from "./mock";
import type {
  Transaction,
  TransactionChanges,
  TransactionIn,
} from "@/types/api";

function requireUserId(): string {
  const id = getCurrentUserId();
  if (!id) throw new Error("Not authenticated");
  return id;
}

export interface TransactionFilters {
  account_id?: string;
  payee?: string;
  minimum_amount?: number;
  maximum_amount?: number;
  after?: string;
  before?: string;
  limit?: number;
  page?: number;
  sort?: string;
}

export const transactionsApi = {
  async list(filters: TransactionFilters = {}): Promise<Transaction[]> {
    if (USE_MOCK_API) return mockApi.listTransactions(requireUserId(), filters);
    return request<Transaction[]>("/transaction", { query: filters as Record<string, string | number | undefined> });
  },

  async create(input: TransactionIn): Promise<Transaction> {
    if (USE_MOCK_API) return mockApi.createTransaction(input);
    return request<Transaction>("/transaction", { method: "POST", body: input });
  },

  async update(
    transactionId: string,
    changes: TransactionChanges,
  ): Promise<Transaction> {
    if (USE_MOCK_API) return mockApi.updateTransaction(transactionId, changes);
    return request<Transaction>(`/transaction/${transactionId}`, {
      method: "PUT",
      body: changes,
    });
  },

  async remove(transactionId: string): Promise<Transaction> {
    if (USE_MOCK_API) return mockApi.deleteTransaction(transactionId);
    return request<Transaction>(`/transaction/${transactionId}`, {
      method: "DELETE",
    });
  },
};
