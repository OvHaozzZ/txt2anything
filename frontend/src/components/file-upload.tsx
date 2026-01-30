'use client';

import { useCallback, useState, useRef, type DragEvent, type ChangeEvent } from 'react';
import { Upload, X, Image as ImageIcon, Film } from 'lucide-react';
import { cn, formatFileSize } from '@/lib/utils';

const SUPPORTED_TYPES = {
  image: ['image/jpeg', 'image/png', 'image/bmp', 'image/webp', 'image/tiff'],
  video: ['video/mp4', 'video/avi', 'video/quicktime', 'video/x-matroska', 'video/webm', 'video/x-ms-wmv'],
};

interface FileUploadProps {
  file: File | null;
  onFileChange: (file: File | null) => void;
  className?: string;
}

export function FileUpload({ file, onFileChange, className }: FileUploadProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const isImageFile = (f: File) => f.type.startsWith('image/');

  const isSupported = (f: File) => {
    const allSupported = [...SUPPORTED_TYPES.image, ...SUPPORTED_TYPES.video];
    return allSupported.some((type) => f.type.startsWith(type.split('/')[0]));
  };

  const processFile = useCallback((f: File) => {
    if (!isSupported(f)) {
      alert('不支持的文件格式，请上传图片或视频文件');
      return;
    }
    onFileChange(f);
    setPreviewUrl(URL.createObjectURL(f));
  }, [onFileChange]);

  const handleDragOver = useCallback((e: DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) processFile(droppedFile);
  }, [processFile]);

  const handleInputChange = useCallback((e: ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) processFile(selectedFile);
  }, [processFile]);

  const handleRemove = useCallback(() => {
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    onFileChange(null);
    setPreviewUrl(null);
    if (inputRef.current) inputRef.current.value = '';
  }, [previewUrl, onFileChange]);

  if (file && previewUrl) {
    return (
      <div className={cn('rounded-2xl p-4 bg-black/[0.02] border border-black/[0.06]', className)}>
        <div className="flex items-center gap-4">
          <div className="flex-shrink-0 w-14 h-14 rounded-xl overflow-hidden bg-black/[0.04]">
            {isImageFile(file) ? (
              <img src={previewUrl} alt="Preview" className="w-full h-full object-cover" />
            ) : (
              <video src={previewUrl} className="w-full h-full object-cover" />
            )}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-[14px] font-medium text-black truncate">{file.name}</p>
            <p className="text-[13px] text-black/40 mt-0.5">{formatFileSize(file.size)}</p>
          </div>
          <button
            onClick={handleRemove}
            className="w-8 h-8 rounded-full flex items-center justify-center text-black/30 hover:text-red-500 hover:bg-red-50 transition-all"
            aria-label="移除文件"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className={cn('relative', className)}>
      <input
        ref={inputRef}
        type="file"
        onChange={handleInputChange}
        accept="image/*,video/*"
        className="hidden"
      />
      <button
        type="button"
        onClick={() => inputRef.current?.click()}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={cn(
          'w-full rounded-2xl py-6 px-4 border border-dashed transition-all duration-200',
          isDragging
            ? 'border-black/30 bg-black/[0.04]'
            : 'border-black/[0.12] hover:border-black/25 bg-transparent hover:bg-black/[0.02]'
        )}
      >
        <div className="flex flex-col items-center gap-2">
          <div className="w-10 h-10 rounded-full bg-black/[0.04] flex items-center justify-center">
            <Upload className="w-5 h-5 text-black/40" />
          </div>
          <div className="text-center">
            <span className="text-[14px] font-medium text-black/70">点击或拖拽上传文件</span>
            <div className="flex items-center justify-center gap-4 mt-1.5 text-[12px] text-black/40">
              <span className="flex items-center gap-1">
                <ImageIcon className="w-3.5 h-3.5" /> 图片
              </span>
              <span className="flex items-center gap-1">
                <Film className="w-3.5 h-3.5" /> 视频
              </span>
            </div>
          </div>
        </div>
      </button>
    </div>
  );
}
