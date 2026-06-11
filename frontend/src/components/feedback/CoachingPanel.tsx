"use client";

import ReactMarkdown from "react-markdown";

type Props = {
  summary: string | null;
};

export default function CoachingPanel({ summary }: Props) {
  if (!summary) {
    return (
      <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl p-6 border border-green-100">
        <h3 className="text-lg font-medium text-green-800 mb-2">🤖 AI教练分析</h3>
        <div className="animate-pulse space-y-2">
          <div className="h-4 bg-green-200 rounded w-3/4" />
          <div className="h-4 bg-green-200 rounded w-1/2" />
          <div className="h-4 bg-green-200 rounded w-5/6" />
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl p-6 border border-green-100">
      <h3 className="text-lg font-medium text-green-800 mb-4">🤖 AI教练分析</h3>
      <div className="prose prose-sm prose-green max-w-none">
        <ReactMarkdown>{summary}</ReactMarkdown>
      </div>
    </div>
  );
}
