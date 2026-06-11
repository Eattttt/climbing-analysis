import type {
  VideoUploadResponse,
  VideoStatusResponse,
  VideoResultsResponse,
} from "./types";

const BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";

export async function uploadVideo(file: File): Promise<VideoUploadResponse> {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${BASE}/api/videos/upload`, { method: "POST", body: form });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "上传失败" }));
    throw new Error(err.detail || "上传失败");
  }
  return res.json();
}

export async function getVideoStatus(videoId: string): Promise<VideoStatusResponse> {
  const res = await fetch(`${BASE}/api/videos/${videoId}/status`);
  if (!res.ok) throw new Error("获取状态失败");
  return res.json();
}

export async function getVideoResults(videoId: string): Promise<VideoResultsResponse> {
  const res = await fetch(`${BASE}/api/videos/${videoId}/results`);
  if (!res.ok) throw new Error("获取结果失败");
  return res.json();
}

export async function sendCoachMessage(
  videoId: string,
  message: string,
): Promise<{ reply: string }> {
  const res = await fetch(`${BASE}/api/coach/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ video_id: videoId, message }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "发送失败" }));
    throw new Error(err.detail || "发送失败");
  }
  return res.json();
}

export async function deleteVideo(videoId: string): Promise<void> {
  await fetch(`${BASE}/api/videos/${videoId}`, { method: "DELETE" });
}

export function getVideoFileUrl(videoId: string): string {
  return `${BASE}/api/videos/${videoId}/file`;
}

export function getExportVideoUrl(videoId: string): string {
  return `${BASE}/api/videos/${videoId}/export`;
}
