import { AlertTriangle } from "lucide-react";

export function DisclaimerBanner() {
  return (
    <div className="disclaimer-accent flex items-start gap-2 text-[13px]">
      <AlertTriangle className="shrink-0 mt-0.5" size={13} />
      <span>
        <strong>Facts only.</strong> No investment advice.{" "}
        Always verify from official fund documents before making financial decisions.
      </span>
    </div>
  );
}
