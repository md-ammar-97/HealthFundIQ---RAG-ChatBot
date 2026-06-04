import { SourceBadge } from "@/components/common/SourceBadge";
import type { SourceType } from "@/lib/types";

interface Props {
  label: string;
  value: string;
  sourceType?: SourceType;
}

export function FactChip({ label, value, sourceType }: Props) {
  return (
    <div className="fact-cell flex flex-col gap-1">
      <div className="flex items-center justify-between gap-2">
        <span className="fact-label">{label}</span>
        {sourceType && <SourceBadge type={sourceType} />}
      </div>
      <span className="fact-value">{value}</span>
    </div>
  );
}
