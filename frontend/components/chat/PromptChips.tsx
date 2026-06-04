"use client";

const CHIPS = [
  { label: "Expense ratio", query: "What is the expense ratio of HDFC Pharma and Healthcare Fund?" },
  { label: "Canada funds", query: "Which healthcare ETFs are available in Canada?" },
  { label: "XLV benchmark", query: "What benchmark does XLV track?" },
  { label: "Biotech focus", query: "Which funds in this corpus are biotech-focused?" },
  { label: "Country-wise", query: "Show healthcare funds available country-wise." },
  { label: "IBB holdings", query: "What are the top holdings of IBB?" },
  { label: "VHT objective", query: "What is the investment objective of VHT?" },
];

interface Props {
  onSelect: (query: string) => void;
}

export function PromptChips({ onSelect }: Props) {
  return (
    <div className="flex flex-wrap gap-2">
      {CHIPS.map(({ label, query }) => (
        <button
          key={label}
          onClick={() => onSelect(query)}
          className="prompt-chip"
        >
          {label}
        </button>
      ))}
    </div>
  );
}
