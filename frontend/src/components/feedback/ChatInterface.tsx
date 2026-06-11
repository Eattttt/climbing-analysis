"use client";

import { useState, useRef, useEffect } from "react";
import { sendCoachMessage } from "@/lib/api";

type Message = {
  role: "user" | "assistant";
  content: string;
};

type Props = {
  videoId: string;
};

export default function ChatInterface({ videoId }: Props) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight });
  }, [messages]);

  const send = async () => {
    const text = input.trim();
    if (!text || loading) return;

    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setLoading(true);

    try {
      const { reply } = await sendCoachMessage(videoId, text);
      setMessages((prev) => [...prev, { role: "assistant", content: reply }]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "抱歉，发送失败，请重试。" },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
      <div className="px-4 py-3 border-b border-gray-100 bg-gray-50">
        <h3 className="font-medium text-gray-800">💬 教练对话</h3>
        <p className="text-xs text-gray-500">可以就视频中的技术问题提问</p>
      </div>

      <div ref={scrollRef} className="h-64 overflow-y-auto p-4 space-y-3">
        {messages.length === 0 && (
          <p className="text-gray-400 text-sm text-center py-8">
            试试问："我在动态动作中有什么问题？"
          </p>
        )}
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-[80%] px-4 py-2 rounded-2xl text-sm ${
                msg.role === "user"
                  ? "bg-green-600 text-white rounded-br-md"
                  : "bg-gray-100 text-gray-800 rounded-bl-md"
              }`}
            >
              {msg.content}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 px-4 py-2 rounded-2xl rounded-bl-md text-sm text-gray-500">
              教练正在思考...
            </div>
          </div>
        )}
      </div>

      <div className="p-3 border-t border-gray-100 flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && send()}
          placeholder="输入你的问题..."
          className="flex-1 px-4 py-2 bg-gray-50 border border-gray-200 rounded-full text-sm focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
          disabled={loading}
        />
        <button
          onClick={send}
          disabled={loading || !input.trim()}
          className="px-4 py-2 bg-green-600 text-white text-sm rounded-full hover:bg-green-700 disabled:opacity-50 transition-colors"
        >
          发送
        </button>
      </div>
    </div>
  );
}
