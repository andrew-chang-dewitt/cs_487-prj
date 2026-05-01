import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { accountsApi } from "@/api/accounts";
import { balanceApi } from "@/api/balance";
import { formatCurrency } from "@/lib/currency";

export function AccountsPage() {
  const qc = useQueryClient();
  const [showClosed, setShowClosed] = useState(false);
  const [newName, setNewName] = useState("");
  const [error, setError] = useState<string | null>(null);

  const accounts = useQuery({
    queryKey: ["accounts", { closed: showClosed }],
    queryFn: () => accountsApi.list(showClosed),
  });

  const createMutation = useMutation({
    mutationFn: (name: string) => accountsApi.create({ name }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["accounts"] });
      qc.invalidateQueries({ queryKey: ["balance"] });
      setNewName("");
      setError(null);
    },
    onError: (err) =>
      setError(err instanceof Error ? err.message : "Couldn't create account"),
  });

  const closeMutation = useMutation({
    mutationFn: (id: string) => accountsApi.close(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["accounts"] });
      qc.invalidateQueries({ queryKey: ["balance"] });
    },
  });

  function onCreate(e: React.FormEvent) {
    e.preventDefault();
    if (!newName.trim()) return;
    createMutation.mutate(newName.trim());
  }

  return (
    <div className="space-y-12">
      <header className="pb-8 rule-double">
        <div className="eyebrow mb-2">Holdings</div>
        <h1 className="font-display text-5xl tracking-tightest">Accounts</h1>
      </header>

      {/* New account form */}
      <section className="bg-paper-100/50 p-8 border-l-2 border-moss-500">
        <div className="eyebrow mb-3">Add an account</div>
        <form onSubmit={onCreate} className="flex items-end gap-4">
          <div className="flex-1">
            <label className="field-label">Name</label>
            <input
              type="text"
              className="field"
              placeholder="e.g. Primary Checking"
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
            />
          </div>
          <button
            type="submit"
            className="btn-primary"
            disabled={!newName.trim() || createMutation.isPending}
          >
            {createMutation.isPending ? "Adding…" : "Add"}
          </button>
        </form>
        {error && (
          <div className="text-sm text-clay-600 mt-4 border-l-2 border-clay-500 pl-3 py-1">
            {error}
          </div>
        )}
      </section>

      {/* Toggle */}
      <div className="flex items-center gap-4">
        <button
          onClick={() => setShowClosed(false)}
          className={
            "text-sm tracking-wide transition-colors " +
            (!showClosed
              ? "text-ink-900 font-medium"
              : "text-ink-400 hover:text-ink-900")
          }
        >
          Open
        </button>
        <span className="text-ink-400/40">/</span>
        <button
          onClick={() => setShowClosed(true)}
          className={
            "text-sm tracking-wide transition-colors " +
            (showClosed
              ? "text-ink-900 font-medium"
              : "text-ink-400 hover:text-ink-900")
          }
        >
          Closed
        </button>
      </div>

      {/* Accounts table */}
      {accounts.isLoading ? (
        <div className="text-sm text-ink-400 py-8">Loading…</div>
      ) : accounts.data?.length === 0 ? (
        <div className="py-12 text-center text-ink-400 text-sm">
          {showClosed ? "No closed accounts." : "No open accounts yet."}
        </div>
      ) : (
        <div>
          <div className="grid grid-cols-[1fr_180px_120px] items-baseline gap-6 py-3 rule-strong eyebrow">
            <span>Account</span>
            <span className="text-right">Balance</span>
            <span></span>
          </div>
          {accounts.data?.map((a) => (
            <AccountRow
              key={a.id}
              accountId={a.id}
              name={a.name}
              closed={a.closed}
              onClose={() => closeMutation.mutate(a.id)}
              isClosing={closeMutation.isPending && closeMutation.variables === a.id}
            />
          ))}
        </div>
      )}
    </div>
  );
}

function AccountRow({
  accountId,
  name,
  closed,
  onClose,
  isClosing,
}: {
  accountId: string;
  name: string;
  closed: boolean;
  onClose: () => void;
  isClosing: boolean;
}) {
  const balance = useQuery({
    queryKey: ["balance", "account", accountId],
    queryFn: () => balanceApi.forAccount(accountId),
  });

  return (
    <div className="grid grid-cols-[1fr_180px_120px] items-baseline gap-6 py-5 rule group">
      <span className="text-ink-900">{name}</span>
      <span className="text-right font-mono tabular text-lg">
        {balance.isLoading ? "···" : formatCurrency(balance.data ?? "0")}
      </span>
      <span className="justify-self-end">
        {!closed && (
          <button
            onClick={onClose}
            className="text-xs uppercase tracking-[0.14em] text-ink-400 hover:text-clay-600 opacity-0 group-hover:opacity-100 transition-all"
            disabled={isClosing}
          >
            {isClosing ? "Closing…" : "Close"}
          </button>
        )}
        {closed && (
          <span className="text-xs uppercase tracking-[0.14em] text-ink-400/60">
            Closed
          </span>
        )}
      </span>
    </div>
  );
}
