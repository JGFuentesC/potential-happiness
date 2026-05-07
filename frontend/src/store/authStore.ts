import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { User } from "@/types";
import { authApi, usersApi } from "@/api/client";

interface AuthState {
  user: User | null;
  token: string | null;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,

      login: async (username, password) => {
        const { data: tokenData } = await authApi.login(username, password);
        localStorage.setItem("token", tokenData.access_token);
        set({ token: tokenData.access_token });

        // Fetch the full user profile immediately after login
        const { data: userData } = await usersApi.me();
        set({ user: userData });
      },

      logout: () => {
        localStorage.removeItem("token");
        localStorage.removeItem("user");
        set({ user: null, token: null });
        window.location.href = "/login";
      },

      refreshUser: async () => {
        if (!get().token) return;
        try {
          const { data } = await usersApi.me();
          set({ user: data });
        } catch {
          // 401 interceptor in client.ts will handle redirect
        }
      },
    }),
    {
      name: "quiniela-auth",
      partialize: (state) => ({ user: state.user, token: state.token }),
    }
  )
);
