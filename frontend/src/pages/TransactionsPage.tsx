import { useState } from "react";
import { Link } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { transactionsApi } from "@/api/transactions";
import { accountsApi } from "@/api/accounts";
import { formatCurrency, amountKind } from "@/lib/currency";
import { formatDateShort } from "@/lib/dates";
import type { Transaction } from "@/types/api";

export function TransactionsPage() {
  const qc = useQueryClient();
  const [accountFilter, setAccountFilter] = useState<string>("");
  const [confirmDelete, setConfirmDelete] = useState<Transaction | null>(null);

  const accounts = useQuery({
    queryKey: ["accounts"],
    queryFn: () => accountsApi.list(),
  });

  const transactions = useQuery({
    queryKey: ["transactions", { account_id: accountFilter || undefined }],
    queryFn: () =>
      transactionsApi.list({
        account_id: accountFilter || undefined,
        limit: 100,
      }),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => transactionsApi.remove(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["transactions"] });
      qc.invalidateQueries({ queryKey: ["balance"] });
      setConfirmDelete(null);
    },
  });

  const accountById = (id: string) =>
    accounts.data?.find((a) => a.id === id)?.name ?? "—";

  return (
    <div className="space-y-10">
      {/* Header */}
      <header className="flex items-end justify-between pb-8 rule-double">
        <div>
          <div className="eyebrow mb-2">All Activity</div>
          <h1 className="font-display text-5xl tracking-tightest">Transactions</h1>
        </div>
        <Link to="/transactions/new" className="btn-primary">
          + New transaction
        </Link>
      </header>

      {/* Filters */}
      <div className="flex items-center gap-6">
        <span className="eyebrow">Filter by account:</span>
        <select
          className="field !w-auto !pr-8"
          value={accountFilter}
          onChange={(e) => setAccountFilter(e.target.value)}
        >
          <option value="">All accounts</option>
          {accounts.data?.map((a) => (
            <option key={a.id} value={a.id}>
              {a.name}
            </option>
          ))}
        </select>
      </div>

      {/* List */}
      {transactions.isLoading ? (
        <div className="text-sm text-ink-400 py-8">Loading…</div>
      ) : transactions.isError ? (
        <div className="text-sm text-clay-600 py-8">Couldn't load transactions.</div>
      ) : transactions.data && transactions.data.length === 0 ? (
        <EmptyState />
      ) : (
        <div>
          {/* Column headers */}
          <div className="grid grid-cols-[80px_1fr_180px_140px_60px] items-baseline gap-6 py-3 rule-strong eyebrow">
            <span>Date</span>
            <span>Payee · Description</span>
            <span>Account</span>
            <span className="text-right">Amount</span>
            <span></span>
          </div>

          {transactions.data?.map((t) => {
            const kind = amountKind(t.amount);
            return (
              <div
                key={t.id}
                className="grid grid-cols-[80px_1fr_180px_140px_60px] items-baseline gap-6 py-4 rule group hover:bg-paper-100/40 -mx-4 px-4 transition-colors"
              >
                <span className="font-mono text-xs text-ink-400 tabular">
                  {formatDateShort(t.timestamp)}
                </span>
                <span>
                  <span className="text-ink-900">{t.payee}</span>
                  {t.description && (
                    <span className="text-ink-400 ml-2 text-sm">— {t.description}</span>
                  )}
                </span>
                <span className="text-xs text-ink-400 truncate">
                  {accountById(t.account_id)}
                </span>
                <span
                  className={
                    "text-right font-mono tabular " +
                    (kind === "credit" ? "text-moss-600" : kind === "debit" ? "text-ink-900" : "text-ink-400")
                  }
                >
                  {formatCurrency(t.amount, { showSign: true })}
                </span>
                <button
                  onClick={() => setConfirmDelete(t)}
                  className="opacity-0 group-hover:opacity-100 text-xs text-ink-400 hover:text-clay-600 transition-all justify-self-end"
                  aria-label="Delete transaction"
                >
                  ×
                </button>
              </div>
            );
          })}

          <div className="mt-8 text-xs text-ink-400 text-center">
            {transactions.data?.length} transaction
            {transactions.data?.length === 1 ? "" : "s"}
          </div>
        </div>
      )}

      {/* Delete confirmation modal */}
      {confirmDelete && (
        <DeleteConfirmModal
          transaction={confirmDelete}
          accountName={accountById(confirmDelete.account_id)}
          isDeleting={deleteMutation.isPending}
          onConfirm={() => deleteMutation.mutate(confirmDelete.id)}
          onCancel={() => setConfirmDelete(null)}
        />
      )}
    </div>
  );
}

function EmptyState() {
  return (
    <div className="py-24 text-center">
      <div className="font-display text-3xl text-ink-400 mb-3">
        Nothing recorded.
      </div>
      <p className="text-sm text-ink-400 mb-8 max-w-sm mx-auto">
        Once you add transactions, they'll appear here in chronological order.
      </p>
      <Link to="/transactions/new" className="btn-primary">
        Record your first transaction
      </Link>
    </div>
  );
}

function DeleteConfirmModal({
  transaction,
  accountName,
  isDeleting,
  onConfirm,
  onCancel,
}: {
  transaction: Transaction;
  accountName: string;
  isDeleting: boolean;
  onConfirm: () => void;
  onCancel: () => void;
}) {
  return (
    <div
      className="fixed inset-0 bg-ink-900/40 backdrop-blur-sm flex items-center justify-center z-50 p-4"
      onClick={onCancel}
    >
      <div
        className="bg-paper-50 max-w-md w-full p-8 shadow-card relative"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="eyebrow text-clay-600 mb-3">Permanent action</div>
        <h3 className="font-display text-3xl mb-6 tracking-tightest">
          Delete this transaction?
        </h3>

        <div className="bg-paper-100 p-5 mb-6 border-l-2 border-ink-600/30">
          <div className="text-sm text-ink-900 font-medium mb-1">
            {transaction.payee}
          </div>
          {transaction.description && (
            <div className="text-xs text-ink-400 mb-2">
              {transaction.description}
            </div>
          )}
          <div className="flex items-baseline justify-between mt-3">
            <span className="text-xs text-ink-400">{accountName}</span>
            <span
              className={
                "font-mono tabular text-lg " +
                (amountKind(transaction.amount) === "credit"
                  ? "text-moss-600"
                  : "text-ink-900")
              }
            >
              {formatCurrency(transaction.amount, { showSign: true })}
            </span>
          </div>
        </div>

        <p className="text-sm text-ink-400 mb-8 leading-relaxed">
          This will be removed from your records and your balance will be updated.
          You can't undo this.
        </p>

        <div className="flex justify-end gap-2">
          <button onClick={onCancel} className="btn-ghost" disabled={isDeleting}>
            Cancel
          </button>
          <button onClick={onConfirm} className="btn-danger" disabled={isDeleting}>
            {isDeleting ? "Deleting…" : "Delete transaction"}
          </button>
        </div>
      </div>
    </div>
  );
}
