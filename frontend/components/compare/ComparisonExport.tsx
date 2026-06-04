import type { FundDetails } from "@/lib/types";
import { formatTimestampShort } from "@/lib/utils";

export function exportComparisonCSV(funds: (FundDetails | undefined)[], names: string[]) {
  const headers = [
    "fund_name", "country", "fund_type", "expense_ratio", "aum",
    "benchmark", "risk_rating", "fund_house", "source_url", "last_updated", "fetch_timestamp",
  ];

  const rows = funds.map((f, i) => {
    if (!f) return headers.map(() => "—");
    return [
      names[i] ?? f.fund_name,
      f.country_or_market,
      f.fund_type,
      f.expense_ratio_or_mer_or_ter ?? "—",
      f.aum ?? "—",
      f.benchmark ?? "—",
      f.risk_rating_or_riskometer ?? "—",
      f.fund_house_or_issuer ?? "—",
      f.official_url ?? f.platform_url,
      f.last_updated_from_source ?? "—",
      formatTimestampShort(f.fetch_timestamp),
    ].map((v) => `"${String(v).replace(/"/g, '""')}"`);
  });

  const csv = [headers.join(","), ...rows.map((r) => r.join(","))].join("\n");
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "healthfundiq_comparison.csv";
  a.click();
  URL.revokeObjectURL(url);
}
