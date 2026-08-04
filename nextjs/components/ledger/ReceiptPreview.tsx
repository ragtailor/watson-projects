"use client";

import { useState } from "react";
import { ImageOff } from "lucide-react";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

type ReceiptPreviewProps = {
  imageUrl: string;
  storeName: string | null;
  onReload: () => void;
  className?: string;
};

/**
 * 영수증 원본 미리보기 — NEXT-004 §3.5
 *
 * imageUrl은 TTL 10분짜리 presigned URL이다. 사용자가 품목을 오래 고치면
 * 만료돼 이미지가 깨진다. 그때 **폼 입력값은 건드리지 않고** 안내만 띄운다.
 *
 * next/image를 쓰지 않는다 — next.config.mjs가 images.unoptimized이고
 * presigned URL은 remotePatterns 등록이 필요해 이득이 없다.
 */
export function ReceiptPreview({
  imageUrl,
  storeName,
  onReload,
  className,
}: ReceiptPreviewProps) {
  const [expired, setExpired] = useState(false);

  if (expired) {
    return (
      <div
        className={cn(
          "flex aspect-[3/4] w-full flex-col items-center justify-center gap-3 rounded-xl border border-dashed border-slate-300 bg-slate-50 p-6 text-center dark:border-gray-700 dark:bg-surface-muted",
          className,
        )}
      >
        <ImageOff className="h-6 w-6 text-neutral-400 dark:text-neutral-500" />
        <p className="text-sm text-neutral-600 dark:text-neutral-400">
          이미지 링크가 만료되었습니다.
          <br />
          입력하신 내용은 그대로 남아 있습니다.
        </p>
        <Button type="button" variant="outline" size="sm" onClick={onReload}>
          다시 불러오기
        </Button>
      </div>
    );
  }

  return (
    <img
      src={imageUrl}
      alt={`${storeName ?? "상호명 미인식"} 영수증 원본`}
      onError={() => setExpired(true)}
      className={cn(
        "aspect-[3/4] w-full rounded-xl border border-slate-200 bg-slate-50 object-contain dark:border-gray-700 dark:bg-surface-muted",
        className,
      )}
    />
  );
}
