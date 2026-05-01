import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { balanceApi } from "@/api/balance";
import { transactionsApi } from "@/api/transactions";
import { accountsApi } from "@/api/accounts";
import { useAuth } from "@/auth/AuthContext";
import { formatCurrency, amountKind } from "@/lib/currency";
import { formatDateShort } from "@/lib/dates";

export function DashboardPage() {
  const { user } = useAuth();

  const balance = useQuery({
    queryKey: ["balance", "total"],
    queryFn: () => balanceApi.total(),
  });

  const recent = useQuery({
    queryKey: ["transactions", { limit: 5 }],
    queryFn: () => transactionsApi.list({ limit: 5 }),
  });

  const accounts = useQuery({
    queryKey: ["accounts"],
    queryFn: () => accountsApi.list(),
  });

  const accountById = (id: string) =>
    accounts.data?.find((a) => a.id === id)?.name ?? "—";

  // Greeting that varies with time of day — small touch
  const hour = new Date().getHours();
  const greeting =
    hour < 5 ? "Up late," : hour < 12 ? "Good morning," : hour < 18 ? "Good afternoon," : "Good evening,";

  return (
    <div className="space-y-16">
      {/* Hero — greeting + total balance */}
      <header>
        <div className="eyebrow mb-2">Overview · Today</div>
        <h1 className="font-display text-5xl tracking-tightest mb-12">
          {greeting} <em className="not-italic text-moss-500">{user?.preferred_name?.toLowerCase() ?? user?.handle}</em>.
        </h1>

        <div className="flex items-baseline gap-12 pb-8 rule-double">
          <div>
            <div className="eyebrow mb-3">Total Balance</div>
            <div className="display-num text-7xl">
              {balance.isLoading ? (
                <span className="text-ink-400">···</span>
              ) : balance.isError ? (
                <span className="text-clay-600 text-2xl">unavailable</span>
              ) : (
                formatCurrency(balance.data ?? "0")
              )}
            </div>
          </div>
          <div className="ml-auto text-right">
            <div className="eyebrow mb-3">Accounts</div>
            <div className="display-num text-3xl">
              {accounts.data?.length ?? "—"}
            </div>
          </div>
        </div>
      </header>

      {/* Recent transactions */}
      <section>
        <div className="flex items-baseline justify-between mb-6">
          <div>
            <div className="eyebrow mb-1">Recent Activity</div>
            <h2 className="font-display text-2xl">Last five transactions</h2>
          </div>
          <Link
            to="/transactions"
            className="text-sm text-ink-400 hover:text-ink-900 transition-colors"
          >
            View all →
          </Link>
        </div>

        {recent.isLoading ? (
          <div className="text-sm text-ink-400 py-8">Loading…</div>
        ) : recent.isError ? (
          <div className="text-sm text-clay-600 py-8">Couldn't load transactions.</div>
        ) : recent.data && recent.data.length === 0 ? (
          <div className="py-12 text-center">
            <div className="text-ink-400 mb-4">No transactions yet.</div>
            <Link to="/transactions/new" className="btn-primary">
              Add your first
            </Link>
          </div>
        ) : (
          <div>
            {recent.data?.map((t) => {
              const kind = amountKind(t.amount);
              return (
                <div
                  key={t.id}
                  className="grid grid-cols-[80px_1fr_140px_120px] items-baseline gap-6 py-4 rule"
                >
                  <span className="font-mono text-xs text-ink-400 tabular">
                    {formatDateShort(t.timestamp)}
                  </span>
                  <span className="text-ink-900">
                    {t.payee}
                    {t.description && (
                      <span className="text-ink-400 ml-2">— {t.description}</span>
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
                </div>
              );
            })}
          </div>
        )}
      </section>

      {/* Accounts summary */}
      <section>
        <div className="flex items-baseline justify-between mb-6">
          <div>
            <div className="eyebrow mb-1">Holdings</div>
            <h2 className="font-display text-2xl">Open accounts</h2>
          </div>
          <Link
            to="/accounts"
            className="text-sm text-ink-400 hover:text-ink-900 transition-colors"
          >
            Manage →
          </Link>
        </div>

        {accounts.data?.length === 0 ? (
          <div className="text-sm text-ink-400 py-8">
            No accounts yet. <Link to="/accounts" className="text-moss-500 hover:underline">Create one</Link>.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-px bg-ink-600/15">
            {accounts.data?.map((a) => (
              <AccountCard key={a.id} accountId={a.id} name={a.name} />
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

function AccountCard({ accountId, name }: { accountId: string; name: string }) {
  const balance = useQuery({
    queryKey: ["balance", "account", accountId],
    queryFn: () => balanceApi.forAccount(accountId),
  });
  return (
    <div className="bg-paper-50 p-6">
      <div className="text-xs uppercase tracking-[0.14em] text-ink-400 mb-3">
        {name}
      </div>
      <div className="display-num text-3xl">
        {balance.isLoading ? "···" : formatCurrency(balance.data ?? "0")}
      </div>
    </div>
  );
}
