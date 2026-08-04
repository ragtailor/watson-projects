"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { usePathname } from "next/navigation";
import { ChevronDown, ChevronUp } from "lucide-react";

import { AuthLoginButton } from "@/components/auth/AuthLoginButton";
import { portfolioCategoryLinks } from "@/components/home/portfolio-data";
import { MobileMenu } from "./MobileMenu";

const secondaryLinks = [
  { href: "/", label: "교육개요" },
  { href: "/notice", label: "FAQ" },
  { href: "/lesson", label: "LESSON" },
  { href: "/ledger", label: "가계부" },
] as const;

const linkCls =
  "py-[3px] text-[11px] uppercase tracking-[0.12em] text-neutral-900 transition-opacity hover:opacity-50 leading-tight";

const utilCls =
  "text-[11px] uppercase tracking-[0.15em] text-neutral-900 transition-opacity hover:opacity-50";

const lessonSubLinks = {
  titanic: [
    { href: "/lesson/titanic/data-collection", label: "데이터 수집" },
    { href: "/lesson/titanic/passenger-list", label: "탑승자 목록" },
    { href: "/lesson/titanic/captain-smith", label: "스미스 선장과 대화" },
  ],
  crawling: [
    { href: "/lesson/crawling/naver-news", label: "네이버 뉴스" },
    { href: "/lesson/crawling/board", label: "게시판 목록" },
    { href: "/lesson/crawling/board/write", label: "게시판 글쓰기" },
  ],
};

