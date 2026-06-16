import { create } from 'zustand'

export const useStore = create((set) => ({
  activeAccount: null,
  setActiveAccount: (account) => set({ activeAccount: account }),

  stats: null,
  setStats: (stats) => set({ stats }),
}))
