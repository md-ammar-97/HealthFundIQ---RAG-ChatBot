import { formatTimestampShort } from "@/lib/utils";

interface Props {
  istTimestamp: string | null | undefined;
  prefix?: string;
  className?: string;
}

export function TimestampDisplay({ istTimestamp, prefix = "Fetched:", className }: Props) {
  if (!istTimestamp) return null;
  return (
    <span className={className ?? "text-[11px] text-missing-gray"}>
      {prefix} {formatTimestampShort(istTimestamp)}
    </span>
  );
}
