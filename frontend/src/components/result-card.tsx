'use client';

import { FileText, Check, Download, RefreshCw } from 'lucide-react';
import { Button } from '@/components/ui';

type ResultState = 'empty' | 'loading' | 'success';

interface ResultCardProps {
  state: ResultState;
  statusMessage?: string;
  downloadUrl?: string;
  formatDescription?: string;
  formatExtension?: string;
  onReset: () => void;
}

export function ResultCard({
  state,
  statusMessage = '',
  downloadUrl = '',
  formatDescription = '文件',
  formatExtension = '',
  onReset,
}: ResultCardProps) {
  return (
    <div className="h-full flex flex-col items-center justify-center p-8 bg-black/[0.02] rounded-2xl border border-black/[0.06]">
      {state === 'empty' && <EmptyState />}
      {state === 'loading' && <LoadingState message={statusMessage} />}
      {state === 'success' && downloadUrl && (
        <SuccessState
          downloadUrl={downloadUrl}
          formatDescription={formatDescription}
          formatExtension={formatExtension}
          onReset={onReset}
        />
      )}
    </div>
  );
}

function EmptyState() {
  return (
    <div className="text-center space-y-4">
      <div className="w-16 h-16 bg-black/[0.04] rounded-2xl flex items-center justify-center mx-auto">
        <FileText className="w-7 h-7 text-black/25" />
      </div>
      <div>
        <h3 className="text-lg font-bold text-black tracking-tight">准备就绪</h3>
        <p className="text-sm text-black/40 mt-1">
          输入内容后生成结构化文档
        </p>
      </div>
    </div>
  );
}

function LoadingState({ message }: { message: string }) {
  return (
    <div className="text-center space-y-4">
      <div className="w-16 h-16 flex items-center justify-center mx-auto">
        <div className="w-10 h-10 border-2 border-black/10 border-t-black/60 rounded-full animate-spin" />
      </div>
      <div>
        <h3 className="text-lg font-bold text-black tracking-tight">{message}</h3>
        <p className="text-sm text-black/40 mt-1">请稍候...</p>
      </div>
    </div>
  );
}

interface SuccessStateProps {
  downloadUrl: string;
  formatDescription: string;
  formatExtension: string;
  onReset: () => void;
}

function SuccessState({ downloadUrl, formatDescription, formatExtension, onReset }: SuccessStateProps) {
  return (
    <div className="text-center space-y-6 w-full max-w-xs">
      <div className="w-16 h-16 bg-black/[0.04] rounded-2xl flex items-center justify-center mx-auto">
        <Check className="w-7 h-7 text-black/70" />
      </div>

      <div>
        <h3 className="text-xl font-bold text-black tracking-tight">生成成功</h3>
        <p className="text-sm text-black/50 mt-1">
          {formatDescription} 已准备好下载
        </p>
      </div>

      <div className="space-y-3">
        <a
          href={downloadUrl}
          className="flex items-center justify-center gap-2 w-full bg-black hover:bg-black/90 text-white font-bold text-[15px] py-3.5 px-5 rounded-xl transition-all shadow-sm hover:shadow active:scale-[0.98]"
        >
          <Download className="w-4 h-4" />
          下载文件 ({formatExtension})
        </a>

        <button
          onClick={onReset}
          className="text-sm font-medium text-black/40 hover:text-black transition-colors flex items-center justify-center gap-2 w-full py-2"
        >
          <RefreshCw className="w-4 h-4" />
          重新生成
        </button>
      </div>
    </div>
  );
}
