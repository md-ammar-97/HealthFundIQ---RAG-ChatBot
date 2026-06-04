"use client";

import { AppShell } from "@/components/layout/AppShell";
import { ComparisonToolbar } from "@/components/compare/ComparisonToolbar";
import { ComparisonTable } from "@/components/compare/ComparisonTable";
import { useFundDetails } from "@/hooks/useFundDetails";
import { useComparisonStore } from "@/stores/comparison";
import type { FundDetails, FundListItem } from "@/lib/types";
import { useQueryClient } from "@tanstack/react-query";

// Prefetches details for a single fund — hooks called at component level (not in loop)
function FundDetailsPreloader({ fund }: { fund: FundListItem }) {
  useFundDetails(fund.fund_id);
  return null;
}

// Reads cached details from the query client
function useDetailsMap(fundIds: string[]): Record<string, FundDetails | undefined> {
  const queryClient = useQueryClient();
  const map: Record<string, FundDetails | undefined> = {};
  for (const id of fundIds) {
    map[id] = queryClient.getQueryData<FundDetails>(["fund-details", id]);
  }
  return map;
}

export default function ComparePage() {
  const { selectedFunds } = useComparisonStore();
  const fundIds = selectedFunds.map((f) => f.fund_id);

  // Build a live detailsMap by re-reading the cache every render
  const detailsMap = useDetailsMap(fundIds);

  return (
    <AppShell hideSourcePanel scrollable>
      {/* Preload details for each selected fund — each renders a hook at component level */}
      {selectedFunds.map((f) => (
        <FundDetailsPreloader key={f.fund_id} fund={f} />
      ))}

      <div className="px-4 py-6 flex flex-col gap-6">
        <div>
          <h1 className="text-[22px] font-bold text-primary">Compare Funds</h1>
          <p className="text-[13px] text-missing-gray mt-1">
            Side-by-side factual comparison of up to 5 funds
          </p>
        </div>

        <ComparisonToolbar detailsMap={detailsMap} />
        <ComparisonTable funds={selectedFunds} detailsMap={detailsMap} />
      </div>
    </AppShell>
  );
}
