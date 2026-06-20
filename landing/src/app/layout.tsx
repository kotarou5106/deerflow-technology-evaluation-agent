import type { Metadata } from "next";

import "@/styles/globals.css";

export const metadata: Metadata = {
  title: "技术评估 Agent",
  description: "面向新技术、方案、平台、论文与开源项目的系统化评估工作流。",
  icons: {
    icon: [
      { url: "/icon.svg", type: "image/svg+xml" },
      { url: "/favicon.ico", sizes: "64x64" },
    ],
    shortcut: "/favicon.ico",
    apple: "/apple-icon.png",
  },
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="zh-CN" className="dark" suppressHydrationWarning>
      <body>{children}</body>
    </html>
  );
}
