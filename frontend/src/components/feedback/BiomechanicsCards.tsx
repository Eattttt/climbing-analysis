"use client";

import type { BiomechanicsFeedbackItem } from "@/lib/types";
import { SEVERITY_COLORS, SEVERITY_ICONS } from "@/lib/constants";

type Props = {
  feedback: BiomechanicsFeedbackItem[];
  onJumpToFrame?: (frame: number) => void;
};

export default function BiomechanicsCards({ feedback, onJumpToFrame }: Props) {
  if (!feedback.length) return null;

  return (
    <div className="space-y-3">
      <h3 className="text-lg font-medium text-gray-800">生物力学分析</h3>
      <div className="grid gap-3">
        {feedback.map((item, i) => (
          <div
            key={i}
            className={`p-4 rounded-xl border ${SEVERITY_COLORS[item.severity] || "bg-gray-50 border-gray-200"}`}
          >
            <div className="flex items-start gap-3">
              <span className="text-lg flex-shrink-0">
                {SEVERITY_ICONS[item.severity] || "ℹ"}
              </span>
              <div className="flex-1 min-w-0">
                <p className="font-medium">{item.title}</p>
                <p className="text-sm mt-1 opacity-80">{item.description}</p>
                {item.frames.length > 0 && onJumpToFrame && (
                  <button
                    onClick={() => onJumpToFrame(item.frames[0])}
                    className="mt-2 text-xs underline opacity-60 hover:opacity-100 transition-opacity"
                  >
                    跳转到相关片段
                  </button>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
