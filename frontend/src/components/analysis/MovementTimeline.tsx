"use client";

import type { MovementEvent } from "@/lib/types";
import { MOVEMENT_COLORS } from "@/lib/constants";

type Props = {
  movements: MovementEvent[];
  duration: number;
  fps: number;
  onSeek: (time: number) => void;
};

export default function MovementTimeline({ movements, duration, fps, onSeek }: Props) {
  if (!movements.length) {
    return (
      <div className="bg-gray-50 rounded-xl p-4">
        <p className="text-gray-500 text-sm text-center">未检测到明显动作变化</p>
      </div>
    );
  }

  return (
    <div className="bg-gray-50 rounded-xl p-4">
      <h3 className="text-sm font-medium text-gray-700 mb-3">动作时间线</h3>
      <div className="relative h-10 bg-gray-200 rounded-lg overflow-hidden">
        {movements.map((m, i) => {
          const start = (m.start_frame / fps) / duration * 100;
          const end = (m.end_frame / fps) / duration * 100;
          const width = Math.max(end - start, 0.5);
          return (
            <div
              key={i}
              className="absolute top-0 h-full flex items-center justify-center cursor-pointer hover:opacity-80 transition-opacity"
              style={{
                left: `${start}%`,
                width: `${width}%`,
                backgroundColor: MOVEMENT_COLORS[m.type] || "#6b7280",
              }}
              onClick={() => onSeek(m.start_frame / fps)}
              title={m.label_cn}
            >
              {width > 3 && (
                <span className="text-white text-xs font-medium truncate px-1">
                  {m.label_cn}
                </span>
              )}
            </div>
          );
        })}
      </div>
      <div className="flex flex-wrap gap-2 mt-3">
        {Array.from(new Set(movements.map((m) => m.type))).map((type) => (
          <span
            key={type}
            className="inline-flex items-center gap-1 text-xs px-2 py-1 rounded-full bg-white border"
          >
            <span
              className="w-2 h-2 rounded-full"
              style={{ backgroundColor: MOVEMENT_COLORS[type] || "#6b7280" }}
            />
            {movements.find((m) => m.type === type)?.label_cn || type}
          </span>
        ))}
      </div>
    </div>
  );
}
