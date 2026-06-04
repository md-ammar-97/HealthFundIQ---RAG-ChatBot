"use client";

import { motion, AnimatePresence } from "motion/react";
import { NotFound } from "@/components/common/NotFound";
import { SourceBadge } from "@/components/common/SourceBadge";
import { getSourceType } from "@/lib/utils";
import type { FundListItem, FundDetails } from "@/lib/types";

interface Props {
  funds: FundListItem[];
  detailsMap: Record<string, FundDetails | undefined>;
}

interface Row {
  field: string;
  getValue: (d: FundDetails) => string | null | undefined;
}

const ROWS: Row[] = [
  { field: "Country / Market", getValue: (d) => d.country_or_market },
  { field: "Fund Type", getValue: (d) => d.fund_type },
  { field: "Subcategory", getValue: (d) => d.domain_subcategory },
  { field: "Ticker / ISIN", getValue: (d) => [d.ticker_or_identifier, d.fund_id].filter(Boolean).join(" / ") },
  { field: "Currency", getValue: (d) => d.currency },
  { field: "Exchange", getValue: (d) => d.exchange },
  { field: "NAV / Price", getValue: (d) => d.nav_or_price },
  { field: "AUM / Net Assets", getValue: (d) => d.aum },
  { field: "Expense Ratio / MER / TER", getValue: (d) => d.expense_ratio_or_mer_or_ter },
  { field: "Benchmark", getValue: (d) => d.benchmark },
  { field: "Risk Rating", getValue: (d) => d.risk_rating_or_riskometer },
  { field: "Fund House / Issuer", getValue: (d) => d.fund_house_or_issuer },
  { field: "Fund Manager", getValue: (d) => d.fund_management },
  { field: "Min. Investment", getValue: (d) => d.minimum_investment },
  { field: "Distribution Policy", getValue: (d) => d.distribution_policy },
  { field: "Last Updated", getValue: (d) => d.last_updated_from_source },
];

export function ComparisonTable({ funds, detailsMap }: Props) {
  if (funds.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-20 gap-3 text-center">
        <p className="text-[15px] text-missing-gray">
          Select funds above to compare them side-by-side.
        </p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto rounded-source border border-border shadow-card">
      <table className="w-full text-[13px] border-collapse">
        <thead>
          <tr className="border-b border-border bg-surface-muted">
            <th className="sticky left-0 bg-surface-muted text-left px-4 py-3 font-semibold text-[11px] uppercase tracking-wider text-missing-gray w-40 z-10">
              Field
            </th>
            <AnimatePresence>
              {funds.map((f) => (
                <motion.th
                  key={f.fund_id}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.2 }}
                  className="text-left px-4 py-3 font-semibold text-primary text-[12px] min-w-[160px]"
                >
                  <div className="flex flex-col gap-1">
                    <span className="line-clamp-2 leading-tight">{f.fund_name}</span>
                    {f.ticker && (
                      <span className="font-mono text-[11px] text-missing-gray">{f.ticker}</span>
                    )}
                  </div>
                </motion.th>
              ))}
            </AnimatePresence>
          </tr>
        </thead>
        <tbody>
          {ROWS.map((row, ri) => (
            <tr
              key={row.field}
              className={`border-b border-border ${ri % 2 === 0 ? "bg-surface" : "bg-surface-muted/40"}`}
            >
              <td className="sticky left-0 bg-inherit px-4 py-3 font-medium text-missing-gray text-[12px] uppercase tracking-wide whitespace-nowrap z-10">
                {row.field}
              </td>
              {funds.map((f) => {
                const details = detailsMap[f.fund_id];
                const value = details ? row.getValue(details) : null;
                return (
                  <td key={f.fund_id} className="px-4 py-3 text-primary">
                    {!details ? (
                      <div className="h-4 w-20 bg-surface-muted animate-pulse rounded" />
                    ) : value ? (
                      <span>{value}</span>
                    ) : (
                      <NotFound />
                    )}
                  </td>
                );
              })}
            </tr>
          ))}
          {/* Source row */}
          <tr className="border-b border-border bg-surface">
            <td className="sticky left-0 bg-surface px-4 py-3 font-medium text-missing-gray text-[12px] uppercase tracking-wide z-10">
              Source
            </td>
            {funds.map((f) => {
              const details = detailsMap[f.fund_id];
              if (!details) return <td key={f.fund_id} className="px-4 py-3" />;
              const url = details.official_url ?? details.platform_url;
              const sourceType = getSourceType(url, details.official_url);
              return (
                <td key={f.fund_id} className="px-4 py-3">
                  <a
                    href={url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-1.5"
                  >
                    <SourceBadge type={sourceType} />
                  </a>
                </td>
              );
            })}
          </tr>
        </tbody>
      </table>
      <p className="px-4 py-2 text-[11px] text-missing-gray border-t border-border">
        Some funds do not publish all fields in the current source set.
      </p>
    </div>
  );
}
