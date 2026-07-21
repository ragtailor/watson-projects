"use client";

import { useEffect } from "react";

export function OAuthRedirectHandler() {
  useEffect(() => {
    const url = new URL(window.location.href);
    const auth = url.searchParams.get("auth");
    if (!auth) return;

    if (auth === "success") {
      alert("로그인되었습니다.");
    } else if (auth === "error") {
      const reason = url.searchParams.get("reason") ?? "unknown";
      alert(`소셜 로그인에 실패했습니다. (${reason})`);
    }

    url.searchParams.delete("auth");
    url.searchParams.delete("reason");
    window.history.replaceState({}, "", url.toString());
  }, []);

  return null;
}
