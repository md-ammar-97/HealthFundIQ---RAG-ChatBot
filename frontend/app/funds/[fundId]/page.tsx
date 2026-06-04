"use client";

import { useParams, useRouter } from "next/navigation";
import { AppShell } from "@/components/layout/AppShell";
import { FundHeader } from "@/components/funds/FundHeader";
import { FundFactsGrid } from "@/components/funds/FundFactsGrid";
import { HoldingsTable } from "@/components/funds/HoldingsTable";
import { ExposureChart } from "@/components/funds/ExposureChart";
import { Skeleton } from "@/components/ui/skeleton";
import { useFunds } from "@/hooks/useFunds";
import { useFundDetails } from "@/hooks/useFundDetails";
import { getSourceType } from "@/lib/utils";
import type { SourceCardData } from "@/lib/types";

export default function FundDetailPage() {
  const { fundId } = useParams<{ fundId: string }>();
  const router = useRouter();
  const { data: allFunds = [] } = useFunds();
  const { data: details, isPending, isError } = useFundDetails(fundId);

  const fund = allFunds.find((f) => f.fund_id === fundId);

  const sources: SourceCardData[] = details
    ? [
        details.official_url
          ? {
              url: details.official_url,
              sourceType: "official",
              fundName: details.fund_name,
              lastUpdated: details.last_updated_from_source ?? undefined,
              fetchTimestamp: details.fetch_timestamp,
            }
          : null,
        {
          url: details.platform_url,
          sourceType: getSourceType(details.platform_url),
          fundName: details.fund_name,
          fetchTimestamp: details.fetch_timestamp,
        },
      ].filter(Boolean) as SourceCardData[]
    : [];

  return (
    <AppShell sources={sources} scrollable>
      <div className="px-4 py-6 flex flex-col gap-6">
        {/* Fund Header */}
        {fund ? (
          <FundHeader fund={fund} />
        ) : (
          <div className="flex flex-col gap-2">
            <Skeleton className="h-7 w-2/3" />
            <Skeleton className="h-4 w-1/3" />
          </div>
        )}

        {/* Facts Grid */}
        {isPending ? (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
            {Array.from({ length: 8 }).map((_, i) => (
              <Skeleton key={i} className="h-14" />
            ))}
          </div>
        ) : isError ? (
          <div className="bg-surface-muted border border-border rounded-card p-4 text-[14px] text-missing-gray">
            No parsed data is available for this fund in the current corpus.{" "}
            <a
              href={fund?.platform_url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-trust-blue underline"
            >
              Check the official source directly.
            </a>
          </div>
        ) : details ? (
          <>
            <FundFactsGrid details={details} />

            {/* Holdings */}
            {details.top_10_holdings && details.top_10_holdings.length > 0 && (
              <div>
                <h3 className="text-[15px] font-semibold text-primary mb-3">Top 10 Holdings</h3>
                <HoldingsTable
                  holdings={details.top_10_holdings}
                  sourceUrl={details.official_url ?? details.platform_url}
                />
              </div>
            )}

            {/* Sector exposure */}
            {details.sector_exposure && details.sector_exposure.length > 0 && (
              <div>
                <h3 className="text-[15px] font-semibold text-primary mb-3">Sector Exposure</h3>
                <div className="max-w-sm">
                  <ExposureChart
                    data={details.sector_exposure}
                    title="Sector Exposure"
                    sourceUrl={details.official_url ?? details.platform_url}
                  />
                </div>
              </div>
            )}

            {/* Geographic exposure */}
            {details.geographic_exposure && details.geographic_exposure.length > 0 && (
              <div>
                <h3 className="text-[15px] font-semibold text-primary mb-3">Geographic Exposure</h3>
                <div className="max-w-sm">
                  <ExposureChart
                    data={details.geographic_exposure}
                    title="Geographic Exposure"
                    sourceUrl={details.official_url ?? details.platform_url}
                  />
                </div>
              </div>
            )}
          </>
        ) : null}

        {/* Ask about this fund */}
        <div className="border border-border rounded-card p-4 flex flex-col gap-3 bg-trust-blue-light">
          <p className="text-[13px] font-semibold text-trust-blue">Ask about this fund</p>
          <div className="flex flex-wrap gap-2">
            {["Expense ratio?", "What benchmark?", "Top holdings?", "Investment objective?", "Risk rating?"].map(
              (q) => (
                <button
                  key={q}
                  onClick={() => router.push(`/research?q=${encodeURIComponent(q)}&fund_id=${fundId}`)}
                  className="prompt-chip text-[12px]"
                >
                  {q}
                </button>
              )
            )}
          </div>
        </div>
      </div>
    </AppShell>
  );
}
