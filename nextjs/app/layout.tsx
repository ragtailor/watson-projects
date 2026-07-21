import type { Metadata } from 'next'
import { Geist } from 'next/font/google'
import { Analytics } from '@vercel/analytics/next'
import { ThemeProvider } from 'next-themes'
import { TopBar } from '@/components/layout/TopBar'
import { LeftSidebar } from '@/components/layout/LeftSidebar'
import { RightPanelProvider, RightPanel } from '@/components/layout/RightPanelContext'
import { OAuthRedirectHandler } from '@/components/auth/OAuthRedirectHandler'
import './globals.css'

const _geist = Geist({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'RAG Tailor | AI 서비스 개발 교육',
  description: 'RAG Tailor은 실무 중심 AI 서비스 개발 교육을 제공합니다. RAG, Multi-Agent, FastAPI 기반 엔터프라이즈 AI 역량을 키웁니다.',
  generator: 'RAG Tailor',
  icons: {
    icon: [
      { url: '/icon-light-32x32.png', media: '(prefers-color-scheme: light)' },
      { url: '/icon-dark-32x32.png', media: '(prefers-color-scheme: dark)' },
      { url: '/icon.svg', type: 'image/svg+xml' },
    ],
    apple: '/apple-icon.png',
  },
}

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="ko" suppressHydrationWarning>
      <body className="bg-white font-sans antialiased dark:bg-[#0a0a0a]">
        <ThemeProvider
          attribute="class"
          defaultTheme="light"
          enableSystem
          disableTransitionOnChange
        >
          <OAuthRedirectHandler />
          <RightPanelProvider>
            <TopBar />
            <div className="mt-12 flex h-[calc(100vh-3rem)] overflow-hidden">
              <LeftSidebar />
              <main
                id="main-scroll"
                className="min-w-0 flex-1 overflow-y-auto text-neutral-900 dark:text-neutral-100"
              >
                {children}
              </main>
              <RightPanel />
            </div>
          </RightPanelProvider>
        </ThemeProvider>

        {process.env.NODE_ENV === 'production' && <Analytics />}
      </body>
    </html>
  )
}
