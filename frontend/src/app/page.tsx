'use client';

import { useState, useEffect, useCallback, type ChangeEvent } from 'react';
import { Sparkles } from 'lucide-react';
import { Header, FileUpload, ResultCard, Sidebar, SidebarSection, SidebarSettings } from '@/components';
import { Button, Textarea, Select, type SelectOption } from '@/components/ui';
import { api } from '@/lib/api';
import type { Format } from '@/lib/types';

const LAYOUT_OPTIONS: SelectOption[] = [
  { value: 'right', label: '向右逻辑' },
  { value: 'map', label: '中心发散' },
  { value: 'tree', label: '树状图' },
  { value: 'org', label: '组织架构' },
];

const STORAGE_KEYS = {
  apiKey: 'ai_xmind_key',
  baseUrl: 'ai_xmind_url',
  sidebarOpen: 'ai_xmind_sidebar',
} as const;

export default function HomePage() {
  const [rawText, setRawText] = useState('');
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [outputFormat, setOutputFormat] = useState('xmind');
  const [layout, setLayout] = useState('right');
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [settings, setSettings] = useState({
    apiKey: '',
    baseUrl: '',
    model: 'gemini-3-flash-preview',
  });
  const [formats, setFormats] = useState<Format[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [statusMessage, setStatusMessage] = useState('');
  const [downloadUrl, setDownloadUrl] = useState('');

  useEffect(() => {
    api.getFormats().then(setFormats);
    const savedApiKey = localStorage.getItem(STORAGE_KEYS.apiKey) || '';
    const savedBaseUrl = localStorage.getItem(STORAGE_KEYS.baseUrl) || '';
    const savedSidebar = localStorage.getItem(STORAGE_KEYS.sidebarOpen);
    setSettings((prev) => ({ ...prev, apiKey: savedApiKey, baseUrl: savedBaseUrl }));
    if (savedSidebar !== null) {
      setSidebarOpen(savedSidebar === 'true');
    }
  }, []);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEYS.apiKey, settings.apiKey);
    localStorage.setItem(STORAGE_KEYS.baseUrl, settings.baseUrl);
  }, [settings.apiKey, settings.baseUrl]);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEYS.sidebarOpen, String(sidebarOpen));
  }, [sidebarOpen]);

  const formatOptions: SelectOption[] = formats.map((f) => ({
    value: f.name,
    label: f.extension,
  }));

  const currentFormat = formats.find((f) => f.name === outputFormat);
  const canGenerate = rawText.trim() || uploadedFile;

  const handleGenerate = useCallback(async () => {
    if (!canGenerate) return;
    setIsLoading(true);
    setDownloadUrl('');

    try {
      let response;
      if (uploadedFile) {
        setStatusMessage(uploadedFile.type.startsWith('video') ? '正在提取视频内容...' : '正在识别图片内容...');
        response = await api.generateFromFile({
          file: uploadedFile,
          format: outputFormat,
          layout,
          api_key: settings.apiKey || undefined,
          base_url: settings.baseUrl || undefined,
          model: settings.model,
          additional_prompt: rawText.trim() || undefined,
        });
      } else {
        setStatusMessage(settings.apiKey ? 'AI 正在提取核心逻辑...' : '正在构建数据结构...');
        response = await api.generate({
          text: rawText,
          api_key: settings.apiKey || undefined,
          base_url: settings.baseUrl || undefined,
          layout,
          format: outputFormat,
          model: settings.model,
        });
      }
      setDownloadUrl(response.download_url);
    } catch (error) {
      alert('错误: ' + (error instanceof Error ? error.message : '未知错误'));
    } finally {
      setIsLoading(false);
    }
  }, [canGenerate, uploadedFile, rawText, outputFormat, layout, settings]);

  const handleReset = useCallback(() => {
    setDownloadUrl('');
    setUploadedFile(null);
  }, []);

  const resultState = isLoading ? 'loading' : downloadUrl ? 'success' : 'empty';

  return (
    <div className="min-h-screen flex flex-col bg-white/80 text-black">
      {/* 渐变光晕背景 */}
      <div className="glow-background">
        <div className="glow-orb glow-orb-1" />
        <div className="glow-orb glow-orb-2" />
        <div className="glow-orb glow-orb-3" />
        <div className="glow-orb glow-orb-4" />
      </div>

      {/* 侧边栏 */}
      <Sidebar
        isOpen={sidebarOpen}
        onToggle={() => setSidebarOpen(!sidebarOpen)}
        title="设置"
      >
        <SidebarSettings settings={settings} onSettingsChange={setSettings} />

        <SidebarSection title="输出选项">
          {formatOptions.length > 0 && (
            <Select
              label="输出格式"
              options={formatOptions}
              value={outputFormat}
              onChange={(e: ChangeEvent<HTMLSelectElement>) => setOutputFormat(e.target.value)}
            />
          )}

          {outputFormat === 'xmind' && (
            <Select
              label="布局方式"
              options={LAYOUT_OPTIONS}
              value={layout}
              onChange={(e: ChangeEvent<HTMLSelectElement>) => setLayout(e.target.value)}
            />
          )}
        </SidebarSection>
      </Sidebar>

      {/* 主内容区域 */}
      <div
        className="flex-1 flex flex-col min-h-screen transition-all duration-300 relative z-10"
        style={{ marginLeft: sidebarOpen ? '256px' : '0' }}
      >
        <Header
          onSidebarToggle={() => setSidebarOpen(!sidebarOpen)}
          showMenuButton={!sidebarOpen}
        />

        <main className="flex-1 flex flex-col lg:flex-row p-8 gap-8 max-w-6xl mx-auto w-full">
          {/* 输入区域 */}
          <div className="flex-1 flex flex-col gap-5 min-w-0">
            <div className="flex items-center justify-between">
              <h2 className="text-base font-bold text-black tracking-tight">输入内容</h2>
              <span className="text-[11px] font-medium text-black/30 uppercase tracking-wider">支持文本或文件</span>
            </div>

            <FileUpload file={uploadedFile} onFileChange={setUploadedFile} />

            <div className="flex items-center gap-3 text-[11px] font-medium text-black/25 uppercase tracking-wider">
              <span className="flex-1 h-px bg-black/[0.06]" />
              <span>或输入文本</span>
              <span className="flex-1 h-px bg-black/[0.06]" />
            </div>

            <Textarea
              value={rawText}
              onChange={(e: ChangeEvent<HTMLTextAreaElement>) => setRawText(e.target.value)}
              placeholder={`请输入一段文本，AI 将自动为您整理成结构化内容...\n\n例如：\n帮我整理一份关于 Python 学习路线的脑图，包含基础语法、数据结构、常用库和Web开发框架。`}
              className="min-h-[240px]"
            />

            <Button
              variant="primary"
              size="lg"
              onClick={handleGenerate}
              disabled={!canGenerate || isLoading}
              isLoading={isLoading}
              className="w-full font-bold text-[15px]"
            >
              <Sparkles className="w-4 h-4" />
              立即生成
            </Button>
          </div>

          {/* 结果区域 */}
          <div className="flex-1 min-w-0 lg:max-w-sm">
            <ResultCard
              state={resultState}
              statusMessage={statusMessage}
              downloadUrl={downloadUrl}
              formatDescription={currentFormat?.description}
              formatExtension={currentFormat?.extension}
              onReset={handleReset}
            />
          </div>
        </main>
      </div>
    </div>
  );
}
