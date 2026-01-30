import { forwardRef, type ButtonHTMLAttributes } from 'react';
import { cn } from '@/lib/utils';

type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'icon';
type ButtonSize = 'sm' | 'md' | 'lg';

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  isLoading?: boolean;
}

const variants: Record<ButtonVariant, string> = {
  primary: 'bg-black hover:bg-black/90 text-white shadow-sm hover:shadow active:scale-[0.98]',
  secondary: 'bg-black/[0.04] text-black hover:bg-black/[0.08] active:bg-black/[0.12]',
  ghost: 'text-black/60 hover:text-black hover:bg-black/[0.04]',
  icon: 'bg-black/[0.04] text-black/60 hover:bg-black/[0.08] hover:text-black',
};

const sizes: Record<ButtonSize, string> = {
  sm: 'text-[13px] px-4 py-2 rounded-lg gap-1.5',
  md: 'text-[13px] px-5 py-2.5 rounded-xl gap-2',
  lg: 'text-[14px] px-6 py-3 rounded-xl gap-2',
};

const iconSizes: Record<ButtonSize, string> = {
  sm: 'p-2 rounded-lg',
  md: 'p-2.5 rounded-xl',
  lg: 'p-3 rounded-xl',
};

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'primary', size = 'md', isLoading, children, disabled, ...props }, ref) => {
    const baseStyles = 'inline-flex items-center justify-center font-medium transition-all duration-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-black/20 focus-visible:ring-offset-2 disabled:opacity-40 disabled:cursor-not-allowed disabled:pointer-events-none';

    return (
      <button
        ref={ref}
        className={cn(
          baseStyles,
          variants[variant],
          variant === 'icon' ? iconSizes[size] : sizes[size],
          className
        )}
        disabled={disabled || isLoading}
        {...props}
      >
        {isLoading ? (
          <span className="w-4 h-4 border-2 border-current/20 border-t-current rounded-full animate-spin" />
        ) : (
          children
        )}
      </button>
    );
  }
);

Button.displayName = 'Button';

export { Button };
