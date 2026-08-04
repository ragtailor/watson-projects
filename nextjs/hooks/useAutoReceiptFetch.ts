"use client";

/**
 * 영수증 자동 처리 페칭 훅 — NEXT-004 §5.3
 *
 * 상태는 판별 유니언 하나로 관리한다(§3.2). isLoading/error/data를 각각
 * useState로 두면 "로딩 중인데 에러도 있음" 같은 불가능한 조합이 생긴다.
 */

import { useCallback, useEffect, useRef, useState } from "react";

import {
  fetchAutoProcessedReceipts,
  type Receipt,
  type ReceiptErrorKind,
  type ReceiptFailure,
} from "@/lib/receiptApi";

export type ReceiptFetchState =
  | { status: "idle" }
  | { status: "loading" }
  | {
      status: "success";
      receipts: Receipt[];
      hasMore: boolean;
      failures: ReceiptFailure[];
    }
  | { status: "error"; kind: ReceiptErrorKind; message: string };

export type UseAutoReceiptFetchResult = {
  state: ReceiptFetchState;
  refetch: () => void;
};

export function useAutoReceiptFetch(): UseAutoReceiptFetchResult {
  const [state, setState] = useState<ReceiptFetchState>({ status: "idle" });

  // 이 API는 OCR 과금과 S3 이동을 일으킨다(FAST-004 §3.2).
  // React 19 개발 모드는 effect를 두 번 실행하므로 마운트당 1회로 잠근다(§3.3).
  const startedRef = useRef(false);
  const inFlightRef = useRef(false);
  const controllerRef = useRef<AbortController | null>(null);
  // 언마운트 후 setState를 막는다.
  const mountedRef = useRef(true);

  const run = useCallback(() => {
    if (inFlightRef.current) return;
    inFlightRef.current = true;

    const controller = new AbortController();
    controllerRef.current = controller;
    setState({ status: "loading" });

    void fetchAutoProcessedReceipts(controller.signal)
      .then((result) => {
        if (controller.signal.aborted || !mountedRef.current) return;
        if (result.ok) {
          setState({
            status: "success",
            receipts: result.receipts,
            hasMore: result.hasMore,
            failures: result.failures,
          });
          return;
        }
        setState({
          status: "error",
          kind: result.kind,
          message: result.message,
        });
      })
      .finally(() => {
        inFlightRef.current = false;
      });
  }, []);

  useEffect(() => {
    mountedRef.current = true;
    if (!startedRef.current) {
      startedRef.current = true;
      run();
    }

    return () => {
      mountedRef.current = false;

      // 개발 모드(StrictMode)는 마운트 직후 cleanup을 한 번 돌리고 effect를
      // 다시 실행한다. 여기서 곧바로 abort하면 startedRef 잠금 때문에 재요청도
      // 일어나지 않아 화면이 로딩 상태로 멈춘다.
      // 그래서 다음 태스크까지 기다렸다가, 그때도 마운트돼 있지 않은
      // '진짜 언마운트'일 때만 취소한다. 요청 횟수는 1회로 유지된다.
      const controller = controllerRef.current;
      setTimeout(() => {
        if (!mountedRef.current) controller?.abort();
      }, 0);
    };
  }, [run]);

  // 재조회는 사용자가 명시적으로 누를 때만 한다. 폴링·자동 재시도는 없다.
  const refetch = useCallback(() => {
    run();
  }, [run]);

  return { state, refetch };
}
