export function HomeContact() {
  return (
    <section className="hidden border-t border-neutral-100 bg-white py-20 dark:border-gray-800 dark:bg-background sm:py-24 lg:block">
      <div className="mx-auto w-full max-w-lg px-4 text-center sm:max-w-xl sm:px-6">
        <p className="text-[10px] uppercase tracking-[0.3em] text-neutral-400 dark:text-neutral-500">
          Contact
        </p>
        <h2 className="mt-3 text-xl font-medium tracking-tight text-neutral-900 dark:text-neutral-100">
          교육 문의
        </h2>
        <p className="mx-auto mt-4 max-w-md text-sm text-neutral-600 dark:text-neutral-400">
          AI 서비스 개발 교육 일정·커리큘럼 문의는 아래 이메일로 연락주세요.
        </p>
        <a
          href="mailto:rex@ragwatson.com"
          className="mt-8 inline-block border border-neutral-900 px-8 py-3 text-[11px] font-medium uppercase tracking-[0.15em] text-neutral-900 transition-colors hover:bg-neutral-900 hover:text-white dark:border-neutral-100 dark:text-neutral-100 dark:hover:bg-neutral-100 dark:hover:text-neutral-900"
        >
          rex@ragwatson.com
        </a>
      </div>
    </section>
  );
}
