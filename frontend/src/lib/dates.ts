/**
 * Date helpers — backend timestamps are ISO-8601 with timezone (TIMESTAMPTZ).
 * new Date() parses them correctly; these wrappers handle display formatting.
 */

/** "Apr 28" — short, ledger-style. */
export function formatDateShort(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleDateString("en-US", { month: "short", day: "numeric" });
}

/** "April 28, 2026" — long, formal. */
export function formatDateLong(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}

/** "Apr 28 · 2:30 PM" — when time matters. */
export function formatDateTime(iso: string): string {
  const d = new Date(iso);
  return `${formatDateShort(iso)} · ${d.toLocaleTimeString("en-US", {
    hour: "numeric",
    minute: "2-digit",
  })}`;
}

/** Returns ISO-8601 string for the current moment, ready for the API. */
export function nowIso(): string {
  return new Date().toISOString();
}

/** Convert a datetime-local form value to ISO-8601 with timezone. */
export function localInputToIso(localValue: string): string {
  // datetime-local gives "2026-04-30T14:30" without timezone
  return new Date(localValue).toISOString();
}

/** Convert an ISO-8601 string to a value usable in <input type="datetime-local">. */
export function isoToLocalInput(iso: string): string {
  const d = new Date(iso);
  // Adjust for timezone offset so the local clock value matches what's in the DB
  const offset = d.getTimezoneOffset() * 60000;
  return new Date(d.getTime() - offset).toISOString().slice(0, 16);
}
