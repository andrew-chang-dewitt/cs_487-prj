import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/auth/AuthContext";

export function LoginPage() {
  const navigate = useNavigate();
  const { login, register, isAuthenticated } = useAuth();
  const [mode, setMode] = useState<"sign-in" | "register">("sign-in");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const [handle, setHandle] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [preferredName, setPreferredName] = useState("");

  if (isAuthenticated) {
    navigate("/", { replace: true });
    return null;
  }

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      if (mode === "sign-in") {
        await login(handle, password);
      } else {
        await register({
          handle,
          password,
          full_name: fullName,
          preferred_name: preferredName || fullName,
        });
      }
      navigate("/", { replace: true });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="min-h-screen grid grid-cols-1 lg:grid-cols-5">
      {/* Left — editorial hero */}
      <div className="hidden lg:flex lg:col-span-3 bg-ink-900 text-paper-50 p-16 flex-col justify-between relative overflow-hidden">
        {/* Subtle paper grain on dark */}
        <div
          className="absolute inset-0 opacity-[0.04] pointer-events-none"
          style={{
            backgroundImage:
              "radial-gradient(rgb(251 249 244) 1px, transparent 1px)",
            backgroundSize: "4px 4px",
          }}
        />

        <div className="relative">
          <div className="eyebrow text-paper-200/70 mb-2">Personal Finance · Ledger</div>
        </div>

        <div className="relative max-w-xl">
          <h1 className="font-display text-7xl leading-[1.05] tracking-tightest mb-8">
            A ledger
            <br />
            <em className="text-moss-400 not-italic font-normal">that earns</em>
            <br />
            its keep.
          </h1>
          <p className="text-paper-100/70 text-base leading-relaxed max-w-sm font-light">
            Track what comes in and what goes out, see where it ends up, and stop
            wondering at the end of the month.
          </p>
        </div>

        <div className="relative flex items-baseline gap-8 text-xs text-paper-200/40 uppercase tracking-[0.2em]">
          <span>CS 487 · Team E</span>
          <span className="rule-strong border-paper-200/20 flex-1" />
          <span>Spring '26</span>
        </div>
      </div>

      {/* Right — form */}
      <div className="col-span-1 lg:col-span-2 flex items-center justify-center p-8 lg:p-12">
        <div className="w-full max-w-sm">
          <div className="eyebrow mb-2">
            {mode === "sign-in" ? "Welcome back" : "Create an account"}
          </div>
          <h2 className="font-display text-4xl mb-10 tracking-tightest">
            {mode === "sign-in" ? "Sign in." : "Get started."}
          </h2>

          <form onSubmit={onSubmit} className="space-y-6">
            <div>
              <label className="field-label">Handle</label>
              <input
                type="text"
                className="field"
                value={handle}
                onChange={(e) => setHandle(e.target.value)}
                autoComplete="username"
                required
                autoFocus
              />
            </div>

            {mode === "register" && (
              <>
                <div>
                  <label className="field-label">Full name</label>
                  <input
                    type="text"
                    className="field"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    required
                  />
                </div>
                <div>
                  <label className="field-label">
                    Preferred name <span className="text-ink-400/60 normal-case tracking-normal">— optional</span>
                  </label>
                  <input
                    type="text"
                    className="field"
                    value={preferredName}
                    onChange={(e) => setPreferredName(e.target.value)}
                  />
                </div>
              </>
            )}

            <div>
              <label className="field-label">Password</label>
              <input
                type="password"
                className="field"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                autoComplete={mode === "sign-in" ? "current-password" : "new-password"}
                required
              />
            </div>

            {error && (
              <div className="text-sm text-clay-600 border-l-2 border-clay-500 pl-3 py-1">
                {error}
              </div>
            )}

            <button type="submit" disabled={submitting} className="btn-primary w-full">
              {submitting
                ? "…"
                : mode === "sign-in"
                  ? "Sign in"
                  : "Create account"}
            </button>
          </form>

          <div className="mt-8 pt-6 rule">
            <button
              onClick={() => {
                setMode(mode === "sign-in" ? "register" : "sign-in");
                setError(null);
              }}
              className="text-sm text-ink-400 hover:text-ink-900 transition-colors"
            >
              {mode === "sign-in"
                ? "Don't have an account? Create one."
                : "Already registered? Sign in."}
            </button>
          </div>

          {import.meta.env.VITE_USE_MOCK_API === "true" && (
            <div className="mt-8 text-[11px] uppercase tracking-[0.14em] text-ink-400 leading-relaxed">
              <span className="text-moss-500">●</span> Mock mode active. Try{" "}
              <code className="font-mono normal-case tracking-normal text-ink-600">
                demo / demo
              </code>{" "}
              for seeded data.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
