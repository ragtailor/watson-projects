"use client";

/**
 * 가계부 화면 컨테이너 — NEXT-004 §3.6 상태 매핑
 *
 * `app/ledger/page.tsx`를 서버 컴포넌트로 유지하기 위해(§4 클라이언트 경계를
 * 좁게) 훅과 상태 분기를 이 컴포넌트가 맡는다.
 *
 * 에러·경고는 토스트가 아니라 인라인 UI로 표시한다 — `<Toaster />`가
 * app/layout.tsx에 마운트돼 있지 않아 toast()가 아무것도 띄우지 않는다(§2.9).
 */

import Link from "next/link";
import { AlertCircle, Inbox, RefreshCw } from "lucide-react";

import { ReceiptLedgerForm } from "@/components/ledger/ReceiptLedgerForm";
import { ReceiptLedgerSkeleton } from "@/components/ledger/ReceiptLedgerSkeleton";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import {
  Empty,
  EmptyDescription,
  EmptyHeader,
  EmptyMedia,
  EmptyTitle,
} from "@/components/ui/empty";
import {
  useAutoReceiptFetch,
  type ReceiptFetchState,
} from "@/hooks/useAutoReceiptFetch";
import type { ReceiptErrorKind } from "@/lib/receiptApi";

type ErrorPanelProps = {
  kind: ReceiptErrorKind;
  message: string;
  onRetry: () => void;
};

function ErrorPanel({ kind, message, onRetry }: ErrorPanelProps) {
  return (
    <Alert
      variant="destructive"
      className="border-slate-200 dark:border-gray-700 dark:bg-surface"
    >
      <AlertCircle />
      <AlertTitle>영수증을 불러오지 못했습니다</AlertTitle>
      <AlertDescription>
        <p>{message}</p>
        {kind === "unauthorized" ? (
          <Button asChild variant="outline" size="sm" className="mt-2">
            <Link href="/login">로그인하러 가기</Link>
          </Button>
        ) : kind === "forbidden" ? null : (
          <Button
            type="button"
            variant="outline"
            size="sm"
            className="mt-2"
            onClick={onRetry}
          >
            <RefreshCw className="h-4 w-4" />
            다시 시도
          </Button>
        )}
      </AlertDescription>
    </Alert>
  );
}

function EmptyPanel() {
  return (
    <Empty className="rounded-2xl border border-slate-200 bg-white dark:border-gray-700 dark:bg-surface">
      <EmptyHeader>
        <EmptyMedia variant="icon">
          <Inbox />
        </EmptyMedia>
        <EmptyTitle>새로 인식할 영수증이 없습니다</EmptyTitle>
        <EmptyDescription>
          영수증 사진을 올리면 이 화면에서 자동으로 인식해 드립니다.
        </EmptyDescription>
      </EmptyHeader>
    </Empty>
  );
}

type SuccessPanelProps = {
  state: Extract<ReceiptFetchState, { status: "success" }>;
  onRefetch: () => void;
};

function SuccessPanel({ state, onRefetch }: SuccessPanelProps) {
  const { receipts, failures, hasMore } = state;

  // 부분 실패를 전체 실패로 취급하지 않는다. 성공분은 그대로 보여 준다.
  const failureBanner = failures.length > 0 && (
    <Alert className="border-amber-300 bg-amber-50 dark:border-gray-700 dark:bg-surface">
      <AlertCircle className="text-amber-600 dark:text-amber-400" />
      <AlertTitle className="text-amber-700 dark:text-amber-400">
        {failures.length}장은 읽지 못했습니다
      </AlertTitle>
      <AlertDescription className="text-amber-700/90 dark:text-amber-400/90">
        나머지 영수증은 아래에서 확인하실 수 있습니다.
      </AlertDescription>
    </Alert>
  );

  if (receipts.length === 0) {
    return (
      <div className="space-y-4">
        {failureBanner}
        <EmptyPanel />
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {failureBanner}

      {receipts.map((receipt) => (
        <ReceiptLedgerForm
          key={receipt.receiptId}
          receipt={receipt}
          onReload={onRefetch}
        />
      ))}

      {hasMore && (
        <div className="flex justify-center pt-2">
          <Button type="button" variant="outline" onClick={onRefetch}>
            더 불러오기
          </Button>
        </div>
      )}
    </div>
  );
}

export function LedgerScreen() {
  const { state, refetch } = useAutoReceiptFetch();

  return (
    <section className="mx-auto w-full max-w-5xl px-4 py-10 md:px-6">
      <header className="mb-6 flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-neutral-900 dark:text-neutral-100">
            가계부
          </h1>
          <p className="mt-1 text-sm text-neutral-500 dark:text-neutral-400">
            올려 두신 영수증을 자동으로 인식했습니다. 내용을 확인하고 고쳐 주세요.
          </p>
        </div>

        {state.status !== "loading" && (
          <Button type="button" variant="outline" size="sm" onClick={refetch}>
            <RefreshCw className="h-4 w-4" />
            다시 불러오기
          </Button>
        )}
      </header>

      {(state.status === "idle" || state.status === "loading") && (
        <ReceiptLedgerSkeleton />
      )}

      {state.status === "error" && (
        <ErrorPanel kind={state.kind} message={state.message} onRetry={refetch} />
      )}

      {state.status === "success" && (
        <SuccessPanel state={state} onRefetch={refetch} />
      )}
    </section>
  );
}
