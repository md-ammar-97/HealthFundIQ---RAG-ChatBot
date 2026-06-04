import { NotFound } from "./NotFound";

interface Props {
  label: string;
  value: string | null | undefined;
  mono?: boolean;
}

export function MetricChip({ label, value, mono }: Props) {
  return (
    <div className="fact-cell flex flex-col">
      <span className="fact-label">{label}</span>
      {value ? (
        <span className={`fact-value ${mono ? "font-mono" : ""}`}>{value}</span>
      ) : (
        <NotFound />
      )}
    </div>
  );
}
