"use client";

import { motion } from "motion/react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { ExternalLink } from "lucide-react";
import { RefusalCard } from "./RefusalCard";
import { MissingDataCard } from "./MissingDataCard";
import { FollowUpChips } from "./FollowUpChips";
import { SourceBadge } from "@/components/common/SourceBadge";
import { TimestampDisplay } from "@/components/common/TimestampDisplay";
import { getSourceType, truncateUrl } from "@/lib/utils";
import type { ChatResponse } from "@/lib/types";

interface Props {
  response: ChatResponse;
  onFollowUp?: (query: string) => void;
}

export function AnswerCard({ response, onFollowUp }: Props) {
  const { answer, source_url, platform_url, last_updated, fetch_timestamp, is_refusal, missing_data, intent, fund_name } = response;

  if (is_refusal) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.2 }}
      >
        <RefusalCard answer={answer} onChipClick={onFollowUp} />
      </motion.div>
    );
  }

  if (missing_data) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.2 }}
      >
        <MissingDataCard answer={answer} />
      </motion.div>
    );
  }

  const primarySourceType = source_url ? getSourceType(source_url, source_url) : "platform";

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2, ease: "easeOut" }}
      className="bg-surface border border-border rounded-card p-5 flex flex-col gap-4 shadow-card"
    >
      {/* Answer text */}
      <div className="prose prose-sm max-w-none text-primary leading-relaxed text-[14px] prose-headings:mt-3 prose-headings:mb-2 prose-p:my-2 prose-ul:my-2 prose-li:my-1 prose-table:my-3">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>
          {answer}
        </ReactMarkdown>
      </div>

      {/* Sources */}
      {(source_url || platform_url) && (
        <div className="border-t border-border pt-3 flex flex-col gap-2">
          <p className="text-[11px] font-semibold uppercase tracking-wider text-missing-gray">
            Sources
          </p>
          {source_url && (
            <div className="flex items-center gap-2 flex-wrap">
              <SourceBadge type={primarySourceType} />
              <a
                href={source_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-trust-blue text-[12px] hover:underline flex items-center gap-1"
              >
                {truncateUrl(source_url, 55)}
                <ExternalLink size={11} />
              </a>
            </div>
          )}
          {platform_url && platform_url !== source_url && (
            <div className="flex items-center gap-2 flex-wrap">
              <SourceBadge type="platform" />
              <a
                href={platform_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-trust-blue text-[12px] hover:underline flex items-center gap-1"
              >
                {truncateUrl(platform_url, 55)}
                <ExternalLink size={11} />
              </a>
            </div>
          )}
          <div className="flex gap-4 flex-wrap mt-1">
            {last_updated && (
              <span className="text-[11px] text-missing-gray">
                Last updated from sources: {last_updated}
              </span>
            )}
            {fetch_timestamp && (
              <TimestampDisplay istTimestamp={fetch_timestamp} prefix="Fetched by HealthFundIQ:" />
            )}
          </div>
        </div>
      )}

      {/* Follow-up chips */}
      {onFollowUp && (
        <div className="border-t border-border pt-3">
          <FollowUpChips intent={intent} fundName={fund_name ?? undefined} onChipClick={onFollowUp} />
        </div>
      )}
    </motion.div>
  );
}
