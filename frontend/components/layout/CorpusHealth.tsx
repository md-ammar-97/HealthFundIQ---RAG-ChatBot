"use client";

import { Database } from "lucide-react";
import { useHealth } from "@/hooks/useHealth";
import { formatTimestampShort } from "@/lib/utils";

export function CorpusHealth() {
  const { data: health } = useHealth();

  return (
    <div className="flex flex-col gap-1 px-1">
      <div className="flex items-center gap-1.5 text-[11px] text-missing-gray">
        <Database size={11} />
        <span className="font-semibold uppercase tracking-wider">Corpus health</span>
      </div>
      {health ? (
        <>
          <p className="text-[11px] text-primary font-medium">
            {health.corpus_chunks.toLocaleString()} chunks indexed
          </p>
          <p className="text-[11px] text-missing-gray">
            Last run: {formatTimestampShort(health.timestamp)}
          </p>
        </>
      ) : (
        <p className="text-[11px] text-missing-gray">Backend unavailable</p>
      )}
    </div>
  );
}
