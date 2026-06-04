import { FileText, Globe, Building2 } from "lucide-react";
import type { SourceType } from "@/lib/types";

interface Props {
  type: SourceType;
  size?: "sm" | "md";
}

const CONFIG = {
  official: { label: "Official", icon: Building2, className: "badge-official" },
  platform: { label: "Platform", icon: Globe, className: "badge-platform" },
  pdf: { label: "PDF", icon: FileText, className: "badge-pdf" },
} as const;

export function SourceBadge({ type, size = "sm" }: Props) {
  const { label, icon: Icon, className } = CONFIG[type];
  return (
    <span className={className}>
      <Icon size={size === "sm" ? 10 : 12} />
      {label}
    </span>
  );
}
