"use client";

import { useRouter } from "next/navigation";
import { ArrowLeft, PlusCircle, CheckCircle, MessageCircle } from "lucide-react";
import { CountryBadge } from "@/components/common/CountryBadge";
import { useComparisonStore } from "@/stores/comparison";
import type { FundListItem } from "@/lib/types";

interface Props {
  fund: FundListItem;
}

export function FundHeader({ fund }: Props) {
  const router = useRouter();
  const { addFund, removeFund, isSelected } = useComparisonStore();
  const selected = isSelected(fund.fund_id);

  return (
    <div className="flex flex-col gap-3">
      <button
        onClick={() => router.back()}
        className="flex items-center gap-1.5 text-[12px] text-missing-gray hover:text-primary w-fit"
      >
        <ArrowLeft size={13} /> Back to Fund Explorer
      </button>

      <div className="flex flex-col gap-2">
        <h1 className="text-[22px] font-bold text-primary leading-tight">
          {fund.fund_name}
        </h1>
        <div className="flex items-center gap-2 flex-wrap">
          <CountryBadge country={fund.country} />
          <span className="text-[13px] text-missing-gray">{fund.fund_type}</span>
          {fund.ticker && (
            <span className="font-mono text-[13px] bg-surface-muted border border-border px-2 py-0.5 rounded text-primary">
              {fund.ticker}
            </span>
          )}
          {fund.isin && (
            <span className="font-mono text-[12px] text-missing-gray">{fund.isin}</span>
          )}
          {fund.currency && (
            <span className="text-[13px] text-missing-gray">{fund.currency}</span>
          )}
          {fund.exchange && (
            <span className="text-[13px] text-missing-gray">{fund.exchange}</span>
          )}
          <span className="text-[13px] text-missing-gray">{fund.domain_subcategory}</span>
        </div>
      </div>

      <div className="flex gap-3">
        <button
          onClick={() => router.push(`/research?fund_id=${fund.fund_id}`)}
          className="flex items-center gap-2 px-3 py-2 rounded-button bg-primary-accent text-white text-[13px] font-medium hover:bg-primary-accent/90 transition-colors"
        >
          <MessageCircle size={14} /> Ask about this fund
        </button>
        <button
          onClick={() => (selected ? removeFund(fund.fund_id) : addFund(fund))}
          className={`flex items-center gap-2 px-3 py-2 rounded-button border text-[13px] font-medium transition-colors ${
            selected
              ? "border-official-green text-official-green bg-green-50"
              : "border-border text-primary hover:border-border-strong"
          }`}
        >
          {selected ? <CheckCircle size={14} /> : <PlusCircle size={14} />}
          {selected ? "Added to Compare" : "+ Compare"}
        </button>
      </div>
    </div>
  );
}
