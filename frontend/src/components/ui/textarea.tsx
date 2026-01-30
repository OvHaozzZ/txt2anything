import { forwardRef, type TextareaHTMLAttributes } from 'react';
import { cn } from '@/lib/utils';

export interface TextareaProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  error?: string;
}

const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ className, label, error, ...props }, ref) => {
    return (
      <div className="flex-1 flex flex-col space-y-2">
        {label && (
          <label className="text-[13px] font-medium text-black/70 block">
            {label}
          </label>
        )}
        <textarea
          ref={ref}
          className={cn(
            'flex-1 w-full bg-black/[0.02]',
            'border border-black/[0.06] hover:border-black/10 focus:border-black/15',
            'rounded-2xl p-5 text-[14px] leading-relaxed resize-none',
            'text-black placeholder:text-black/30',
            'focus:outline-none focus:bg-white',
            'transition-all duration-200 scrollbar-minimal',
            error && 'bg-red-50 border-red-200',
            className
          )}
          {...props}
        />
        {error && (
          <p className="text-xs text-red-500">{error}</p>
        )}
      </div>
    );
  }
);

Textarea.displayName = 'Textarea';

export { Textarea };
