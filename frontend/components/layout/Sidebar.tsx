"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { MessageCircle, Search, BarChart3, BookOpen, Info } from "lucide-react";
import { cn } from "@/lib/utils";
import { DisclaimerBanner } from "./DisclaimerBanner";
import { ChatHistory } from "./ChatHistory";
import { CorpusHealth } from "./CorpusHealth";

const NAV = [
  { href: "/research", label: "Ask AI", icon: MessageCircle },
  { href: "/funds", label: "Fund Explorer", icon: Search },
  { href: "/compare", label: "Compare Funds", icon: BarChart3 },
  { href: "/sources", label: "Sources", icon: BookOpen },
  { href: "/about", label: "About", icon: Info },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="flex flex-col h-full py-4 px-3 gap-4 overflow-hidden">
      {/* Navigation */}
      <nav className="flex flex-col gap-1 shrink-0">
        {NAV.map(({ href, label, icon: Icon }) => {
          const active = pathname === href || pathname.startsWith(href + "/");
          return (
            <Link
              key={href}
              href={href}
              className={cn(
                "flex items-center gap-2.5 px-3 py-2 rounded-lg text-[13px] font-medium transition-colors",
                active
                  ? "bg-primary-accent/10 text-primary-accent"
                  : "text-missing-gray hover:bg-surface-muted hover:text-primary"
              )}
            >
              <Icon size={15} />
              {label}
            </Link>
          );
        })}
      </nav>

      <div className="border-t border-border shrink-0" />

      {/* Chat History — scrollable, takes remaining space */}
      <div className="flex-1 min-h-0 overflow-y-auto scrollbar-thin">
        <ChatHistory />
      </div>

      {/* Footer */}
      <div className="shrink-0 flex flex-col gap-3 border-t border-border pt-3">
        <DisclaimerBanner />
        <p className="text-[11px] text-missing-gray px-1">
          7 markets · ~34 funds · Daily refresh 10 AM IST
        </p>
        <CorpusHealth />
      </div>
    </aside>
  );
}
