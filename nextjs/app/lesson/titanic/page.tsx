"use client";

import { useEffect, useRef, useState } from "react";
import { Send } from "lucide-react";

import { LessonDataCollectionUpload } from "@/components/lesson/LessonDataCollectionUpload";
import { SetRightPanel } from "@/components/layout/RightPanelContext";
import { TocPanel } from "@/components/layout/panels/TocPanel";
import { PageNav } from "@/components/layout/PageNav";

const TOC_SECTIONS = [
  { label: "데이터 수집", href: "#data-collection" },
  { label: "탑승자 목록", href: "#passenger-list" },
  { label: "스미스 선장과 대화", href: "#captain-smith" },
];

/* ── 탑승자 목록 섹션 ── */
interface WalterInfo { id: number; name: string; memo: string }

function PassengerListSection() {
  const [walter, setWalter] = useState<WalterInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/titanic/walter/myself`)
      .then((r) => { if (!r.ok) throw new Error("API 호출 실패"); return r.json() as Promise<WalterInfo>; })
      .then(setWalter)
      .catch((e) => setError(e instanceof Error ? e.message : "오류 발생"))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="mt-4">
      {loading && (
        <p className="text-sm text-neutral-500 dark:text-neutral-500">불러오는 중…</p>
      )}
      {error && (
        <p className="rounded border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800 dark:border-red-800/50 dark:bg-red-950/30 dark:text-red-400">
          {error}
        </p>
      )}
      {walter && (
        <div className="rounded border border-neutral-200 p-4 text-sm text-neutral-700 dark:border-gray-700 dark:text-neutral-300">
          <p><span className="font-medium text-neutral-500 dark:text-neutral-400">ID:</span> {walter.id}</p>
          <p className="mt-1"><span className="font-medium text-neutral-500 dark:text-neutral-400">이름:</span> {walter.name}</p>
          <p className="mt-1"><span className="font-medium text-neutral-500 dark:text-neutral-400">메모:</span> {walter.memo}</p>
        </div>
      )}
    </div>
  );
}

/* ── 스미스 선장 채팅 섹션 ── */
type Message = { role: "user" | "assistant"; text: string };

const SYSTEM_INSTRUCTION = `당신은 타이타닉호의 선장 에드워드 존 스미스(Captain Edward John Smith)입니다.
1912년 4월 항해 중이며, 승객 및 승무원의 질문에 선장으로서 답변합니다.
- 품위 있고 침착한 어조를 유지합니다.
- 타이타닉과 당시 시대에 관한 역사적 사실을 바탕으로 답변합니다.
- 항상 한국어로 답변합니다.
- 답변은 간결하고 명확하게 합니다.`;

const API_BASE = process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") ?? "";

function CaptainSmithChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (messages.length === 0 && !loading) return;
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  async function send() {
    const text = input.trim();
    if (!text || loading) return;
    const next: Message[] = [...messages, { role: "user", text }];
    setMessages(next);
    setInput("");
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/api/titanic/smith/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages: next, systemInstruction: SYSTEM_INSTRUCTION }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error ?? "오류 발생");
      setMessages([...next, { role: "assistant", text: data.text }]);
    } catch (e) {
      setError(e instanceof Error ? e.message : "오류가 발생했습니다.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mt-4 flex h-[480px] flex-col rounded border border-neutral-200 dark:border-gray-700">
      {/* 메시지 영역 */}
      <div className="flex-1 space-y-4 overflow-y-auto px-4 py-4">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center py-12 text-center text-neutral-400 dark:text-neutral-500">
            <span className="mb-3 text-5xl">⚓</span>
            <p className="text-sm">스미스 선장에게 질문을 입력하세요.</p>
          </div>
        )}
        {messages.map((msg, i) => (
          <div key={i} className={`flex gap-3 ${msg.role === "user" ? "flex-row-reverse" : ""}`}>
            {msg.role === "assistant" && (
              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-neutral-800 text-base dark:bg-neutral-700">
                🎩
              </div>
            )}
            <div className={`max-w-[75%] rounded px-3 py-2 text-sm leading-relaxed ${
              msg.role === "user"
                ? "bg-neutral-900 text-white dark:bg-neutral-700 dark:text-neutral-100"
                : "bg-neutral-100 text-neutral-800 dark:bg-surface-muted dark:text-neutral-200"
            }`}>
              {msg.text}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex gap-3">
            <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-neutral-800 text-base dark:bg-neutral-700">🎩</div>
            <div className="flex items-center gap-1 rounded bg-neutral-100 px-3 py-2 dark:bg-surface-muted">
              {[0, 150, 300].map((d) => (
                <span key={d} className="h-1.5 w-1.5 animate-bounce rounded-full bg-neutral-400 dark:bg-neutral-600" style={{ animationDelay: `${d}ms` }} />
              ))}
            </div>
          </div>
        )}
        {error && (
          <p className="rounded bg-red-50 px-3 py-2 text-sm text-red-700 dark:bg-red-950/30 dark:text-red-400">
            {error}
          </p>
        )}
        <div ref={bottomRef} />
      </div>

      {/* 입력 영역 */}
      <div className="shrink-0 border-t border-neutral-200 p-3 dark:border-gray-700">
        <div className="flex gap-2">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); } }}
            placeholder="선장님께 질문하세요… (Enter 전송)"
            rows={2}
            className="flex-1 resize-none rounded border border-neutral-200 bg-white px-3 py-2 text-sm placeholder:text-neutral-400 focus:border-neutral-400 focus:outline-none dark:border-gray-700 dark:bg-surface-muted dark:text-neutral-100 dark:placeholder:text-neutral-600 dark:focus:border-gray-500"
          />
          <button
            type="button"
            onClick={send}
            disabled={!input.trim() || loading}
            className="shrink-0 rounded bg-neutral-900 px-3 text-white hover:bg-neutral-700 disabled:bg-neutral-300 dark:bg-neutral-700 dark:hover:bg-neutral-600 dark:disabled:bg-neutral-800"
          >
            <Send className="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  );
}

/* ── 페이지 ── */
export default function TitanicPage() {
  return (
    <>
      <SetRightPanel>
        <TocPanel
          sections={TOC_SECTIONS}
          next={{ label: "크롤링 — 네이버 뉴스", href: "/lesson/crawling/naver-news" }}
        />
      </SetRightPanel>

      {/* 헤더 */}
      <div className="mb-12">
        <p className="text-[10px] uppercase tracking-[0.3em] text-neutral-400 dark:text-neutral-500">
          머신러닝 · 타이타닉
        </p>
        <h1 className="mt-2 text-2xl font-semibold text-neutral-900 dark:text-neutral-100">
          타이타닉
        </h1>
        <p className="mt-3 text-sm leading-relaxed text-neutral-600 dark:text-neutral-400">
          타이타닉 침몰 데이터를 활용한 기초 데이터 분석 및 분류 모델 구현 강의입니다.
          아래 세 단계를 순서대로 실습합니다.
        </p>
      </div>

      <div className="space-y-20">
        {/* 1. 데이터 수집 */}
        <section id="data-collection" className="scroll-mt-16">
          <h2 className="mb-1 text-lg font-semibold text-neutral-900 dark:text-neutral-100">
            1. 데이터 수집
          </h2>
          <p className="mb-6 text-sm leading-relaxed text-neutral-600 dark:text-neutral-400">
            캐글(Kaggle)에서 다운로드한 Titanic CSV를 업로드합니다.
            수집된 데이터는 이후 Neon DB에 적재하는 단계로 이어집니다.
          </p>
          <LessonDataCollectionUpload />
        </section>

        {/* 2. 탑승자 목록 */}
        <section id="passenger-list" className="scroll-mt-16">
          <h2 className="mb-1 text-lg font-semibold text-neutral-900 dark:text-neutral-100">
            2. 탑승자 목록
          </h2>
          <p className="mb-2 text-sm leading-relaxed text-neutral-600 dark:text-neutral-400">
            데이터베이스에 저장된 타이타닉 탑승자 정보를 확인합니다.
          </p>
          <PassengerListSection />
        </section>

        {/* 3. 스미스 선장과 대화 */}
        <section id="captain-smith" className="scroll-mt-16">
          <h2 className="mb-1 text-lg font-semibold text-neutral-900 dark:text-neutral-100">
            3. 스미스 선장과 대화
          </h2>
          <p className="mb-2 text-sm leading-relaxed text-neutral-600 dark:text-neutral-400">
            타이타닉호의 선장 에드워드 스미스와 대화해보세요.
            1912년 항해 당시의 이야기를 들을 수 있습니다.
          </p>
          <CaptainSmithChat />
        </section>
      </div>

      <PageNav
        prev={{ label: "수업용 홈", href: "/lesson" }}
        next={{ label: "크롤링 — 네이버 뉴스", href: "/lesson/crawling/naver-news" }}
      />
    </>
  );
}
