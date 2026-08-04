import { PortfolioItem } from "./PortfolioItem";
import { portfolioItems } from "./portfolio-data";

export function PortfolioGrid() {
  const featured =
    portfolioItems.find((item) => item.featured) ?? portfolioItems[0];
  const rest = portfolioItems.filter((item) => item.id !== featured.id);
  const topRow = rest.slice(0, 4);
  const bottomRight = rest.slice(4, 8);

  return (
    <section id="portfolio" className="hidden bg-white py-16 dark:bg-background sm:py-20 lg:block">
      <div className="mx-auto w-full max-w-5xl px-3 sm:px-4">
        <div className="mb-8 text-center">
          <p className="text-[10px] uppercase tracking-[0.3em] text-neutral-400 dark:text-neutral-500">
            Curriculum
          </p>
          <h2 className="mt-2 text-sm font-medium uppercase tracking-[0.12em] text-neutral-900 dark:text-neutral-100">
            교육 과정
          </h2>
        </div>

        <div className="grid grid-cols-2 gap-1 sm:grid-cols-4 sm:gap-1.5">
          {topRow.map((item) => (
            <PortfolioItem key={item.id} item={item} />
          ))}

          <PortfolioItem
            item={featured}
            featured
            className="col-span-2 row-span-2"
          />

          {bottomRight.map((item) => (
            <PortfolioItem key={item.id} item={item} />
          ))}
        </div>
      </div>
    </section>
  );
}
