import type { Metadata } from "next";

import { LedgerScreen } from "@/components/ledger/LedgerScreen";

export const metadata: Metadata = {
  title: "가계부 | RAG Tailor",
  description: "S3에 올린 영수증을 자동으로 인식해 가계부 항목으로 정리합니다.",
};

/** 서버 컴포넌트 껍데기. 상태와 폼은 LedgerScreen(클라이언트)이 맡는다. */
export default function LedgerPage() {
  return <LedgerScreen />;
}
