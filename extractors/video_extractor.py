"""
视频内容提取器
使用 OCR 和语音识别从视频中提取内容
"""

from typing import Set, List, Dict, Optional, Any
from pathlib import Path
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import os

from .base import BaseExtractor
from .engines.ocr_engine import OCREngine
from .engines.speech_engine import SpeechEngine
from .engines.video_processor import VideoProcessor


@dataclass
class ContentItem:
    """内容项"""
    timestamp: float
    text: str
    source: str  # 'ocr' 或 'speech'


class VideoExtractor(BaseExtractor):
    """视频内容提取器"""

    SUPPORTED_FORMATS = {'.mp4', '.avi', '.mov', '.mkv', '.webm', '.wmv'}

    def __init__(
        self,
        ocr_engine: Optional[OCREngine] = None,
        speech_engine: Optional[SpeechEngine] = None,
        video_processor: Optional[VideoProcessor] = None
    ):
        """
        初始化视频提取器

        参数:
            ocr_engine: OCR 引擎实例
            speech_engine: 语音识别引擎实例
            video_processor: 视频处理器实例
        """
        self._ocr = ocr_engine
        self._speech = speech_engine
        self._video = video_processor or VideoProcessor()

    def _ensure_ocr(self):
        """确保 OCR 引擎可用"""
        if self._ocr is None:
            self._ocr = OCREngine()

    def _ensure_speech(self):
        """确保语音引擎可用"""
        if self._speech is None:
            self._speech = SpeechEngine()

    @property
    def supported_formats(self) -> Set[str]:
        return self.SUPPORTED_FORMATS

    def extract(self, file_path: str, **options) -> str:
        """
        从视频中提取文本内容

        参数:
            file_path: 视频文件路径
            options:
                - extract_ocr: bool, 是否提取 OCR（默认 True）
                - extract_speech: bool, 是否提取语音（默认 True）
                - frame_interval: float, 帧间隔秒数（默认 5.0）
                - max_frames: int, 最大帧数（默认 50）
                - whisper_model: str, Whisper 模型大小（默认 'base'）
                - parallel: bool, 是否并行处理（默认 True）
                - title: str, 自定义标题

        返回:
            合并后的缩进格式文本
        """
        extract_ocr = options.get('extract_ocr', True)
        extract_speech = options.get('extract_speech', True)
        parallel = options.get('parallel', True)
        title = options.get('title', None)

        ocr_items: List[ContentItem] = []
        speech_items: List[ContentItem] = []

        if parallel and extract_ocr and extract_speech:
            # 并行处理 OCR 和语音识别
            with ThreadPoolExecutor(max_workers=2) as executor:
                ocr_future = executor.submit(
                    self._extract_ocr, file_path, options
                )
                speech_future = executor.submit(
                    self._extract_speech, file_path, options
                )

                ocr_items = ocr_future.result()
                speech_items = speech_future.result()
        else:
            # 串行处理
            if extract_ocr:
                ocr_items = self._extract_ocr(file_path, options)
            if extract_speech:
                speech_items = self._extract_speech(file_path, options)

        # 按时间线合并结果
        return self._merge_by_timeline(ocr_items, speech_items, file_path, title)

    def _extract_ocr(self, file_path: str, options: dict) -> List[ContentItem]:
        """提取视频帧中的文字"""
        self._ensure_ocr()

        interval = options.get('frame_interval', 5.0)
        max_frames = options.get('max_frames', 50)

        # 提取帧
        frames = self._video.extract_frames(
            file_path,
            interval=interval,
            max_frames=max_frames
        )

        items: List[ContentItem] = []
        seen_texts = set()  # 用于去重

        try:
            for frame_info in frames:
                try:
                    from PIL import Image
                    image = Image.open(frame_info['path'])
                    result = self._ocr.recognize(image)

                    for item in result:
                        text = item['text'].strip()
                        # 简单去重：完全相同的文本只保留一次
                        if text and text not in seen_texts and len(text) > 2:
                            seen_texts.add(text)
                            items.append(ContentItem(
                                timestamp=frame_info['timestamp'],
                                text=text,
                                source='ocr'
                            ))
                except Exception:
                    continue
        finally:
            # 清理临时帧文件
            self._video.cleanup_frames(frames)

        return items

    def _extract_speech(self, file_path: str, options: dict) -> List[ContentItem]:
        """提取视频中的语音"""
        self._ensure_speech()

        model_size = options.get('whisper_model', 'base')

        # 检查视频是否有音频
        info = self._video.get_video_info(file_path)
        if not info.get('has_audio', True):
            return []

        # 提取音频
        audio_path = None
        try:
            audio_path = self._video.extract_audio(file_path)

            # 语音识别
            result = self._speech.transcribe(audio_path, model_size=model_size)

            items: List[ContentItem] = []
            for segment in result.get('segments', []):
                text = segment['text'].strip()
                if text:
                    items.append(ContentItem(
                        timestamp=segment['start'],
                        text=text,
                        source='speech'
                    ))

            return items
        except Exception:
            return []
        finally:
            if audio_path and os.path.exists(audio_path):
                try:
                    os.remove(audio_path)
                except OSError:
                    pass

    def _merge_by_timeline(
        self,
        ocr_items: List[ContentItem],
        speech_items: List[ContentItem],
        file_path: str,
        custom_title: Optional[str]
    ) -> str:
        """
        按时间线合并 OCR 和语音识别结果

        将画面文字和语音内容按时间戳交织排列
        """
        title = custom_title or Path(file_path).stem

        if not ocr_items and not speech_items:
            return f"{title}\n  （未能从视频中提取内容）"

        # 合并所有内容项并按时间戳排序
        all_items = ocr_items + speech_items
        all_items.sort(key=lambda x: x.timestamp)

        lines = [title]

        for item in all_items:
            timestamp_str = self._format_timestamp(item.timestamp)
            if item.source == 'ocr':
                # OCR 内容用【画面】标记
                lines.append(f"  [{timestamp_str}] 【画面】{item.text}")
            else:
                # 语音内容直接显示
                lines.append(f"  [{timestamp_str}] {item.text}")

        return "\n".join(lines)

    def _format_timestamp(self, seconds: float) -> str:
        """格式化时间戳为 MM:SS 格式"""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"

    def extract_ocr_only(self, file_path: str, **options) -> str:
        """仅提取 OCR 内容"""
        options['extract_speech'] = False
        return self.extract(file_path, **options)

    def extract_speech_only(self, file_path: str, **options) -> str:
        """仅提取语音内容"""
        options['extract_ocr'] = False
        return self.extract(file_path, **options)
