import { type ReactNode } from 'react';
import { cn } from '@/lib/utils';

interface CardProps {
  children: ReactNode;
  className?: string;
  variant?: 'default' | 'bordered';
}

export function Card({ children, className, variant = 'default' }: CardProps) {
  return (
    <div
      className={cn(
        'flex-1 flex flex-col rounded-xl min-w-[320px]',
        variant === 'bordered'
          ? 'border border-neutral-200 bg-white'
          : 'bg-neutral-50',
        className
      )}
    >
      {children}
    </div>
  );
}

interface CardContentProps {
  children: ReactNode;
  className?: string;
}

export function CardContent({ children, className }: CardContentProps) {
  return (
    <div className={cn('flex-1 flex flex-col p-6 gap-4', className)}>
      {children}
    </div>
  );
}

interface CardHeaderProps {
  title: string;
  badge?: string;
}

export function CardHeader({ title, badge }: CardHeaderProps) {
  return (
    <div className="flex items-center justify-between">
      <label className="text-sm font-medium text-neutral-700 flex items-center gap-2">
        <span className="w-1.5 h-1.5 rounded-full bg-neutral-400" />
        {title}
      </label>
      {badge && (
        <span className="text-[10px] font-medium text-neutral-400 bg-neutral-100 px-2 py-1 rounded">
          {badge}
        </span>
      )}
    </div>
  );
}
