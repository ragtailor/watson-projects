"use client";

import Link from "next/link";
import React, { useEffect, useState } from "react";
import { usePathname } from "next/navigation";
import { ChevronDown, ChevronUp, X } from "lucide-react";

const lessonItems = [
  {
    key: "algorithm",
    label: "알고리즘",
    basePath: "/lesson/algorithm",
    children: [
      { label: "욕심쟁이", href: "/lesson/algorithm/greedy" },
      { label: "DP", href: "/lesson/algorithm/dp" },
      { label: "이분 탐색", href: "/lesson/algorithm/binary-search" },
      { label: "DFS", href: "/lesson/algorithm/dfs" },
      { label: "BFS", href: "/lesson/algorithm/bfs" },
      { label: "정렬", href: "/lesson/algorithm/sorting" },
      { label: "재귀", href: "/lesson/algorithm/recursion" },
      { label: "투 포인터", href: "/lesson/algorithm/two-pointers" },
      { label: "스택 / 큐", href: "/lesson/algorithm/stack-queue" },
      { label: "해시", href: "/lesson/algorithm/hash" },
    ],
  },
  {
    key: "ml",
    label: "머신러닝",
    basePath: "/lesson/titanic",
    children: [
      { label: "타이타닉", href: "/lesson/titanic" },
    ],
  },
  {
    key: "crawling",
    label: "크롤링",
    basePath: "/lesson/crawling",
    children: [
      { label: "네이버 뉴스", href: "/lesson/crawling/naver-news" },
      { label: "게시판 목록", href: "/lesson/crawling/board" },
      { label: "게시판 글쓰기", href: "/lesson/crawling/board/write" },
    ],
  },
  {
    key: "rag-system",
    label: "RAG SYSTEM",
    basePath: "/lesson/rag-system",
    children: [
      { label: "축구 마스터", href: "/lesson/rag-system/moneyball" },
    ],
  },
];

const linkCls =
  "block py-[3px] text-[14px] leading-tight transition-colors hover:text-neutral-900 dark:hover:text-neutral-100";

export function LessonSectionNav({
  onNavigate,
}: {
  onNavigate?: () => void;
}) {
  const pathname = usePathname();
  const [open, setOpen] = useState<Record<string, boolean>>({});

  useEffect(() => {
    const initial: Record<string, boolean> = {};
    lessonItems.forEach(({ key, basePath }) => {
      if (pathname.startsWith(basePath)) initial[key] = true;
    });
    setOpen(initial);
  }, [pathname]);

  return (
    <div>
      <p className="mb-1.5 text-[11px] uppercase tracking-[0.2em] text-neutral-400 dark:text-neutral-500">
        수업용
      </p>

      {lessonItems.map(({ key, label, basePath, children }) => (
        <div key={key}>
          <button
            type="button"
            onClick={() => setOpen((v) => ({ ...v, [key]: !v[key] }))}
            className="flex w-full items-center justify-between py-[3px] text-left text-[14px] text-neutral-900 transition-opacity hover:opacity-60 dark:text-neutral-100"
          >
            {label}
            {open[key] ? (
              <ChevronUp className="h-3 w-3 shrink-0" />
            ) : (
              <ChevronDown className="h-3 w-3 shrink-0" />
            )}
          </button>

          {open[key] && (
            <ul className="mb-1 ml-1 border-l border-neutral-200 dark:border-gray-700">
              {children.map(({ label: cl, href }) => (
                <li key={href}>
                  <Link
                    href={href}
                    onClick={onNavigate}
                    className={`${linkCls} pl-2 ${
                      pathname === href || pathname.startsWith(href + "/")
                        ? "font-medium text-neutral-900 dark:text-neutral-100"
                        : "text-neutral-500 dark:text-neutral-400"
                    }`}
                  >
                    {cl}
                  </Link>
                </li>
              ))}
            </ul>
          )}
        </div>
      ))}

      <Link
        href="/lesson/samsung"
        onClick={onNavigate}
        className={`${linkCls} ${
          pathname.startsWith("/lesson/samsung")
            ? "text-neutral-900 dark:text-neutral-100"
            : "text-neutral-700 dark:text-neutral-400"
        }`}
      >
        삼성전자 분석
      </Link>

      <MailCompose />
    </div>
  );
}

function MailCompose() {
  const pathname = usePathname();
  return (
    <div className="mt-3 border-t border-neutral-200 pt-3 dark:border-gray-700">
      <Link
        href="/lesson/mail"
        className={`${linkCls} ${
          pathname === "/lesson/mail"
            ? "text-neutral-900 dark:text-neutral-100"
            : "text-neutral-700 dark:text-neutral-400"
        }`}
      >
        메일관리
      </Link>
      <Link
        href="/lesson/contacts"
        className={`${linkCls} mt-0.5 ${
          pathname.startsWith("/lesson/contacts")
            ? "text-neutral-900 dark:text-neutral-100"
            : "text-neutral-700 dark:text-neutral-400"
        }`}
      >
        주소록
      </Link>
    </div>
  );
}

export function LeftSidebar() {
  const pathname = usePathname();
  const isLesson = pathname.startsWith("/lesson");

  if (!isLesson) return null;

  return (
    <aside className="hidden h-full w-52 shrink-0 overflow-y-auto border-r border-neutral-100 bg-neutral-50 px-4 py-6 dark:border-gray-800 dark:bg-[#111111] md:block">
      <LessonSectionNav />
    </aside>
  );
}
