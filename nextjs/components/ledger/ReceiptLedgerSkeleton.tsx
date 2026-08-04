import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";

type ReceiptLedgerSkeletonProps = {
  className?: string;
};

/** OCR·파싱에 2~4초가 걸리므로 결과 카드와 같은 골격으로 자리를 잡아 둔다. */
export function ReceiptLedgerSkeleton({
  className,
}: ReceiptLedgerSkeletonProps) {
  return (
    <div
      className={cn(
        "rounded-2xl border border-slate-200 bg-white p-5 dark:border-gray-700 dark:bg-surface",
        className,
      )}
      aria-busy="true"
      aria-live="polite"
    >
      <span className="sr-only">영수증을 인식하는 중입니다.</span>
      <div className="grid gap-6 md:grid-cols-[minmax(0,320px)_1fr]">
        <Skeleton className="aspect-[3/4] w-full rounded-xl" />
        <div className="space-y-4">
          <Skeleton className="h-5 w-32" />
          <Skeleton className="h-11 w-full rounded-xl" />
          <Skeleton className="h-5 w-24" />
          <Skeleton className="h-11 w-full rounded-xl" />
          <Skeleton className="h-5 w-20" />
          <div className="space-y-2">
            <Skeleton className="h-10 w-full rounded-lg" />
            <Skeleton className="h-10 w-full rounded-lg" />
            <Skeleton className="h-10 w-full rounded-lg" />
          </div>
          <Skeleton className="h-11 w-40 rounded-xl" />
        </div>
      </div>
    </div>
  );
}
