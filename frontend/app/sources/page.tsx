import { Suspense } from "react";
import { AppShell } from "@/components/layout/AppShell";
import { CorpusStatusTable } from "@/components/sources/CorpusStatusTable";

export default function SourcesPage() {
  return (
    <AppShell hideSourcePanel scrollable>
      <div className="px-4 py-6">
        <Suspense>
          <CorpusStatusTable />
        </Suspense>
      </div>
    </AppShell>
  );
}
