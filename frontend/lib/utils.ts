import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";
import type { SourceType } from "./types";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// IST → PDT/PST conversion (no external library needed)
// DST: 2nd Sunday of March → 1st Sunday of November
function getNthSundayUTC(year: number, month: number, n: number): Date {
  // month: 0-indexed (2=March, 10=November)
  const firstDay = new Date(Date.UTC(year, month, 1));
  const dayOfWeek = firstDay.getUTCDay(); // 0=Sun
  const daysToFirstSunday = dayOfWeek === 0 ? 0 : 7 - dayOfWeek;
  const nthSundayDay = daysToFirstSunday + (n - 1) * 7 + 1;
  return new Date(Date.UTC(year, month, nthSundayDay));
}

export function convertISTtoPDTPST(istTimestamp: string): string {
  if (!istTimestamp) return "";
  const date = new Date(istTimestamp); // JS correctly parses +05:30
  if (isNaN(date.getTime())) return istTimestamp;

  const year = date.getUTCFullYear();
  const dstStart = getNthSundayUTC(year, 2, 2); // March, 2nd Sunday
  dstStart.setUTCHours(10, 0, 0, 0); // 02:00 PST (UTC-8) = 10:00 UTC

  const dstEnd = getNthSundayUTC(year, 10, 1); // November, 1st Sunday
  dstEnd.setUTCHours(9, 0, 0, 0); // 02:00 PDT (UTC-7) = 09:00 UTC

  const isDST = date >= dstStart && date < dstEnd;
  const offsetHours = isDST ? -7 : -8;
  const label = isDST ? "PDT" : "PST";

  const local = new Date(date.getTime() + offsetHours * 3_600_000);
  const iso = local.toISOString();
  // Format: "Jun 3, 2026, 09:42 PDT"
  const datePart = iso.slice(0, 10); // YYYY-MM-DD
  const timePart = iso.slice(11, 16); // HH:MM
  const [y, m, d] = datePart.split("-").map(Number);
  const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  return `${months[m - 1]} ${d}, ${y}, ${timePart} ${label}`;
}

export function formatTimestampShort(istTimestamp: string | null | undefined): string {
  if (!istTimestamp) return "—";
  return convertISTtoPDTPST(istTimestamp);
}

export function getSourceType(url: string, officialUrl?: string | null): SourceType {
  if (!url) return "platform";
  if (officialUrl && url === officialUrl) return "official";
  if (url.toLowerCase().endsWith(".pdf")) return "pdf";
  const platformDomains = [
    "groww.in", "etf.com", "tmxmoney.com", "tmx.com", "justETF.com",
    "justetf.com", "finance.yahoo.com", "yahoo.com", "hkex.com.hk",
    "sgx.com", "morningstar.com",
  ];
  if (platformDomains.some((d) => url.toLowerCase().includes(d))) return "platform";
  return "official";
}

export function formatCurrency(value: string | null | undefined, currency?: string): string {
  if (!value) return "—";
  return currency ? `${value} ${currency}` : value;
}

export function truncateUrl(url: string, maxLen = 50): string {
  if (url.length <= maxLen) return url;
  const domain = url.replace(/^https?:\/\//, "").split("/")[0];
  return `${domain}/...`;
}

export function groupFundsByCountry<T extends { country: string }>(
  funds: T[]
): Record<string, T[]> {
  return funds.reduce<Record<string, T[]>>((acc, fund) => {
    (acc[fund.country] ??= []).push(fund);
    return acc;
  }, {});
}

export const COUNTRY_ORDER = [
  "India", "USA", "Canada", "China/HK", "Japan", "Singapore", "UK/Europe",
];
