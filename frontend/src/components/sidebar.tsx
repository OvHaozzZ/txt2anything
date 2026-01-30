'use client';

import { type ReactNode } from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { cn } from '@/lib/utils';

interface SidebarProps {
  isOpen: boolean;
  onToggle: () => void;
  children: ReactNode;
  title?: string;
  className?: string;
}

export function Sidebar({ isOpen, onToggle, children, title = '设置', className }: SidebarProps) {
  return (
    <>
      {/* 侧边栏 */}
      <aside
        className={cn(
          'fixed top-0 left-0 h-full z-40 bg-white',
          'sidebar-transition flex flex-col',
          isOpen ? 'w-64' : 'w-0',
          className
        )}
      >
        {/* 侧边栏内容 */}
        <div
          className={cn(
            'flex-1 flex flex-col overflow-hidden w-64',
            isOpen ? 'opacity-100' : 'opacity-0 pointer-events-none'
          )}
        >
          {/* 标题栏 */}
          <div className="flex items-center justify-between h-14 px-5 border-b border-black/[0.06]">
            <h2 className="text-sm font-semibold text-black">{title}</h2>
            <button
              onClick={onToggle}
              className="w-7 h-7 rounded-full flex items-center justify-center hover:bg-black/[0.04] text-black/40 hover:text-black/70 transition-colors"
              aria-label="收起侧边栏"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
          </div>

          {/* 内容区域 */}
          <div className="flex-1 overflow-y-auto scrollbar-minimal px-5 py-6">
            {children}
          </div>
        </div>
      </aside>

      {/* 右侧分隔线 */}
      <div
        className={cn(
          'fixed top-0 h-full w-px bg-black/[0.06] z-40 transition-all duration-300',
          isOpen ? 'left-64' : 'left-0 opacity-0'
        )}
      />

      {/* 展开按钮 - 侧边栏关闭时显示 */}
      <button
        onClick={onToggle}
        className={cn(
          'fixed left-4 top-4 z-30',
          'w-9 h-9 bg-white rounded-full shadow-sm border border-black/[0.08]',
          'flex items-center justify-center',
          'text-black/50 hover:text-black hover:shadow-md',
          'transition-all duration-200',
          isOpen ? 'opacity-0 pointer-events-none scale-90' : 'opacity-100 scale-100'
        )}
        aria-label="展开侧边栏"
      >
        <ChevronRight className="w-4 h-4" />
      </button>

      {/* 遮罩层 - 移动端 */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/10 z-30 md:hidden backdrop-blur-sm"
          onClick={onToggle}
        />
      )}
    </>
  );
}

interface SidebarSectionProps {
  title: string;
  children: ReactNode;
  className?: string;
}

export function SidebarSection({ title, children, className }: SidebarSectionProps) {
  return (
    <div className={cn('mb-8', className)}>
      <h3 className="text-[11px] font-medium text-black/40 uppercase tracking-wider mb-4">
        {title}
      </h3>
      <div className="space-y-4">
        {children}
      </div>
    </div>
  );
}
