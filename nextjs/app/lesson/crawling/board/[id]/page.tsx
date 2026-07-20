export const dynamic = "force-dynamic";

import Link from "next/link";
import { notFound } from "next/navigation";
import { Button } from "@/components/ui/button";

const API_BASE = process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") ?? "";

interface Post {
  id: number;
  title: string;
  author: string;
  content: string;
  fileUrl: string | null;
  fileName: string | null;
  createdAt: string;
}

async function getPost(id: string): Promise<Post | null> {
  try {
    const res = await fetch(`${API_BASE}/api/board/${id}`, { cache: "no-store" });
    if (!res.ok) return null;
    return (await res.json()) as Post;
  } catch {
    return null;
  }
}

export default async function BoardDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const post = await getPost(id);
  if (!post) notFound();

  return (
    <>
      <p className="text-[10px] uppercase tracking-[0.3em] text-neutral-400">
        Lesson · Crawling
      </p>
      <h1 className="mt-2 text-sm font-medium uppercase tracking-[0.12em] text-neutral-900">
        4. 게시판 상세보기
      </h1>

      <div className="mt-8 max-w-xl">
        <div className="border border-neutral-200 p-6 space-y-5">
          <div>
            <p className="text-xs text-neutral-400 uppercase tracking-[0.08em]">제목</p>
            <p className="mt-1 text-sm font-medium text-neutral-900">{post.title}</p>
          </div>

          <div className="flex gap-8">
            <div>
              <p className="text-xs text-neutral-400 uppercase tracking-[0.08em]">작성자</p>
              <p className="mt-1 text-sm text-neutral-700">{post.author}</p>
            </div>
            <div>
              <p className="text-xs text-neutral-400 uppercase tracking-[0.08em]">작성일</p>
              <p className="mt-1 text-sm text-neutral-700">{post.createdAt}</p>
            </div>
          </div>

          <hr className="border-neutral-100" />

          <div>
            <p className="text-xs text-neutral-400 uppercase tracking-[0.08em]">내용</p>
            <p className="mt-2 whitespace-pre-wrap text-sm leading-relaxed text-neutral-700">
              {post.content}
            </p>
          </div>

          {post.fileUrl && (
            <>
              <hr className="border-neutral-100" />
              <div>
                <p className="text-xs text-neutral-400 uppercase tracking-[0.08em]">첨부파일</p>
                <a
                  href={post.fileUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="mt-2 inline-flex items-center gap-1.5 text-sm text-blue-600 hover:underline"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                    <polyline points="7 10 12 15 17 10" />
                    <line x1="12" y1="15" x2="12" y2="3" />
                  </svg>
                  {post.fileName ?? "첨부파일 다운로드"}
                </a>
              </div>
            </>
          )}
        </div>

        <div className="mt-4">
          <Button asChild variant="outline" className="rounded-none">
            <Link href="/lesson/crawling/board">목록으로</Link>
          </Button>
        </div>
      </div>
    </>
  );
}