export function SiteNav() {
  const [menuOpen, setMenuOpen] = useState(false);
  const [shopOpen, setShopOpen] = useState(true);
  const [isDesktop, setIsDesktop] = useState(false);
  const [titanicOpen, setTitanicOpen] = useState(false);
  const [crawlingOpen, setCrawlingOpen] = useState(false);
  const pathname = usePathname();

  useEffect(() => {
    const mq = window.matchMedia("(min-width: 1024px)");
    setIsDesktop(mq.matches);
    const handler = (e: MediaQueryListEvent) => {
      setIsDesktop(e.matches);
      if (e.matches) setMenuOpen(false);
    };
    mq.addEventListener("change", handler);
    return () => mq.removeEventListener("change", handler);
  }, []);

  // 현재 경로에 따라 아코디언 자동 오픈
  useEffect(() => {
    if (pathname.startsWith("/lesson/titanic")) setTitanicOpen(true);
    if (pathname.startsWith("/lesson/crawling")) setCrawlingOpen(true);
  }, [pathname]);

  useEffect(() => {
    document.body.style.overflow = menuOpen ? "hidden" : "";
    return () => {
      document.body.style.overflow = "";
    };
  }, [menuOpen]);

  const isLessonPage = pathname.startsWith("/lesson");

  const lessonNav = (
    <div className="mt-3">
      <p className="mb-1 text-[9px] uppercase tracking-[0.2em] text-neutral-400">
        수업용
      </p>

      {/* 타이타닉 */}
      <button
        type="button"
        onClick={() => setTitanicOpen((v) => !v)}
        className="flex w-full items-center justify-between py-[3px] text-left text-[11px] text-neutral-900 transition-opacity hover:opacity-50"
      >
        타이타닉
        {titanicOpen ? (
          <ChevronUp className="h-3 w-3 shrink-0" />
        ) : (
          <ChevronDown className="h-3 w-3 shrink-0" />
        )}
      </button>
      {titanicOpen && (
        <ul className="mb-1 ml-1 border-l border-neutral-200">
          {lessonSubLinks.titanic.map(({ href, label }) => (
            <li key={href}>
              <Link
                href={href}
                className={`block py-[3px] pl-2 text-[10px] leading-tight transition-colors hover:text-neutral-900 ${
                  pathname === href ? "text-neutral-900" : "text-neutral-500"
                }`}
              >
                {label}
              </Link>
            </li>
          ))}
        </ul>
      )}

      {/* 크롤링 */}
      <button
        type="button"
        onClick={() => setCrawlingOpen((v) => !v)}
        className="flex w-full items-center justify-between py-[3px] text-left text-[11px] text-neutral-900 transition-opacity hover:opacity-50"
      >
        크롤링
        {crawlingOpen ? (
          <ChevronUp className="h-3 w-3 shrink-0" />
        ) : (
          <ChevronDown className="h-3 w-3 shrink-0" />
        )}
      </button>
      {crawlingOpen && (
        <ul className="mb-1 ml-1 border-l border-neutral-200">
          {lessonSubLinks.crawling.map(({ href, label }) => (
            <li key={href}>
              <Link
                href={href}
                className={`block py-[3px] pl-2 text-[10px] leading-tight transition-colors hover:text-neutral-900 ${
                  pathname === href || pathname.startsWith(href + "/")
                    ? "text-neutral-900"
                    : "text-neutral-500"
                }`}
              >
                {label}
              </Link>
            </li>
          ))}
        </ul>
      )}

      {/* 삼성전자 분석 */}
      <Link
        href="/lesson/samsung"
        className={`block py-[3px] text-[11px] transition-opacity hover:opacity-50 ${
          pathname.startsWith("/lesson/samsung")
            ? "text-neutral-900"
            : "text-neutral-900"
        }`}
      >
        삼성전자 분석
      </Link>
    </div>
  );

  if (isDesktop) {
    return (
      <>
        {/* ── Desktop: 좌측 고정 사이드바 ─── */}
        <aside className="fixed inset-y-0 left-0 z-50 flex w-44 flex-col overflow-y-auto bg-white pb-6 pl-4 pr-2 pt-4">
          <Link
            href="/"
            className="mb-6 block shrink-0 text-base font-bold tracking-tight text-neutral-900"
          >
            RAG<span className="text-sky-600"> Tailor</span>
          </Link>

          <nav className="flex flex-col" aria-label="카테고리">
            {portfolioCategoryLinks.map(({ label, href }) => {
              const isActive =
                href === "/"
                  ? pathname === "/"
                  : pathname === href || pathname.startsWith(href + "/");
              return (
                <Link
                  key={label}
                  href={href}
                  className={`${linkCls} ${isActive ? "opacity-100" : ""}`}
                >
                  {label}
                </Link>
              );
            })}
          </nav>

          <p className="my-2 shrink-0 text-[11px] text-neutral-400">—</p>

          <nav className="flex flex-col" aria-label="보조 메뉴">
            {secondaryLinks.map(({ href, label }) => (
              <Link key={href} href={href} className={linkCls}>
                {label}
              </Link>
            ))}
            <a href="mailto:rex@ragwatson.com" className={linkCls}>
              CONTACT
            </a>
            <AuthLoginButton className="h-auto justify-start rounded-none border-0 bg-transparent px-0 py-[3px] text-left text-[11px] font-normal uppercase tracking-[0.12em] text-neutral-900 shadow-none hover:bg-transparent hover:opacity-50" />
          </nav>

          {/* 레슨 페이지 인라인 수업용 아코디언 */}
          {isLessonPage && lessonNav}

          <p className="mt-auto shrink-0 pt-4 text-[10px] text-neutral-400">
            © 2026 RAG Tailor
          </p>
        </aside>

        {/* ── Desktop: 우상단 유틸리티 ─── */}
        <div className="fixed right-0 top-0 z-50 flex items-center gap-5 p-4">
          <a href="mailto:rex@ragwatson.com" className={utilCls}>
            CONTACT
          </a>
          <AuthLoginButton className="rounded-none border-0 bg-transparent px-0 py-0 text-[11px] font-normal uppercase tracking-[0.15em] text-neutral-900 shadow-none hover:bg-transparent hover:opacity-50" />
        </div>
      </>
    );
  }

  return (
    <>
      {/* ── Mobile: 상단 바 ─── */}
      <header className="fixed inset-x-0 top-0 z-50 flex h-12 items-center justify-between bg-white px-4">
        <Link
          href="/"
          onClick={() => setMenuOpen(false)}
          className="text-sm font-bold tracking-tight text-neutral-900"
        >
          RAG<span className="text-sky-600"> Tailor</span>
        </Link>

        <div className="flex items-center gap-4">
          <a href="mailto:rex@ragwatson.com" className={utilCls}>
            CONTACT
          </a>
          <button
            type="button"
            onClick={() => setMenuOpen((v) => !v)}
            className={utilCls}
            aria-expanded={menuOpen}
            aria-controls="mobile-menu"
          >
            {menuOpen ? "CLOSE" : "MENU"}
          </button>
        </div>
      </header>

      {/* ── Mobile: 메뉴 오버레이 ─── */}
      {menuOpen && (
        <div
          id="mobile-menu"
          className="fixed inset-0 z-40 bg-white pt-12"
          role="dialog"
          aria-modal="true"
          aria-label="모바일 메뉴"
        >
          <MobileMenu
            onClose={() => setMenuOpen(false)}
            shopOpen={shopOpen}
            onToggleShop={() => setShopOpen((v) => !v)}
            isLessonPage={isLessonPage}
            titanicOpen={titanicOpen}
            onToggleTitanic={() => setTitanicOpen((v) => !v)}
            crawlingOpen={crawlingOpen}
            onToggleCrawling={() => setCrawlingOpen((v) => !v)}
          />
        </div>
      )}
    </>
  );
}
