"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  ChevronsUpDown,
  Globe,
  Layers,
  Menu,
  MonitorSmartphone,
  Shield,
  ShieldCheck,
  Sparkles,
  Workflow,
  X,
} from "lucide-react";

import { AuthLoginButton } from "@/components/auth/AuthLoginButton";

const solutionsColumns = [
  [
    { icon: Sparkles, title: "AI", desc: "Build intelligent applications with AI at the edge" },
    { icon: Globe, title: "Network", desc: "Global network services for performance and reliability" },
    { icon: Workflow, title: "Workflows", desc: "Orchestrate complex multi-step processes" },
  ],
  [
    { icon: ShieldCheck, title: "AI Security", desc: "Secure and control AI adoption without slowing innovation." },
    { icon: Layers, title: "Platforms", desc: "Build platforms on Cloudflare's infrastructure" },
  ],
  [
    { icon: MonitorSmartphone, title: "Frontends", desc: "Deploy frontend applications globally in seconds" },
    { icon: Shield, title: "Security", desc: "Protect your applications from threats" },
  ],
];

function SolutionsDropdown() {
  return (
    <div className="grid w-[720px] grid-cols-3 gap-8 rounded-2xl bg-neutral-100 p-6 shadow-lg">
      {solutionsColumns.map((column, i) => (
        <div key={i} className="flex flex-col gap-5">
          {column.map(({ icon: Icon, title, desc }) => (
            <div key={title} className="flex items-start gap-3">
              <Icon className="mt-0.5 h-5 w-5 shrink-0 text-neutral-700" />
              <div>
                <p className="text-sm font-semibold text-neutral-900">{title}</p>
                <p className="mt-0.5 text-xs leading-snug text-neutral-600">{desc}</p>
              </div>
            </div>
          ))}
        </div>
      ))}
    </div>
  );
}

function PlaceholderDropdown() {
  return (
    <div className="w-[240px] rounded-2xl bg-neutral-100 p-6 shadow-lg">
      <p className="text-sm text-neutral-500">준비 중입니다</p>
    </div>
  );
}

const navItems = [
  { label: "Products", dropdown: PlaceholderDropdown },
  { label: "Solutions", dropdown: SolutionsDropdown },
  { label: "Resources", dropdown: PlaceholderDropdown },
  { label: "Pricing", dropdown: null },
] as const;

export function TopBar() {
  const pathname = usePathname();
  const [drawerOpen, setDrawerOpen] = useState(false);

  // 로그인 후 대시보드는 자체 상단바를 쓰므로 사이트 공통 TopBar를 띄우지 않는다.
  if (pathname.startsWith("/dashboard")) return null;

  return (
    <>
      <header className="fixed inset-x-0 top-0 z-50 flex h-16 items-center justify-between bg-white px-6">
        {/* 로고 */}
        <Link href="/" className="shrink-0 text-lg font-bold tracking-tight text-neutral-900">
          RAG<span className="text-sky-600"> Tailor</span>
        </Link>

        {/* 데스크탑 네비게이션 */}
        <nav className="hidden items-center gap-1 lg:flex" aria-label="주 메뉴">
          {navItems.map(({ label, dropdown: Dropdown }) =>
            Dropdown ? (
              <div key={label} className="group relative">
                <button
                  type="button"
                  className="flex items-center gap-1 rounded-md px-3 py-2 text-sm font-medium text-neutral-900 transition-colors group-hover:bg-neutral-100"
                >
                  {label}
                  <ChevronsUpDown className="h-3.5 w-3.5" />
                </button>

                {/* 드롭다운 팝업 */}
                <div className="invisible absolute left-1/2 top-full -translate-x-1/2 pt-2 opacity-0 transition-opacity duration-150 group-hover:visible group-hover:opacity-100">
                  <Dropdown />
                </div>
              </div>
            ) : (
              <button
                key={label}
                type="button"
                className="flex items-center gap-1 rounded-md px-3 py-2 text-sm font-medium text-neutral-900 transition-colors hover:bg-neutral-100"
              >
                {label}
              </button>
            ),
          )}
        </nav>

        {/* 데스크탑 우측 유틸리티 */}
        <div className="hidden shrink-0 items-center gap-5 lg:flex">
          <AuthLoginButton
            label="Login"
            className="rounded-full border border-neutral-300 bg-white px-4 py-2 text-sm font-medium text-neutral-900 shadow-none hover:bg-neutral-50"
          />
          <button
            type="button"
            className="rounded-full bg-neutral-900 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-neutral-800"
          >
            Contact sales
          </button>
        </div>

        {/* 모바일: 햄버거 */}
        <button
          type="button"
          onClick={() => setDrawerOpen((v) => !v)}
          className="flex items-center text-neutral-900 lg:hidden"
          aria-expanded={drawerOpen}
          aria-controls="mobile-drawer"
          aria-label={drawerOpen ? "메뉴 닫기" : "메뉴 열기"}
        >
          {drawerOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
        </button>
      </header>

      {/* 모바일 드로어 */}
      {drawerOpen && (
        <>
          <div
            className="fixed inset-0 z-40 bg-black/20 lg:hidden"
            onClick={() => setDrawerOpen(false)}
            aria-hidden="true"
          />
          <div
            id="mobile-drawer"
            role="dialog"
            aria-modal="true"
            aria-label="모바일 메뉴"
            className="fixed inset-x-0 top-16 z-50 flex flex-col gap-1 bg-white p-4 shadow-lg lg:hidden"
          >
            {navItems.map(({ label, dropdown }) => (
              <button
                key={label}
                type="button"
                className="flex items-center justify-between rounded-md px-3 py-3 text-left text-sm font-medium text-neutral-900 hover:bg-neutral-100"
              >
                {label}
                {dropdown && <ChevronsUpDown className="h-3.5 w-3.5" />}
              </button>
            ))}
            <div className="mt-2 flex flex-col gap-2 border-t border-neutral-100 pt-4">
              <AuthLoginButton
                label="Login"
                className="w-full rounded-full border border-neutral-300 bg-white px-4 py-2 text-sm font-medium text-neutral-900 shadow-none hover:bg-neutral-50"
              />
              <button
                type="button"
                className="w-full rounded-full bg-neutral-900 px-4 py-2 text-sm font-medium text-white hover:bg-neutral-800"
              >
                Contact sales
              </button>
            </div>
          </div>
        </>
      )}
    </>
  );
}
