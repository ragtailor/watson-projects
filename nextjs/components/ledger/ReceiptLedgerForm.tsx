"use client";

import { useForm, useWatch } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { AlertTriangle } from "lucide-react";

import { ReceiptItemList } from "@/components/ledger/ReceiptItemList";
import { ReceiptPreview } from "@/components/ledger/ReceiptPreview";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  ledgerFormSchema,
  sumItemPrices,
  toFormValues,
  formatWon,
  type LedgerFormValues,
} from "@/lib/ledgerForm";
import type { Receipt } from "@/lib/receiptApi";

type ReceiptLedgerFormProps = {
  receipt: Receipt;
  onReload: () => void;
};

const inputCls =
  "h-11 rounded-xl border-slate-200 bg-slate-50/50 dark:border-gray-700 dark:bg-surface-muted dark:text-neutral-100";

/** 파싱 실패로 null이 온 필드에 붙이는 표시. 사용자가 어디를 볼지 알게 한다. */
function MissingBadge() {
  return (
    <Badge variant="outline" className="border-amber-500 text-amber-600 dark:text-amber-400">
      확인 필요
    </Badge>
  );
}

export function ReceiptLedgerForm({ receipt, onReload }: ReceiptLedgerFormProps) {
  const {
    register,
    control,
    setValue,
    handleSubmit,
    formState: { errors },
  } = useForm<LedgerFormValues>({
    resolver: zodResolver(ledgerFormSchema),
    defaultValues: toFormValues(receipt),
  });

  const watchedItems = useWatch({ control, name: "items" }) ?? [];
  const watchedTotal = useWatch({ control, name: "totalAmount" });

  const itemsSum = sumItemPrices(watchedItems);
  const total = Number.isFinite(watchedTotal) ? watchedTotal : 0;
  const mismatch = itemsSum !== total;

  // 저장 API(POST .../entries)가 백엔드에 없다 — NEXT-004 §2.3 · §5.6.
  // 없는 엔드포인트를 부르는 죽은 코드를 미리 쓰지 않는다.
  const onSubmit = handleSubmit(() => {});

  return (
    <form
      onSubmit={onSubmit}
      className="rounded-2xl border border-slate-200 bg-white p-5 dark:border-gray-700 dark:bg-surface"
    >
      {receipt.needsManualReview && (
        <div className="mb-4 flex items-center gap-2">
          <AlertTriangle className="h-4 w-4 text-amber-500" />
          <span className="text-sm font-medium text-amber-600 dark:text-amber-400">
            확인이 필요한 항목이 있습니다.
          </span>
        </div>
      )}

      <div className="grid gap-6 md:grid-cols-[minmax(0,320px)_1fr]">
        <ReceiptPreview
          imageUrl={receipt.imageUrl}
          storeName={receipt.storeName}
          onReload={onReload}
        />

        <div className="space-y-5">
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <Label htmlFor={`${receipt.receiptId}-store`} className="dark:text-neutral-300">
                상호명
              </Label>
              {receipt.storeName === null && <MissingBadge />}
            </div>
            <Input
              id={`${receipt.receiptId}-store`}
              {...register("storeName")}
              className={inputCls}
            />
            {errors.storeName && (
              <p className="text-xs text-destructive">{errors.storeName.message}</p>
            )}
          </div>

          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <Label htmlFor={`${receipt.receiptId}-date`} className="dark:text-neutral-300">
                결제 일시
              </Label>
              {receipt.transactionDate === null && <MissingBadge />}
            </div>
            <Input
              id={`${receipt.receiptId}-date`}
              type="datetime-local"
              {...register("transactionDate")}
              className={inputCls}
            />
            {errors.transactionDate && (
              <p className="text-xs text-destructive">{errors.transactionDate.message}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label className="dark:text-neutral-300">구매 품목</Label>
            <ReceiptItemList control={control} register={register} errors={errors} />
          </div>

          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <Label htmlFor={`${receipt.receiptId}-total`} className="dark:text-neutral-300">
                총 금액
              </Label>
              {receipt.totalAmount === null && <MissingBadge />}
            </div>
            <Input
              id={`${receipt.receiptId}-total`}
              type="number"
              inputMode="numeric"
              {...register("totalAmount", { valueAsNumber: true })}
              className={inputCls}
            />
            {errors.totalAmount && (
              <p className="text-xs text-destructive">{errors.totalAmount.message}</p>
            )}

            {/* 검산은 안내만 한다. 값을 자동으로 덮어쓰면 사용자가 틀린 걸 알 수 없다. */}
            {mismatch && (
              <div className="flex flex-wrap items-center gap-2 rounded-lg bg-amber-50 px-3 py-2 text-xs text-amber-700 dark:bg-surface-muted dark:text-amber-400">
                <span>
                  품목 합계 {formatWon(itemsSum)} · 총액 {formatWon(total)} — 차액{" "}
                  {formatWon(Math.abs(itemsSum - total))}
                </span>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() =>
                    setValue("totalAmount", itemsSum, { shouldValidate: true })
                  }
                >
                  합계로 맞추기
                </Button>
              </div>
            )}
          </div>

          <div className="flex items-center gap-3 pt-1">
            <Button type="submit" disabled className="rounded-full">
              가계부 저장
            </Button>
            <span className="text-xs text-neutral-500 dark:text-neutral-400">
              저장 API 준비 중입니다.
            </span>
          </div>
        </div>
      </div>
    </form>
  );
}
