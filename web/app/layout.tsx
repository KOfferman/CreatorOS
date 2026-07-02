import "./globals.css";
import type { Metadata } from "next";
import React from "react";
import Script from "next/script";

export const metadata: Metadata = {
  title: "CreatorOS AI Platform",
  description: "Frontend for CreatorOS AI platform"
};

export default function RootLayout({
  children
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <Script src="https://cdn.tailwindcss.com" strategy="beforeInteractive" />
        {children}
      </body>
    </html>
  );
}
