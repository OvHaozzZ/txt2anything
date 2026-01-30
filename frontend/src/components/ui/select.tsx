'use client';

import { useState, useRef, useEffect, type SelectHTMLAttributes } from 'react';
import { ChevronDown, Check } from 'lucide-react';
import { cn } from '@/lib/utils';

export interface SelectOption {
  value: string;
  label: string;
}

export interface SelectProps extends Omit<SelectHTMLAttributes<HTMLSelectElement>, 'children' | 'onChange'> {
  label?: string;
  options: SelectOption[];
  error?: string;
  value?: string;
  onChange?: (e: { target: { value: string } }) => void;
}

const Select = ({ className, label, options, error, value, onChange }: SelectProps) => {
  const [isOpen, setIsOpen] = useState(false);
  const [selectedValue, setSelectedValue] = useState(value || options[0]?.value || '');
  const containerRef = useRef<HTMLDivElement>(null);

  // 同步外部 value
  useEffect(() => {
    if (value !== undefined) {
      setSelectedValue(value);
    }
  }, [value]);

  // 点击外部关闭
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const selectedOption = options.find(opt => opt.value === selectedValue);

  const handleSelect = (optionValue: string) => {
    setSelectedValue(optionValue);
    setIsOpen(false);
    onChange?.({ target: { value: optionValue } });
  };

  return (
    <div className="space-y-2" ref={containerRef}>
      {label && (
        <label className="text-xs font-bold text-black/50 uppercase tracking-wider block">
          {label}
        </label>
      )}
      <div className="relative">
        {/* 触发按钮 */}
        <button
          type="button"
          onClick={() => setIsOpen(!isOpen)}
          className={cn(
            'w-full pl-4 pr-10 py-3 text-[13px] font-medium text-left',
            'bg-white border border-black/10 rounded-2xl text-black shadow-sm',
            'focus:border-black/20 focus:ring-2 focus:ring-black/5 outline-none',
            'cursor-pointer hover:border-black/20 hover:shadow-md transition-all duration-200',
            error && 'bg-red-50 border-red-200',
            className
          )}
        >
          {selectedOption?.label || '请选择'}
        </button>

        {/* 箭头图标 */}
        <div className="absolute inset-y-0 right-0 flex items-center pr-4 pointer-events-none text-black/40">
          <ChevronDown className={cn(
            'w-4 h-4 transition-transform duration-200',
            isOpen && 'rotate-180'
          )} />
        </div>

        {/* 下拉选项列表 */}
        {isOpen && (
          <div className={cn(
            'absolute z-50 w-full mt-2 py-1',
            'bg-white border border-black/10 rounded-2xl shadow-xl',
            'animate-in fade-in-0 zoom-in-95 duration-200',
            'max-h-60 overflow-auto'
          )}>
            {options.map((option) => (
              <button
                key={option.value}
                type="button"
                onClick={() => handleSelect(option.value)}
                className={cn(
                  'w-full px-4 py-2.5 text-[13px] font-medium text-left',
                  'flex items-center justify-between',
                  'hover:bg-black/[0.04] transition-colors duration-150',
                  'first:rounded-t-xl last:rounded-b-xl',
                  option.value === selectedValue
                    ? 'text-blue-600 bg-blue-50/50'
                    : 'text-black/80'
                )}
              >
                <span>{option.label}</span>
                {option.value === selectedValue && (
                  <Check className="w-4 h-4 text-blue-600" />
                )}
              </button>
            ))}
          </div>
        )}
      </div>
      {error && (
        <p className="text-xs text-red-500">{error}</p>
      )}
    </div>
  );
};

Select.displayName = 'Select';

export { Select };
