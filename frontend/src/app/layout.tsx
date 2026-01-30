import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
});

export const metadata: Metadata = {
  title: 'txt2anything - AI Structural Converter',
  description: 'Convert text, images, and videos into structured mind maps and documents using AI',
  keywords: ['mind map', 'xmind', 'markdown', 'ppt', 'ai', 'converter'],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="zh-CN" className={inter.variable}>
      <body className="min-h-screen font-sans antialiased selection:bg-neutral-200 selection:text-neutral-900">
        {children}
      </body>
    </html>
  );
}
