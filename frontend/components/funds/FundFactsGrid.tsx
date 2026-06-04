import { MetricChip } from "@/components/common/MetricChip";
import { TimestampDisplay } from "@/components/common/TimestampDisplay";
import { SourceBadge } from "@/components/common/SourceBadge";
import { ExternalLink } from "lucide-react";
import { getSourceType } from "@/lib/utils";
import type { FundDetails } from "@/lib/types";

interface Props {
  details: FundDetails;
}

export function FundFactsGrid({ details }: Props) {
  const sourceType = getSourceType(
    details.official_url ?? details.platform_url,
    details.official_url
  );

  return (
    <div className="flex flex-col gap-4">
      {/* Key metrics — 4 up */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
        <MetricChip label="NAV / Price" value={details.nav_or_price} />
        <MetricChip label="AUM / Net Assets" value={details.aum} />
        <MetricChip label="Expense Ratio / MER / TER" value={details.expense_ratio_or_mer_or_ter} />
        <MetricChip label="Benchmark" value={details.benchmark} />
      </div>

      {/* Fund details — 4 up */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
        <MetricChip label="Fund House / Issuer" value={details.fund_house_or_issuer} />
        <MetricChip label="Fund Manager" value={details.fund_management} />
        <MetricChip label="Risk Rating" value={details.risk_rating_or_riskometer} />
        <MetricChip label="Distribution Policy" value={details.distribution_policy} />
      </div>

      {/* Additional */}
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
        <MetricChip label="Minimum Investment" value={details.minimum_investment} />
        {details.minimum_sip && (
          <MetricChip label="Minimum SIP" value={details.minimum_sip} />
        )}
        <MetricChip label="Exit Load / Redemption Fee" value={details.exit_load_or_redemption_fee} />
      </div>

      {/* Investment objective */}
      {details.investment_objective && (
        <div className="bg-surface-muted border border-border rounded-source p-4">
          <p className="text-[11px] font-semibold uppercase tracking-wider text-missing-gray mb-2">
            Investment Objective
          </p>
          <p className="text-[14px] text-primary leading-relaxed">
            {details.investment_objective}
          </p>
        </div>
      )}

      {/* Source metadata */}
      <div className="flex flex-wrap items-center gap-3 pt-2 border-t border-border text-[12px] text-missing-gray">
        <div className="flex items-center gap-1.5">
          <SourceBadge type={sourceType} />
          {(details.official_url ?? details.platform_url) && (
            <a
              href={details.official_url ?? details.platform_url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-trust-blue hover:underline flex items-center gap-1"
            >
              {new URL(details.official_url ?? details.platform_url).hostname}
              <ExternalLink size={11} />
            </a>
          )}
        </div>
        {details.last_updated_from_source && (
          <span>Last updated from sources: {details.last_updated_from_source}</span>
        )}
        {details.fetch_timestamp && (
          <TimestampDisplay
            istTimestamp={details.fetch_timestamp}
            prefix="Fetched by HealthFundIQ:"
          />
        )}
      </div>
    </div>
  );
}
