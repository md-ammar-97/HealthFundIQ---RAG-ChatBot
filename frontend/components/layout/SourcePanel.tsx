"use client";

import { motion, AnimatePresence } from "motion/react";
import { ExternalLink } from "lucide-react";
import { truncateUrl, formatTimestampShort } from "@/lib/utils";
import type { SourceCardData } from "@/lib/types";

interface Props {
  sources?: SourceCardData[];
}

const SOURCE_ORDER = { official: 0, pdf: 1, platform: 2 } as const;

export function SourcePanel({ sources = [] }: Props) {
  const sorted = [...sources].sort(
    (a, b) => SOURCE_ORDER[a.sourceType] - SOURCE_ORDER[b.sourceType]
  );

  return (
    <aside className="flex flex-col h-full overflow-y-auto scrollbar-thin py-4 px-3 gap-4">
      <p className="text-[11px] font-semibold uppercase tracking-wider text-missing-gray">
        Sources used
      </p>

      <AnimatePresence mode="popLayout">
        {sorted.length === 0 ? (
          <motion.p
            key="empty"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-[12px] text-missing-gray"
          >
            Sources will appear here after a query.
          </motion.p>
        ) : (
          sorted.map((src, i) => (
            <motion.div
              key={src.url + i}
              initial={{ opacity: 0, x: 16 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.25, delay: i * 0.04 }}
              className="bg-surface-muted border border-border rounded-source p-3 flex flex-col gap-2"
            >
              <div className="flex items-start justify-between gap-2">
                <span
                  className={
                    src.sourceType === "official"
                      ? "badge-official"
                      : src.sourceType === "pdf"
                      ? "badge-pdf"
                      : "badge-platform"
                  }
                >
                  {src.sourceType === "official"
                    ? "Official"
                    : src.sourceType === "pdf"
                    ? "PDF"
                    : "Platform"}
                </span>
                <a
                  href={src.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="shrink-0 text-trust-blue hover:opacity-80"
                >
                  <ExternalLink size={13} />
                </a>
              </div>
              {src.fundName && (
                <p className="text-[12px] font-medium text-primary leading-tight">
                  {src.fundName}
                </p>
              )}
              <p className="source-url text-trust-blue text-[11px] break-all">
                {truncateUrl(src.url, 45)}
              </p>
              {src.lastUpdated && (
                <p className="text-[11px] text-missing-gray">
                  Updated: {src.lastUpdated}
                </p>
              )}
              {src.fetchTimestamp && (
                <p className="text-[11px] text-missing-gray">
                  Fetched: {formatTimestampShort(src.fetchTimestamp)}
                </p>
              )}
            </motion.div>
          ))
        )}
      </AnimatePresence>

    </aside>
  );
}
