import { NavLink, Outlet } from "react-router-dom";
import { useAuth } from "@/auth/AuthContext";

export function AppShell() {
  const { user, logout } = useAuth();

  return (
    <div className="min-h-screen flex">
      {/* ─── Sidebar ─────────────────────────────────────────────────── */}
      <aside className="w-64 shrink-0 border-r border-ink-600/15 bg-paper-50 flex flex-col">
        <div className="p-8 pb-6">
          <div className="eyebrow mb-1">Personal Finance</div>
          <div className="font-display text-3xl tracking-tightest leading-none">
            Ledger
          </div>
        </div>

        <nav className="flex-1 px-4">
          <NavItem to="/" end label="Overview" />
          <NavItem to="/transactions" label="Transactions" />
          <NavItem to="/accounts" label="Accounts" />
        </nav>

        {/* User block at bottom */}
        <div className="p-6 border-t border-ink-600/15">
          <div className="eyebrow mb-1">Signed in as</div>
          <div className="text-sm text-ink-900 font-medium mb-3">
            {user?.preferred_name || user?.full_name}
            <span className="text-ink-400 font-normal"> · @{user?.handle}</span>
          </div>
          <button
            onClick={logout}
            className="text-xs uppercase tracking-[0.14em] text-ink-400 hover:text-clay-600 transition-colors"
          >
            Sign out
          </button>
        </div>
      </aside>

      {/* ─── Main content ───────────────────────────────────────────── */}
      <main className="flex-1 overflow-y-auto">
        <div className="max-w-5xl mx-auto p-12">
          <Outlet />
        </div>
      </main>
    </div>
  );
}

function NavItem({
  to,
  label,
  end,
}: {
  to: string;
  label: string;
  end?: boolean;
}) {
  return (
    <NavLink
      to={to}
      end={end}
      className={({ isActive }) =>
        `block px-4 py-2.5 text-sm transition-colors ` +
        (isActive
          ? "text-ink-900 font-medium border-l-2 border-moss-500 -ml-[2px] pl-[14px]"
          : "text-ink-400 hover:text-ink-900 border-l-2 border-transparent -ml-[2px] pl-[14px]")
      }
    >
      {label}
    </NavLink>
  );
}
