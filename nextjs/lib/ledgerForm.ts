/**
 * 가계부 영수증 폼 스키마 — NEXT-004 §3.7 · §5.4
 *
 * 폼과 품목 리스트가 함께 참조하므로 별도 모듈에 둔다
 * (컴포넌트끼리 서로 임포트하면 순환 참조가 된다).
 */

import { z } from "zod";

import type { Receipt } from "@/lib/receiptApi";

const quantitySchema = z
  .number({ invalid_type_error: "수량을 숫자로 입력해 주세요." })
  .int("수량은 정수여야 합니다.")
  .min(1, "수량은 1 이상이어야 합니다.");

// 금액은 원 단위 정수다. 부동소수 연산을 쓰지 않는다.
const priceSchema = z
  .number({ invalid_type_error: "금액을 숫자로 입력해 주세요." })
  .int("금액은 원 단위 정수여야 합니다.")
  .min(0, "금액은 0 이상이어야 합니다.");

export const ledgerFormSchema = z.object({
  storeName: z.string().trim().min(1, "상호명을 입력해 주세요."),
  transactionDate: z.string().trim().min(1, "결제 일시를 입력해 주세요."),
  items: z.array(
    z.object({
      name: z.string().trim().min(1, "품목명을 입력해 주세요."),
      quantity: quantitySchema,
      price: priceSchema,
    }),
  ),
  totalAmount: priceSchema,
});

export type LedgerFormValues = z.infer<typeof ledgerFormSchema>;

/**
 * `<input type="datetime-local">`의 값 형식으로 맞춘다.
 * 백엔드는 타임존 없는 로컬 시각(`2026-08-04T10:00:00`)을 주므로 변환은 없고,
 * 이 입력의 기본 정밀도가 '분'이라 초 부분만 잘라 낸다.
 */
function toDateTimeLocal(value: string | null): string {
  if (!value) return "";
  return value.slice(0, 16);
}

/** 파싱 실패로 null이 온 필드는 빈 값으로 채운다. 임의로 지어내지 않는다. */
export function toFormValues(receipt: Receipt): LedgerFormValues {
  return {
    storeName: receipt.storeName ?? "",
    transactionDate: toDateTimeLocal(receipt.transactionDate),
    items: receipt.items.map((item) => ({
      name: item.name,
      quantity: item.quantity,
      price: item.price,
    })),
    totalAmount: receipt.totalAmount ?? 0,
  };
}

/** 품목 금액은 행 합계다(FAST-004 §3.6 예시 기준). 그래서 단순 합이 총액과 맞아야 한다. */
export function sumItemPrices(items: LedgerFormValues["items"]): number {
  return items.reduce(
    (acc, item) => acc + (Number.isFinite(item.price) ? item.price : 0),
    0,
  );
}

export function formatWon(value: number): string {
  return `${value.toLocaleString("ko-KR")}원`;
}
