"use client";

import { X, Download, Trash2, Plus } from "lucide-react";
import { motion, AnimatePresence } from "motion/react";
import { useComparisonStore } from "@/stores/comparison";
import { useFunds } from "@/hooks/useFunds";
import { exportComparisonCSV } from "./ComparisonExport";
import type { FundDetails } from "@/lib/types";
import { useState } from "react";

interface Props {
  detailsMap: Record<string, FundDetails | undefined>;
}

export function ComparisonToolbar({ detailsMap }: Props) {
  const { selectedFunds, removeFund, clearAll, addFund, isSelected } = useComparisonStore();
  const { data: allFunds = [] } = useFunds();
  const [search, setSearch] = useState("");
  const [showDropdown, setShowDropdown] = useState(false);

  const filtered = allFunds
    .filter((f) => !isSelected(f.fund_id))
    .filter(
      (f) =>
        f.fund_name.toLowerCase().includes(search.toLowerCase()) ||
        (f.ticker ?? "").toLowerCase().includes(search.toLowerCase()) ||
        f.country.toLowerCase().includes(search.toLowerCase())
    )
    .slice(0, 8);

  function handleExport() {
    const details = selectedFunds.map((f) => detailsMap[f.fund_id]);
    const names = selectedFunds.map((f) => f.fund_name);
    exportComparisonCSV(details, names);
  }

  return (
    <div className="flex flex-col gap-3">
      {/* Selected chips */}
      <div className="flex flex-wrap items-center gap-2">
        <AnimatePresence>
          {selectedFunds.map((f) => (
            <motion.span
              key={f.fund_id}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              transition={{ duration: 0.15 }}
              className="flex items-center gap-1.5 bg-trust-blue-light border border-trust-blue/20 rounded-chip px-3 py-1 text-[12px] text-trust-blue font-medium"
            >
              {f.ticker ?? f.fund_name.slice(0, 12)}
              <button onClick={() => removeFund(f.fund_id)} className="hover:opacity-70">
                <X size={11} />
              </button>
            </motion.span>
          ))}
        </AnimatePresence>

        {/* Add fund */}
        {selectedFunds.length < 5 && (
          <div className="relative">
            <button
              onClick={() => setShowDropdown(!showDropdown)}
              className="flex items-center gap-1.5 border border-dashed border-border rounded-chip px-3 py-1 text-[12px] text-missing-gray hover:border-primary-accent hover:text-primary-accent transition-colors"
            >
              <Plus size={12} /> Add fund
            </button>
            {showDropdown && (
              <div className="absolute left-0 top-full mt-1 z-50 bg-surface border border-border rounded-card shadow-drawer w-72">
                <input
                  autoFocus
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  placeholder="Search funds…"
                  className="w-full px-3 py-2 text-[13px] border-b border-border focus:outline-none"
                />
                {filtered.length === 0 ? (
                  <p className="px-3 py-3 text-[12px] text-missing-gray">No matching funds</p>
                ) : (
                  filtered.map((f) => (
                    <button
                      key={f.fund_id}
                      onClick={() => {
                        addFund(f);
                        setShowDropdown(false);
                        setSearch("");
                      }}
                      className="w-full text-left px-3 py-2 text-[13px] hover:bg-surface-muted flex flex-col"
                    >
                      <span className="font-medium text-primary">{f.fund_name}</span>
                      <span className="text-[11px] text-missing-gray">
                        {f.country} · {f.fund_type}
                      </span>
                    </button>
                  ))
                )}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Actions */}
      {selectedFunds.length > 0 && (
        <div className="flex gap-2">
          <button
            onClick={handleExport}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-button border border-border text-[12px] text-primary hover:bg-surface-muted transition-colors"
          >
            <Download size={13} /> Export CSV
          </button>
          <button
            onClick={clearAll}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-button border border-border text-[12px] text-error-red hover:bg-red-50 transition-colors"
          >
            <Trash2 size={13} /> Clear all
          </button>
        </div>
      )}
    </div>
  );
}
