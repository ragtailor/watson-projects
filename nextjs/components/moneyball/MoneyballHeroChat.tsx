"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { ChevronDown, Mic, Plus, SendHorizontal, SlidersHorizontal } from "lucide-react";

import { cn } from "@/lib/utils";

type Role = "user" | "assistant";

type ChatMessage = { id: string; role: Role; text: string };

const MODEL_OPTIONS = [
  { key: "fast", label: "빠른 응답" },
  { key: "pro", label: "고품질" },
] as const;

const SYSTEM_INSTRUCTION =
  "너는 축구 데이터와 통계, 규칙, 선수·팀 전력 분석에 특화된 '축구 마스터' 챗봇이다. " +
  "축구 관련 질문에는 전문적이고 근거 있게 답하고, 축구와 무관한 질문에는 축구에 빗대어 재치 있게 안내한다.";

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "") ??
  "";

function parseApiError(data: unknown, fallback: string): string {
  if (!data || typeof data !== "object") return fallback;
  const body = data as {
    detail?: unknown;
    error?: unknown;
    message?: unknown;
  };
  const rawError = body.detail ?? body.error ?? body.message;
  if (typeof rawError === "string") return rawError;
  if (typeof rawError === "object" && rawError !== null) {
    if ("message" in rawError && typeof (rawError as any).message === "string") {
      return (rawError as any).message;
    }
    if ("status" in rawError && typeof (rawError as any).status === "string") {
      return `${String((rawError as any).message ?? fallback)} (${(rawError as any).status})`;
    }
  }
  if (Array.isArray(rawError)) {
    return rawError
      .map((item) =>
        typeof item === "object" && item !== null && "msg" in item
          ? String((item as { msg: string }).msg)
          : String(item)
      )
      .join(", ");
  }
  return fallback;
}

function uid() {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
}

type MoneyballHeroChatProps = {
  className?: string;
};

