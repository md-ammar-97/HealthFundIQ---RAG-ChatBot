"use client";

import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";
import type { ChatMessage, SourceCardData } from "@/lib/types";

export interface HistoryEntry {
  id: string;
  query: string;
  timestamp: string; // ISO string — safe for JSON serialization
}

const THIRTY_DAYS_MS = 30 * 24 * 60 * 60 * 1000;

function pruneOld(entries: HistoryEntry[]): HistoryEntry[] {
  return entries.filter(
    (e) => Date.now() - new Date(e.timestamp).getTime() < THIRTY_DAYS_MS
  );
}

interface ChatStore {
  messages: ChatMessage[];
  sources: SourceCardData[];
  history: HistoryEntry[];
  addMessage: (msg: ChatMessage) => void;
  setSources: (sources: SourceCardData[]) => void;
  clearMessages: () => void;
  clearHistory: () => void;
}

export const useChatStore = create<ChatStore>()(
  persist(
    (set) => ({
      messages: [],
      sources: [],
      history: [],

      addMessage: (msg) => {
        set((s) => ({ messages: [...s.messages, msg] }));
        // Persist user queries to 30-day history
        if (msg.role === "user") {
          const entry: HistoryEntry = {
            id: msg.id,
            query: msg.content,
            timestamp: new Date().toISOString(),
          };
          set((s) => ({
            history: pruneOld([entry, ...s.history]),
          }));
        }
      },

      setSources: (sources) => set({ sources }),
      clearMessages: () => set({ messages: [], sources: [] }),
      clearHistory: () => set({ history: [] }),
    }),
    {
      name: "healthfundiq-chat",
      storage: createJSONStorage(() => localStorage),
      // Only persist history — messages are in-memory (current session only)
      partialize: (s) => ({ history: s.history }),
      onRehydrateStorage: () => (state) => {
        if (state) {
          state.history = pruneOld(state.history);
        }
      },
    }
  )
);
