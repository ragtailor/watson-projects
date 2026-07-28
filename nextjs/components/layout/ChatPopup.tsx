"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { Bot, SendHorizontal, X } from "lucide-react";

import { DialogClose } from "@/components/ui/dialog";
import { cn } from "@/lib/utils";

type Role = "user" | "assistant";
type ChatMessage = { id: string; role: Role; text: string };

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "") ?? "";

function parseApiError(data: unknown, fallback: string): string {
  if (!data || typeof data !== "object") return fallback;
  const body = data as { detail?: unknown; error?: unknown; message?: unknown };
  const rawError = body.detail ?? body.error ?? body.message;
  if (typeof rawError === "string") return rawError;
  return fallback;
}

function uid() {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
}

export function ChatPopup() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [draft, setDraft] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const listRef = useRef<HTMLDivElement>(null);
  const sessionIdRef = useRef<string | null>(null);

  useEffect(() => {
    const el = listRef.current;
    if (!el) return;
    el.scrollTop = el.scrollHeight;
  }, [messages, loading]);

  const send = useCallback(async () => {
    const trimmed = draft.trim();
    if (!trimmed || loading) return;

    const userMsg: ChatMessage = { id: uid(), role: "user", text: trimmed };
    setDraft("");
    setError(null);
    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);

    try {
      // star_craft 허브: 시멘틱 의도 판단 → LangChain 챗봇 엔진
      const res = await fetch(`${API_BASE}/api/star-craft/semantic/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: sessionIdRef.current,
          message: trimmed,
        }),
      });
      const data = (await res.json()) as {
        session_id?: string;
        reply?: string;
        detail?: unknown;
      };
      if (!res.ok) {
        throw new Error(parseApiError(data, `요청 실패 (${res.status})`));
      }
      const reply = data.reply?.trim();
      if (!reply) throw new Error("빈 응답을 받았습니다.");
      if (data.session_id) sessionIdRef.current = data.session_id;
      setMessages((prev) => [...prev, { id: uid(), role: "assistant", text: reply }]);
    } catch (e) {
      const msg = e instanceof Error ? e.message : "알 수 없는 오류";
      setError(msg);
      setMessages((prev) => prev.filter((m) => m.id !== userMsg.id));
      setDraft(trimmed);
    } finally {
      setLoading(false);
    }
  }, [draft, loading]);

  const onKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      void send();
    }
  };

  return (
    <div className="flex h-full w-full flex-col bg-white">
      {/* 헤더 */}
      <div className="flex h-14 shrink-0 items-center justify-between border-b border-neutral-100 bg-white px-4">
        <div className="flex items-center gap-2">
          <span className="h-2 w-2 shrink-0 rounded-full bg-emerald-500" aria-hidden="true" />
          <span className="text-base font-semibold text-neutral-900">채팅</span>
        </div>
        <DialogClose className="rounded-full p-1.5 text-neutral-400 transition-colors hover:bg-neutral-100 hover:text-neutral-600">
          <X className="h-5 w-5" />
          <span className="sr-only">닫기</span>
        </DialogClose>
      </div>

      {/* 메시지 목록 */}
      <div ref={listRef} className="flex-1 space-y-4 overflow-y-auto px-4 py-4">
        {messages.length === 0 && (
          <p className="mt-10 text-center text-sm text-neutral-400">무엇이든 물어보세요.</p>
        )}
        {messages.length > 0 && (
          <div className="flex items-center gap-3 text-xs font-medium text-neutral-400">
            <span className="h-px flex-1 bg-neutral-100" />
            오늘
            <span className="h-px flex-1 bg-neutral-100" />
          </div>
        )}
        {messages.map((m) =>
          m.role === "assistant" ? (
            <div key={m.id} className="flex items-end justify-start gap-2">
              <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-blue-50">
                <Bot className="h-4 w-4 text-blue-500" />
              </span>
              <div className="max-w-[70%] whitespace-pre-wrap rounded-2xl rounded-bl-sm bg-neutral-100 px-3.5 py-2.5 text-sm leading-relaxed text-neutral-900">
                {m.text}
              </div>
            </div>
          ) : (
            <div key={m.id} className="flex justify-end">
              <div className="max-w-[70%] whitespace-pre-wrap rounded-2xl rounded-br-sm bg-blue-600 px-3.5 py-2.5 text-sm leading-relaxed text-white">
                {m.text}
              </div>
            </div>
          ),
        )}
        {loading && (
          <div className="flex items-end justify-start gap-2">
            <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-blue-50">
              <Bot className="h-4 w-4 text-blue-500" />
            </span>
            <div className="max-w-[70%] rounded-2xl rounded-bl-sm bg-neutral-100 px-3.5 py-2.5 text-sm text-neutral-400">
              입력 중…
            </div>
          </div>
        )}
      </div>

      {error && (
        <p className="px-4 pb-1 text-xs text-rose-600" role="alert">
          {error}
        </p>
      )}

      {/* 입력 바 */}
      <div className="flex shrink-0 items-end gap-2 border-t border-neutral-100 bg-white px-3 py-2.5">
        <textarea
          rows={1}
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={onKeyDown}
          disabled={loading}
          placeholder="메시지 보내기"
          className="max-h-28 flex-1 resize-none rounded-full border border-neutral-200 bg-neutral-50 px-4 py-2.5 text-sm text-neutral-900 outline-none placeholder:text-neutral-400 focus:border-neutral-300 disabled:opacity-60"
        />
        <button
          type="button"
          onClick={() => void send()}
          disabled={loading || !draft.trim()}
          className={cn(
            "inline-flex h-10 w-10 shrink-0 items-center justify-center rounded-full transition-colors disabled:cursor-not-allowed",
            draft.trim() && !loading
              ? "text-blue-600 hover:bg-blue-50"
              : "text-neutral-300",
          )}
        >
          <SendHorizontal className="h-5 w-5" strokeWidth={2.2} />
        </button>
      </div>
    </div>
  );
}
