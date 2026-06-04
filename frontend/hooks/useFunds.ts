"use client";

import { useQuery } from "@tanstack/react-query";
import { fetchFunds } from "@/lib/api";

export function useFunds(country?: string | null) {
  return useQuery({
    queryKey: ["funds", country ?? "all"],
    queryFn: () => fetchFunds(country),
    staleTime: 5 * 60_000,
    retry: 2,
  });
}
