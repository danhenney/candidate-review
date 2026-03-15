import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "후보 평가 시스템 | CJ온큐베이팅",
  description: "CJ온스타일 온큐베이팅 지원자 심사 도구",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ko">
      <body className="bg-gray-50 min-h-screen">
        <nav className="bg-white border-b border-gray-200 px-6 py-4">
          <div className="max-w-7xl mx-auto flex items-center justify-between">
            <a href="/" className="text-xl font-bold text-gray-900">
              후보 평가 시스템
            </a>
            <div className="flex gap-6">
              <a
                href="/upload"
                className="text-gray-600 hover:text-gray-900 text-sm font-medium"
              >
                1. 서류 입력
              </a>
              <a
                href="/"
                className="text-gray-600 hover:text-gray-900 text-sm font-medium"
              >
                2. 개별 리뷰
              </a>
              <a
                href="/"
                className="text-gray-600 hover:text-gray-900 text-sm font-medium"
              >
                3. 전체 요약
              </a>
            </div>
          </div>
        </nav>
        <main className="max-w-7xl mx-auto px-6 py-8">{children}</main>
      </body>
    </html>
  );
}
