import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { AuthProvider } from "@/providers/auth-provider";
import { ThemeProvider } from "@/providers/theme-provider";
import { Toaster } from "@/components/ui/toaster";

const inter = Inter({ subsets: ["latin"], variable: "--font-sans" });

export const metadata: Metadata = {
  title: "Paper Clarity",
  description: "AI-powered clarity for your clauses.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          <AuthProvider>
            {children}
            <Toaster />
          </AuthProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