export function MoneyballHeroChat({ className }: MoneyballHeroChatProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [draft, setDraft] = useState("");
  const [modelKey, setModelKey] = useState<(typeof MODEL_OPTIONS)[number]["key"]>("fast");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const listRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    const el = listRef.current;
    if (!el) return;
    el.scrollTop = el.scrollHeight;
  }, [messages, loading]);

  const resizeTextarea = useCallback(() => {
    const ta = textareaRef.current;
    if (!ta) return;
    ta.style.height = "0px";
    ta.style.height = `${Math.min(ta.scrollHeight, 160)}px`;
  }, []);

  useEffect(() => {
    resizeTextarea();
  }, [draft, resizeTextarea]);

  const send = useCallback(async () => {
    const trimmed = draft.trim();
    if (!trimmed || loading) return;

    const userMsg: ChatMessage = { id: uid(), role: "user", text: trimmed };
    setDraft("");
    setError(null);
    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);

    try {
      const res = await fetch(`${API_BASE}/api/gemini/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          messages: [{ role: "user", text: trimmed }],
          modelKey,
          systemInstruction: SYSTEM_INSTRUCTION,
        }),
      });
      const data = (await res.json()) as { text?: string; detail?: unknown };
      if (!res.ok) {
        throw new Error(parseApiError(data, `요청 실패 (${res.status})`));
      }
      const reply = data.text?.trim();
      if (!reply) {
        throw new Error("빈 응답을 받았습니다.");
      }
      setMessages((prev) => [
        ...prev,
        { id: uid(), role: "assistant", text: reply },
      ]);
    } catch (e) {
      const msg = e instanceof Error ? e.message : "알 수 없는 오류";
      setError(msg);
      setMessages((prev) => prev.filter((m) => m.id !== userMsg.id));
      setDraft(trimmed);
    } finally {
      setLoading(false);
    }
  }, [draft, loading, messages]);

  const onKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      void send();
    }
  };

  const startVoice = () => {
    if (typeof window === "undefined") return;

    type RecResult = { transcript?: string };
    type RecEvent = { results: ArrayLike<{ 0?: RecResult }> };
    type RecCtor = new () => {
      lang: string;
      interimResults: boolean;
      maxAlternatives: number;
      start: () => void;
      onresult: ((ev: RecEvent) => void) | null;
      onerror: (() => void) | null;
    };

    const w = window as Window & {
      SpeechRecognition?: RecCtor;
      webkitSpeechRecognition?: RecCtor;
    };
    const SR = w.SpeechRecognition ?? w.webkitSpeechRecognition;
    if (!SR) {
      setError("이 브라우저에서는 음성 입력을 지원하지 않습니다.");
      return;
    }
    const rec = new SR();
    rec.lang = "ko-KR";
    rec.interimResults = false;
    rec.maxAlternatives = 1;
    rec.onresult = (ev: RecEvent) => {
      const text = ev.results[0]?.[0]?.transcript?.trim();
      if (text) setDraft((d) => (d ? `${d} ${text}` : text));
    };
    rec.onerror = () => setError("음성 인식 중 오류가 발생했습니다.");
    try {
      rec.start();
    } catch {
      setError("음성 입력을 시작할 수 없습니다.");
    }
  };

  return (
    <div className={cn("w-full max-w-lg sm:max-w-xl", className)}>
      {/* 메시지 목록 */}
      {messages.length > 0 && (
        <div
          ref={listRef}
          className="mb-4 max-h-[min(40vh,320px)] space-y-3 overflow-y-auto rounded-2xl border border-slate-200 bg-white p-4 shadow-sm dark:border-gray-700 dark:bg-[#111111]"
        >
          {messages.map((m) => (
            <div
              key={m.id}
              className={
                m.role === "user"
                  ? "ml-8 rounded-2xl rounded-tr-sm bg-emerald-100 px-4 py-2.5 text-sm text-slate-800 dark:bg-emerald-900/40 dark:text-emerald-100"
                  : "mr-8 whitespace-pre-wrap rounded-2xl rounded-tl-sm border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm text-slate-800 dark:border-gray-700 dark:bg-[#1a1a1a] dark:text-slate-200"
              }
            >
              {m.text}
            </div>
          ))}
          {loading && (
            <div className="mr-8 rounded-2xl rounded-tl-sm border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm text-slate-500 dark:border-gray-700 dark:bg-[#1a1a1a] dark:text-slate-400">
              축구 마스터가 분석 중입니다…
            </div>
          )}
        </div>
      )}

      {/* 입력창 */}
      <div className="rounded-[1.75rem] border border-slate-200 bg-white p-4 shadow-md shadow-slate-200/60 ring-1 ring-slate-100 dark:border-gray-700 dark:bg-[#111111] dark:shadow-none dark:ring-gray-800">
        <textarea
          ref={textareaRef}
          rows={1}
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={onKeyDown}
          placeholder="축구 마스터에게 물어보기"
          disabled={loading}
          className="w-full resize-none bg-transparent px-1 py-2 text-[15px] leading-relaxed text-slate-900 outline-none placeholder:text-slate-400 disabled:opacity-60 dark:text-slate-100 dark:placeholder:text-slate-600"
        />

        <div className="mt-2 flex flex-wrap items-center justify-between gap-3 border-t border-slate-100 pt-3 dark:border-gray-800">
          {/* 좌측 버튼 */}
          <div className="flex items-center gap-1">
            <button
              type="button"
              title="첨부 (준비 중)"
              disabled
              className="inline-flex h-10 w-10 items-center justify-center rounded-full text-slate-400 opacity-40 dark:text-slate-600"
              aria-disabled
            >
              <Plus className="h-5 w-5" strokeWidth={2} />
            </button>
            <button
              type="button"
              title="도구 (준비 중)"
              disabled
              className="inline-flex items-center gap-1.5 rounded-full px-2 py-1.5 text-sm text-slate-400 opacity-40 dark:text-slate-600"
              aria-disabled
            >
              <SlidersHorizontal className="h-4 w-4" />
              도구
            </button>
          </div>

          {/* 우측 버튼 */}
          <div className="flex items-center gap-2">
            {/* 모델 선택 */}
            <div className="relative">
              <select
                value={modelKey}
                onChange={(e) =>
                  setModelKey(e.target.value as (typeof MODEL_OPTIONS)[number]["key"])
                }
                disabled={loading}
                className="h-10 appearance-none rounded-full border border-slate-200 bg-slate-50 py-0 pr-9 pl-3 text-sm text-slate-800 outline-none hover:border-slate-300 focus:border-emerald-400 focus:ring-1 focus:ring-emerald-200 disabled:opacity-50 dark:border-gray-700 dark:bg-[#1a1a1a] dark:text-slate-200 dark:hover:border-gray-600 dark:focus:border-emerald-500 dark:focus:ring-emerald-900"
              >
                {MODEL_OPTIONS.map((o) => (
                  <option key={o.key} value={o.key}>
                    {o.label}
                  </option>
                ))}
              </select>
              <ChevronDown className="pointer-events-none absolute top-1/2 right-2.5 h-4 w-4 -translate-y-1/2 text-slate-500 dark:text-slate-400" />
            </div>

            {/* 마이크 */}
            <button
              type="button"
              onClick={startVoice}
              disabled={loading}
              title="음성 입력"
              className="inline-flex h-10 w-10 items-center justify-center rounded-full text-slate-600 hover:bg-slate-100 hover:text-slate-900 disabled:opacity-40 dark:text-slate-400 dark:hover:bg-gray-800 dark:hover:text-slate-100"
            >
              <Mic className="h-5 w-5" />
            </button>

            {/* 전송 */}
            <button
              type="button"
              onClick={() => void send()}
              disabled={loading || !draft.trim()}
              title="보내기"
              className="inline-flex h-10 w-10 items-center justify-center rounded-full bg-emerald-600 text-white hover:bg-emerald-500 disabled:cursor-not-allowed disabled:opacity-35 dark:bg-emerald-500 dark:hover:bg-emerald-400"
            >
              <SendHorizontal className="h-5 w-5" strokeWidth={2.2} />
            </button>
          </div>
        </div>
      </div>

      {/* 에러 */}
      {error && (
        <p className="mt-3 text-center text-sm text-rose-600 dark:text-rose-400" role="alert">
          {error}
        </p>
      )}

      {/* 면책 고지 */}
      <p className="mt-4 text-center text-xs leading-relaxed text-slate-500 dark:text-slate-500">
        축구 마스터는 AI로서 실수를 할 수 있으며, 경기 기록·통계도 부정확할 수 있습니다.{" "}
        <a
          href="https://policies.google.com/privacy"
          target="_blank"
          rel="noopener noreferrer"
          className="underline underline-offset-2 hover:text-slate-700 dark:hover:text-slate-300"
        >
          Google 개인정보처리방침
        </a>
      </p>
    </div>
  );
}
