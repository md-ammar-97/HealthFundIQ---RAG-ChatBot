"use client";

import { motion } from "motion/react";
import { useRouter } from "next/navigation";
import { ArrowRight, PlusCircle, CheckCircle } from "lucide-react";
import { CountryBadge } from "@/components/common/CountryBadge";
import { NotFound } from "@/components/common/NotFound";
import { useFundDetails } from "@/hooks/useFundDetails";
import { useComparisonStore } from "@/stores/comparison";
import type { FundListItem } from "@/lib/types";

interface Props {
  fund: FundListItem;
  index?: number;
}

export function FundCard({ fund, index = 0 }: Props) {
  const router = useRouter();
  const { data: details, isPending } = useFundDetails(fund.fund_id);
  const { addFund, removeFund, isSelected } = useComparisonStore();
  const selected = isSelected(fund.fund_id);

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2, delay: index * 0.04 }}
      className="bg-surface border border-border rounded-card p-4 flex flex-col gap-3 fund-card-hover cursor-pointer"
      onClick={() => router.push(`/funds/${fund.fund_id}`)}
    >
      {/* Header */}
      <div className="flex items-start justify-between gap-2">
        <div className="flex flex-col gap-1 min-w-0">
          <p className="text-[14px] font-semibold text-primary leading-tight line-clamp-2">
            {fund.fund_name}
          </p>
          <div className="flex items-center gap-1.5 flex-wrap">
            <CountryBadge country={fund.country} />
            {fund.ticker && (
              <span className="font-mono text-[11px] text-missing-gray bg-surface-muted px-1.5 py-0.5 rounded">
                {fund.ticker}
              </span>
            )}
            <span className="text-[11px] text-missing-gray">{fund.fund_type}</span>
          </div>
        </div>
      </div>

      {/* Financial fields */}
      <div className="grid grid-cols-2 gap-2">
        <div className="fact-cell">
          <div className="fact-label">Expense Ratio / MER</div>
          {isPending ? (
            <div className="h-4 w-16 bg-surface-muted animate-pulse rounded mt-1" />
          ) : details?.expense_ratio_or_mer_or_ter ? (
            <div className="fact-value">{details.expense_ratio_or_mer_or_ter}</div>
          ) : (
            <NotFound />
          )}
        </div>
        <div className="fact-cell">
          <div className="fact-label">AUM / Net Assets</div>
          {isPending ? (
            <div className="h-4 w-20 bg-surface-muted animate-pulse rounded mt-1" />
          ) : details?.aum ? (
            <div className="fact-value">{details.aum}</div>
          ) : (
            <NotFound />
          )}
        </div>
        <div className="fact-cell col-span-2">
          <div className="fact-label">Benchmark</div>
          {isPending ? (
            <div className="h-4 w-32 bg-surface-muted animate-pulse rounded mt-1" />
          ) : details?.benchmark ? (
            <div className="fact-value text-[13px]">{details.benchmark}</div>
          ) : (
            <NotFound />
          )}
        </div>
      </div>

      {/* Actions */}
      <div className="flex gap-2 mt-1" onClick={(e) => e.stopPropagation()}>
        <button
          onClick={() => router.push(`/research?fund_id=${fund.fund_id}`)}
          className="flex items-center gap-1 text-[12px] text-trust-blue hover:underline"
        >
          Ask about this fund
        </button>
        <span className="text-border">·</span>
        <button
          onClick={() =>
            selected ? removeFund(fund.fund_id) : addFund(fund)
          }
          className={`flex items-center gap-1 text-[12px] transition-colors ${
            selected ? "text-official-green" : "text-missing-gray hover:text-primary-accent"
          }`}
        >
          {selected ? (
            <>
              <CheckCircle size={13} /> Added
            </>
          ) : (
            <>
              <PlusCircle size={13} /> Compare
            </>
          )}
        </button>
        <span className="text-border ml-auto">·</span>
        <button
          onClick={() => router.push(`/funds/${fund.fund_id}`)}
          className="flex items-center gap-1 text-[12px] text-missing-gray hover:text-primary"
        >
          <ArrowRight size={12} />
        </button>
      </div>
    </motion.div>
  );
}
