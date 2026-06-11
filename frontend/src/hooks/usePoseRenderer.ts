"use client";

import { useRef, useCallback, useEffect } from "react";
import type { PoseFrameResult } from "@/lib/types";
import { POSE_CONNECTIONS } from "@/lib/constants";

export function usePoseRenderer(
  canvasRef: React.RefObject<HTMLCanvasElement | null>,
  poses: PoseFrameResult[],
  fps: number,
  sampleRate: number = 5,
) {
  const animRef = useRef<number>(0);

  const findPoseForTime = useCallback(
    (timeMs: number): PoseFrameResult | null => {
      if (!poses.length) return null;
      const targetFrame = (timeMs / 1000) * fps;
      let best = poses[0];
      let bestDist = Math.abs(best.frame_number - targetFrame);
      for (const p of poses) {
        const dist = Math.abs(p.frame_number - targetFrame);
        if (dist < bestDist) {
          best = p;
          bestDist = dist;
        }
      }
      return best;
    },
    [poses, fps],
  );

  const draw = useCallback(
    (video: HTMLVideoElement, canvas: HTMLCanvasElement) => {
      const ctx = canvas.getContext("2d");
      if (!ctx) return;

      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;

      ctx.clearRect(0, 0, canvas.width, canvas.height);

      const timeMs = video.currentTime * 1000;
      const pose = findPoseForTime(timeMs);
      if (!pose || pose.confidence === 0) return;

      const kps = pose.landmarks_2d;
      const w = canvas.width;
      const h = canvas.height;

      for (const [i, j] of POSE_CONNECTIONS) {
        const a = kps[i];
        const b = kps[j];
        if (!a || !b) continue;
        if (a.visibility < 0.3 || b.visibility < 0.3) continue;

        const avgVis = (a.visibility + b.visibility) / 2;
        const color =
          avgVis > 0.7
            ? "#22c55e"
            : avgVis > 0.4
              ? "#eab308"
              : "#ef4444";

        ctx.beginPath();
        ctx.moveTo(a.x * w, a.y * h);
        ctx.lineTo(b.x * w, b.y * h);
        ctx.strokeStyle = color;
        ctx.lineWidth = 3;
        ctx.stroke();
      }

      for (let i = 0; i < kps.length; i++) {
        const kp = kps[i];
        if (!kp || kp.visibility < 0.3) continue;

        ctx.beginPath();
        ctx.arc(kp.x * w, kp.y * h, 4, 0, 2 * Math.PI);
        ctx.fillStyle = kp.visibility > 0.7 ? "#22c55e" : "#eab308";
        ctx.fill();
      }
    },
    [findPoseForTime],
  );

  return { draw };
}
