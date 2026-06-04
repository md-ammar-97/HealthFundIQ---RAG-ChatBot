"use client";

import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { FundListItem } from "@/lib/types";

interface ComparisonStore {
  selectedFunds: FundListItem[];
  addFund: (fund: FundListItem) => void;
  removeFund: (fundId: string) => void;
  clearAll: () => void;
  isSelected: (fundId: string) => boolean;
}

export const useComparisonStore = create<ComparisonStore>()(
  persist(
    (set, get) => ({
      selectedFunds: [],
      addFund: (fund) => {
        const { selectedFunds } = get();
        if (selectedFunds.length >= 5) return;
        if (selectedFunds.some((f) => f.fund_id === fund.fund_id)) return;
        set({ selectedFunds: [...selectedFunds, fund] });
      },
      removeFund: (fundId) =>
        set((s) => ({
          selectedFunds: s.selectedFunds.filter((f) => f.fund_id !== fundId),
        })),
      clearAll: () => set({ selectedFunds: [] }),
      isSelected: (fundId) => get().selectedFunds.some((f) => f.fund_id === fundId),
    }),
    { name: "healthfundiq-comparison" }
  )
);
