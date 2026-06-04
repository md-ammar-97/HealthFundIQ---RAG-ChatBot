import { FactChip } from "./FactChip";
import type { SourceType } from "@/lib/types";

interface FactItem {
  label: string;
  value: string;
  sourceType?: SourceType;
}

interface Props {
  facts: FactItem[];
}

export function FactGrid({ facts }: Props) {
  return (
    <div className="grid grid-cols-2 gap-2">
      {facts.map((f) => (
        <FactChip key={f.label} label={f.label} value={f.value} sourceType={f.sourceType} />
      ))}
    </div>
  );
}
