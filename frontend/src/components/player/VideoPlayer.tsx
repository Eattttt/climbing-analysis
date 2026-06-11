"use client";

import { useRef, useEffect, useState } from "react";
import { usePoseRenderer } from "@/hooks/usePoseRenderer";
import type { PoseFrameResult } from "@/lib/types";

type Props = {
  videoUrl: string;
  poses: PoseFrameResult[];
  fps: number;
  seekTo?: number | null;
};

export default function VideoPlayer({ videoUrl, poses, fps, seekTo }: Props) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [playing, setPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [aspectRatio, setAspectRatio] = useState(16 / 9);

  const { draw } = usePoseRenderer(canvasRef, poses, fps);

  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    const updateCanvasBounds = () => {
      const container = containerRef.current;
      const canvas = canvasRef.current;
      if (!container || !canvas) return;

      const cw = container.clientWidth;
      const ch = container.clientHeight;
      const vw = video.videoWidth;
      const vh = video.videoHeight;
      if (!vw || !vh) return;

      const containerAR = cw / ch;
      const videoAR = vw / vh;

      let displayW: number, displayH: number, offsetX: number, offsetY: number;

      if (videoAR > containerAR) {
        displayW = cw;
        displayH = cw / videoAR;
        offsetX = 0;
        offsetY = (ch - displayH) / 2;
      } else {
        displayH = ch;
        displayW = ch * videoAR;
        offsetX = (cw - displayW) / 2;
        offsetY = 0;
      }

      canvas.style.left = `${offsetX}px`;
      canvas.style.top = `${offsetY}px`;
      canvas.style.width = `${displayW}px`;
      canvas.style.height = `${displayH}px`;
    };

    const onFrame = () => {
      if (canvasRef.current) {
        draw(video, canvasRef.current);
      }
      setCurrentTime(video.currentTime);
      requestAnimationFrame(onFrame);
    };

    const onLoaded = () => {
      setDuration(video.duration);
      const ar = video.videoWidth / video.videoHeight;
      if (ar > 0) setAspectRatio(ar);
      requestAnimationFrame(onFrame);
      updateCanvasBounds();
    };

    const onResize = () => updateCanvasBounds();

    video.addEventListener("loadedmetadata", onLoaded);
    window.addEventListener("resize", onResize);

    const observer = new ResizeObserver(updateCanvasBounds);
    if (containerRef.current) observer.observe(containerRef.current);

    return () => {
      video.removeEventListener("loadedmetadata", onLoaded);
      window.removeEventListener("resize", onResize);
      observer.disconnect();
    };
  }, [draw]);

  useEffect(() => {
    if (seekTo != null && videoRef.current) {
      videoRef.current.currentTime = seekTo;
    }
  }, [seekTo]);

  const togglePlay = () => {
    const video = videoRef.current;
    if (!video) return;
    if (video.paused) {
      video.play();
      setPlaying(true);
    } else {
      video.pause();
      setPlaying(false);
    }
  };

  const formatTime = (s: number) => {
    const m = Math.floor(s / 60);
    const sec = Math.floor(s % 60);
    return `${m}:${sec.toString().padStart(2, "0")}`;
  };

  return (
    <div className="rounded-xl overflow-hidden bg-black">
      <div
        ref={containerRef}
        className="relative w-full cursor-pointer"
        style={{ aspectRatio: aspectRatio }}
        onClick={togglePlay}
      >
        <video
          ref={videoRef}
          src={videoUrl}
          className="absolute inset-0 w-full h-full object-contain"
          playsInline
        />
        <canvas
          ref={canvasRef}
          className="absolute pointer-events-none"
        />
        {!playing && (
          <div className="absolute inset-0 flex items-center justify-center bg-black/30 z-10">
            <span className="text-white text-5xl">▶</span>
          </div>
        )}
      </div>

      <div className="bg-gray-900 px-4 py-3 flex items-center gap-4">
        <button
          onClick={togglePlay}
          className="text-white hover:text-green-400 transition-colors"
        >
          {playing ? "⏸" : "▶"}
        </button>

        <span className="text-gray-400 text-sm font-mono">
          {formatTime(currentTime)}
        </span>

        <input
          type="range"
          min={0}
          max={duration || 0}
          step={0.1}
          value={currentTime}
          onChange={(e) => {
            const t = parseFloat(e.target.value);
            if (videoRef.current) videoRef.current.currentTime = t;
            setCurrentTime(t);
          }}
          className="flex-1 h-1 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-green-500"
        />

        <span className="text-gray-400 text-sm font-mono">
          {formatTime(duration)}
        </span>
      </div>
    </div>
  );
}
