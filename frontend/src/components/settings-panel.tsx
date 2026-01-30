'use client';

import { type ChangeEvent } from 'react';
import { Input, Select, type SelectOption } from '@/components/ui';
import { SidebarSection } from './sidebar';

const MODEL_OPTIONS: SelectOption[] = [
  { value: 'gemini-3-flash-preview', label: 'Gemini 3.0 Flash' },
  { value: 'gemini-3-pro-preview', label: 'Gemini 3.0 Pro' },
];

interface SettingsData {
  apiKey: string;
  baseUrl: string;
  model: string;
}

interface SidebarSettingsProps {
  settings: SettingsData;
  onSettingsChange: (settings: SettingsData) => void;
}

export function SidebarSettings({ settings, onSettingsChange }: SidebarSettingsProps) {
  const handleChange = (key: keyof SettingsData, value: string) => {
    onSettingsChange({ ...settings, [key]: value });
  };

  return (
    <>
      <SidebarSection title="API 配置">
        <Input
          type="password"
          label="API Key"
          placeholder="sk-..."
          value={settings.apiKey}
          onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange('apiKey', e.target.value)}
        />
        <Input
          type="text"
          label="Base URL"
          placeholder="https://api.openai.com/v1"
          value={settings.baseUrl}
          onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange('baseUrl', e.target.value)}
        />
        <Select
          label="模型"
          options={MODEL_OPTIONS}
          value={settings.model}
          onChange={(e: ChangeEvent<HTMLSelectElement>) => handleChange('model', e.target.value)}
        />
        <p className="text-[11px] text-black/40 mt-2 leading-relaxed">
          留空 API Key 则不使用 AI，仅按缩进生成
        </p>
      </SidebarSection>
    </>
  );
}

// 保留旧的 SettingsPanel 组件以保持兼容性
interface SettingsPanelProps {
  isOpen: boolean;
  settings: SettingsData;
  onSettingsChange: (settings: SettingsData) => void;
}

export function SettingsPanel({ isOpen, settings, onSettingsChange }: SettingsPanelProps) {
  const handleChange = (key: keyof SettingsData, value: string) => {
    onSettingsChange({ ...settings, [key]: value });
  };

  if (!isOpen) return null;

  return (
    <div className="bg-black/[0.02] p-5 rounded-2xl border border-black/[0.06]">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Input
          type="password"
          label="API Key"
          placeholder="sk-..."
          value={settings.apiKey}
          onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange('apiKey', e.target.value)}
        />
        <Input
          type="text"
          label="Base URL (可选)"
          placeholder="https://api.openai.com/v1"
          value={settings.baseUrl}
          onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange('baseUrl', e.target.value)}
        />
        <Select
          label="模型"
          options={MODEL_OPTIONS}
          value={settings.model}
          onChange={(e: ChangeEvent<HTMLSelectElement>) => handleChange('model', e.target.value)}
        />
      </div>
      <p className="text-[11px] text-black/40 mt-3">
        留空 API Key 则不使用 AI，仅按缩进生成
      </p>
    </div>
  );
}
