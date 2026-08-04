"use client";

import {
  useFieldArray,
  type Control,
  type FieldErrors,
  type UseFormRegister,
} from "react-hook-form";
import { Plus, Trash2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import type { LedgerFormValues } from "@/lib/ledgerForm";

type ReceiptItemListProps = {
  control: Control<LedgerFormValues>;
  register: UseFormRegister<LedgerFormValues>;
  errors: FieldErrors<LedgerFormValues>;
};

const inputCls =
  "h-9 rounded-lg border-slate-200 bg-white dark:border-gray-700 dark:bg-surface-muted dark:text-neutral-100";

/**
 * 구매 품목 리스트 — 행 추가·삭제가 되는 동적 폼.
 *
 * useFieldArray를 쓰는 이유는 인덱스 관리를 직접 하지 않기 위해서다.
 * FormData 방식으로는 행을 지울 때 남은 행의 값이 밀리기 쉽다.
 */
export function ReceiptItemList({
  control,
  register,
  errors,
}: ReceiptItemListProps) {
  const { fields, append, remove } = useFieldArray({ control, name: "items" });

  return (
    <div className="space-y-3">
      <div className="overflow-x-auto rounded-xl border border-slate-200 dark:border-gray-700">
        <Table>
          <TableHeader>
            <TableRow className="dark:border-gray-700">
              <TableHead className="dark:text-neutral-300">품목명</TableHead>
              <TableHead className="w-24 dark:text-neutral-300">수량</TableHead>
              <TableHead className="w-32 dark:text-neutral-300">금액</TableHead>
              <TableHead className="w-12" />
            </TableRow>
          </TableHeader>
          <TableBody>
            {fields.length === 0 && (
              <TableRow className="dark:border-gray-700">
                <TableCell
                  colSpan={4}
                  className="py-6 text-center text-sm text-neutral-500 dark:text-neutral-400"
                >
                  인식된 품목이 없습니다. 아래에서 직접 추가해 주세요.
                </TableCell>
              </TableRow>
            )}

            {fields.map((field, index) => {
              const rowError = errors.items?.[index];
              return (
                <TableRow key={field.id} className="dark:border-gray-700">
                  <TableCell className="align-top">
                    <Input
                      {...register(`items.${index}.name`)}
                      aria-label={`${index + 1}번 품목명`}
                      className={inputCls}
                    />
                    {rowError?.name && (
                      <p className="mt-1 text-xs text-destructive">
                        {rowError.name.message}
                      </p>
                    )}
                  </TableCell>
                  <TableCell className="align-top">
                    <Input
                      type="number"
                      inputMode="numeric"
                      {...register(`items.${index}.quantity`, {
                        valueAsNumber: true,
                      })}
                      aria-label={`${index + 1}번 수량`}
                      className={inputCls}
                    />
                    {rowError?.quantity && (
                      <p className="mt-1 text-xs text-destructive">
                        {rowError.quantity.message}
                      </p>
                    )}
                  </TableCell>
                  <TableCell className="align-top">
                    <Input
                      type="number"
                      inputMode="numeric"
                      {...register(`items.${index}.price`, {
                        valueAsNumber: true,
                      })}
                      aria-label={`${index + 1}번 금액`}
                      className={inputCls}
                    />
                    {rowError?.price && (
                      <p className="mt-1 text-xs text-destructive">
                        {rowError.price.message}
                      </p>
                    )}
                  </TableCell>
                  <TableCell className="align-top">
                    <Button
                      type="button"
                      variant="ghost"
                      size="icon"
                      onClick={() => remove(index)}
                      aria-label={`${index + 1}번 품목 삭제`}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </div>

      <Button
        type="button"
        variant="outline"
        size="sm"
        onClick={() => append({ name: "", quantity: 1, price: 0 })}
      >
        <Plus className="h-4 w-4" />
        품목 추가
      </Button>
    </div>
  );
}
