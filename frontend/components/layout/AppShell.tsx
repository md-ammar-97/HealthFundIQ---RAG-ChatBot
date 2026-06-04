import { Sidebar } from "./Sidebar";
import { SourcePanel } from "./SourcePanel";
import type { SourceCardData } from "@/lib/types";

interface Props {
  children: React.ReactNode;
  sources?: SourceCardData[];
  hideSidebar?: boolean;
  hideSourcePanel?: boolean;
  /** Pass true for pages that need the main area to be scrollable (all pages except /research) */
  scrollable?: boolean;
}

export function AppShell({
  children,
  sources,
  hideSidebar = false,
  hideSourcePanel = false,
  scrollable = false,
}: Props) {
  return (
    <div className="flex flex-1 overflow-hidden">
      {/* LEFT SIDEBAR — 22% / 3 cols */}
      {!hideSidebar && (
        <div className="hidden lg:flex w-[22%] min-w-[200px] max-w-[260px] shrink-0 border-r border-border bg-surface h-[calc(100vh-56px)] sticky top-14">
          <div className="w-full">
            <Sidebar />
          </div>
        </div>
      )}

      {/* MAIN WORKSPACE — 53% / 6 cols */}
      <main
        className={`flex-1 min-w-0 h-[calc(100vh-56px)] ${
          scrollable ? "overflow-y-auto" : "overflow-hidden"
        } ${hideSidebar ? "max-w-3xl mx-auto" : ""}`}
      >
        {children}
      </main>

      {/* RIGHT SOURCE PANEL — 25% / 3 cols */}
      {!hideSourcePanel && (
        <div className="hidden xl:flex w-[25%] min-w-[220px] max-w-[300px] shrink-0 border-l border-border bg-surface h-[calc(100vh-56px)] sticky top-14">
          <div className="w-full">
            <SourcePanel sources={sources} />
          </div>
        </div>
      )}
    </div>
  );
}
