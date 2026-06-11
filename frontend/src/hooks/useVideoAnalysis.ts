"use client";

import { useState, useEffect, useCallback } from "react";
import { getVideoStatus, getVideoResults } from "@/lib/api";
import type { VideoStatusResponse, VideoResultsResponse } from "@/lib/types";

type AnalysisState = {
  status: VideoStatusResponse | null;
  results: VideoResultsResponse | null;
  isLoading: boolean;
  error: string | null;
};

export function useVideoAnalysis(videoId: string) {
  const [state, setState] = useState<AnalysisState>({
    status: null,
    results: null,
    isLoading: true,
    error: null,
  });

  const fetchStatus = useCallback(async () => {
    try {
      const status = await getVideoStatus(videoId);
      setState((s) => ({ ...s, status }));

      if (status.status === "COMPLETED") {
        const results = await getVideoResults(videoId);
        setState((s) => ({ ...s, results, isLoading: false }));
        return true;
      }
      if (status.status === "FAILED") {
        setState((s) => ({
          ...s,
          isLoading: false,
          error: status.error_message || "分析失败",
        }));
        return true;
      }
      return false;
    } catch (err) {
      setState((s) => ({
        ...s,
        error: err instanceof Error ? err.message : "网络错误",
        isLoading: false,
      }));
      return true;
    }
  }, [videoId]);

  useEffect(() => {
    let cancelled = false;
    let timer: ReturnType<typeof setInterval>;

    const poll = async () => {
      const done = await fetchStatus();
      if (done && !cancelled) {
        clearInterval(timer);
      }
    };

    poll();
    timer = setInterval(poll, 2000);

    return () => {
      cancelled = true;
      clearInterval(timer);
    };
  }, [fetchStatus]);

  return state;
}
