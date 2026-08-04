/**
 * 영수증 자동 OCR API 계층 — NEXT-004 §5.1 · §5.2
 *
 * 백엔드 계약은 FAST-004 §3.6을 따른다.
 * 이 모듈은 **예외를 던지지 않는다.** 실패도 결과 객체로 돌려주므로
 * 호출부에 try/catch가 새지 않는다.
 */

import { z } from "zod";

import { getAccessToken } from "@/lib/accessToken";

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "") ??
  "http://127.0.0.1:8000";

/** FAST-004 §2.3에서 확정된 경로. 부작용이 있어 GET이 아니라 POST다. */
const AUTO_PROCESS_PATH = "/api/dumb-and-dumber/receipts/auto-process";

// ── 응답 스키마 ─────────────────────────────────────────────────────────────
// 외부 입력이므로 캐스팅하지 않고 파싱한다. storeName / transactionDate /
// totalAmount는 파싱 실패 시 백엔드가 null을 보낸다(FAST-004 §3.5).

const receiptItemSchema = z.object({
  name: z.string(),
  quantity: z.number(),
  price: z.number(),
});

const receiptSchema = z.object({
  receiptId: z.string(),
  imageUrl: z.string(),
  storeName: z.string().nullable(),
  transactionDate: z.string().nullable(),
  items: z.array(receiptItemSchema),
  totalAmount: z.number().nullable(),
  needsManualReview: z.boolean(),
});

const receiptFailureSchema = z.object({
  objectKey: z.string(),
  reason: z.string(),
});

const autoProcessResponseSchema = z.object({
  success: z.boolean(),
  data: z.object({
    receipts: z.array(receiptSchema),
    hasMore: z.boolean(),
    failures: z.array(receiptFailureSchema),
  }),
});

export type ReceiptItem = z.infer<typeof receiptItemSchema>;
export type Receipt = z.infer<typeof receiptSchema>;
export type ReceiptFailure = z.infer<typeof receiptFailureSchema>;

// ── 에러 종류 ───────────────────────────────────────────────────────────────
// HTTP 상태를 화면이 직접 보지 않도록 여기서 종류로 번역한다(NEXT-004 §3.2).

export type ReceiptErrorKind =
  | "unauthorized"
  | "forbidden"
  | "unavailable"
  | "network"
  | "unknown";

const ERROR_MESSAGES: Record<ReceiptErrorKind, string> = {
  unauthorized: "로그인이 필요합니다.",
  forbidden: "이 기능을 사용할 권한이 없습니다.",
  unavailable: "영수증 저장소가 준비되지 않았습니다. 잠시 후 다시 시도해 주세요.",
  network: "서버에 연결할 수 없습니다.",
  unknown: "영수증을 불러오지 못했습니다.",
};

export type ReceiptFetchResult =
  | {
      ok: true;
      receipts: Receipt[];
      hasMore: boolean;
      failures: ReceiptFailure[];
    }
  | { ok: false; kind: ReceiptErrorKind; message: string };

function fail(kind: ReceiptErrorKind): ReceiptFetchResult {
  return { ok: false, kind, message: ERROR_MESSAGES[kind] };
}

function kindFromStatus(status: number): ReceiptErrorKind {
  if (status === 401) return "unauthorized";
  if (status === 403) return "forbidden";
  if (status === 503) return "unavailable";
  return "unknown";
}

/**
 * S3의 미처리 영수증을 OCR로 읽어 온다.
 *
 * 토큰이 없으면 네트워크 호출 없이 즉시 unauthorized로 끝낸다.
 * 백엔드 `detail` 원문은 화면에 노출하지 않는다 — 내부 정보가 새지 않도록
 * 위 ERROR_MESSAGES의 고정 문구만 쓴다.
 */
export async function fetchAutoProcessedReceipts(
  signal: AbortSignal,
): Promise<ReceiptFetchResult> {
  const token = getAccessToken();
  if (!token) return fail("unauthorized");

  let response: Response;
  try {
    response = await fetch(`${API_BASE}${AUTO_PROCESS_PATH}`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      signal,
    });
  } catch {
    // AbortError도 여기로 온다. 호출부(훅)가 signal.aborted로 구분한다.
    return fail("network");
  }

  if (!response.ok) return fail(kindFromStatus(response.status));

  let raw: unknown;
  try {
    raw = await response.json();
  } catch {
    return fail("unknown");
  }

  const parsed = autoProcessResponseSchema.safeParse(raw);
  if (!parsed.success || !parsed.data.success) return fail("unknown");

  const { receipts, hasMore, failures } = parsed.data.data;
  return { ok: true, receipts, hasMore, failures };
}
