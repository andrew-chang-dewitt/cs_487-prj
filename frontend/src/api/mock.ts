/**
 * Mock API — in-memory implementation of the backend contract.
 *
 * Toggle on with VITE_USE_MOCK_API=true. Used heavily in early development
 * because the real backend's CRUD methods raise TodoError until they're
 * implemented. Lets us build, demo, and iterate on the UI without waiting.
 *
 * Data shape exactly matches types/api.ts. If you change the schema, mirror
 * the change here so both code paths stay equivalent.
 */

import type {
  Account,
  AccountChanges,
  AccountIn,
  Transaction,
  TransactionChanges,
  TransactionIn,
  User,
  UserIn,
} from "@/types/api";

const STORAGE_KEY = "ledger.mock-state.v1";

interface MockState {
  users: User[];
  passwords: Record<string, string>; // user_id -> password
  accounts: Account[];
  transactions: Transaction[];
}

function uuid(): string {
  // Crypto API for real-looking UUIDs in dev. randomUUID is widely supported.
  return crypto.randomUUID();
}

function loadState(): MockState {
  const raw = localStorage.getItem(STORAGE_KEY);
  if (raw) {
    try {
      return JSON.parse(raw) as MockState;
    } catch {
      // fall through to seed
    }
  }
  return seed();
}

function saveState(s: MockState): void {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(s));
}

function seed(): MockState {
  const userId = uuid();
  const checkingId = uuid();
  const savingsId = uuid();
  const cashId = uuid();

  const now = Date.now();
  const day = 24 * 60 * 60 * 1000;
  const iso = (offsetDays: number): string =>
    new Date(now - offsetDays * day).toISOString();

  const transactions: Transaction[] = [
    { id: uuid(), account_id: checkingId, amount: "2850.00", description: "biweekly paycheck", payee: "Acme Corp Payroll", timestamp: iso(2), spent_from: null },
    { id: uuid(), account_id: checkingId, amount: "-1450.00", description: "rent — april", payee: "Maple Property Mgmt", timestamp: iso(3), spent_from: null },
    { id: uuid(), account_id: checkingId, amount: "-67.43", description: null, payee: "Green Mart Grocery", timestamp: iso(4), spent_from: null },
    { id: uuid(), account_id: checkingId, amount: "-12.00", description: "monthly subscription", payee: "Spotify", timestamp: iso(5), spent_from: null },
    { id: uuid(), account_id: checkingId, amount: "-4.85", description: "morning latte", payee: "Cafe Otto", timestamp: iso(6), spent_from: null },
    { id: uuid(), account_id: checkingId, amount: "-89.20", description: null, payee: "Shell Gas", timestamp: iso(7), spent_from: null },
    { id: uuid(), account_id: cashId, amount: "-22.00", description: "dinner with mark", payee: "The Standard Diner", timestamp: iso(8), spent_from: null },
    { id: uuid(), account_id: savingsId, amount: "500.00", description: "monthly transfer", payee: "Self — savings auto", timestamp: iso(10), spent_from: null },
    { id: uuid(), account_id: checkingId, amount: "-32.50", description: null, payee: "Pharmacy on Main", timestamp: iso(11), spent_from: null },
    { id: uuid(), account_id: checkingId, amount: "-145.00", description: "annual fee", payee: "ChiTech Membership", timestamp: iso(13), spent_from: null },
    { id: uuid(), account_id: checkingId, amount: "-58.40", description: null, payee: "Green Mart Grocery", timestamp: iso(14), spent_from: null },
    { id: uuid(), account_id: cashId, amount: "-15.00", description: "tip", payee: "Cash withdrawal", timestamp: iso(16), spent_from: null },
    { id: uuid(), account_id: checkingId, amount: "2850.00", description: "biweekly paycheck", payee: "Acme Corp Payroll", timestamp: iso(16), spent_from: null },
  ];

  return {
    users: [
      {
        id: userId,
        handle: "demo",
        full_name: "Demo User",
        preferred_name: "Demo",
      },
    ],
    passwords: { [userId]: "demo" },
    accounts: [
      { id: checkingId, user_id: userId, name: "Primary Checking", closed: false },
      { id: savingsId, user_id: userId, name: "High-Yield Savings", closed: false },
      { id: cashId, user_id: userId, name: "Pocket Cash", closed: false },
    ],
    transactions,
  };
}

// Simulate network latency so loading states are exercised in dev.
function delay<T>(value: T, ms = 150): Promise<T> {
  return new Promise((resolve) => setTimeout(() => resolve(value), ms));
}

