"use client";

import {
  createContext,
  useContext,
  useState,
  useEffect,
  type ReactNode,
} from "react";

type Ctx = {
  content: ReactNode;
  setContent: (node: ReactNode) => void;
};

const RightPanelContext = createContext<Ctx>({
  content: null,
  setContent: () => {},
});

export function RightPanelProvider({ children }: { children: ReactNode }) {
  const [content, setContent] = useState<ReactNode>(null);
  return (
    <RightPanelContext.Provider value={{ content, setContent }}>
      {children}
    </RightPanelContext.Provider>
  );
}

export function useRightPanel() {
  return useContext(RightPanelContext);
}

/** 각 페이지에서 우측 패널 내용을 주입할 때 사용 */
export function SetRightPanel({ children }: { children: ReactNode }) {
  const { setContent } = useRightPanel();
  useEffect(() => {
    setContent(children);
    return () => setContent(null);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
  return null;
}

/** layout.tsx 에서 렌더링하는 우측 패널 */
export function RightPanel() {
  const { content } = useRightPanel();
  if (!content) return null;
  return (
    <aside className="hidden h-full w-[200px] shrink-0 overflow-y-auto border-l border-neutral-100 bg-neutral-50 p-4 dark:border-gray-800 dark:bg-surface lg:block">
      {content}
    </aside>
  );
}
