import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { transactionsApi } from "@/api/transactions";
import { accountsApi } from "@/api/accounts";
import { localInputToIso, isoToLocalInput, nowIso } from "@/lib/dates";
import { ApiError } from "@/types/api";

type EntryKind = "expense" | "income";

export function NewTransactionPage() {
  const navigate = useNavigate();
  const qc = useQueryClient();

  const accounts = useQuery({
    queryKey: ["accounts"],
    queryFn: () => accountsApi.list(),
  });

  // Form state
  const [accountId, setAccountId] = useState("");
  const [kind, setKind] = useState<EntryKind>("expense");
  const [amountInput, setAmountInput] = useState("");
  const [payee, setPayee] = useState("");
  const [description, setDescription] = useState("");
  const [timestampLocal, setTimestampLocal] = useState(isoToLocalInput(nowIso()));
  const [error, setError] = useState<string | null>(null);

  // Default to first account once loaded
  useEffect(() => {
    if (accounts.data && accounts.data.length > 0 && !accountId) {
      setAccountId(accounts.data[0].id);
    }
  }, [accounts.data, accountId]);

  const createMutation = useMutation({
    mutationFn: () => {
      const numericAmount = parseFloat(amountInput);
      if (Number.isNaN(numericAmount)) {
        throw new Error("Please enter a valid amount.");
      }
      // Apply sign based on selected kind
      const signed = kind === "expense" ? -Math.abs(numericAmount) : Math.abs(numericAmount);

      return transactionsApi.create({
        account_id: accountId,
        amount: signed.toFixed(2),
        payee: payee.trim(),
        timestamp: localInputToIso(timestampLocal),
        description: description.trim() || undefined,
      });
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["transactions"] });
      qc.invalidateQueries({ queryKey: ["balance"] });
      navigate("/transactions");
    },
    onError: (err) => {
      if (err instanceof ApiError) {
        setError(`${err.status}: ${JSON.stringify(err.body)}`);
      } else {
        setError(err instanceof Error ? err.message : "Couldn't save transaction");
      }
    },
  });

  function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    if (!accountId) return setError("Select an account first.");
    if (!payee.trim()) return setError("Payee is required.");
    if (!amountInput.trim()) return setError("Amount is required.");
    createMutation.mutate();
  }

  // No accounts yet — block the form, send to accounts page
  if (accounts.isSuccess && accounts.data.length === 0) {
    return (
      <div className="py-24 text-center max-w-md mx-auto">
        <div className="eyebrow mb-2">Hold up</div>
        <h1 className="font-display text-4xl mb-4 tracking-tightest">
          You need an account first.
        </h1>
        <p className="text-sm text-ink-400 mb-8 leading-relaxed">
          Transactions belong to accounts. Create your first one — checking,
          savings, cash, whatever — and then come back to record activity.
        </p>
        <Link to="/accounts" className="btn-primary">
          Set up an account
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-2xl">
      <header className="pb-8 mb-12 rule-double">
        <Link
          to="/transactions"
          className="text-xs text-ink-400 hover:text-ink-900 transition-colors"
        >
          ← Back to transactions
        </Link>
        <div className="eyebrow mt-4 mb-2">New entry</div>
        <h1 className="font-display text-5xl tracking-tightest">
          Record a transaction
        </h1>
      </header>

      <form onSubmit={onSubmit} className="space-y-10">
        {/* Kind toggle — expense or income */}
        <div>
          <label className="field-label mb-3">Type</label>
          <div className="inline-flex border border-ink-600/20">
            <button
              type="button"
              onClick={() => setKind("expense")}
              className={
                "px-5 py-2 text-sm tracking-wide transition-colors " +
                (kind === "expense"
                  ? "bg-ink-900 text-paper-50"
                  : "text-ink-400 hover:text-ink-900")
              }
            >
              Expense
            </button>
            <button
              type="button"
              onClick={() => setKind("income")}
              className={
                "px-5 py-2 text-sm tracking-wide transition-colors " +
                (kind === "income"
                  ? "bg-moss-600 text-paper-50"
                  : "text-ink-400 hover:text-ink-900")
              }
            >
              Income
            </button>
          </div>
        </div>

        {/* Amount */}
        <div className="grid grid-cols-2 gap-8">
          <div>
            <label className="field-label">Amount</label>
            <div className="flex items-baseline">
              <span className="display-num text-3xl text-ink-400 mr-1">$</span>
              <input
                type="text"
                inputMode="decimal"
                pattern="[0-9]*\.?[0-9]*"
                className="field display-num text-3xl tracking-tightest"
                placeholder="0.00"
                value={amountInput}
                onChange={(e) => {
                  // Only allow digits and a single decimal
                  const v = e.target.value.replace(/[^0-9.]/g, "");
                  if ((v.match(/\./g) || []).length <= 1) setAmountInput(v);
                }}
                required
              />
            </div>
          </div>

          {/* Account */}
          <div>
            <label className="field-label">Account</label>
            <select
              className="field"
              value={accountId}
              onChange={(e) => setAccountId(e.target.value)}
              required
            >
              {accounts.isLoading && <option>Loading…</option>}
              {accounts.data?.map((a) => (
                <option key={a.id} value={a.id}>
                  {a.name}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Payee */}
        <div>
          <label className="field-label">Payee</label>
          <input
            type="text"
            className="field"
            placeholder="Who is this with?"
            value={payee}
            onChange={(e) => setPayee(e.target.value)}
            required
          />
        </div>

        {/* Description (optional) */}
        <div>
          <label className="field-label">
            Description{" "}
            <span className="normal-case tracking-normal text-ink-400/60">
              — optional
            </span>
          </label>
          <input
            type="text"
            className="field"
            placeholder="A note for your future self"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />
        </div>

        {/* Timestamp */}
        <div className="max-w-xs">
          <label className="field-label">Date & time</label>
          <input
            type="datetime-local"
            className="field"
            value={timestampLocal}
            onChange={(e) => setTimestampLocal(e.target.value)}
            required
          />
        </div>

        {error && (
          <div className="text-sm text-clay-600 border-l-2 border-clay-500 pl-3 py-2">
            {error}
          </div>
        )}

        <div className="flex items-center justify-between pt-8 rule-strong">
          <Link to="/transactions" className="btn-ghost">
            Cancel
          </Link>
          <button
            type="submit"
            className="btn-primary"
            disabled={createMutation.isPending}
          >
            {createMutation.isPending ? "Saving…" : "Save transaction"}
          </button>
        </div>
      </form>
    </div>
  );
}
