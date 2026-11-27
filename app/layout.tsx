import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "PROJECT NOMAD | Community-Owned Sovereign AI",
  description:
    "An open-source, offline-first community knowledge and AI infrastructure prototype."
};

export default function RootLayout({
  children
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
