import { forwardRef, type InputHTMLAttributes } from 'react';
import { cn } from '@/lib/utils';

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ className, label, error, type = 'text', ...props }, ref) => {
    return (
      <div className="space-y-2">
        {label && (
          <label className="text-[13px] font-medium text-black/70 block">
            {label}
          </label>
        )}
        <input
          type={type}
          ref={ref}
          className={cn(
            'w-full text-[13px] px-3.5 py-2.5 rounded-xl',
            'bg-black/[0.03] border border-transparent text-black',
            'focus:bg-white focus:border-black/10 focus:ring-0 outline-none',
            'hover:bg-black/[0.05]',
            'transition-all duration-200 placeholder:text-black/30',
            error && 'bg-red-50 border-red-200 focus:border-red-300',
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

Input.displayName = 'Input';

export { Input };
