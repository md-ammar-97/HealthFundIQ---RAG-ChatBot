import { cn } from "@/lib/utils";

const COUNTRY_COLORS: Record<string, string> = {
  India: "bg-orange-50 text-orange-700 border-orange-200",
  USA: "bg-blue-50 text-blue-700 border-blue-200",
  Canada: "bg-red-50 text-red-700 border-red-200",
  "China/HK": "bg-rose-50 text-rose-700 border-rose-200",
  Japan: "bg-purple-50 text-purple-700 border-purple-200",
  Singapore: "bg-teal-50 text-teal-700 border-teal-200",
  "UK/Europe": "bg-indigo-50 text-indigo-700 border-indigo-200",
};

interface Props {
  country: string;
}

export function CountryBadge({ country }: Props) {
  const colors = COUNTRY_COLORS[country] ?? "bg-gray-50 text-gray-600 border-gray-200";
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-chip border px-2 py-0.5 text-[11px] font-medium",
        colors
      )}
    >
      {country}
    </span>
  );
}
