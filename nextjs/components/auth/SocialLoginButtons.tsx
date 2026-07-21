"use client";

import { cn } from "@/lib/utils";

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "") ??
  "http://127.0.0.1:8000";

type Provider = {
  id: string;
  label: string;
  className: string;
  icon: React.ReactNode;
};

const providers: Provider[] = [
  {
    id: "google",
    label: "Google로 로그인",
    className: "bg-white border border-slate-200 dark:border-gray-700",
    icon: (
      <svg viewBox="0 0 48 48" className="h-5 w-5">
        <path
          fill="#FFC107"
          d="M43.611,20.083H42V20H24v8h11.303c-1.649,4.657-6.08,8-11.303,8c-6.627,0-12-5.373-12-12c0-6.627,5.373-12,12-12c3.059,0,5.842,1.154,7.961,3.039l5.657-5.657C34.046,6.053,29.268,4,24,4C12.955,4,4,12.955,4,24c0,11.045,8.955,20,20,20c11.045,0,20-8.955,20-20C44,22.659,43.862,21.35,43.611,20.083z"
        />
        <path
          fill="#FF3D00"
          d="M6.306,14.691l6.571,4.819C14.655,15.108,18.961,12,24,12c3.059,0,5.842,1.154,7.961,3.039l5.657-5.657C34.046,6.053,29.268,4,24,4C16.318,4,9.656,8.337,6.306,14.691z"
        />
        <path
          fill="#4CAF50"
          d="M24,44c5.166,0,9.86-1.977,13.409-5.192l-6.19-5.238C29.211,35.091,26.715,36,24,36c-5.202,0-9.619-3.317-11.283-7.946l-6.522,5.025C9.505,39.556,16.227,44,24,44z"
        />
        <path
          fill="#1976D2"
          d="M43.611,20.083L43.595,20H24v8h11.303c-0.792,2.237-2.231,4.166-4.087,5.571c0.001-0.001,0.002-0.001,0.003-0.002l6.19,5.238C36.971,39.205,44,34,44,24C44,22.659,43.862,21.35,43.611,20.083z"
        />
      </svg>
    ),
  },
  {
    id: "naver",
    label: "네이버로 로그인",
    className: "bg-[#03C75A]",
    icon: (
      <svg viewBox="0 0 24 24" className="h-5 w-5 fill-white">
        <path d="M16.273 12.845 7.376 0H0v24h7.727V11.155L16.624 24H24V0h-7.727z" />
      </svg>
    ),
  },
  {
    id: "kakao",
    label: "카카오로 로그인",
    className: "bg-[#FEE500]",
    icon: (
      <svg viewBox="0 0 24 24" className="h-5 w-5 fill-[#391B1B]">
        <path d="M12 3C6.477 3 2 6.633 2 11.032c0 2.822 1.822 5.302 4.573 6.729-.2.75-.725 2.719-.83 3.145-.13.529.194.523.407.38.167-.112 2.653-1.804 3.73-2.535.68.099 1.38.15 2.12.15 5.523 0 10-3.633 10-8.03C22 6.632 17.523 3 12 3z" />
      </svg>
    ),
  },
  {
    id: "x",
    label: "X로 로그인",
    className: "bg-black",
    icon: (
      <svg viewBox="0 0 24 24" className="h-5 w-5 fill-white">
        <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
      </svg>
    ),
  },
];

export function SocialLoginButtons() {
  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3">
        <div className="h-px flex-1 bg-slate-200 dark:bg-gray-700" />
        <span className="text-xs text-slate-400 dark:text-neutral-500">또는</span>
        <div className="h-px flex-1 bg-slate-200 dark:bg-gray-700" />
      </div>
      <div className="flex justify-center gap-3">
        {providers.map((p) => (
          <button
            key={p.id}
            type="button"
            aria-label={p.label}
            title={p.label}
            onClick={() => {
              window.location.href = `${API_BASE}/api/kingsman/oauth/${p.id}/authorize`;
            }}
            className={cn(
              "flex h-11 w-11 items-center justify-center rounded-full shadow-sm transition hover:scale-105 hover:shadow-md",
              p.className,
            )}
          >
            {p.icon}
          </button>
        ))}
      </div>
    </div>
  );
}
