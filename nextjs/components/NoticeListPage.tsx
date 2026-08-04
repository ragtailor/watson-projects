"use client";

import { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import { PenSquare, Search, User, Calendar, Trash2, Inbox } from "lucide-react";

interface Notice {
  id: string;
  title: string;
  content: string;
  author: string;
  createdAt: string;
  isPinned: boolean;
  category: string;
}

const initialNotices: Notice[] = [
  { id: "1", title: "2024년 상반기 워크샵 안내", content: "안녕하세요, 팀원 여러분. 2024년 상반기 워크샵이 다음 주 금요일에 진행될 예정입니다. 장소는 강남 컨퍼런스 센터이며, 오전 10시부터 시작합니다. 모든 팀원의 참석을 부탁드립니다.", author: "김대표", createdAt: "2024-01-15T09:00:00Z", isPinned: true, category: "공지" },
  { id: "2", title: "신규 프로젝트 킥오프 미팅", content: "새로운 프로젝트가 시작됩니다. 이번 프로젝트는 고객사의 요청에 따라 3개월 내 완료해야 합니다. 관련 부서별 담당자는 목요일 오후 2시 회의실 A로 모여주세요.", author: "박팀장", createdAt: "2024-01-14T14:30:00Z", isPinned: false, category: "업무" },
  { id: "3", title: "사내 동호회 모집 안내", content: "2024년 사내 동호회를 새롭게 모집합니다. 관심 있는 분야의 동호회에 가입하시거나, 새로운 동호회를 개설하실 수 있습니다.", author: "이인사", createdAt: "2024-01-13T11:00:00Z", isPinned: false, category: "기타" },
  { id: "4", title: "보안 교육 필수 이수 안내", content: "전 직원 대상 연간 보안 교육이 진행됩니다. 온라인 교육으로 진행되며, 이번 주 금요일까지 반드시 이수해주시기 바랍니다.", author: "최보안", createdAt: "2024-01-12T16:00:00Z", isPinned: true, category: "공지" },
  { id: "5", title: "연말 정산 서류 제출 안내", content: "2023년 연말 정산 관련 서류를 제출해주시기 바랍니다. 제출 기한은 1월 20일까지이며, 인사팀 담당자에게 직접 제출하시거나 이메일로 보내주시면 됩니다.", author: "정회계", createdAt: "2024-01-10T10:00:00Z", isPinned: false, category: "업무" },
];

const categories = ["전체", "공지", "업무", "기타"];

const getCategoryClassName = (category: string): string => {
  switch (category) {
    case "공지":
      return "bg-blue-100 text-blue-700 hover:bg-blue-100 dark:bg-blue-900/40 dark:text-blue-400 dark:hover:bg-blue-900/40";
    case "업무":
      return "bg-green-100 text-green-700 hover:bg-green-100 dark:bg-green-900/40 dark:text-green-400 dark:hover:bg-green-900/40";
    default:
      return "bg-gray-100 text-gray-700 hover:bg-gray-100 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-gray-800";
  }
};

const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}.${month}.${day}`;
};

const truncateContent = (content: string, maxLength = 80): string => {
  if (content.length <= maxLength) return content;
  return content.slice(0, maxLength) + "...";
};

interface NoticeListPageProps {
  notices?: Notice[];
  onDelete?: (id: string) => void;
  onNavigate?: (page: string, id?: string) => void;
}

export default function NoticeListPage({
  notices: externalNotices,
  onDelete: externalOnDelete,
  onNavigate = () => {},
}: NoticeListPageProps) {
  const [internalNotices, setInternalNotices] = useState<Notice[]>(initialNotices);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("전체");
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [newNotice, setNewNotice] = useState({ title: "", content: "", category: "공지", isPinned: false });

  const notices = externalNotices ?? internalNotices;
  const onDelete = externalOnDelete ?? ((id: string) => {
    setInternalNotices((prev) => prev.filter((n) => n.id !== id));
  });

  const handleSubmitNotice = () => {
    if (!newNotice.title.trim() || !newNotice.content.trim()) return;
    const notice: Notice = {
      id: Date.now().toString(),
      title: newNotice.title,
      content: newNotice.content,
      author: "작성자",
      createdAt: new Date().toISOString(),
      isPinned: newNotice.isPinned,
      category: newNotice.category,
    };
    setInternalNotices((prev) => [notice, ...prev]);
    setNewNotice({ title: "", content: "", category: "공지", isPinned: false });
    setIsDialogOpen(false);
  };

  const filteredNotices = notices
    .filter((notice) => {
      if (selectedCategory !== "전체" && notice.category !== selectedCategory) return false;
      if (searchQuery) {
        const q = searchQuery.toLowerCase();
        return notice.title.toLowerCase().includes(q) || notice.author.toLowerCase().includes(q);
      }
      return true;
    })
    .sort((a, b) => {
      if (a.isPinned && !b.isPinned) return -1;
      if (!a.isPinned && b.isPinned) return 1;
      return new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime();
    });

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-background">
      <div className="mx-auto max-w-4xl px-4 py-8">

        {/* 헤더 */}
        <header className="mb-8 flex items-center justify-between">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-neutral-100">
            공지사항 게시판
          </h1>
          <Button onClick={() => setIsDialogOpen(true)}>
            <PenSquare className="mr-2 h-4 w-4" />
            새 공지 작성
          </Button>
        </header>

        {/* 검색 + 필터 */}
        <div className="mb-6 space-y-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400 dark:text-neutral-500" />
            <Input
              placeholder="제목 또는 작성자 검색..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10 dark:border-gray-700 dark:bg-surface dark:text-neutral-100 dark:placeholder:text-neutral-600"
            />
          </div>
          <div className="flex flex-wrap gap-2">
            {categories.map((category) => (
              <Button
                key={category}
                variant={selectedCategory === category ? "default" : "outline"}
                size="sm"
                onClick={() => setSelectedCategory(category)}
                className={
                  selectedCategory === category
                    ? ""
                    : "text-gray-600 hover:text-gray-900 dark:border-gray-700 dark:text-neutral-400 dark:hover:text-neutral-100"
                }
              >
                {category}
              </Button>
            ))}
          </div>
        </div>

        {/* 공지 카드 목록 */}
        {filteredNotices.length > 0 ? (
          <div className="space-y-4">
            {filteredNotices.map((notice) => (
              <Card
                key={notice.id}
                className={`transition-shadow duration-200 hover:shadow-lg ${
                  notice.isPinned
                    ? "border-amber-200 bg-amber-50 dark:border-amber-800/50 dark:bg-amber-900/10"
                    : "border-gray-100 bg-white dark:border-gray-800 dark:bg-surface"
                }`}
              >
                <CardContent className="p-5">
                  {/* 배지 */}
                  <div className="mb-3 flex flex-wrap items-center gap-2">
                    {notice.isPinned && (
                      <Badge
                        variant="secondary"
                        className="bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-400"
                      >
                        📌 고정
                      </Badge>
                    )}
                    <Badge
                      variant="secondary"
                      className={getCategoryClassName(notice.category)}
                    >
                      {notice.category}
                    </Badge>
                  </div>

                  {/* 제목 */}
                  <h2
                    className="mb-2 cursor-pointer text-lg font-semibold text-gray-900 hover:text-blue-600 dark:text-neutral-100 dark:hover:text-blue-400"
                    onClick={() => onNavigate("detail", notice.id)}
                  >
                    {notice.title}
                  </h2>

                  {/* 본문 미리보기 */}
                  <p className="mb-4 text-sm leading-relaxed text-gray-600 dark:text-neutral-400">
                    {truncateContent(notice.content)}
                  </p>

                  {/* 하단 메타 + 삭제 */}
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4 text-sm text-gray-500 dark:text-neutral-500">
                      <span className="flex items-center gap-1">
                        <User className="h-4 w-4" />
                        {notice.author}
                      </span>
                      <span className="flex items-center gap-1">
                        <Calendar className="h-4 w-4" />
                        {formatDate(notice.createdAt)}
                      </span>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => onDelete(notice.id)}
                      className="text-red-400 hover:bg-red-50 hover:text-red-600 dark:hover:bg-red-950/30 dark:hover:text-red-400"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center py-16 text-gray-500 dark:text-neutral-500">
            <Inbox className="mb-4 h-12 w-12" />
            <p className="text-lg">검색 결과가 없습니다</p>
          </div>
        )}
      </div>

      {/* 새 공지 작성 다이얼로그 */}
      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent className="max-h-[85vh] w-[66vw] max-w-4xl overflow-y-auto dark:border-gray-700 dark:bg-surface">
          <DialogHeader>
            <DialogTitle className="text-xl font-bold dark:text-neutral-100">새 공지 작성</DialogTitle>
          </DialogHeader>

          <div className="space-y-6 py-4">
            <div className="space-y-2">
              <Label htmlFor="title" className="text-sm font-medium dark:text-neutral-300">제목</Label>
              <Input
                id="title"
                placeholder="공지 제목을 입력하세요"
                value={newNotice.title}
                onChange={(e) => setNewNotice((p) => ({ ...p, title: e.target.value }))}
                className="w-full dark:border-gray-700 dark:bg-surface-muted dark:text-neutral-100 dark:placeholder:text-neutral-600"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="category" className="text-sm font-medium dark:text-neutral-300">카테고리</Label>
              <Select
                value={newNotice.category}
                onValueChange={(v) => setNewNotice((p) => ({ ...p, category: v }))}
              >
                <SelectTrigger className="w-full max-w-xs dark:border-gray-700 dark:bg-surface-muted dark:text-neutral-100">
                  <SelectValue placeholder="카테고리 선택" />
                </SelectTrigger>
                <SelectContent className="dark:border-gray-700 dark:bg-surface-muted">
                  <SelectItem value="공지">공지</SelectItem>
                  <SelectItem value="업무">업무</SelectItem>
                  <SelectItem value="기타">기타</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="content" className="text-sm font-medium dark:text-neutral-300">내용</Label>
              <Textarea
                id="content"
                placeholder="공지 내용을 입력하세요"
                value={newNotice.content}
                onChange={(e) => setNewNotice((p) => ({ ...p, content: e.target.value }))}
                className="min-h-[200px] w-full resize-none dark:border-gray-700 dark:bg-surface-muted dark:text-neutral-100 dark:placeholder:text-neutral-600"
              />
            </div>

            <div className="flex items-center gap-2">
              <Checkbox
                id="isPinned"
                checked={newNotice.isPinned}
                onCheckedChange={(checked) => setNewNotice((p) => ({ ...p, isPinned: checked === true }))}
              />
              <Label htmlFor="isPinned" className="cursor-pointer text-sm font-medium dark:text-neutral-300">
                상단 고정
              </Label>
            </div>
          </div>

          <DialogFooter className="gap-2">
            <Button variant="outline" onClick={() => setIsDialogOpen(false)} className="dark:border-gray-700 dark:text-neutral-300 dark:hover:bg-gray-800">
              취소
            </Button>
            <Button
              onClick={handleSubmitNotice}
              disabled={!newNotice.title.trim() || !newNotice.content.trim()}
            >
              작성 완료
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
