"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState, useRef, type FormEvent, type DragEvent } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";

const boardListHref = "/lesson/crawling/board";

const SQL = `CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(100),
    content TEXT NOT NULL,
    file_url TEXT,
    file_name VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_posts_created_at ON posts (created_at DESC);`;

export default function CrawlingBoardWritePage() {
  const router = useRouter();
  const [title, setTitle] = useState("");
  const [author, setAuthor] = useState("");
  const [content, setContent] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [files, setFiles] = useState<File[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [copied, setCopied] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (file) setFiles([file]);
  }

  function handleDrop(e: DragEvent<HTMLDivElement>) {
    e.preventDefault();
    setIsDragging(false);
    const pdf = Array.from(e.dataTransfer.files).find((f) => f.type === "application/pdf");
    if (pdf) setFiles([pdf]);
  }

  function removeFile(index: number) {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  }

  function formatSize(bytes: number) {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  }

  function handleCopy() {
    navigator.clipboard.writeText(SQL);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!title.trim() || !content.trim()) { setError("제목과 내용을 입력해주세요."); return; }
    setSubmitting(true);
    setError(null);

    let fileUrl: string | null = null;
    let fileName: string | null = null;

    if (files.length > 0) {
      const formData = new FormData();
      formData.append("file", files[0]);
      const uploadRes = await fetch("/api/upload", { method: "POST", body: formData });
      if (!uploadRes.ok) {
        const data = await uploadRes.json();
        setError(data.error ?? "파일 업로드 중 오류가 발생했습니다.");
        setSubmitting(false);
        return;
      }
      const uploaded = await uploadRes.json();
      fileUrl = uploaded.url;
      fileName = uploaded.fileName;
    }

    const res = await fetch("/api/board", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title, author, content, fileUrl, fileName }),
    });
    if (!res.ok) {
      const data = await res.json();
      setError(data.error ?? "등록 중 오류가 발생했습니다.");
      setSubmitting(false);
      return;
    }
    router.push(boardListHref);
    router.refresh();
  }

  const codeCls = "rounded bg-neutral-100 px-1 py-0.5 font-mono text-xs dark:bg-gray-800 dark:text-gray-300";

  return (
    <>
      <p className="text-[10px] uppercase tracking-[0.3em] text-neutral-400 dark:text-neutral-500">
        Lesson · Crawling
      </p>
      <h1 className="mt-2 text-sm font-medium uppercase tracking-[0.12em] text-neutral-900 dark:text-neutral-100">
        3. 게시판 글쓰기
      </h1>
      <p className="mt-3 max-w-xl text-sm leading-relaxed text-neutral-600 dark:text-neutral-400">
        새 글을 작성하면 게시판 목록에 추가됩니다.
      </p>

      <form onSubmit={handleSubmit} className="mt-8 max-w-xl space-y-5">
        <div className="space-y-2">
          <Label htmlFor="title" className="dark:text-neutral-300">제목</Label>
          <Input id="title" value={title} onChange={(e) => setTitle(e.target.value)} placeholder="제목을 입력하세요" className="rounded-none dark:border-gray-700 dark:bg-surface dark:text-neutral-100 dark:placeholder:text-neutral-600" />
        </div>
        <div className="space-y-2">
          <Label htmlFor="author" className="dark:text-neutral-300">작성자</Label>
          <Input id="author" value={author} onChange={(e) => setAuthor(e.target.value)} placeholder="이름을 입력하세요 (선택)" className="rounded-none dark:border-gray-700 dark:bg-surface dark:text-neutral-100 dark:placeholder:text-neutral-600" />
        </div>
        <div className="space-y-2">
          <Label htmlFor="content" className="dark:text-neutral-300">내용</Label>
          <Textarea id="content" value={content} onChange={(e) => setContent(e.target.value)} rows={8} placeholder="내용을 입력하세요" className="rounded-none dark:border-gray-700 dark:bg-surface dark:text-neutral-100 dark:placeholder:text-neutral-600" />
        </div>

        <div className="space-y-2">
          <Label className="dark:text-neutral-300">파일 첨부</Label>
          <div
            onClick={() => fileInputRef.current?.click()}
            onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
            onDragLeave={() => setIsDragging(false)}
            onDrop={handleDrop}
            className={`flex cursor-pointer flex-col items-center justify-center gap-2 border border-dashed px-4 py-8 text-sm transition-colors ${
              isDragging
                ? "border-neutral-900 bg-neutral-50 dark:border-neutral-100 dark:bg-surface-muted"
                : "border-neutral-300 text-neutral-400 hover:border-neutral-500 hover:text-neutral-600 dark:border-gray-700 dark:text-neutral-500 dark:hover:border-gray-500 dark:hover:text-neutral-400"
            }`}
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
              <polyline points="17 8 12 3 7 8" />
              <line x1="12" y1="3" x2="12" y2="15" />
            </svg>
            <span>클릭하거나 파일을 드래그하여 업로드</span>
            <input ref={fileInputRef} type="file" accept=".pdf,application/pdf" className="hidden" onChange={handleFileChange} />
          </div>

          {files.length > 0 && (
            <ul className="mt-2 space-y-1">
              {files.map((file, i) => (
                <li key={i} className="flex items-center justify-between border border-neutral-200 px-3 py-2 text-sm dark:border-gray-700">
                  <span className="truncate text-neutral-700 dark:text-neutral-300">{file.name}</span>
                  <span className="ml-4 shrink-0 text-neutral-400 dark:text-neutral-500">{formatSize(file.size)}</span>
                  <button type="button" onClick={() => removeFile(i)} className="ml-4 shrink-0 text-neutral-400 hover:text-red-500 dark:text-neutral-500 dark:hover:text-red-400" aria-label="삭제">✕</button>
                </li>
              ))}
            </ul>
          )}
        </div>

        {error && (
          <p className="rounded-sm bg-red-50 px-3 py-2 text-sm text-red-700 dark:bg-red-950/30 dark:text-red-400">{error}</p>
        )}

        <div className="flex gap-2">
          <Button type="submit" disabled={submitting} className="rounded-none">
            {submitting ? (files.length > 0 ? "업로드 중..." : "등록 중...") : "등록"}
          </Button>
          <Button type="button" variant="outline" className="rounded-none dark:border-gray-700 dark:text-neutral-300 dark:hover:bg-gray-800" asChild>
            <Link href={boardListHref}>취소</Link>
          </Button>
        </div>
      </form>

      <hr className="my-10 border-neutral-200 dark:border-gray-800" />

      <div className="max-w-xl space-y-6 text-sm text-neutral-700 dark:text-neutral-300">
        <div>
          <p className="leading-relaxed">Next.js에서 Neon DB(PostgreSQL)로 데이터를 직접 삽입할 수 있도록 설계한 SQL 테이블 생성 스크립트입니다.</p>
          <p className="mt-1 leading-relaxed text-neutral-500 dark:text-neutral-500">화면에 있는 제목, 작성자, 내용 입력 필드와 파일 첨부(Vercel Blob URL 저장용) 기능을 모두 반영하였습니다.</p>
        </div>

        <div>
          <h2 className="font-semibold text-neutral-900 dark:text-neutral-100">🛠️ Neon DB (PostgreSQL) 테이블 생성 SQL</h2>
          <p className="mt-1 text-neutral-500 dark:text-neutral-500">Neon DB의 SQL Editor나 데이터베이스 클라이언트에서 아래 명령어를 실행하여 테이블을 생성하세요.</p>
          <div className="relative mt-3">
            <pre className="overflow-x-auto rounded-sm border border-neutral-200 bg-neutral-50 p-4 text-xs leading-relaxed text-neutral-800 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-200">
              {SQL}
            </pre>
            <button
              type="button"
              onClick={handleCopy}
              className="absolute right-2 top-2 flex items-center gap-1 rounded-sm border border-neutral-300 bg-white px-2 py-1 text-xs text-neutral-600 transition-colors hover:border-neutral-500 hover:text-neutral-900 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-300 dark:hover:border-gray-400 dark:hover:text-gray-100"
            >
              {copied ? (
                <><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12" /></svg>복사됨</>
              ) : (
                <><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2" /><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" /></svg>복사</>
              )}
            </button>
          </div>
        </div>

        <div>
          <h2 className="font-semibold text-neutral-900 dark:text-neutral-100">💡 Next.js 및 Vercel Blob 연동 시 참고 팁</h2>
          <p className="mt-1 text-neutral-500 dark:text-neutral-500">Next.js Server Actions나 API Route에서 데이터를 등록할 때 구조는 대략 다음과 같이 흘러가게 됩니다.</p>
          <ol className="mt-3 list-decimal space-y-2 pl-5 text-neutral-600 dark:text-neutral-400">
            <li><span className="font-medium text-neutral-800 dark:text-neutral-200">Vercel Blob 업로드:</span> 사용자가 파일을 첨부하고 &apos;등록&apos;을 누르면, 프론트엔드 또는 서버에서 Vercel Blob SDK(<code className={codeCls}>@vercel/blob</code>)의 <code className={codeCls}>put()</code> 메소드를 사용해 파일을 먼저 업로드합니다.</li>
            <li><span className="font-medium text-neutral-800 dark:text-neutral-200">URL 확보:</span> 업로드가 성공하면 Vercel Blob으로부터 <code className={codeCls}>https://xxxxxx.public.blob.vercel-storage.com/...</code> 형태의 <code className={codeCls}>url</code>을 응답받습니다.</li>
            <li><span className="font-medium text-neutral-800 dark:text-neutral-200">Neon DB 저장:</span> 이 <code className={codeCls}>url</code> 값과 사용자가 입력한 <code className={codeCls}>title</code>, <code className={codeCls}>author</code>, <code className={codeCls}>content</code>를 함께 Neon DB의 <code className={codeCls}>posts</code> 테이블에 INSERT 합니다.</li>
          </ol>
          <p className="mt-3 text-neutral-500 dark:text-neutral-500"><code className={codeCls}>file_url</code> 컬럼은 <code className={codeCls}>TEXT</code> 타입으로 지정하는 것이 가장 안전합니다.</p>
        </div>
      </div>
    </>
  );
}
