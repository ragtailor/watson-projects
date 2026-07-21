"use client";

import Link from "next/link";
import {
  BarChart3,
  Bot,
  ChevronRight,
  Clock,
  Cpu,
  Database,
  Globe,
  Home,
  Image as ImageIcon,
  LifeBuoy,
  Network,
  Search,
  ShieldAlert,
  ShieldCheck,
  Sparkles,
  User,
  Zap,
} from "lucide-react";

const topItems = [
  { icon: Home, label: "계정 홈" },
  { icon: Clock, label: "최근" },
  { icon: Globe, label: "학습 도메인" },
];

const navGroups = [
  {
    label: "Observe",
    items: [
      { icon: BarChart3, label: "Analytics" },
      { icon: Cpu, label: "Investigate" },
    ],
  },
  {
    label: "Build",
    items: [
      { icon: Cpu, label: "Compute" },
      { icon: Bot, label: "AI" },
      { icon: Database, label: "Storage & databases" },
      { icon: ImageIcon, label: "Media" },
    ],
  },
  {
    label: "Protect & connect",
    items: [
      { icon: ShieldCheck, label: "Application security" },
      { icon: ShieldAlert, label: "Zero Trust" },
      { icon: Network, label: "Networking" },
      { icon: Zap, label: "Delivery & performance" },
    ],
  },
];

const shortcuts = [
  { label: "LESSON 목록", href: "/lesson" },
  { label: "공지사항", href: "/notice" },
];

export default function DashboardPage() {
  return (
    <div className="fixed inset-0 z-40 flex flex-col bg-white text-neutral-900 dark:bg-[#0a0a0a] dark:text-neutral-100">
      {/* 대시보드 전용 상단바 */}
      <header className="flex h-12 shrink-0 items-center justify-between border-b border-neutral-100 px-4 dark:border-gray-800">
        <span className="flex items-center gap-2 text-sm font-medium">
          <span className="flex h-6 w-6 items-center justify-center rounded bg-sky-600 text-[11px] font-bold text-white">
            T
          </span>
          Taylor@ragtailor.com
        </span>

        <div className="flex items-center gap-4 text-sm text-neutral-500 dark:text-neutral-400">
          <span className="flex items-center gap-1.5">
            <Sparkles className="h-4 w-4" /> Ask AI
          </span>
          <span className="flex items-center gap-1.5">
            <LifeBuoy className="h-4 w-4" /> Support
          </span>
          <span className="flex h-7 w-7 items-center justify-center rounded-full bg-neutral-200 dark:bg-neutral-700">
            <User className="h-4 w-4" />
          </span>
        </div>
      </header>

      <div className="flex flex-1 overflow-hidden">
        {/* 사이드바 — 아직 실제 페이지가 없어 클릭 연결은 끊어둔 상태 */}
        <aside className="hidden w-60 shrink-0 flex-col overflow-y-auto border-r border-neutral-100 px-3 py-4 dark:border-gray-800 md:flex">
          <div className="mb-3 flex items-center gap-2 rounded-lg border border-neutral-200 px-3 py-2 text-sm text-neutral-400 dark:border-gray-700">
            <Search className="h-3.5 w-3.5" />
            Quick search...
            <span className="ml-auto text-[10px] text-neutral-300 dark:text-neutral-600">Ctrl K</span>
          </div>

          {topItems.map(({ icon: Icon, label }) => (
            <div
              key={label}
              className="flex cursor-not-allowed items-center gap-2 rounded px-2 py-1.5 text-sm text-neutral-500 dark:text-neutral-400"
            >
              <Icon className="h-4 w-4" />
              {label}
            </div>
          ))}

          {navGroups.map((group) => (
            <div key={group.label} className="mt-4">
              <p className="mb-1 px-2 text-[11px] uppercase tracking-wide text-neutral-400 dark:text-neutral-500">
                {group.label}
              </p>
              {group.items.map(({ icon: Icon, label }) => (
                <div
                  key={label}
                  className="flex cursor-not-allowed items-center gap-2 rounded px-2 py-1.5 text-sm text-neutral-500 opacity-70 dark:text-neutral-400"
                >
                  <Icon className="h-4 w-4" />
                  {label}
                  <ChevronRight className="ml-auto h-3.5 w-3.5" />
                </div>
              ))}
            </div>
          ))}

          <div className="mt-auto cursor-not-allowed border-t border-neutral-100 pt-3 text-sm text-neutral-400 dark:border-gray-800 dark:text-neutral-500">
            계정 관리
          </div>
        </aside>

        {/* 메인 콘텐츠 */}
        <main className="flex-1 overflow-y-auto px-6 py-10">
          <div className="mx-auto max-w-2xl text-center">
            <h1 className="text-2xl font-bold">이어서 진행하세요.</h1>
            <div className="mx-auto mt-6 flex max-w-md items-center gap-2 rounded-full border border-neutral-200 px-4 py-2.5 text-sm text-neutral-400 dark:border-gray-700">
              <Search className="h-4 w-4" />
              Search
            </div>
          </div>

          <div className="mx-auto mt-10 max-w-md">
            <p className="mb-2 text-sm font-medium text-neutral-500 dark:text-neutral-400">바로가기</p>
            <div className="divide-y divide-neutral-100 rounded-lg border border-neutral-100 dark:divide-gray-800 dark:border-gray-800">
              {shortcuts.map(({ label, href }) => (
                <Link
                  key={href}
                  href={href}
                  className="flex items-center justify-between px-4 py-3 text-sm transition-colors hover:bg-neutral-50 dark:hover:bg-neutral-900"
                >
                  {label}
                  <ChevronRight className="h-3.5 w-3.5 text-neutral-400" />
                </Link>
              ))}
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
