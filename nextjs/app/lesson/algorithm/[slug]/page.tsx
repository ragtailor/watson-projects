import { notFound } from "next/navigation";
import { PageNav } from "@/components/layout/PageNav";

const ALGORITHMS: Record<string, {
  label: string;
  description: string;
  complexity: { time: string; space: string };
  points: string[];
  prev?: { label: string; href: string };
  next?: { label: string; href: string };
}> = {
  greedy: {
    label: "욕심쟁이 (Greedy)",
    description: "현재 상태에서 가장 좋아 보이는 선택을 반복하는 알고리즘. 전체 최적해를 보장하지 않지만 특정 조건에서 최적해를 구할 수 있다.",
    complexity: { time: "O(n log n) ~ O(n)", space: "O(1)" },
    points: [
      "탐욕적 선택 속성 (Greedy Choice Property) 확인이 선행 조건",
      "최적 부분 구조 (Optimal Substructure) 가 성립해야 함",
      "대표 문제: 거스름돈, 활동 선택, 크루스칼 MST",
      "DP 보다 구현이 단순하고 빠르나 적용 범위가 좁음",
    ],
    next: { label: "DP", href: "/lesson/algorithm/dp" },
  },
  dp: {
    label: "DP (Dynamic Programming)",
    description: "중복되는 부분 문제를 메모이제이션 또는 타뷸레이션으로 저장해 재계산을 피하는 기법. 최적 부분 구조와 중복 부분 문제 속성이 필요하다.",
    complexity: { time: "O(n²) ~ O(n·k)", space: "O(n) ~ O(n²)" },
    points: [
      "Top-down(재귀 + 메모): 자연스러운 구현, 스택 오버플로 주의",
      "Bottom-up(반복): 공간 최적화 유리, LCS·배낭·행렬 연쇄 곱셈 등",
      "점화식 도출이 핵심 — 상태 정의 → 전이 관계 → 기저 조건",
      "대표 문제: 피보나치, 최장 공통 부분 수열(LCS), 0/1 배낭",
    ],
    prev: { label: "욕심쟁이", href: "/lesson/algorithm/greedy" },
    next: { label: "이분 탐색", href: "/lesson/algorithm/binary-search" },
  },
  "binary-search": {
    label: "이분 탐색 (Binary Search)",
    description: "정렬된 배열에서 탐색 범위를 절반씩 줄여 나가는 알고리즘. O(log n) 시간에 원하는 값을 찾는다.",
    complexity: { time: "O(log n)", space: "O(1)" },
    points: [
      "입력이 반드시 정렬되어 있어야 함",
      "left, right, mid 포인터로 범위를 좁혀 나감",
      "경계 조건(left ≤ right vs left < right) 이 버그의 주원인",
      "대표 문제: 특정 값 탐색, 파라메트릭 서치, 정렬 위치 탐색",
    ],
    prev: { label: "DP", href: "/lesson/algorithm/dp" },
    next: { label: "DFS", href: "/lesson/algorithm/dfs" },
  },
  dfs: {
    label: "DFS (깊이 우선 탐색)",
    description: "그래프나 트리에서 한 방향으로 최대한 깊이 탐색한 뒤 되돌아오는 방식. 재귀 또는 명시적 스택으로 구현한다.",
    complexity: { time: "O(V + E)", space: "O(V)" },
    points: [
      "방문 배열(visited)로 무한 루프를 방지",
      "사이클 감지, 위상 정렬, 강한 연결 요소 탐색에 활용",
      "재귀 깊이가 깊으면 스택 오버플로 발생 — 반복 DFS 고려",
      "대표 문제: 미로 탐색, 연결 요소 개수, 백트래킹",
    ],
    prev: { label: "이분 탐색", href: "/lesson/algorithm/binary-search" },
    next: { label: "BFS", href: "/lesson/algorithm/bfs" },
  },
  bfs: {
    label: "BFS (너비 우선 탐색)",
    description: "그래프나 트리에서 시작 노드와 가까운 노드부터 단계적으로 탐색하는 방식. 큐(Queue)로 구현한다.",
    complexity: { time: "O(V + E)", space: "O(V)" },
    points: [
      "최단 거리(가중치 없는 그래프) 보장 — DFS 는 보장 안 함",
      "큐에 넣을 때 방문 표시하는 것이 올바른 구현",
      "레벨 단위 처리(BFS 트리의 깊이) 쉽게 구분 가능",
      "대표 문제: 최단 경로, 이분 그래프 판별, 다중 시작점 BFS",
    ],
    prev: { label: "DFS", href: "/lesson/algorithm/dfs" },
    next: { label: "정렬", href: "/lesson/algorithm/sorting" },
  },
  sorting: {
    label: "정렬 (Sorting)",
    description: "데이터를 특정 기준으로 순서를 매기는 알고리즘군. 비교 기반 정렬은 O(n log n) 이 하한이다.",
    complexity: { time: "O(n log n)", space: "O(1) ~ O(n)" },
    points: [
      "퀵 정렬: 평균 O(n log n), 최악 O(n²) — 피벗 선택이 핵심",
      "병합 정렬: 항상 O(n log n), 안정 정렬, O(n) 추가 공간 필요",
      "힙 정렬: O(n log n), 제자리 정렬, 불안정 정렬",
      "계수 정렬: O(n + k), 값 범위가 작을 때 선형 정렬 가능",
    ],
    prev: { label: "BFS", href: "/lesson/algorithm/bfs" },
    next: { label: "재귀", href: "/lesson/algorithm/recursion" },
  },
  recursion: {
    label: "재귀 (Recursion)",
    description: "함수가 자기 자신을 호출해 문제를 더 작은 부분으로 쪼개 해결하는 기법. 기저 조건(base case) 이 반드시 필요하다.",
    complexity: { time: "문제에 따라 다름", space: "O(호출 깊이)" },
    points: [
      "기저 조건 누락 시 무한 재귀 → 스택 오버플로",
      "재귀 트리를 그려 시간·공간 복잡도를 분석",
      "꼬리 재귀 최적화(TCO) — JS/Python은 미지원",
      "대표 문제: 팩토리얼, 피보나치, 하노이 탑, 순열/조합",
    ],
    prev: { label: "정렬", href: "/lesson/algorithm/sorting" },
    next: { label: "투 포인터", href: "/lesson/algorithm/two-pointers" },
  },
  "two-pointers": {
    label: "투 포인터 (Two Pointers)",
    description: "두 개의 포인터를 이용해 배열이나 리스트를 순회하면서 조건을 만족하는 쌍을 찾는 기법. O(n²) 문제를 O(n) 으로 줄인다.",
    complexity: { time: "O(n)", space: "O(1)" },
    points: [
      "정렬된 배열에서 합이 특정 값인 두 수 찾기에 효과적",
      "슬라이딩 윈도우와 함께 연속 부분 배열 문제에 적용",
      "왼쪽·오른쪽 포인터가 교차하면 탐색 종료",
      "대표 문제: 두 수의 합, 세 수의 합, 가장 긴 부분 문자열",
    ],
    prev: { label: "재귀", href: "/lesson/algorithm/recursion" },
    next: { label: "스택 / 큐", href: "/lesson/algorithm/stack-queue" },
  },
  "stack-queue": {
    label: "스택 / 큐 (Stack / Queue)",
    description: "스택은 LIFO, 큐는 FIFO 자료구조. 많은 알고리즘의 근간이 되는 기본 자료구조다.",
    complexity: { time: "push/pop/enqueue/dequeue: O(1)", space: "O(n)" },
    points: [
      "스택: 함수 호출 스택, DFS, 괄호 짝 맞추기, 단조 스택",
      "큐: BFS, 프린터 대기열, 슬라이딩 윈도우 최솟값",
      "덱(Deque): 양쪽에서 삽입·삭제 — 슬라이딩 윈도우 최적화",
      "우선순위 큐(힙): O(log n) 삽입·삭제, 다익스트라·프림에 활용",
    ],
    prev: { label: "투 포인터", href: "/lesson/algorithm/two-pointers" },
    next: { label: "해시", href: "/lesson/algorithm/hash" },
  },
  hash: {
    label: "해시 (Hash)",
    description: "키를 해시 함수로 변환해 O(1) 평균 시간에 검색·삽입·삭제를 수행하는 자료구조. 충돌 처리 전략이 성능의 핵심이다.",
    complexity: { time: "평균 O(1), 최악 O(n)", space: "O(n)" },
    points: [
      "충돌 해결: 체이닝(연결 리스트) vs 개방 주소법(선형 탐사 등)",
      "해시 함수의 균등 분포가 성능을 결정",
      "JS Map/Set, Python dict/set 은 모두 해시 기반",
      "대표 문제: 두 수의 합(O(n)), 중복 탐지, 빈도 카운팅",
    ],
    prev: { label: "스택 / 큐", href: "/lesson/algorithm/stack-queue" },
  },
};

