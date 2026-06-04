"use client";

import { useRouter } from "next/navigation";
import { motion } from "motion/react";
import { Activity, Globe, TrendingUp, ShieldCheck } from "lucide-react";
import { PromptChips } from "@/components/chat/PromptChips";
import { QueryInput } from "@/components/chat/QueryInput";
import { LanguageTypewriter } from "@/components/chat/LanguageTypewriter";
import { DisclaimerBanner } from "@/components/layout/DisclaimerBanner";

const COVERAGE = [
  { label: "India", flag: "🇮🇳" },
  { label: "USA", flag: "🇺🇸" },
  { label: "Canada", flag: "🇨🇦" },
  { label: "China/HK", flag: "🇭🇰" },
  { label: "Japan", flag: "🇯🇵" },
  { label: "Singapore", flag: "🇸🇬" },
  { label: "UK/Europe", flag: "🇬🇧" },
];

const FEATURES = [
  { icon: Activity, label: "~34 healthcare funds" },
  { icon: Globe, label: "7 global markets" },
  { icon: TrendingUp, label: "Daily refresh 10 AM IST" },
  { icon: ShieldCheck, label: "Every answer cites its source" },
];

export default function HomePage() {
  const router = useRouter();

  function handleQuery(query: string) {
    router.push(`/research?q=${encodeURIComponent(query)}`);
  }

  return (
    <div className="min-h-[calc(100vh-56px)] flex flex-col items-center justify-center px-4 py-12 bg-background">
      <div className="w-full max-w-2xl flex flex-col gap-8">
        {/* Hero */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          className="flex flex-col gap-4 text-center"
        >
          <div className="flex items-center justify-center gap-3 mb-2">
            <motion.div
              className="flex items-center justify-center w-12 h-12 rounded-xl bg-brand-teal text-white"
              animate={{ scale: [1, 1.06, 1, 1.04, 1] }}
              transition={{ duration: 1.4, repeat: Infinity, ease: "easeInOut" }}
            >
              <Activity size={24} strokeWidth={2.5} />
            </motion.div>
            <h1 className="text-[32px] font-bold text-primary leading-tight">
              HealthFund<span className="text-brand-teal">IQ</span>
            </h1>
          </div>
          <p className="text-[20px] font-semibold text-primary leading-tight text-balance">
            Ask. Compare. Verify global healthcare funds —<br />
            <span className="text-missing-gray font-normal text-[17px]">
              with facts, not financial advice.
            </span>
          </p>
          <p className="text-[14px] text-missing-gray max-w-lg mx-auto leading-relaxed">
            HealthFundIQ retrieves and presents factual information about healthcare, pharma, biotech,
            and med-tech funds across 7 markets. Every answer cites its source.
          </p>
        </motion.div>

        {/* Multilingual support indicator */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.4, delay: 0.08 }}
        >
          <LanguageTypewriter />
        </motion.div>

        {/* Query input */}
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.1 }}
        >
          <QueryInput onSubmit={handleQuery} placeholder="Ask a factual question about a healthcare fund…" />
        </motion.div>

        {/* Example chips */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.4, delay: 0.2 }}
          className="flex flex-col gap-2"
        >
          <p className="text-[12px] text-missing-gray text-center">Example questions:</p>
          <div className="flex flex-wrap justify-center gap-2">
            <PromptChips onSelect={handleQuery} />
          </div>
        </motion.div>

        {/* Disclaimer */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.4, delay: 0.3 }}
        >
          <DisclaimerBanner />
        </motion.div>

        {/* Coverage strip */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.4, delay: 0.4 }}
          className="flex flex-col gap-3"
        >
          <div className="flex justify-center gap-4 flex-wrap">
            {FEATURES.map(({ icon: Icon, label }) => (
              <div key={label} className="flex items-center gap-1.5 text-[12px] text-missing-gray">
                <Icon size={13} className="text-brand-teal" />
                {label}
              </div>
            ))}
          </div>
          <div className="flex justify-center flex-wrap gap-2">
            {COVERAGE.map(({ flag, label }) => (
              <span key={label} className="text-[13px] text-missing-gray">
                {flag} {label}
              </span>
            ))}
          </div>
        </motion.div>
      </div>
    </div>
  );
}
