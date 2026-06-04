import { HelpCircle } from "lucide-react";

interface Props {
  answer: string;
}

export function MissingDataCard({ answer }: Props) {
  return (
    <div className="bg-background border border-border rounded-card p-5 flex flex-col gap-2">
      <div className="flex items-start gap-2">
        <HelpCircle size={15} className="text-missing-gray shrink-0 mt-0.5" />
        <p className="text-[14px] text-missing-gray leading-relaxed">{answer}</p>
      </div>
    </div>
  );
}
