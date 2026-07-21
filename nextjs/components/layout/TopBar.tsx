"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { usePathname } from "next/navigation";
import { Menu, X } from "lucide-react";

import { AuthLoginButton } from "@/components/auth/AuthLoginButton";
import { ThemeToggle } from "@/components/ThemeToggle";
import { LessonSectionNav } from "./LeftSidebar";

const globalLinks = [
  { href: "/", label: "교육개요" },
  { href: "/lesson", label: "LESSON" },
  { href: "/notice", label: "FAQ" },
] as const;

const utilCls =
  "text-[11px] uppercase tracking-[0.15em] text-neutral-900 transition-opacity hover:opacity-50 dark:text-neutral-100";

export function TopBar() {
  const [drawerOpen, setDrawerOpen] = useState(false);
  const pathname = usePathname();
  const isLesson = pathname.startsWith("/lesson");
  const drawerRef = useRef<HTMLDivElement>(null);

  useEffect(() => { setDrawerOpen(false); }, [pathname]);

  useEffect(() => {
    document.body.style.overflow = drawerOpen ? "hidden" : "";
    return () => { document.body.style.overflow = ""; };
  }, [drawerOpen]);

  // 로그인 후 대시보드는 자체 상단바를 쓰므로 사이트 공통 TopBar를 띄우지 않는다.
  if (pathname.startsWith("/dashboard")) return null;

  return (
    <>
      <header className="fixed inset-x-0 top-0 z-50 flex h-12 items-center justify-between border-b border-neutral-100 bg-white px-4 dark:border-gray-800 dark:bg-[#0a0a0a]">
        {/* 로고 */}
        <Link href="/" className="shrink-0 text-sm font-bold tracking-tight text-neutral-900 dark:text-neutral-100">
          RAG<span className="text-sky-600"> Tailor</span>
        </Link>

        {/* 데스크탑 글로벌 네비 */}
        <nav className="hidden items-center gap-6 md:flex" aria-label="글로벌 네비">
          {globalLinks.map(({ href, label }) => (
            <Link key={href} href={href} className={utilCls}>{label}</Link>
          ))}
          <a href="mailto:rex@ragwatson.com" className={utilCls}>CONTACT</a>
        </nav>

        {/* 데스크탑 우측: ThemeToggle + Login */}
        <div className="hidden items-center gap-3 md:flex">
          <ThemeToggle />
          <AuthLoginButton className="rounded-none border-0 bg-transparent px-0 py-0 text-[11px] font-normal uppercase tracking-[0.15em] text-neutral-900 shadow-none hover:bg-transparent hover:opacity-50 dark:text-neutral-100" />
        </div>

        {/* 모바일: ThemeToggle + 햄버거 */}
        <div className="flex items-center gap-3 md:hidden">
          <ThemeToggle />
          <button
            type="button"
            onClick={() => setDrawerOpen((v) => !v)}
            className={`${utilCls}`}
            aria-expanded={drawerOpen}
            aria-controls="mobile-drawer"
            aria-label={drawerOpen ? "메뉴 닫기" : "메뉴 열기"}
          >
            {drawerOpen ? "CLOSE" : "MENU"}
          </button>
        </div>
      </header>

      {/* 모바일 드로어 */}
      {drawerOpen && (
        <>
          <div
            className="fixed inset-0 z-40 bg-black/20 md:hidden"
            onClick={() => setDrawerOpen(false)}
            aria-hidden="true"
          />
          <div
            id="mobile-drawer"
            ref={drawerRef}
            role="dialog"
            aria-modal="true"
            aria-label="모바일 메뉴"
            className="fixed bottom-0 left-0 top-0 z-50 flex w-[min(85vw,208px)] flex-col overflow-y-auto bg-white shadow-xl dark:bg-[#111111] md:hidden"
          >
            {/* 드로어 헤더 */}
            <div className="flex h-12 shrink-0 items-center justify-between border-b border-neutral-100 px-4 dark:border-gray-800">
              <Link
                href="/"
                onClick={() => setDrawerOpen(false)}
                className="text-sm font-bold tracking-tight text-neutral-900 dark:text-neutral-100"
              >
                RAG<span className="text-sky-600"> Tailor</span>
              </Link>
              <button
                type="button"
                onClick={() => setDrawerOpen(false)}
                className="text-neutral-500 hover:text-neutral-900 dark:text-neutral-400 dark:hover:text-neutral-100"
                aria-label="닫기"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            {/* 드로어 본문 */}
            <nav className="flex flex-col px-4 py-4" aria-label="모바일 메뉴">
              <div className="border-b border-neutral-100 pb-4 dark:border-gray-800">
                <p className="mb-2 text-[9px] uppercase tracking-[0.2em] text-neutral-400 dark:text-neutral-500">메뉴</p>
                {globalLinks.map(({ href, label }) => (
                  <Link
                    key={href}
                    href={href}
                    onClick={() => setDrawerOpen(false)}
                    className="block py-2 text-sm font-medium text-neutral-900 hover:opacity-60 dark:text-neutral-100"
                  >
                    {label}
                  </Link>
                ))}
                <a
                  href="mailto:rex@ragwatson.com"
                  className="block py-2 text-sm font-medium text-neutral-900 hover:opacity-60 dark:text-neutral-100"
                >
                  CONTACT
                </a>
                <div className="pt-1">
                  <AuthLoginButton className="h-auto w-full justify-start rounded-none border-0 bg-transparent p-0 py-2 text-left text-sm font-medium text-neutral-900 shadow-none hover:bg-transparent hover:opacity-60 dark:text-neutral-100" />
                </div>
              </div>

              {isLesson && (
                <div className="pt-4">
                  <LessonSectionNav onNavigate={() => setDrawerOpen(false)} />
                </div>
              )}
            </nav>
          </div>
        </>
      )}
    </>
  );
}
