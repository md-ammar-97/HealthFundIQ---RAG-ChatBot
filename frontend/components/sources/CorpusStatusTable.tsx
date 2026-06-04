"use client";

import { useState } from "react";
import { CheckCircle, XCircle, ExternalLink } from "lucide-react";
import { motion } from "motion/react";
import { EvidenceDrawer } from "./EvidenceDrawer";
import { SourceBadge } from "@/components/common/SourceBadge";
import { TimestampDisplay } from "@/components/common/TimestampDisplay";
import { getSourceType } from "@/lib/utils";
import { useFunds } from "@/hooks/useFunds";
import { useFundDetails } from "@/hooks/useFundDetails";
import { useHealth } from "@/hooks/useHealth";
import type { SourceCardData } from "@/lib/types";

function FundStatusRow({
  fundId, fundName, country, platformUrl, officialUrl, index,
  onViewEvidence,
}: {
  fundId: string; fundName: string; country: string;
  platformUrl: string; officialUrl?: string | null; index: number;
  onViewEvidence: (src: SourceCardData) => void;
}) {
  const { data: details, isPending, isError } = useFundDetails(fundId);
  const available = !isPending && !isError && !!details;
  const url = officialUrl ?? platformUrl;
  const sourceType = getSourceType(url, officialUrl);

  return (
    <motion.tr
      initial={{ opacity: 0, y: 4 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.02 }}
      className="border-b border-border hover:bg-surface-muted/50"
    >
      <td className="px-4 py-3 text-primary font-medium text-[13px]">{fundName}</td>
      <td className="px-4 py-3 text-[13px] text-missing-gray">{country}</td>
      <td className="px-4 py-3">
        <SourceBadge type={sourceType} />
      </td>
      <td className="px-4 py-3">
        {isPending ? (
          <div className="h-3 w-16 bg-surface-muted animate-pulse rounded" />
        ) : available ? (
          <TimestampDisplay
            istTimestamp={details?.fetch_timestamp}
            prefix=""
            className="text-[11px] text-missing-gray"
          />
        ) : (
          <span className="text-[11px] text-missing-gray">—</span>
        )}
      </td>
      <td className="px-4 py-3">
        {isPending ? (
          <div className="h-3 w-16 bg-surface-muted animate-pulse rounded" />
        ) : available ? (
          <span className="flex items-center gap-1 text-[12px] text-official-green font-medium">
            <CheckCircle size={13} /> Available
          </span>
        ) : (
          <span className="flex items-center gap-1 text-[12px] text-error-red font-medium">
            <XCircle size={13} /> No data
          </span>
        )}
      </td>
      <td className="px-4 py-3">
        <div className="flex items-center gap-2">
          <a href={url} target="_blank" rel="noopener noreferrer" className="text-trust-blue hover:opacity-80">
            <ExternalLink size={13} />
          </a>
          {available && (
            <button
              onClick={() =>
                onViewEvidence({
                  url,
                  sourceType,
                  fundName,
                  fetchTimestamp: details?.fetch_timestamp,
                  lastUpdated: details?.last_updated_from_source ?? undefined,
                  answerExcerpt: details?.investment_objective ?? undefined,
                })
              }
              className="text-[11px] text-trust-blue hover:underline"
            >
              View
            </button>
          )}
        </div>
      </td>
    </motion.tr>
  );
}

export function CorpusStatusTable() {
  const { data: health } = useHealth();
  const { data: funds = [] } = useFunds();
  const [evidenceSource, setEvidenceSource] = useState<SourceCardData | null>(null);

  return (
    <>
      <div className="flex flex-col gap-4">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-[18px] font-semibold text-primary">Corpus Status</h2>
            {health && (
              <p className="text-[12px] text-missing-gray mt-0.5">
                Last refreshed: <TimestampDisplay istTimestamp={health.timestamp} prefix="" className="text-[12px] text-primary inline" />
                {" · "}{health.corpus_chunks.toLocaleString()} chunks indexed
              </p>
            )}
          </div>
        </div>

        {/* Table */}
        <div className="overflow-x-auto rounded-source border border-border shadow-card">
          <table className="w-full text-[13px]">
            <thead>
              <tr className="bg-surface-muted border-b border-border">
                {["Fund", "Country", "Source Type", "Last Fetched", "Status", "Actions"].map((h) => (
                  <th key={h} className="text-left px-4 py-3 font-semibold text-[11px] uppercase tracking-wider text-missing-gray">
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {funds.map((f, i) => (
                <FundStatusRow
                  key={f.fund_id}
                  fundId={f.fund_id}
                  fundName={f.fund_name}
                  country={f.country}
                  platformUrl={f.platform_url}
                  officialUrl={f.official_url}
                  index={i}
                  onViewEvidence={setEvidenceSource}
                />
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {evidenceSource && (
        <EvidenceDrawer
          source={evidenceSource}
          isOpen={true}
          onClose={() => setEvidenceSource(null)}
        />
      )}
    </>
  );
}
