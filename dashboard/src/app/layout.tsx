import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Providers } from "@/lib/providers";
import { AsyncErrorBoundary } from "@/components/ui/async-error-boundary";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Headless PM Dashboard",
  description: "Real-time project management dashboard for LLM agents",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className} suppressHydrationWarning>
        <AsyncErrorBoundary>
          <Providers>{children}</Providers>
        </AsyncErrorBoundary>
      </body>
    </html>
  );
}
