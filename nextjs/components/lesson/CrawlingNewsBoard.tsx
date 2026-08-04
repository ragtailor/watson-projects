import { Newspaper } from "lucide-react";

interface DummyNews {
  id: number;
  category: string;
  title: string;
  summary: string;
  date: string;
}

const dummyNews: DummyNews[] = [
  { id: 1, category: "IT/과학", title: "AI 에이전트 시장 빠르게 성장... 기업 도입 확대", summary: "국내 주요 기업들이 업무 자동화를 위한 AI 에이전트 도입을 늘리고 있다는 소식입니다.", date: "2026.06.12" },
  { id: 2, category: "경제", title: "코스피, 외국인 매수에 강세 마감", summary: "외국인과 기관의 동시 매수세에 힘입어 코스피가 상승 마감했습니다.", date: "2026.06.12" },
  { id: 3, category: "사회", title: "전국 대부분 지역 맑음, 낮 기온 평년보다 높아", summary: "오늘은 전국이 대체로 맑은 가운데 낮 기온은 평년보다 다소 높을 전망입니다.", date: "2026.06.12" },
  { id: 4, category: "스포츠", title: "프로야구, 주말 3연전 매진 행렬", summary: "주말 프로야구 경기가 전 구장 매진을 기록하며 흥행을 이어가고 있습니다.", date: "2026.06.11" },
  { id: 5, category: "정치", title: "국회, 디지털 산업 육성 법안 논의", summary: "디지털 산업 육성을 위한 신규 법안이 국회 상임위에서 논의될 예정입니다.", date: "2026.06.11" },
  { id: 6, category: "세계", title: "글로벌 반도체 수요 회복세 뚜렷", summary: "주요 반도체 제조사들의 실적 발표를 앞두고 수요 회복 기대감이 커지고 있습니다.", date: "2026.06.11" },
  { id: 7, category: "문화", title: "이번 주말 추천 전시·공연 정보", summary: "주말을 알차게 보낼 수 있는 전시회와 공연 소식을 모았습니다.", date: "2026.06.11" },
  { id: 8, category: "생활", title: "여름 휴가철 앞두고 항공권 예약 급증", summary: "여름 휴가 시즌을 앞두고 국내외 항공권 예약이 크게 늘었습니다.", date: "2026.06.10" },
  { id: 9, category: "건강", title: "환절기 면역력 관리법, 전문가 조언", summary: "환절기 건강 관리를 위한 전문가들의 생활 습관 조언을 정리했습니다.", date: "2026.06.10" },
];

export function CrawlingNewsBoard() {
  return (
    <div className="mt-8">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {dummyNews.map((news) => (
          <article
            key={news.id}
            className="flex flex-col rounded-lg border border-neutral-200 bg-white dark:border-gray-700 dark:bg-surface"
          >
            <div className="flex h-32 items-center justify-center rounded-t-lg bg-neutral-100 text-neutral-300 dark:bg-surface-muted dark:text-neutral-600">
              <Newspaper className="h-10 w-10" strokeWidth={1.25} aria-hidden />
            </div>
            <div className="flex flex-1 flex-col gap-2 p-4">
              <span className="text-[10px] uppercase tracking-[0.15em] text-neutral-400 dark:text-neutral-500">
                {news.category} · 네이버 뉴스
              </span>
              <h3 className="line-clamp-2 text-sm font-medium leading-snug text-neutral-900 dark:text-neutral-100">
                {news.title}
              </h3>
              <p className="line-clamp-2 text-xs leading-relaxed text-neutral-500 dark:text-neutral-400">
                {news.summary}
              </p>
              <span className="mt-auto text-xs text-neutral-400 dark:text-neutral-500">{news.date}</span>
            </div>
          </article>
        ))}
      </div>
    </div>
  );
}
