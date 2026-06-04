interface Props {
  label?: string;
}
export function NotFound({ label = "Not found in corpus" }: Props) {
  return <span className="not-found">{label}</span>;
}
