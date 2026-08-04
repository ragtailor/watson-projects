"use client";

import { FileSpreadsheet, Upload, X } from "lucide-react";
import { useCallback, useRef, useState } from "react";

function validateCsv(file: File): string | null {
  if (!file.name.toLowerCase().endsWith(".csv")) return "CSV 파일만 업로드할 수 있습니다.";
  return null;
}

interface Props {
  onClose: () => void;
  onSuccess: () => void;
}

export function ContactsUpload({ onClose, onSuccess }: Props) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [message, setMessage] = useState<{ type: "ok" | "err"; text: string } | null>(null);
  const [lastFile, setLastFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);

  const uploadFile = useCallback(async (file: File) => {
    setIsUploading(true);
    try {
      const formData = new FormData();
      formData.append("file", file);
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/sherlock-homes/mycroft/upload`,
        { method: "POST", body: formData }
      );
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "업로드 실패");
      }
      const result = await response.json();
      setMessage({ type: "ok", text: `${result.count}개 연락처가 등록되었습니다.` });
      setTimeout(() => { onSuccess(); onClose(); }, 1500);
    } catch (err) {
      setMessage({ type: "err", text: `업로드 오류: ${err instanceof Error ? err.message : "알 수 없는 오류"}` });
    } finally {
      setIsUploading(false);
    }
  }, [onClose, onSuccess]);

  const applyFile = useCallback((file: File | undefined) => {
    if (!file) return;
    const err = validateCsv(file);
    if (err) { setMessage({ type: "err", text: err }); setLastFile(null); return; }
    setLastFile(file);
    setMessage({ type: "ok", text: `${file.name} (${(file.size / 1024).toFixed(1)} KB) 선택됨` });
    uploadFile(file);
  }, [uploadFile]);

  const onDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault(); setIsDragging(false); applyFile(e.dataTransfer.files?.[0]);
  }, [applyFile]);

  return (
    <>
      <div
        className="fixed inset-0 z-40 bg-black/30 dark:bg-black/50"
        onClick={onClose}
        aria-hidden="true"
      />
      <div
        role="dialog"
        aria-modal="true"
        aria-label="주소록 CSV 업로드"
        className="fixed left-1/2 top-1/2 z-50 w-[min(92vw,520px)] -translate-x-1/2 -translate-y-1/2 rounded-lg bg-white shadow-2xl dark:bg-surface"
      >
        {/* 헤더 */}
        <div className="flex h-12 items-center justify-between border-b border-neutral-100 px-5 dark:border-gray-800">
          <span className="text-sm font-medium text-neutral-900 dark:text-neutral-100">
            주소록 등록
          </span>
          <button
            type="button"
            onClick={onClose}
            className="text-neutral-400 hover:text-neutral-900 dark:hover:text-neutral-100"
            aria-label="닫기"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* 본문 */}
        <div className="space-y-5 px-5 py-6">
          <input
            ref={inputRef}
            type="file"
            accept=".csv,text/csv"
            className="sr-only"
            aria-label="Google 주소록 CSV 파일 선택"
            onChange={(e) => { applyFile(e.target.files?.[0]); e.target.value = ""; }}
          />

          {/* 드래그 앤 드롭 */}
          <div
            role="region"
            aria-label="CSV 드래그 앤 드롭 업로드 영역"
            onDrop={onDrop}
            onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
            onDragLeave={(e) => { e.preventDefault(); setIsDragging(false); }}
            className={[
              "flex min-h-[180px] flex-col items-center justify-center gap-3 rounded-lg border-2 border-dashed px-6 py-8 transition-colors",
              isDragging
                ? "border-neutral-900 bg-neutral-50 dark:border-neutral-100 dark:bg-surface-muted"
                : "border-neutral-200 bg-neutral-50/50 dark:border-gray-700 dark:bg-surface/50",
            ].join(" ")}
          >
            <FileSpreadsheet className="h-10 w-10 text-neutral-400 dark:text-neutral-500" strokeWidth={1.25} aria-hidden />
            <p className="text-center text-sm text-neutral-700 dark:text-neutral-300">
              Google 주소록에서 내보낸 CSV를 끌어다 놓으세요
            </p>
            <p className="text-center text-xs text-neutral-500 dark:text-neutral-500">
              contacts.google.com → 내보내기 → Google CSV
            </p>
          </div>

          {/* 구분선 */}
          <div className="relative">
            <div className="absolute inset-0 flex items-center" aria-hidden>
              <div className="w-full border-t border-neutral-200 dark:border-gray-700" />
            </div>
            <div className="relative flex justify-center text-[10px] uppercase tracking-[0.2em]">
              <span className="bg-white px-3 text-neutral-400 dark:bg-surface dark:text-neutral-500">또는</span>
            </div>
          </div>

          {/* 파일 선택 버튼 */}
          <div className="flex flex-col items-center gap-2">
            <button
              type="button"
              onClick={() => inputRef.current?.click()}
              disabled={isUploading}
              className="inline-flex items-center justify-center gap-2 rounded-none border border-neutral-900 bg-neutral-900 px-8 py-3 text-xs font-medium uppercase tracking-[0.12em] text-white transition-opacity hover:opacity-80 disabled:cursor-not-allowed disabled:opacity-50 dark:border-neutral-100 dark:bg-neutral-100 dark:text-neutral-900"
            >
              <Upload className="h-4 w-4" aria-hidden />
              {isUploading ? "업로드 중..." : "파일 선택"}
            </button>
          </div>

          {/* 결과 메시지 */}
          {message && (
            <p
              role="status"
              className={
                message.type === "ok"
                  ? "rounded-sm bg-neutral-100 px-4 py-3 text-sm text-neutral-800 dark:bg-surface-muted dark:text-neutral-200"
                  : "rounded-sm bg-red-50 px-4 py-3 text-sm text-red-800 dark:bg-red-950/30 dark:text-red-400"
              }
            >
              {message.text}
            </p>
          )}

          {lastFile && !message && (
            <p className="text-center text-xs text-neutral-400 dark:text-neutral-500">
              선택된 파일: {lastFile.name} · {(lastFile.size / 1024).toFixed(1)} KB
            </p>
          )}
        </div>
      </div>
    </>
  );
}
