"use client";

import { useCallback, useEffect, useRef, useState } from "react";

interface ContactHit {
  id: number;
  name: string;
  nickname: string | null;
  email: string | null;
}

export default function MailPage() {
  const [query, setQuery]     = useState("");          // 검색어 (수신자 입력창)
  const [to, setTo]           = useState("");          // 최종 이메일 주소
  const [hits, setHits]       = useState<ContactHit[]>([]);
  const [open, setOpen]       = useState(false);
  const [message, setMessage] = useState("");
  const [status, setStatus]   = useState<"idle" | "sending" | "done" | "error">("idle");
  const wrapRef               = useRef<HTMLDivElement>(null);
  const debounceRef           = useRef<ReturnType<typeof setTimeout> | null>(null);

  // 검색어 변경 시 API 호출 (200ms 디바운스)
  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    if (!query.trim()) { setHits([]); setOpen(false); return; }

    debounceRef.current = setTimeout(async () => {
      try {
        const res = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL}/api/sherlock-homes/mycroft/contacts/search?q=${encodeURIComponent(query)}`
        );
        const data: ContactHit[] = await res.json();
        setHits(data);
        setOpen(data.length > 0);
      } catch {
        setHits([]); setOpen(false);
      }
    }, 200);
  }, [query]);

  // 외부 클릭 시 드롭다운 닫기
  useEffect(() => {
    function onOutside(e: MouseEvent) {
      if (wrapRef.current && !wrapRef.current.contains(e.target as Node)) setOpen(false);
    }
    document.addEventListener("mousedown", onOutside);
    return () => document.removeEventListener("mousedown", onOutside);
  }, []);

  const selectContact = useCallback((hit: ContactHit) => {
    setQuery(hit.name);
    setTo(hit.email ?? "");
    setOpen(false);
  }, []);

  async function handleSend() {
    if (!message.trim() || !to) return;
    setStatus("sending");
    try {
      const res = await fetch("/api/send-mail", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ to, message }),
      });
      if (!res.ok) throw new Error();
      setStatus("done");
      setQuery(""); setTo(""); setMessage("");
      setTimeout(() => setStatus("idle"), 2000);
    } catch {
      setStatus("error");
      setTimeout(() => setStatus("idle"), 3000);
    }
  }

  return (
    <div>
      <div className="mb-8 border-b border-neutral-100 pb-8 dark:border-gray-800">
        <p className="text-[10px] uppercase tracking-[0.3em] text-neutral-400 dark:text-neutral-500">Mail</p>
        <h1 className="mt-2 text-2xl font-semibold text-neutral-900 dark:text-neutral-100">메일보내기</h1>
      </div>

      <div className="flex flex-col gap-6">
        {/* 수신자 — 이름 검색 + 이메일 자동완성 */}
        <div className="flex flex-col gap-2">
          <label className="text-[10px] uppercase tracking-[0.12em] text-neutral-500 dark:text-neutral-400">
            수신자
          </label>
          <div ref={wrapRef} className="relative">
            <input
              type="text"
              value={query}
              onChange={(e) => { setQuery(e.target.value); setTo(""); }}
              placeholder="이름 입력 (주소록 자동완성)"
              className="w-full rounded border border-neutral-200 bg-white px-3 py-2.5 text-sm text-neutral-900 placeholder-neutral-400 focus:outline-none dark:border-gray-700 dark:bg-surface-muted dark:text-neutral-100 dark:placeholder-neutral-600"
            />

            {/* 드롭다운 */}
            {open && (
              <ul className="absolute left-0 right-0 top-full z-50 mt-1 overflow-hidden rounded border border-neutral-200 bg-white shadow-lg dark:border-gray-700 dark:bg-surface-muted">
                {hits.map((hit) => (
                  <li key={hit.id}>
                    <button
                      type="button"
                      onMouseDown={(e) => { e.preventDefault(); selectContact(hit); }}
                      className="flex w-full items-center justify-between px-3 py-2.5 text-left text-sm hover:bg-neutral-50 dark:hover:bg-surface-hover"
                    >
                      <span className="text-neutral-900 dark:text-neutral-100">{hit.name}</span>
                      <span className="ml-4 shrink-0 text-xs text-neutral-400 dark:text-neutral-500">
                        {hit.email ?? "이메일 없음"}
                      </span>
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>

          {/* 선택된 이메일 표시 */}
          {to && (
            <p className="text-xs text-neutral-500 dark:text-neutral-400">
              → <span className="text-neutral-700 dark:text-neutral-300">{to}</span>
            </p>
          )}
        </div>

        {/* 주요내용 */}
        <div className="flex flex-col gap-2">
          <label className="text-[10px] uppercase tracking-[0.12em] text-neutral-500 dark:text-neutral-400">
            주요내용
          </label>
          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="전달할 내용을 입력하세요"
            rows={10}
            className="resize-none rounded border border-neutral-200 bg-white px-3 py-2.5 text-sm text-neutral-900 placeholder-neutral-400 focus:outline-none dark:border-gray-700 dark:bg-surface-muted dark:text-neutral-100 dark:placeholder-neutral-600"
          />
        </div>

        <div className="flex justify-end">
          <button
            type="button"
            onClick={handleSend}
            disabled={status === "sending" || !message.trim() || !to}
            className="rounded bg-neutral-900 px-6 py-2 text-sm text-white transition-opacity hover:opacity-70 disabled:opacity-30 dark:bg-neutral-100 dark:text-neutral-900"
          >
            {status === "idle" && "전송"}
            {status === "sending" && "전송 중..."}
            {status === "done" && "완료"}
            {status === "error" && "실패"}
          </button>
        </div>
      </div>
    </div>
  );
}
