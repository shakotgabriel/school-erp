import { create } from "zustand";
import { persist } from "zustand/middleware";

import { loginApi, meApi } from "../lib/auth";
import { setApiAccessToken } from "../lib/apiClient";

import type { AuthUser, Role } from "../types/user";

export type { AuthUser, Role } from "../types/user";

type AuthState = {
  accessToken: string | null;
  refreshToken: string | null;
  user: AuthUser | null;

  isLoading: boolean;
  error: string | null;

  setAuth: (payload: { accessToken: string; refreshToken: string; user: AuthUser }) => void;
  clearError: () => void;

  isAuthed: () => boolean;
  hasRole: (role: Role | Role[]) => boolean;

  login: (payload: { identifier: string; password: string }) => Promise<void>;
  fetchMe: () => Promise<void>;
  logout: () => void;
};

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      accessToken: null,
      refreshToken: null,
      user: null,

      isLoading: false,
      error: null,

      setAuth: ({ accessToken, refreshToken, user }) => {
        setApiAccessToken(accessToken);
        set({ accessToken, refreshToken, user });
      },
      clearError: () => set({ error: null }),

      isAuthed: () => {
        const { accessToken, user } = get();
        return Boolean(accessToken && user);
      },
      hasRole: (role) => {
        const currentRole = get().user?.role;
        if (!currentRole) return false;
        return Array.isArray(role) ? role.includes(currentRole) : currentRole === role;
      },

      login: async ({ identifier, password }) => {
        set({ isLoading: true, error: null });
        try {
          const result = await loginApi({ identifier, password });
          setApiAccessToken(result.accessToken);
          set({
            accessToken: result.accessToken,
            refreshToken: result.refreshToken,
            user: result.user,
            isLoading: false,
            error: null,
          });
        } catch (e) {
          const message = e instanceof Error ? e.message : "Login failed";
          set({ isLoading: false, error: message });
          throw e;
        }
      },

      fetchMe: async () => {
        const { accessToken } = get();
        if (!accessToken) return;

        setApiAccessToken(accessToken);
        set({ isLoading: true, error: null });
        try {
          const user = await meApi();
          set({ user, isLoading: false, error: null });
        } catch (e) {
          const message = e instanceof Error ? e.message : "Failed to load user";
          set({ isLoading: false, error: message });
          throw e;
        }
      },

      logout: () => {
        setApiAccessToken(null);
        set({ accessToken: null, refreshToken: null, user: null, error: null, isLoading: false });
      },
    }),
    {
      name: "school-erp-auth",
      partialize: (state) => ({
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        user: state.user,
      }),
      onRehydrateStorage: () => (state) => {
        const accessToken = state?.accessToken ?? null;
        setApiAccessToken(accessToken);
      },
    }
  )
);
