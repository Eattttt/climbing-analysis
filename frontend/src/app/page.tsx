"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { uploadVideo } from "@/lib/api";

export default function HomePage() {
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [dragOver, setDragOver] = useState(false);

  const handleFile = (f: File) => {
    const ext = f.name.split(".").pop()?.toLowerCase();
    if (!ext || !["mp4", "mov", "avi", "mkv"].includes(ext)) {
      setError("请上传 MP4 或 MOV 格式的视频文件");
      return;
    }
    if (f.size > 500 * 1024 * 1024) {
      setError("文件过大，最大支持 500MB");
      return;
    }
    setFile(f);
    setError(null);
  };

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    setError(null);
    try {
      const res = await uploadVideo(file);
      router.push(`/analysis/${res.video_id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "上传失败");
    } finally {
      setUploading(false);
    }
  };

  return (
    <main className="min-h-screen flex flex-col items-center justify-center p-8">
      <div className="max-w-2xl w-full">
        <h1 className="text-4xl font-bold text-center mb-2">🧗 攀岩视频分析系统</h1>
        <p className="text-gray-500 text-center mb-12">
          上传攀岩视频，获取专业的技术分析和教练指导
        </p>

        <div
          className={`border-2 border-dashed rounded-2xl p-16 text-center transition-colors cursor-pointer ${
            dragOver
              ? "border-green-500 bg-green-50"
              : file
                ? "border-green-400 bg-green-50/50"
                : "border-gray-300 hover:border-gray-400"
          }`}
          onDragOver={(e) => {
            e.preventDefault();
            setDragOver(true);
          }}
          onDragLeave={() => setDragOver(false)}
          onDrop={(e) => {
            e.preventDefault();
            setDragOver(false);
            if (e.dataTransfer.files[0]) handleFile(e.dataTransfer.files[0]);
          }}
          onClick={() => {
            const input = document.createElement("input");
            input.type = "file";
            input.accept = "video/mp4,video/quicktime,video/*";
            input.onchange = (e) => {
              const target = e.target as HTMLInputElement;
              if (target.files?.[0]) handleFile(target.files[0]);
            };
            input.click();
          }}
        >
          {file ? (
            <div>
              <p className="text-lg font-medium text-green-700">已选择文件</p>
              <p className="text-gray-600 mt-1">{file.name}</p>
              <p className="text-gray-400 text-sm mt-1">
                {(file.size / (1024 * 1024)).toFixed(1)} MB
              </p>
            </div>
          ) : (
            <div>
              <p className="text-6xl mb-4">📹</p>
              <p className="text-lg font-medium text-gray-700">
                拖放视频文件到此处
              </p>
              <p className="text-gray-400 mt-2">或点击选择文件</p>
              <p className="text-gray-400 text-sm mt-4">支持 MP4、MOV 格式，最大 500MB</p>
            </div>
          )}
        </div>

        {error && (
          <p className="text-red-500 text-center mt-4">{error}</p>
        )}

        {file && (
          <button
            onClick={handleUpload}
            disabled={uploading}
            className="mt-6 w-full py-4 bg-green-600 text-white text-lg font-medium rounded-xl hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {uploading ? "上传中..." : "开始分析"}
          </button>
        )}

        <div className="mt-12 grid grid-cols-3 gap-6 text-center">
          <div className="p-4">
            <p className="text-2xl mb-2">🎯</p>
            <p className="font-medium">姿态估计</p>
            <p className="text-sm text-gray-500">精准追踪全身33个关键点</p>
          </div>
          <div className="p-4">
            <p className="text-2xl mb-2">📊</p>
            <p className="font-medium">动作分析</p>
            <p className="text-sm text-gray-500">自动识别旗式、折膝等动作</p>
          </div>
          <div className="p-4">
            <p className="text-2xl mb-2">🤖</p>
            <p className="font-medium">AI教练</p>
            <p className="text-sm text-gray-500">专业的中文技术指导</p>
          </div>
        </div>
      </div>
    </main>
  );
}
