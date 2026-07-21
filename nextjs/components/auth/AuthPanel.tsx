"use client";

import { useState } from "react";

import { SocialLoginButtons } from "@/components/auth/SocialLoginButtons";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { cn } from "@/lib/utils";

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "") ??
  "http://127.0.0.1:8000";

type AuthTab = "login" | "signup";

type AuthPanelProps = {
  defaultTab?: AuthTab;
  className?: string;
  onSuccess?: () => void;
};

const inputCls =
  "h-11 rounded-xl border-slate-200 bg-slate-50/50 dark:border-gray-700 dark:bg-[#1a1a1a] dark:text-neutral-100 dark:placeholder:text-neutral-600";

export function AuthPanel({
  defaultTab = "login",
  className,
  onSuccess,
}: AuthPanelProps) {
  const [tab, setTab] = useState<AuthTab>(defaultTab);
  const [signupLoading, setSignupLoading] = useState(false);

  const handleLogin = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    onSuccess?.();
  };

  const handleSignup = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    const formProps = Object.fromEntries(formData.entries());

    setSignupLoading(true);
    try {
      const res = await fetch(`${API_BASE}/signup`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formProps),
      });

      const data = (await res.json()) as {
        message?: string;
        detail?: string | { msg?: string }[];
      };

      if (!res.ok) {
        const detail =
          typeof data.detail === "string"
            ? data.detail
            : Array.isArray(data.detail)
              ? data.detail.map((d) => d.msg ?? String(d)).join(", ")
              : "회원가입 요청에 실패했습니다.";
        alert(detail);
        return;
      }

      onSuccess?.();
    } catch {
      alert("서버에 연결할 수 없습니다. 백엔드가 실행 중인지 확인해 주세요.");
    } finally {
      setSignupLoading(false);
    }
  };

  return (
    <div className={cn("w-full", className)}>
      <Tabs
        value={tab}
        onValueChange={(v) => setTab(v as AuthTab)}
        className="gap-6"
      >
        <TabsList className="grid h-11 w-full grid-cols-2 rounded-full bg-slate-100 p-1 dark:bg-[#1a1a1a]">
          <TabsTrigger
            value="login"
            className="rounded-full data-[state=active]:bg-white data-[state=active]:text-sky-700 data-[state=active]:shadow-sm dark:text-neutral-400 dark:data-[state=active]:bg-[#111111] dark:data-[state=active]:text-sky-400"
          >
            로그인
          </TabsTrigger>
          <TabsTrigger
            value="signup"
            className="rounded-full data-[state=active]:bg-white data-[state=active]:text-sky-700 data-[state=active]:shadow-sm dark:text-neutral-400 dark:data-[state=active]:bg-[#111111] dark:data-[state=active]:text-sky-400"
          >
            회원가입
          </TabsTrigger>
        </TabsList>

        {/* 로그인 탭 */}
        <TabsContent value="login" className="mt-0 space-y-5">
          <form onSubmit={handleLogin} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="login-user-id" className="dark:text-neutral-300">사용자 ID</Label>
              <Input id="login-user-id" name="userId" type="text" autoComplete="username" placeholder="아이디를 입력하세요" required className={inputCls} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="login-password" className="dark:text-neutral-300">비밀번호</Label>
              <Input id="login-password" name="password" type="password" autoComplete="current-password" placeholder="비밀번호를 입력하세요" required className={inputCls} />
            </div>
            <Button type="submit" className="h-11 w-full rounded-full bg-sky-600 text-base font-semibold hover:bg-sky-500 dark:bg-sky-500 dark:hover:bg-sky-400">
              로그인
            </Button>
          </form>
          <SocialLoginButtons />
        </TabsContent>

        {/* 회원가입 탭 */}
        <TabsContent value="signup" className="mt-0 space-y-5">
          <form onSubmit={handleSignup} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="signup-id" className="dark:text-neutral-300">아이디</Label>
              <Input id="signup-id" name="userId" type="text" autoComplete="username" placeholder="아이디" required className={inputCls} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="signup-password" className="dark:text-neutral-300">비밀번호</Label>
              <Input id="signup-password" name="password" type="password" autoComplete="new-password" placeholder="비밀번호" required className={inputCls} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="signup-nickname" className="dark:text-neutral-300">닉네임</Label>
              <Input id="signup-nickname" name="nickname" type="text" autoComplete="nickname" placeholder="닉네임" required className={inputCls} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="signup-email" className="dark:text-neutral-300">이메일</Label>
              <Input id="signup-email" name="email" type="email" autoComplete="email" placeholder="example@email.com" required className={inputCls} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="signup-address" className="dark:text-neutral-300">주소</Label>
              <Input id="signup-address" name="address" type="text" autoComplete="street-address" placeholder="주소를 입력하세요" required className={inputCls} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="signup-phone" className="dark:text-neutral-300">전화번호</Label>
              <Input id="signup-phone" name="phone" type="tel" autoComplete="tel" placeholder="010-0000-0000" required className={inputCls} />
            </div>
            <Button
              type="submit"
              disabled={signupLoading}
              className="h-11 w-full rounded-full bg-sky-600 text-base font-semibold hover:bg-sky-500 dark:bg-sky-500 dark:hover:bg-sky-400"
            >
              {signupLoading ? "처리 중..." : "회원가입"}
            </Button>
          </form>
        </TabsContent>
      </Tabs>
    </div>
  );
}
