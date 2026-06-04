"use client";

import Link from "next/link";
import { motion } from "motion/react";
import { Activity, RefreshCw } from "lucide-react";
import { useHealth } from "@/hooks/useHealth";
import { formatTimestampShort } from "@/lib/utils";

export function TopBar() {
  const { data: health, isPending } = useHealth();

  return (
    <header className="sticky top-0 z-50 w-full border-b border-border bg-surface-dark/95 backdrop-blur-sm">
      <div className="flex h-14 items-center justify-between px-4 lg:px-6">
        {/* Wordmark */}
        <Link href="/" className="flex items-center gap-2 select-none">
          <motion.div
            className="flex items-center justify-center w-8 h-8 rounded-lg bg-brand-teal text-white"
            animate={{ scale: [1, 1.06, 1, 1.04, 1] }}
            transition={{ duration: 1.4, repeat: Infinity, ease: "easeInOut" }}
          >
            <Activity size={16} strokeWidth={2.5} />
          </motion.div>
          <div className="flex flex-col leading-none">
            <span className="text-[15px] font-bold text-white tracking-tight">
              HealthFund<span className="text-brand-teal">IQ</span>
            </span>
            <span className="text-[10px] text-slate-400 hidden sm:block">
              Ask. Compare. Verify.
            </span>
          </div>
        </Link>

        {/* Center — tagline */}
        <span className="hidden md:block text-[12px] text-slate-400 font-medium">
          Facts only · No investment advice
        </span>

        {/* Corpus refresh timestamp */}
        <div className="flex items-center gap-1.5 text-[11px] text-slate-400">
          <RefreshCw size={11} />
          {isPending ? (
            <span className="animate-pulse">Loading…</span>
          ) : health ? (
            <span>
              Last refresh:{" "}
              <span className="text-slate-300 font-medium">
                {formatTimestampShort(health.timestamp)}
              </span>
            </span>
          ) : (
            <span>Backend offline</span>
          )}
        </div>
      </div>
    </header>
  );
}
