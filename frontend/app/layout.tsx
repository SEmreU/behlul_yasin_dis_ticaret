import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Yasin Dış Ticaret İstihbarat",
  description: "AI-powered foreign trade intelligence platform",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return children;
}
