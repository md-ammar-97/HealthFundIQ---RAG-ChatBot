"use client";

import { useMutation } from "@tanstack/react-query";
import { postChat } from "@/lib/api";
import { useChatStore } from "@/stores/chat";
import { getSourceType } from "@/lib/utils";
import type { ChatRequest } from "@/lib/types";

export function useChat() {
  const { addMessage, setSources } = useChatStore();

  return useMutation({
    mutationFn: (req: ChatRequest) => postChat(req),

    // Global callbacks — guaranteed to fire even if the component that called
    // mutate() remounts mid-request (Suspense re-evaluation with useSearchParams).
    onSuccess: (response) => {
      addMessage({
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: response.answer,
        response,
        timestamp: new Date(),
      });

      const newSources = [];
      if (response.source_url) {
        newSources.push({
          url: response.source_url,
          sourceType: getSourceType(response.source_url, response.source_url),
          lastUpdated: response.last_updated ?? undefined,
          fetchTimestamp: response.fetch_timestamp ?? undefined,
          answerExcerpt: response.answer.slice(0, 200),
        });
      }
      if (response.platform_url && response.platform_url !== response.source_url) {
        newSources.push({
          url: response.platform_url,
          sourceType: "platform" as const,
          fetchTimestamp: response.fetch_timestamp ?? undefined,
        });
      }
      setSources(newSources);
    },

    onError: (err) => {
      const msg =
        err instanceof Error ? err.message : "HealthFundIQ is temporarily unavailable.";
      addMessage({
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: msg,
        response: {
          answer: msg,
          source_url: null,
          platform_url: null,
          last_updated: null,
          fetch_timestamp: null,
          is_refusal: false,
          intent: "ERROR",
          missing_data: false,
          fund_name: null,
        },
        timestamp: new Date(),
      });
    },
  });
}
