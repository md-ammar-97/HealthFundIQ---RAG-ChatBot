"use client";

import { useRouter } from "next/navigation";
import { Trash2 } from "lucide-react";
import { useChatStore } from "@/stores/chat";
import type { HistoryEntry } from "@/stores/chat";

function groupByDate(entries: HistoryEntry[]): [string, HistoryEntry[]][] {
  const now = new Date();
  const todayStr = now.toDateString();
  const yesterdayStr = new Date(now.getTime() - 86_400_000).toDateString();

  const map = new Map<string, HistoryEntry[]>();
  for (const entry of entries) {
    const d = new Date(entry.timestamp).toDateString();
    const label =
      d === todayStr
        ? "Today"
        : d === yesterdayStr
        ? "Yesterday"
        : new Date(entry.timestamp).toLocaleDateString("en-US", {
            month: "short",
            day: "numeric",
          });
    if (!map.has(label)) map.set(label, []);
    map.get(label)!.push(entry);
  }
  return Array.from(map.entries());
}

export function ChatHistory() {
  const router = useRouter();
  const { history, clearHistory } = useChatStore();

  if (history.length === 0) {
    return (
      <p className="text-[12px] text-missing-gray px-1 leading-relaxed">
        No history yet — ask a question to get started.
      </p>
    );
  }

  const groups = groupByDate(history);

  return (
    <div className="flex flex-col gap-3">
      <div className="flex items-center justify-between px-1">
        <p className="text-[11px] font-semibold uppercase tracking-wider text-missing-gray">
          History
        </p>
        <button
          onClick={clearHistory}
          className="flex items-center gap-1 text-[11px] text-missing-gray hover:text-error-red transition-colors"
          title="Clear all history"
        >
          <Trash2 size={11} />
          Clear
        </button>
      </div>

      {groups.map(([label, entries]) => (
        <div key={label} className="flex flex-col gap-0.5">
          <p className="text-[10px] font-semibold uppercase tracking-wider text-missing-gray/60 px-1 mb-1">
            {label}
          </p>
          {entries.map((entry) => (
            <button
              key={entry.id}
              onClick={() =>
                router.push(`/research?q=${encodeURIComponent(entry.query)}`)
              }
              className="text-left px-2 py-1.5 rounded-lg text-[12px] text-missing-gray hover:bg-surface-muted hover:text-primary transition-colors leading-snug"
              title={entry.query}
            >
              {entry.query.length > 52
                ? entry.query.slice(0, 52) + "…"
                : entry.query}
            </button>
          ))}
        </div>
      ))}
    </div>
  );
}
