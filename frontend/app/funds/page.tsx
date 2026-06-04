"use client";

import { Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { AppShell } from "@/components/layout/AppShell";
import { FundCard } from "@/components/funds/FundCard";
import { EmptyState } from "@/components/common/EmptyState";
import { useFunds } from "@/hooks/useFunds";
import { groupFundsByCountry, COUNTRY_ORDER } from "@/lib/utils";
import { Skeleton } from "@/components/ui/skeleton";

function FundExplorerContent() {
  const searchParams = useSearchParams();
  const country = searchParams.get("country") ?? undefined;
  const { data: funds = [], isPending } = useFunds(country);

  const grouped = groupFundsByCountry(funds);
  const orderedKeys = COUNTRY_ORDER.filter((c) => !!grouped[c]);
  if (!country) {/* use grouped */} else { /* country filtered */ }

  const displayKeys = country ? (funds.length > 0 ? [country] : []) : orderedKeys;

  return (
    <AppShell scrollable>
      <div className="px-4 py-6 flex flex-col gap-6">
        <div>
          <h1 className="text-[22px] font-bold text-primary">Fund Explorer</h1>
          <p className="text-[13px] text-missing-gray mt-1">
            {country ? `Showing funds in ${country}` : "~34 healthcare funds across 7 markets"}
          </p>
        </div>

        {isPending ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="rounded-card border border-border p-4 flex flex-col gap-3">
                <Skeleton className="h-5 w-3/4" />
                <Skeleton className="h-4 w-1/2" />
                <div className="grid grid-cols-2 gap-2">
                  <Skeleton className="h-12" />
                  <Skeleton className="h-12" />
                  <Skeleton className="h-12 col-span-2" />
                </div>
              </div>
            ))}
          </div>
        ) : funds.length === 0 ? (
          <EmptyState
            title="No funds found"
            description="No funds match the selected filters. Try changing the country or subcategory."
          />
        ) : (
          displayKeys.map((key) => {
            const countryFunds = grouped[key] ?? [];
            if (!countryFunds.length) return null;
            return (
              <div key={key} className="flex flex-col gap-3">
                <div className="flex items-center gap-3">
                  <h2 className="text-[15px] font-semibold text-primary">{key}</h2>
                  <span className="text-[12px] text-missing-gray">
                    {countryFunds.length} fund{countryFunds.length !== 1 ? "s" : ""}
                  </span>
                  <div className="flex-1 border-t border-border" />
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  {countryFunds.map((f, i) => (
                    <FundCard key={f.fund_id} fund={f} index={i} />
                  ))}
                </div>
              </div>
            );
          })
        )}
      </div>
    </AppShell>
  );
}

export default function FundsPage() {
  return (
    <Suspense>
      <FundExplorerContent />
    </Suspense>
  );
}
