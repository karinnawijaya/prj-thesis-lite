import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "ArtWeave Lite",
  description: "ArtWeave Lite — compare artworks with concise summaries.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-skywash text-slate-900">
        {children}
      </body>
    </html>
  );
}