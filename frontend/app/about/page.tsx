import { AppShell } from "@/components/layout/AppShell";
import { ShieldCheck } from "lucide-react";

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="flex flex-col gap-3">
      <h2 className="text-[17px] font-semibold text-primary border-b border-border pb-2">{title}</h2>
      <div className="text-[14px] text-primary leading-relaxed">{children}</div>
    </section>
  );
}

export default function AboutPage() {
  return (
    <AppShell hideSourcePanel scrollable>
      <div className="px-4 py-6 max-w-3xl flex flex-col gap-8">
        <div>
          <h1 className="text-[22px] font-bold text-primary">About HealthFundIQ</h1>
          <p className="text-[13px] text-missing-gray mt-1">Methodology, scope, and disclaimer</p>
        </div>

        <Section title="What is HealthFundIQ?">
          <p>
            HealthFundIQ is a <strong>facts-only RAG (Retrieval-Augmented Generation) assistant</strong> for
            global healthcare fund data. It retrieves and presents factual information about healthcare,
            pharma, biotech, and med-tech funds across 7 markets from public sources. Every answer cites
            its source URL, source type, and fetch timestamp.
          </p>
          <p className="mt-2">
            HealthFundIQ is <strong>not</strong> an investment advisor. It does not provide buy/sell
            recommendations, portfolio guidance, return predictions, or personalized financial advice.
          </p>
        </Section>

        <Section title="How does it work?">
          <ol className="list-decimal list-inside space-y-1 text-[13px]">
            <li>Public fund pages and official documents are fetched daily at 10:00 AM IST.</li>
            <li>Pages are parsed and normalized — expense ratio, MER, TER → one vocabulary.</li>
            <li>Chunks are embedded using a local BGE model and stored in ChromaDB.</li>
            <li>Your query is classified (factual/comparison/advice/out-of-scope).</li>
            <li>Relevant chunks are retrieved and reranked (official sources boosted).</li>
            <li>The Groq LLM (llama-3.3-70b-versatile) generates a cited, facts-only answer.</li>
            <li>Every answer references the source URL, type, and timestamps.</li>
          </ol>
        </Section>

        <Section title="Markets covered">
          <ul className="list-disc list-inside space-y-1 text-[13px]">
            {[
              ["🇮🇳 India", "5 funds — HDFC, Nippon, Mirae, SBI, ICICI pharma/healthcare mutual funds"],
              ["🇺🇸 USA", "5 funds — XLV, VHT, IXJ, IBB, FHLC healthcare/biotech ETFs"],
              ["🇨🇦 Canada", "5 funds — HHL, XHC, ZHU, TDOC, MEDX healthcare ETFs"],
              ["🇭🇰 China/HK", "4 funds — 2820.HK, 3174.HK, 3069.HK, KUR China healthcare ETFs"],
              ["🇯🇵 Japan", "4 funds — 1621.T, 2639.T, HEAL, GNOM Japan healthcare ETFs"],
              ["🇸🇬 Singapore", "3 funds — Wellington, Amova, Fidelity healthcare/biotech funds"],
              ["🇬🇧 UK/Europe", "5 funds — iShares, Xtrackers, Lyxor, HSBC UCITS healthcare ETFs"],
            ].map(([market, desc]) => (
              <li key={market}><strong>{market}</strong> — {desc}</li>
            ))}
          </ul>
        </Section>

        <Section title="What fields are extracted?">
          <div className="grid grid-cols-2 gap-1 text-[13px]">
            {[
              "NAV / Price", "AUM / Net Assets", "Expense Ratio / MER / TER",
              "Benchmark", "Risk Rating / Riskometer", "Fund House / Issuer",
              "Fund Manager", "Investment Objective", "Distribution Policy",
              "Top 10 Holdings", "Sector Exposure", "Geographic Exposure",
              "Minimum Investment", "Minimum SIP", "Exit Load / Redemption Fee",
            ].map((f) => (
              <span key={f} className="text-missing-gray">· {f}</span>
            ))}
          </div>
        </Section>

        <Section title="Source types">
          <div className="flex flex-col gap-2 text-[13px]">
            <div className="flex items-start gap-2">
              <span className="badge-official shrink-0">Official</span>
              <span>Issuer, AMC, exchange, or regulator website — factsheet or fund page URL. Cited first in all answers.</span>
            </div>
            <div className="flex items-start gap-2">
              <span className="badge-platform shrink-0">Platform</span>
              <span>Groww, ETF.com, TMX Money, JustETF, Yahoo Finance, HKEX. Used when official URL is unavailable.</span>
            </div>
            <div className="flex items-start gap-2">
              <span className="badge-pdf shrink-0">PDF</span>
              <span>Downloaded PDF factsheet, Fund Facts, or ETF Facts document. High-quality but may be less current.</span>
            </div>
          </div>
        </Section>

        <Section title="What HealthFundIQ cannot do">
          <ul className="list-disc list-inside space-y-1 text-[13px] text-missing-gray">
            <li>Provide investment advice or buy/sell recommendations</li>
            <li>Predict or forecast fund returns or performance</li>
            <li>Build or optimize a portfolio</li>
            <li>Provide personalized financial guidance based on user profile</li>
            <li>Answer questions about funds outside the covered corpus</li>
            <li>Process or store any personal or financial account information</li>
          </ul>
        </Section>

        <Section title="How fresh is the data?">
          <p className="text-[13px]">
            The corpus is refreshed daily at <strong>10:00 AM IST</strong> (displayed as PDT/PST in the UI).
            Every answer shows the fetch timestamp so you know exactly how old the data is.
            If a source failed during the latest refresh, the answer may use data from a previous run —
            this is clearly indicated in the Sources screen.
          </p>
        </Section>

        {/* Full disclaimer */}
        <div className="bg-refusal-bg border border-yellow-200 rounded-card p-5 flex flex-col gap-3">
          <div className="flex items-center gap-2 text-refusal-amber font-semibold">
            <ShieldCheck size={16} /> Disclaimer
          </div>
          <p className="text-[13px] text-refusal-amber leading-relaxed">
            HealthFundIQ provides factual information sourced from public fund pages, official issuer
            documents, and publicly accessible financial data platforms. It does not provide investment
            advice, buy/sell recommendations, portfolio construction guidance, return predictions, or
            personalized financial guidance.
          </p>
          <p className="text-[13px] text-refusal-amber leading-relaxed">
            All information is sourced from public sources and may not reflect the most current fund data.
            Always verify details from official fund documents and consult a qualified financial adviser
            before making investment decisions.
          </p>
          <p className="text-[13px] font-semibold text-refusal-amber">
            HealthFundIQ is a research tool and information assistant only.
          </p>
        </div>
      </div>
    </AppShell>
  );
}
