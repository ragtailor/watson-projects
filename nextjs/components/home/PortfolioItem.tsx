import { cn } from "@/lib/utils";

import type { PortfolioItemData } from "./portfolio-data";

type PortfolioItemProps = {
  item: PortfolioItemData;
  featured?: boolean;
  className?: string;
};

export function PortfolioItem({
  item,
  featured = false,
  className,
}: PortfolioItemProps) {
  return (
    <article className={cn("group flex flex-col", className)}>
      <div
        className={cn(
          "relative flex items-center justify-center border border-neutral-200 bg-neutral-50 transition-colors group-hover:border-neutral-400 dark:border-gray-800 dark:bg-surface dark:group-hover:border-gray-500",
          featured ? "aspect-[3/4] min-h-[320px]" : "aspect-square",
        )}
      >
        <span className="px-4 text-center text-[10px] font-medium uppercase tracking-[0.2em] text-neutral-400 dark:text-neutral-600">
          작품 준비중입니다
        </span>
      </div>
      <div className="mt-2 space-y-0.5 px-0.5 text-center">
        <p className="text-[10px] uppercase tracking-[0.15em] text-neutral-500 dark:text-neutral-400">
          {item.tag}
        </p>
        <h3 className="text-[11px] leading-snug text-neutral-900 dark:text-neutral-200">
          {item.title}
        </h3>
      </div>
    </article>
  );
}
