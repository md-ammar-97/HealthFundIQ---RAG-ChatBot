import { SearchX } from "lucide-react";

interface Props {
  title?: string;
  description?: string;
}

export function EmptyState({
  title = "No results",
  description = "Try adjusting your filters.",
}: Props) {
  return (
    <div className="flex flex-col items-center justify-center py-16 gap-3 text-center">
      <SearchX size={32} className="text-missing-gray opacity-40" />
      <p className="text-[15px] font-semibold text-primary">{title}</p>
      <p className="text-[13px] text-missing-gray max-w-xs">{description}</p>
    </div>
  );
}
