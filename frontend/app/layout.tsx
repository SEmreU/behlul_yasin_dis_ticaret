import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "TradeRadar - Dış Ticaret İstihbarat Platformu",
  description: "AI-powered foreign trade intelligence platform",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return children as React.ReactElement;
}
