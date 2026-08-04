import Link from "next/link";

export function HomeFooter() {
  return (
    <footer className="border-t border-neutral-100 bg-white px-4 py-6 dark:border-gray-800 dark:bg-background sm:px-6">
      <div className="mx-auto flex w-full max-w-5xl flex-col items-center justify-between gap-3 px-4 text-center text-[10px] uppercase tracking-[0.12em] text-neutral-500 dark:text-neutral-400 sm:flex-row sm:text-left">
        <p>
          <span className="text-neutral-900 dark:text-neutral-100">RAG Tailor</span> — AI Education
        </p>
        <div className="flex items-center gap-6">
          <Link href="/notice" className="hover:text-neutral-900 dark:hover:text-neutral-100">
            공지사항
          </Link>
          <a href="mailto:rex@ragwatson.com" className="hover:text-neutral-900 dark:hover:text-neutral-100">
            rex@ragwatson.com
          </a>
        </div>
      </div>
    </footer>
  );
}
