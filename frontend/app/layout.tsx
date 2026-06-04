import type { Metadata } from "next";
import { Suspense } from "react";
import "./globals.css";
import { Providers } from "./providers";
import { TopBar } from "@/components/layout/TopBar";

export const metadata: Metadata = {
  title: "HealthFundIQ — Global Healthcare Funds Research",
  description:
    "Ask. Compare. Verify global healthcare funds — with facts, not financial advice. Covers India, USA, Canada, China/HK, Japan, Singapore, and UK/Europe.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="min-h-screen bg-background font-sans antialiased">
        <Providers>
          <div className="flex flex-col min-h-screen">
            <Suspense>
              <TopBar />
            </Suspense>
            <Suspense>{children}</Suspense>
          </div>
        </Providers>
      </body>
    </html>
  );
}
