/**
 * API client — single chokepoint for every request to the backend.
 *
 * Why this exists:
 *   1. Auth is currently a `?user_id=<uuid>` query param. When the backend
 *      ships JWT auth, we swap one block of code here and every call site
 *      keeps working.
 *   2. Errors get parsed into a single ApiError type instead of leaking
 *      raw fetch responses into UI code.
 *   3. The base URL comes from VITE_API_BASE_URL — flip it to a deployed
 *      origin without touching any other file.
 */

import { ApiError } from "@/types/api";

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "/api";

/** The current dev user's UUID. Set by AuthContext on login/register. */
let currentUserId: string | null = null;

export function setCurrentUserId(id: string | null): void {
  currentUserId = id;
}

export function getCurrentUserId(): string | null {
  return currentUserId;
}

interface RequestOptions {
  /** HTTP method (default: GET). */
  method?: "GET" | "POST" | "PUT" | "DELETE";
  /** JSON body — will be stringified. */
  body?: unknown;
  /** Extra query params to append. user_id is added automatically. */
  query?: Record<string, string | number | undefined>;
  /** Override Content-Type (e.g. for form-urlencoded auth). */
  contentType?: string;
  /** Use raw body instead of JSON.stringify (for form-urlencoded). */
  rawBody?: BodyInit;
  /** Skip auto-attaching user_id (e.g. for POST /user, /token). */
  skipAuth?: boolean;
}

export async function request<T>(
  path: string,
  opts: RequestOptions = {},
): Promise<T> {
  const url = new URL(`${BASE_URL}${path}`, window.location.origin);

  // Attach auth. Today: user_id query param. Tomorrow: Bearer header.
  // To migrate, replace this block with:
  //   if (!opts.skipAuth && token) headers["Authorization"] = `Bearer ${token}`;
  if (!opts.skipAuth && currentUserId) {
    url.searchParams.set("user_id", currentUserId);
  }

  // Additional query params
  if (opts.query) {
    for (const [key, value] of Object.entries(opts.query)) {
      if (value !== undefined && value !== null && value !== "") {
        url.searchParams.set(key, String(value));
      }
    }
  }

  const headers: Record<string, string> = {
    Accept: "application/json",
  };

  let body: BodyInit | undefined;
  if (opts.rawBody !== undefined) {
    body = opts.rawBody;
    if (opts.contentType) headers["Content-Type"] = opts.contentType;
  } else if (opts.body !== undefined) {
    headers["Content-Type"] = opts.contentType ?? "application/json";
    body = JSON.stringify(opts.body);
  }

  const response = await fetch(url.toString(), {
    method: opts.method ?? "GET",
    headers,
    body,
  });

  // Parse body once. Some endpoints return empty bodies (e.g. some DELETEs).
  let parsed: unknown = null;
  const text = await response.text();
  if (text.length > 0) {
    try {
      parsed = JSON.parse(text);
    } catch {
      parsed = text;
    }
  }

  if (!response.ok) {
    throw new ApiError(response.status, response.statusText, parsed);
  }

  return parsed as T;
}
