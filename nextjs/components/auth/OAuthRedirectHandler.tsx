"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export function OAuthRedirectHandler() {
  const router = useRouter();

  useEffect(() => {
    const url = new URL(window.location.href);
    const auth = url.searchParams.get("auth");
    if (!auth) return;

    if (auth === "success") {
      router.replace("/dashboard");
      return;
    }

    const reason = url.searchParams.get("reason") ?? "unknown";
    alert(`소셜 로그인에 실패했습니다. (${reason})`);
    url.searchParams.delete("auth");
    url.searchParams.delete("reason");
    window.history.replaceState({}, "", url.toString());
  }, [router]);

  return null;
}
