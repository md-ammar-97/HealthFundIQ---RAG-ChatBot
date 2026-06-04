import { ExternalLink } from "lucide-react";
import { SourceBadge } from "@/components/common/SourceBadge";
import { TimestampDisplay } from "@/components/common/TimestampDisplay";
import { truncateUrl } from "@/lib/utils";
import type { SourceCardData } from "@/lib/types";

interface Props {
  source: SourceCardData;
}

export function SourceCard({ source }: Props) {
  return (
    <div className="bg-surface-muted border border-border rounded-source p-3 flex flex-col gap-2">
      <div className="flex items-start justify-between gap-2">
        <SourceBadge type={source.sourceType} />
        <a
          href={source.url}
          target="_blank"
          rel="noopener noreferrer"
          className="shrink-0 text-trust-blue hover:opacity-80"
        >
          <ExternalLink size={13} />
        </a>
      </div>
      {source.fundName && (
        <p className="text-[13px] font-medium text-primary leading-tight">{source.fundName}</p>
      )}
      <p className="text-trust-blue text-[11px] break-all">{truncateUrl(source.url, 50)}</p>
      {source.lastUpdated && (
        <p className="text-[11px] text-missing-gray">Updated: {source.lastUpdated}</p>
      )}
      {source.fetchTimestamp && (
        <TimestampDisplay istTimestamp={source.fetchTimestamp} prefix="Fetched:" />
      )}
    </div>
  );
}
