"use client";

import { useQuery } from "@tanstack/react-query";
import { fetchFundDetails } from "@/lib/api";

export function useFundDetails(fundId: string | null | undefined) {
  return useQuery({
    queryKey: ["fund-details", fundId],
    queryFn: () => fetchFundDetails(fundId!),
    enabled: !!fundId,
    staleTime: 10 * 60_000,
    retry: 1,
  });
}