type Props = { params: Promise<{ slug: string }> };

export async function generateStaticParams() {
  return Object.keys(ALGORITHMS).map((slug) => ({ slug }));
}

export default async function AlgorithmPage({ params }: Props) {
  const { slug } = await params;
  const algo = ALGORITHMS[slug];
  if (!algo) notFound();

  return (
    <>
      {/* 헤더 */}
      <div className="mb-10">
        <p className="text-[10px] uppercase tracking-[0.3em] text-neutral-400 dark:text-neutral-500">
          알고리즘
        </p>
        <h1 className="mt-2 text-2xl font-semibold text-neutral-900 dark:text-neutral-100">
          {algo.label}
        </h1>
        <p className="mt-3 text-sm leading-relaxed text-neutral-600 dark:text-neutral-400">
          {algo.description}
        </p>
      </div>

      {/* 복잡도 */}
      <div className="mb-10 flex gap-6 rounded border border-neutral-100 bg-neutral-50 px-5 py-4 text-sm dark:border-gray-800 dark:bg-surface">
        <div>
          <p className="mb-0.5 text-[10px] uppercase tracking-[0.15em] text-neutral-400 dark:text-neutral-500">시간 복잡도</p>
          <p className="font-mono font-medium text-neutral-900 dark:text-neutral-100">{algo.complexity.time}</p>
        </div>
        <div className="border-l border-neutral-200 pl-6 dark:border-gray-700">
          <p className="mb-0.5 text-[10px] uppercase tracking-[0.15em] text-neutral-400 dark:text-neutral-500">공간 복잡도</p>
          <p className="font-mono font-medium text-neutral-900 dark:text-neutral-100">{algo.complexity.space}</p>
        </div>
      </div>

      {/* 핵심 포인트 */}
      <div className="mb-10">
        <h2 className="mb-4 text-base font-semibold text-neutral-900 dark:text-neutral-100">핵심 포인트</h2>
        <ul className="space-y-3">
          {algo.points.map((point, i) => (
            <li key={i} className="flex items-start gap-3 text-sm text-neutral-700 dark:text-neutral-300">
              <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-neutral-400 dark:bg-neutral-500" />
              {point}
            </li>
          ))}
        </ul>
      </div>

      {/* 준비 중 안내 */}
      <div className="rounded border border-neutral-100 bg-neutral-50 px-5 py-6 text-center text-sm text-neutral-500 dark:border-gray-800 dark:bg-surface dark:text-neutral-500">
        실습 코드 및 문제풀이 콘텐츠 준비 중입니다.
      </div>

      <PageNav prev={algo.prev} next={algo.next} />
    </>
  );
}
