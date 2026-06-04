"use client";

const FOLLOW_UP_BY_INTENT: Record<string, string[]> = {
  FACTUAL: [
    "Show top holdings",
    "What is the expense ratio?",
    "What is the benchmark?",
    "Show AUM",
    "What is the risk rating?",
  ],
  COMPARISON: [
    "Compare expense ratios",
    "Compare AUM",
    "Compare benchmarks",
    "Show country-wise funds",
  ],
  ADVICE: [
    "Compare expense ratios",
    "Show AUM",
    "Show benchmark",
    "Show top holdings",
  ],
  OUT_OF_SCOPE: [
    "Show India funds",
    "Show USA healthcare ETFs",
    "Compare expense ratios",
    "Which funds are biotech-focused?",
  ],
  MISSING: [
    "Show available fields",
    "Compare with another fund",
    "Show expense ratio",
  ],
};

// Chips that are fund-specific and should have "for {fund}" appended when a fund is known
const FUND_SPECIFIC_CHIPS = new Set([
  "Show top holdings",
  "What is the expense ratio?",
  "What is the benchmark?",
  "Show AUM",
  "What is the risk rating?",
  "Show expense ratio",
  "Show benchmark",
  "Show top holdings",
]);

interface Props {
  intent: string;
  fundName?: string;
  onChipClick: (query: string) => void;
}

export function FollowUpChips({ intent, fundName, onChipClick }: Props) {
  const chips = FOLLOW_UP_BY_INTENT[intent] ?? FOLLOW_UP_BY_INTENT.FACTUAL;
  return (
    <div className="flex flex-wrap gap-2">
      {chips.slice(0, 4).map((q) => {
        const query = fundName && FUND_SPECIFIC_CHIPS.has(q) ? `${q} for ${fundName}` : q;
        return (
          <button key={q} onClick={() => onChipClick(query)} className="prompt-chip text-[12px]">
            {q}
          </button>
        );
      })}
    </div>
  );
}
