/**
 * Format an amount string (as returned by the API) for display.
 *
 * Important: the API sends amounts as strings, not numbers, to preserve
 * decimal precision (Postgres NUMERIC). Convert with parseFloat at the
 * boundary; never store as a number in app state.
 */

export function formatCurrency(amount: string | number, options: { showSign?: boolean } = {}): string {
  const n = typeof amount === "string" ? parseFloat(amount) : amount;
  if (Number.isNaN(n)) return "—";

  const formatter = new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });

  const formatted = formatter.format(Math.abs(n));

  if (options.showSign) {
    if (n > 0) return `+${formatted}`;
    if (n < 0) return `−${formatted}`;
  }
  return n < 0 ? `−${formatted}` : formatted;
}

/** Returns "credit" for positive amounts, "debit" for negative, "zero" for 0. */
export function amountKind(amount: string | number): "credit" | "debit" | "zero" {
  const n = typeof amount === "string" ? parseFloat(amount) : amount;
  if (n > 0) return "credit";
  if (n < 0) return "debit";
  return "zero";
}
