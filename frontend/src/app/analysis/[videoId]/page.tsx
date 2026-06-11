"use client";

import { useState } from "react";
import { useParams } from "next/navigation";
import { useVideoAnalysis } from "@/hooks/useVideoAnalysis";
import { getVideoFileUrl, getExportVideoUrl } from "@/lib/api";
import VideoPlayer from "@/components/player/VideoPlayer";
import MovementTimeline from "@/components/analysis/MovementTimeline";
import BiomechanicsCards from "@/components/feedback/BiomechanicsCards";
import CoachingPanel from "@/components/feedback/CoachingPanel";
import ChatInterface from "@/components/feedback/ChatInterface";

export default function AnalysisPage() {
  const params = useParams();
  const videoId = params.videoId as string;
  const { status, results, isLoading, error } = useVideoAnalysis(videoId);
  const [seekTo, setSeekTo] = useState<number | null>(null);
  const [exporting, setExporting] = useState(false);

  const handleExport = () => {
    setExporting(true);
    window.open(getExportVideoUrl(videoId), "_blank");
    setTimeout(() => setExporting(false), 3000);
  };

  if (error) {
    return (
      <main className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-6xl mb-4">❌</p>
          <h1 className="text-2xl font-bold text-red-600 mb-2">分析失败</h1>
          <p className="text-gray-600">{error}</p>
          <a
            href="/"
            className="mt-6 inline-block px-6 py-3 bg-green-600 text-white rounded-xl hover:bg-green-700"
          >
            重新上传
          </a>
        </div>
      </main>
    );
  }

  if (isLoading || !results) {
    return (
      <main className="min-h-screen flex items-center justify-center">
        <div className="text-center max-w-md">
          <div className="text-6xl mb-6 animate-bounce">🧗</div>
          <h1 className="text-2xl font-bold mb-4">正在分析视频</h1>
          <div className="w-full bg-gray-200 rounded-full h-3 mb-4">
            <div
              className="bg-green-600 h-3 rounded-full transition-all duration-500"
              style={{ width: `${(status?.progress ?? 0) * 100}%` }}
            />
          </div>
          <p className="text-gray-600">{status?.stage_name || "准备中..."}</p>
          <p className="text-gray-400 text-sm mt-2">
            {Math.round((status?.progress ?? 0) * 100)}% 完成
          </p>
        </div>
      </main>
    );
  }

  const handleSeek = (time: number) => {
    setSeekTo(time);
    setTimeout(() => setSeekTo(null), 100);
  };

  return (
    <main className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold text-gray-900">🧗 攀岩视频分析</h1>
            <p className="text-sm text-gray-500">{results.video.filename}</p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={handleExport}
              disabled={exporting}
              className="px-4 py-2 text-sm bg-green-600 text-white hover:bg-green-700 rounded-lg transition-colors disabled:opacity-50"
            >
              {exporting ? "导出中..." : "导出视频"}
            </button>
            <a
              href="/"
              className="px-4 py-2 text-sm bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
            >
              分析新视频
            </a>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-6 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-4">
            <VideoPlayer
              videoUrl={getVideoFileUrl(videoId)}
              poses={results.poses}
              fps={results.video.fps}
              seekTo={seekTo}
            />

            <MovementTimeline
              movements={results.movements}
              duration={results.video.duration}
              fps={results.video.fps}
              onSeek={handleSeek}
            />

            {Object.keys(results.joint_angle_stats).length > 0 && (
              <div className="bg-white rounded-xl p-4 border border-gray-200">
                <h3 className="text-sm font-medium text-gray-700 mb-3">关节角度统计</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  {Object.entries(results.joint_angle_stats).map(([joint, stat]) => (
                    <div key={joint} className="text-center p-2 bg-gray-50 rounded-lg">
                      <p className="text-xs text-gray-500">{joint.replace(/_/g, " ")}</p>
                      <p className="text-lg font-bold text-gray-800">{stat.avg.toFixed(0)}°</p>
                      <p className="text-xs text-gray-400">
                        {stat.min.toFixed(0)}° - {stat.max.toFixed(0)}°
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          <div className="space-y-4">
            <BiomechanicsCards
              feedback={results.biomechanics_feedback}
              onJumpToFrame={(frame) => handleSeek(frame / results.video.fps)}
            />

            <CoachingPanel summary={results.coaching_summary} />

            <ChatInterface videoId={videoId} />
          </div>
        </div>
      </div>
    </main>
  );
}
