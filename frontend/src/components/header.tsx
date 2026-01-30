'use client';

import { Menu } from 'lucide-react';
import { Button } from '@/components/ui';
import Image from 'next/image';

interface HeaderProps {
  onSidebarToggle?: () => void;
  showMenuButton?: boolean;
}

export function Header({ onSidebarToggle, showMenuButton = false }: HeaderProps) {
  return (
    <header className="h-16 px-6 flex items-center justify-between border-b border-black/[0.06] bg-white/60 backdrop-blur-sm">
      <div className="flex items-center gap-4">
        {showMenuButton && (
          <Button
            variant="ghost"
            size="sm"
            onClick={onSidebarToggle}
            aria-label="菜单"
            className="mr-1"
          >
            <Menu className="w-5 h-5" />
          </Button>
        )}

        {/* Logo */}
        <div className="relative w-9 h-9 rounded-xl overflow-hidden bg-black/[0.04] shadow-sm">
          <Image
            src="/static/logo.png"
            alt="Logo"
            width={36}
            height={36}
            className="w-full h-full object-cover"
          />
        </div>

        {/* Title */}
        <div>
          <h1 className="text-lg font-bold tracking-tight text-black font-display">
            txt2anything
          </h1>
          <p className="text-[10px] text-black/40 font-medium tracking-wide uppercase -mt-0.5">
            AI Structural Converter
          </p>
        </div>
      </div>

      <div className="flex items-center gap-4">
        <a
          href="https://github.com/OvHaozzZ/txt2anything"
          target="_blank"
          rel="noopener noreferrer"
          className="text-[13px] font-medium text-black/40 hover:text-black transition-colors"
        >
          GitHub
        </a>
      </div>
    </header>
  );
}
