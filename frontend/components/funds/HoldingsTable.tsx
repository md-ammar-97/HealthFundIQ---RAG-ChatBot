import type { Holding } from "@/lib/types";

interface Props {
  holdings: Holding[];
  sourceUrl?: string | null;
}

export function HoldingsTable({ holdings, sourceUrl }: Props) {
  return (
    <div className="flex flex-col gap-2">
      <div className="overflow-hidden rounded-source border border-border">
        <table className="w-full text-[13px]">
          <thead>
            <tr className="bg-surface-muted border-b border-border">
              <th className="text-left px-3 py-2 font-semibold text-[11px] uppercase tracking-wider text-missing-gray">
                #
              </th>
              <th className="text-left px-3 py-2 font-semibold text-[11px] uppercase tracking-wider text-missing-gray">
                Holding
              </th>
              {holdings[0]?.ticker && (
                <th className="text-left px-3 py-2 font-semibold text-[11px] uppercase tracking-wider text-missing-gray">
                  Ticker
                </th>
              )}
              <th className="text-right px-3 py-2 font-semibold text-[11px] uppercase tracking-wider text-missing-gray">
                Weight
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {holdings.map((h, i) => (
              <tr key={i} className="hover:bg-surface-muted/50 transition-colors">
                <td className="px-3 py-2 text-missing-gray w-8">{i + 1}</td>
                <td className="px-3 py-2 text-primary font-medium">{h.name}</td>
                {h.ticker !== undefined && (
                  <td className="px-3 py-2 font-mono text-[12px] text-missing-gray">
                    {h.ticker ?? "—"}
                  </td>
                )}
                <td className="px-3 py-2 text-right text-primary font-semibold">
                  {typeof h.weight === "number" ? `${h.weight.toFixed(2)}%` : h.weight}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {sourceUrl && (
        <p className="text-[11px] text-missing-gray">
          Source: {new URL(sourceUrl).hostname}
        </p>
      )}
      <p className="text-[11px] text-missing-gray">
        Note: Charts display only corpus-available factual data.
      </p>
    </div>
  );
}
