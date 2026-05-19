import { create } from "zustand";
import { persist } from "zustand/middleware";
import { makeId } from "../utils/id";

export const useUserStore = create(
  persist(
    (set, get) => ({
      user: null,
      accessToken: null,
      login: ({ user, accessToken }) => set({ user, accessToken }),
      register: ({ user, accessToken }) => set({ user, accessToken }),
      logout: () => set({ user: null, accessToken: null }),
      setAccessToken: (accessToken) => set({ accessToken }),
      isAuthenticated: () => Boolean(get().accessToken)
    }),
    { name: "potioncheck-user" }
  )
);

export const useProfileStore = create(
  persist(
    (set) => ({
      allergies: [],
      healthConditions: [],
      dietType: "None",
      updateProfile: (profile) => set(profile),
      resetProfile: () => set({ allergies: [], healthConditions: [], dietType: "None" })
    }),
    { name: "potioncheck-profile" }
  )
);

export const useScanStore = create(
  persist(
    (set, get) => ({
      currentScan: null,
      currentAnalysis: null,
      scanHistory: [],
      setCurrentScan: (currentScan) => set({ currentScan }),
      setCurrentAnalysis: (currentAnalysis) => set({ currentAnalysis }),
      addScanToHistory: (scan) => {
        const next = [scan, ...get().scanHistory].slice(0, 50);
        set({ scanHistory: next });
      }
    }),
    { name: "potioncheck-scans" }
  )
);

export const useUIStore = create((set, get) => ({
  loading: false,
  error: null,
  activeTab: "barcode",
  toasts: [],
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
  setActiveTab: (activeTab) => set({ activeTab }),
  toast: (toast) => {
    const item = { id: makeId("toast"), type: "info", ...toast };
    set({ toasts: [item, ...get().toasts].slice(0, 3) });
    window.setTimeout(() => get().dismissToast(item.id), toast.duration ?? 4000);
  },
  dismissToast: (id) => set({ toasts: get().toasts.filter((toast) => toast.id !== id) })
}));
