/**
 * AuthContext — provides current user state and login/register/logout
 * to the rest of the app.
 *
 * Today: the "user" is just an in-memory User object. We persist the user_id
 * to localStorage so refreshes don't kick people out, and call setCurrentUserId
 * on the API client so requests get auto-tagged.
 *
 * When real JWTs arrive: store the access_token alongside the user, and
 * change setCurrentUserId in api/client.ts to attach it as a Bearer header
 * instead of a query param.
 */

import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";
import { authApi } from "@/api/auth";
import { setCurrentUserId } from "@/api/client";
import type { User, UserIn } from "@/types/api";

interface AuthContextValue {
  user: User | null;
  isAuthenticated: boolean;
  loading: boolean;
  login: (handle: string, password: string) => Promise<void>;
  register: (input: UserIn, andLogin?: boolean) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

const STORAGE_KEY = "ledger.auth.v1";

interface PersistedAuth {
  user: User;
  password?: string; // only stored to enable mock-mode auto-login
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  // Restore from localStorage on mount.
  useEffect(() => {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) {
      try {
        const parsed = JSON.parse(raw) as PersistedAuth;
        setUser(parsed.user);
        setCurrentUserId(parsed.user.id);
      } catch {
        localStorage.removeItem(STORAGE_KEY);
      }
    }
    setLoading(false);
  }, []);

  const login = useCallback(async (handle: string, password: string) => {
    const u = await authApi.login(handle, password);
    setUser(u);
    setCurrentUserId(u.id);
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ user: u }));
  }, []);

  const register = useCallback(async (input: UserIn, andLogin = true) => {
    const u = await authApi.register(input);
    if (andLogin) {
      setUser(u);
      setCurrentUserId(u.id);
      localStorage.setItem(STORAGE_KEY, JSON.stringify({ user: u }));
    }
  }, []);

  const logout = useCallback(() => {
    setUser(null);
    setCurrentUserId(null);
    localStorage.removeItem(STORAGE_KEY);
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      isAuthenticated: user !== null,
      loading,
      login,
      register,
      logout,
    }),
    [user, loading, login, register, logout],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
