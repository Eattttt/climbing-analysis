import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "攀岩视频分析系统",
  description: "攀岩视频分析、指导、纠正智能体",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="zh-CN">
      <body className="min-h-screen">{children}</body>
    </html>
  );
}
