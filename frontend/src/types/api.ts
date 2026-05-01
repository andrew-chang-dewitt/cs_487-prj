/**
 * API types — mirror the Pydantic models in backend/src/models/* and the
 * SQL schema in database/schema/*.
 *
 * Naming convention:
 *   - <Resource>      = read shape (what GET returns)
 *   - <Resource>In    = create shape (what POST expects)
 *   - <Resource>Changes = patch shape (what PUT expects, all fields optional)
 *
 * Caveats worth knowing:
 *   - The backend's CRUD methods currently raise TodoError (501). Until
 *     they're wired up, real responses for anything beyond "create user"
 *     will not be 200/201. Use the mock API layer in dev (see api/mock.ts).
 *   - `amount` arrives as a string, not a number — Postgres NUMERIC types
 *     serialize as strings to preserve decimal precision. Convert with
 *     parseFloat() only at display time; never store as a number.
 *   - `timestamp` is ISO-8601 with timezone (TIMESTAMPTZ). new Date(ts)
 *     parses it correctly.
 */

// ─── User ─────────────────────────────────────────────────────────────────

export interface User {
  id: string;
  handle: string;
  full_name: string;
  preferred_name: string;
}

export interface UserIn {
  handle: string;
  password: string;
  full_name: string;
  preferred_name: string; // required by Pydantic UserBase, despite nullable column
}

export interface UserChanges {
  handle?: string;
  full_name?: string;
  preferred_name?: string;
}

// ─── Account ──────────────────────────────────────────────────────────────

export interface Account {
  id: string;
  user_id: string;
  name: string;
  closed: boolean;
}

export interface AccountIn {
  name: string;
  closed?: boolean; // defaults to false on the backend
}

export interface AccountChanges {
  name?: string;
  closed?: boolean;
}

// ─── Transaction ──────────────────────────────────────────────────────────

export interface Transaction {
  id: string;
  account_id: string;
  amount: string;             // numeric — string in JSON
  description: string | null;
  payee: string;
  timestamp: string;          // ISO-8601 with timezone
  spent_from: string | null;  // category id, nullable
}

export interface TransactionIn {
  account_id: string;
  amount: number | string;
  payee: string;
  timestamp: string;
  description?: string;
  spent_from?: string;
}

export interface TransactionChanges {
  account_id?: string;
  amount?: number | string;
  payee?: string;
  timestamp?: string;
  description?: string;
  spent_from?: string;
}

// ─── Auth ─────────────────────────────────────────────────────────────────

export interface Token {
  access_token: string;
  token_type: "bearer";
}

// ─── API errors ───────────────────────────────────────────────────────────

/** FastAPI validation error shape — what 422 responses look like. */
export interface ValidationError {
  detail: Array<{
    loc: (string | number)[];
    msg: string;
    type: string;
  }>;
}

/** Generic API error wrapper used by the client. */
export class ApiError extends Error {
  constructor(
    public status: number,
    public statusText: string,
    public body: unknown,
  ) {
    super(`${status} ${statusText}`);
    this.name = "ApiError";
  }
}
