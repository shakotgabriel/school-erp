import { create } from "zustand";
import { fetchNotifications, type Notification } from "../lib/notifications";

interface NotificationState {
  notifications: Notification[];
  isLoading: boolean;
  error: string | null;
  fetchAll: () => Promise<void>;
}

export const useNotificationStore = create<NotificationState>((set) => ({
  notifications: [],
  isLoading: false,
  error: null,
  fetchAll: async () => {
    set({ isLoading: true, error: null });
    try {
      const notifications = await fetchNotifications();
      set({ notifications, isLoading: false });
    } catch (e) {
      set({ error: e instanceof Error ? e.message : "Failed to fetch notifications", isLoading: false });
    }
  },
}));
