import { AlertTriangle } from "lucide-react";

const FOLLOW_UPS = [
  "Compare expense ratios",
  "Show AUM",
  "Show benchmark",
  "Show top holdings",
  "Show risk rating",
  "Country-wise funds",
];

interface Props {
  answer: string;
  onChipClick?: (q: string) => void;
}

export function RefusalCard({ answer, onChipClick }: Props) {
  return (
    <div className="bg-refusal-bg border border-yellow-300 rounded-card p-5 flex flex-col gap-3">
      <div className="flex items-start gap-2">
        <AlertTriangle size={16} className="text-refusal-amber shrink-0 mt-0.5" />
        <p className="text-[14px] text-refusal-amber font-medium leading-snug">{answer}</p>
      </div>
      {onChipClick && (
        <div className="flex flex-wrap gap-2">
          {FOLLOW_UPS.map((q) => (
            <button
              key={q}
              onClick={() => onChipClick(q)}
              className="prompt-chip text-[12px]"
            >
              {q}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
