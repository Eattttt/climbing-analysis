import type {
  VideoUploadResponse,
  VideoStatusResponse,
  VideoResultsResponse,
} from "./types";

const BASE = process.env.NEXT_PUBLIC_API_URL || "";

export function uploadVideo(
  file: File,
  onProgress?: (percent: number) => void,
): Promise<VideoUploadResponse> {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    const form = new FormData();
    form.append("file", file);

    xhr.upload.onprogress = (e) => {
      if (e.lengthComputable && onProgress) {
        onProgress(Math.round((e.loaded / e.total) * 100));
      }
    };

    xhr.onload = () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        resolve(JSON.parse(xhr.responseText));
      } else {
        try {
          const err = JSON.parse(xhr.responseText);
          reject(new Error(err.detail || "上传失败"));
        } catch {
          reject(new Error("上传失败"));
        }
      }
    };

    xhr.onerror = () => reject(new Error("网络错误"));
    xhr.open("POST", `${BASE}/api/videos/upload`);
    xhr.send(form);
  });
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
