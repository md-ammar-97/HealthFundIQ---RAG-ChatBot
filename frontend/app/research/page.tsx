"use client";

import { useEffect, useRef, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { motion, AnimatePresence } from "motion/react";
import { AppShell } from "@/components/layout/AppShell";
import { HealthcareBackdrop } from "@/components/backdrop/HealthcareBackdrop";
import { QueryInput } from "@/components/chat/QueryInput";
import { PromptChips } from "@/components/chat/PromptChips";
import { AnswerCard } from "@/components/chat/AnswerCard";
import { LoadingState } from "@/components/chat/LoadingState";
import { useChat } from "@/hooks/useChat";
import { useChatStore } from "@/stores/chat";
import type { ChatMessage } from "@/lib/types";

function ResearchContent() {
  const searchParams = useSearchParams();
  const { mutate, isPending } = useChat();
  const { messages, addMessage } = useChatStore();

  const scrollRef = useRef<HTMLDivElement>(null);
  const didAutoSubmit = useRef(false);

  const initialQuery = searchParams.get("q");
  const fundId = searchParams.get("fund_id");

  // Auto-scroll to bottom whenever messages or pending state changes
  useEffect(() => {
    const el = scrollRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [messages, isPending]);

  // Pre-fill query from URL on first load
  useEffect(() => {
    if (initialQuery && !didAutoSubmit.current) {
      didAutoSubmit.current = true;
      handleQuery(initialQuery);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [initialQuery]);

  function handleQuery(query: string) {
    const userMsg: ChatMessage = {
      id: Date.now().toString(),
      role: "user",
      content: query,
      timestamp: new Date(),
    };
    addMessage(userMsg);
    // onSuccess / onError are handled globally in useChat hook —
    // guaranteed to fire even if this component remounts mid-request.
    mutate({ query, fund_id: fundId || undefined });
  }

  const hasMessages = messages.length > 0;

  return (
    <>
      <HealthcareBackdrop />
      <AppShell hideSourcePanel>
        <div className="relative z-10 flex flex-col" style={{ height: "calc(100vh - 56px)" }}>

          {/* ── Scrollable message area ── */}
          <div
            ref={scrollRef}
            className="flex-1 overflow-y-auto scrollbar-thin px-4 pt-4 pb-2"
          >
            {/* Welcome / example chips before first message */}
            <AnimatePresence>
              {!hasMessages && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="flex flex-col gap-4 py-8"
                >
                  <div className="text-center">
                    <h2 className="text-[22px] font-bold text-primary mb-1">Ask AI</h2>
                    <p className="text-[14px] text-missing-gray">
                      Factual fund research with cited sources
                    </p>
                  </div>
                  <PromptChips onSelect={handleQuery} />
                </motion.div>
              )}
            </AnimatePresence>

            {/* Chat messages */}
            <div className="flex flex-col gap-4">
              {messages.map((msg) => (
                <div key={msg.id}>
                  {msg.role === "user" ? (
                    <div className="flex justify-end">
                      <div className="bg-primary-accent text-white rounded-card rounded-br-sm px-4 py-2.5 max-w-[80%] text-[14px]">
                        {msg.content}
                      </div>
                    </div>
                  ) : (
                    msg.response && (
                      <AnswerCard response={msg.response} onFollowUp={handleQuery} />
                    )
                  )}
                </div>
              ))}

              {/* Loading state */}
              <AnimatePresence>
                {isPending && (
                  <motion.div
                    key="loading"
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0 }}
                    transition={{ duration: 0.1 }}
                  >
                    <LoadingState />
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>

          {/* ── Docked input — always visible, never inside scroll area ── */}
          <div className="shrink-0 px-4 py-3 border-t border-border bg-background/90 backdrop-blur-sm">
            <QueryInput onSubmit={handleQuery} isLoading={isPending} />
          </div>

        </div>
      </AppShell>
    </>
  );
}

export default function ResearchPage() {
  return (
    <Suspense fallback={
      <div className="flex items-center justify-center h-[calc(100vh-56px)] text-missing-gray text-[14px]">
        Loading…
      </div>
    }>
      <ResearchContent />
    </Suspense>
  );
}
