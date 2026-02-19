import { create } from "zustand";
import { persist } from "zustand/middleware";
import { api, toApiError } from "@/lib/apiClient";

type DashboardEndpoint = "overview" | "students" | "finance" | "staff" | "academic";

type DashboardState = {
  // cache key -> merged data
  cache: Record<string, any>;

  isLoading: boolean;
  error: string | null;

  // fetch and cache
  fetchDashboard: (params: { role: string; endpoints: DashboardEndpoint[]; force?: boolean }) => Promise<any>;
  getDashboard: (params: { role: string; endpoints: DashboardEndpoint[] }) => any;

  clearError: () => void;
  clearCache: () => void;
};

function makeKey(role: string, endpoints: DashboardEndpoint[]) {
  return `${role}::${endpoints.slice().sort().join(",")}`;
}

export const useDashboardStore = create<DashboardState>()(
  persist(
    (set, get) => ({
      cache: {},
      isLoading: false,
      error: null,

      clearError: () => set({ error: null }),
      clearCache: () => set({ cache: {} }),

      getDashboard: ({ role, endpoints }) => {
        const key = makeKey(role, endpoints);
        return get().cache[key];
      },

      fetchDashboard: async ({ role, endpoints, force }) => {
        const key = makeKey(role, endpoints);

        const existing = get().cache[key];
        if (existing && !force) return existing;

        set({ isLoading: true, error: null });

        try {
          const results = await Promise.all(
            endpoints.map(async (ep) => {
              const res = await api.get(`/dashboard/${ep}/`);
              return [ep, res.data] as const;
            })
          );

          const merged: Record<string, any> = {};
          for (const [ep, payload] of results) merged[ep] = payload;

          set((state) => ({
            cache: { ...state.cache, [key]: merged },
            isLoading: false,
            error: null,
          }));

          return merged;
        } catch (e) {
          const err = toApiError(e);
          set({ isLoading: false, error: err.message });
          throw err;
        }
      },
    }),
    {
      name: "school-erp-dashboard-cache",
      // optional: persist cache so dashboard loads instantly after refresh
      partialize: (state) => ({ cache: state.cache }),
    }
  )
);
