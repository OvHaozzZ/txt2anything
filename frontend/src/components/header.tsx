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
    <header className="h-14 px-6 flex items-center justify-between border-b border-black/[0.06] bg-white">
      <div className="flex items-center gap-3">
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
        <div className="relative w-8 h-8 rounded-lg overflow-hidden bg-black/[0.04]">
          <Image
            src="/static/logo.png"
            alt="Logo"
            width={32}
            height={32}
            className="w-full h-full object-cover"
          />
        </div>

        {/* Title */}
        <h1 className="text-[15px] font-semibold text-black">
          txt2anything
        </h1>
      </div>

      <div className="flex items-center gap-3">
        <a
          href="https://github.com/OvHaozzZ/txt2anything"
          target="_blank"
          rel="noopener noreferrer"
          className="text-[13px] text-black/50 hover:text-black transition-colors"
        >
          GitHub
        </a>
      </div>
    </header>
  );
}