export const mockApi = {
  // ── User ──
  async createUser(input: UserIn): Promise<User> {
    const state = loadState();
    if (state.users.some((u) => u.handle === input.handle)) {
      const err = new Error(`User with handle ${input.handle} already exists.`);
      (err as Error & { status?: number }).status = 409;
      throw err;
    }
    const user: User = {
      id: uuid(),
      handle: input.handle,
      full_name: input.full_name,
      preferred_name: input.preferred_name,
    };
    state.users.push(user);
    state.passwords[user.id] = input.password;
    saveState(state);
    return delay(user);
  },

  async authenticate(handle: string, password: string): Promise<User> {
    const state = loadState();
    const user = state.users.find((u) => u.handle === handle);
    if (!user || state.passwords[user.id] !== password) {
      const err = new Error("Invalid handle or password");
      (err as Error & { status?: number }).status = 401;
      throw err;
    }
    return delay(user);
  },

  async getUser(userId: string): Promise<User> {
    const state = loadState();
    const user = state.users.find((u) => u.id === userId);
    if (!user) throw new Error("User not found");
    return delay(user);
  },

  // ── Account ──
  async listAccounts(userId: string, includeClosed = false): Promise<Account[]> {
    const state = loadState();
    const accounts = state.accounts.filter(
      (a) => a.user_id === userId && (includeClosed ? a.closed : !a.closed),
    );
    return delay(accounts);
  },

  async createAccount(userId: string, input: AccountIn): Promise<Account> {
    const state = loadState();
    const account: Account = {
      id: uuid(),
      user_id: userId,
      name: input.name,
      closed: input.closed ?? false,
    };
    state.accounts.push(account);
    saveState(state);
    return delay(account);
  },

  async updateAccount(accountId: string, changes: AccountChanges): Promise<Account> {
    const state = loadState();
    const idx = state.accounts.findIndex((a) => a.id === accountId);
    if (idx === -1) throw new Error("Account not found");
    state.accounts[idx] = { ...state.accounts[idx], ...changes };
    saveState(state);
    return delay(state.accounts[idx]);
  },

  // ── Transaction ──
  async listTransactions(
    userId: string,
    filters: { account_id?: string; limit?: number; page?: number } = {},
  ): Promise<Transaction[]> {
    const state = loadState();
    const userAccountIds = new Set(
      state.accounts.filter((a) => a.user_id === userId).map((a) => a.id),
    );
    let txs = state.transactions.filter((t) => userAccountIds.has(t.account_id));
    if (filters.account_id) {
      txs = txs.filter((t) => t.account_id === filters.account_id);
    }
    txs = [...txs].sort(
      (a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime(),
    );
    const limit = filters.limit ?? 50;
    const page = filters.page ?? 0;
    return delay(txs.slice(page * limit, (page + 1) * limit));
  },

  async createTransaction(input: TransactionIn): Promise<Transaction> {
    const state = loadState();
    const tx: Transaction = {
      id: uuid(),
      account_id: input.account_id,
      amount: typeof input.amount === "number" ? input.amount.toFixed(2) : input.amount,
      description: input.description ?? null,
      payee: input.payee,
      timestamp: input.timestamp,
      spent_from: input.spent_from ?? null,
    };
    state.transactions.push(tx);
    saveState(state);
    return delay(tx);
  },

  async updateTransaction(
    transactionId: string,
    changes: TransactionChanges,
  ): Promise<Transaction> {
    const state = loadState();
    const idx = state.transactions.findIndex((t) => t.id === transactionId);
    if (idx === -1) throw new Error("Transaction not found");
    const next = { ...state.transactions[idx] };
    if (changes.account_id !== undefined) next.account_id = changes.account_id;
    if (changes.amount !== undefined) {
      next.amount =
        typeof changes.amount === "number" ? changes.amount.toFixed(2) : changes.amount;
    }
    if (changes.description !== undefined) next.description = changes.description ?? null;
    if (changes.payee !== undefined) next.payee = changes.payee;
    if (changes.timestamp !== undefined) next.timestamp = changes.timestamp;
    if (changes.spent_from !== undefined) next.spent_from = changes.spent_from ?? null;
    state.transactions[idx] = next;
    saveState(state);
    return delay(next);
  },

  async deleteTransaction(transactionId: string): Promise<Transaction> {
    const state = loadState();
    const idx = state.transactions.findIndex((t) => t.id === transactionId);
    if (idx === -1) throw new Error("Transaction not found");
    const [removed] = state.transactions.splice(idx, 1);
    saveState(state);
    return delay(removed);
  },

  // ── Balance ──
  async accountBalance(accountId: string): Promise<string> {
    const state = loadState();
    const sum = state.transactions
      .filter((t) => t.account_id === accountId)
      .reduce((acc, t) => acc + parseFloat(t.amount), 0);
    return delay(sum.toFixed(2));
  },

  async totalBalance(userId: string): Promise<string> {
    const state = loadState();
    const accountIds = new Set(
      state.accounts
        .filter((a) => a.user_id === userId && !a.closed)
        .map((a) => a.id),
    );
    const sum = state.transactions
      .filter((t) => accountIds.has(t.account_id))
      .reduce((acc, t) => acc + parseFloat(t.amount), 0);
    return delay(sum.toFixed(2));
  },

  // Reset everything — useful during development
  __reset(): void {
    localStorage.removeItem(STORAGE_KEY);
  },
};

export const USE_MOCK_API = import.meta.env.VITE_USE_MOCK_API === "true";
