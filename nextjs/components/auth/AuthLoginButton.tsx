"use client";

import Link from "next/link";

import { cn } from "@/lib/utils";

type AuthLoginButtonProps = {
  className?: string;
  label?: string;
};

export function AuthLoginButton({ className, label = "로그인" }: AuthLoginButtonProps) {
  return (
    <Link
      href="/login"
      className={cn(
        "inline-flex items-center justify-center rounded-full border border-slate-200 bg-slate-50 px-3 py-2 text-xs font-semibold text-slate-800 transition-colors hover:bg-slate-100 sm:px-4 sm:text-sm",
        className,
      )}
    >
      {label}
    </Link>
  );
}
