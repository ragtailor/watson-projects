import {
  Building2,
  Calendar,
  Clock,
  Cloud,
  Presentation,
} from "lucide-react";

const overviewLines = [
  "K-Digital Training",
  "디지털 선도기업 아카데미",
  "[IBM x RedHat]",
  "AI Transformation - AX Academy",
];

const programDetails = [
  {
    icon: Cloud,
    label: "교육과정",
    value: "[IBM x RedHat] AI Transformation - AX Academy",
  },
  {
    icon: Calendar,
    label: "개강일정",
    value: "(8기) 7월 예정",
  },
  {
    icon: Building2,
    label: "교육장소",
    value: "하이미디어 추후 공지",
  },
  {
    icon: Clock,
    label: "학습시간",
    value: "매주 월~금 (am09:30 ~ pm18:30까지)",
  },
  {
    icon: Presentation,
    label: "교육방법",
    value: "오프라인 수업",
  },
] as const;

export function HomeEducationOverview() {
  return (
    <section
      id="services"
      className="hidden border-t border-neutral-100 bg-white py-16 dark:border-gray-800 dark:bg-background sm:py-24 lg:block"
    >
      <div className="mx-auto w-full max-w-lg px-4 text-center sm:max-w-xl md:max-w-2xl lg:max-w-4xl">
        <h2 className="text-2xl font-bold tracking-tight text-neutral-900 dark:text-neutral-100 sm:text-3xl">
          모집 개요
        </h2>
        <div className="mt-6 space-y-1 text-sm leading-relaxed text-neutral-600 dark:text-neutral-400 sm:text-base">
          {overviewLines.map((line) => (
            <p key={line}>{line}</p>
          ))}
        </div>

        <ul className="mt-12 divide-y divide-neutral-200 border-t border-neutral-200 text-left dark:divide-gray-800 dark:border-gray-800 sm:mt-14">
          {programDetails.map(({ icon: Icon, label, value }) => (
            <li
              key={label}
              className="flex flex-col items-center gap-2 py-6 text-center sm:flex-row sm:items-start sm:gap-4 sm:text-left"
            >
              <Icon
                className="h-5 w-5 shrink-0 text-neutral-400 dark:text-neutral-500"
                strokeWidth={1.5}
                aria-hidden
              />
              <div className="min-w-0 flex-1 space-y-1">
                <p className="text-sm font-medium text-neutral-900 dark:text-neutral-100">
                  {label}
                </p>
                <p className="text-sm leading-relaxed text-neutral-600 dark:text-neutral-400">
                  {value}
                </p>
              </div>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
