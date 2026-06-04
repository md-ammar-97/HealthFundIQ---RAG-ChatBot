"use client";

import { motion, AnimatePresence } from "motion/react";
import { X, ExternalLink, Copy, Check } from "lucide-react";
import { useState } from "react";
import { SourceBadge } from "@/components/common/SourceBadge";
import { TimestampDisplay } from "@/components/common/TimestampDisplay";
import type { SourceCardData } from "@/lib/types";

interface Props {
  source: SourceCardData;
  isOpen: boolean;
  onClose: () => void;
}

export function EvidenceDrawer({ source, isOpen, onClose }: Props) {
  const [copied, setCopied] = useState(false);

  function handleCopy() {
    navigator.clipboard.writeText(source.url);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-40 bg-black/20"
            onClick={onClose}
          />
          {/* Drawer */}
          <motion.div
            initial={{ y: "100%" }}
            animate={{ y: 0 }}
            exit={{ y: "100%" }}
            transition={{ type: "spring", stiffness: 300, damping: 30 }}
            className="fixed bottom-0 left-0 right-0 z-50 bg-surface border-t border-border rounded-t-drawer shadow-drawer max-h-[60vh] overflow-y-auto"
          >
            <div className="flex flex-col gap-4 p-5">
              {/* Header */}
              <div className="flex items-start justify-between">
                <div className="flex flex-col gap-1">
                  <p className="text-[15px] font-semibold text-primary">
                    Evidence
                    {source.fundName ? ` — ${source.fundName}` : ""}
                  </p>
                  <SourceBadge type={source.sourceType} />
                </div>
                <button onClick={onClose} className="text-missing-gray hover:text-primary">
                  <X size={18} />
                </button>
              </div>

              {/* Metadata */}
              <div className="bg-surface-muted rounded-source p-3 flex flex-col gap-1.5 text-[12px]">
                <div className="flex items-center gap-2">
                  <span className="text-missing-gray">Source URL:</span>
                  <a
                    href={source.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-trust-blue hover:underline truncate"
                  >
                    {source.url}
                  </a>
                </div>
                {source.lastUpdated && (
                  <div className="flex gap-2">
                    <span className="text-missing-gray">Last updated from source:</span>
                    <span className="text-primary">{source.lastUpdated}</span>
                  </div>
                )}
                {source.fetchTimestamp && (
                  <TimestampDisplay
                    istTimestamp={source.fetchTimestamp}
                    prefix="Fetched by HealthFundIQ:"
                  />
                )}
              </div>

              {/* Excerpt */}
              {source.answerExcerpt && (
                <div className="flex flex-col gap-2">
                  <p className="text-[11px] font-semibold uppercase tracking-wider text-missing-gray">
                    Answer excerpt
                  </p>
                  <div className="bg-surface-muted border border-border rounded-source p-3 text-[13px] text-primary leading-relaxed">
                    {source.answerExcerpt}
                  </div>
                </div>
              )}

              {/* Actions */}
              <div className="flex gap-3">
                <a
                  href={source.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-2 px-3 py-2 rounded-button bg-primary-accent text-white text-[13px] font-medium hover:bg-primary-accent/90 transition-colors"
                >
                  <ExternalLink size={13} /> Open original source
                </a>
                <button
                  onClick={handleCopy}
                  className="flex items-center gap-2 px-3 py-2 rounded-button border border-border text-[13px] hover:bg-surface-muted transition-colors"
                >
                  {copied ? <Check size={13} className="text-official-green" /> : <Copy size={13} />}
                  {copied ? "Copied" : "Copy URL"}
                </button>
                <button
                  onClick={onClose}
                  className="ml-auto flex items-center gap-1 text-[12px] text-missing-gray hover:text-primary"
                >
                  Close <X size={11} />
                </button>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
