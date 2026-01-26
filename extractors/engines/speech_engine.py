"""
语音识别引擎模块
封装 faster-whisper 进行语音转文字
"""

from typing import Dict, Any, Optional, List
from pathlib import Path


class SpeechEngine:
    """faster-whisper 语音识别引擎封装"""

    MODEL_SIZES = ['tiny', 'base', 'small', 'medium', 'large-v2', 'large-v3']

    def __init__(self, default_model: str = 'base', device: str = 'auto'):
        """
        初始化语音识别引擎

        参数:
            default_model: 默认模型大小
            device: 运行设备 ('auto', 'cpu', 'cuda')
        """
        self._default_model = default_model
        self._device = device
        self._models: Dict[str, Any] = {}  # 缓存已加载的模型

    def _get_model(self, model_size: str):
        """获取或加载模型"""
        if model_size not in self._models:
            try:
                from faster_whisper import WhisperModel
            except ImportError:
                raise ImportError(
                    "faster-whisper 未安装。请运行: pip install faster-whisper"
                )

            # 确定计算设备和类型
            device = self._device
            if device == 'auto':
                device = 'cuda'
                compute_type = 'float16'
            elif device == 'cuda':
                compute_type = 'float16'
            else:
                device = 'cpu'
                compute_type = 'int8'

            try:
                self._models[model_size] = WhisperModel(
                    model_size,
                    device=device,
                    compute_type=compute_type
                )
            except Exception:
                # GPU 不可用，回退到 CPU
                self._models[model_size] = WhisperModel(
                    model_size,
                    device='cpu',
                    compute_type='int8'
                )

        return self._models[model_size]

    def transcribe(
        self,
        audio_path: str,
        model_size: Optional[str] = None,
        language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        转录音频文件

        参数:
            audio_path: 音频文件路径
            model_size: 模型大小（默认使用初始化时的设置）
            language: 语言代码（None 表示自动检测）

        返回:
            {
                'text': str,           # 完整文本
                'language': str,       # 检测到的语言
                'segments': [          # 分段信息
                    {
                        'start': float,
                        'end': float,
                        'text': str
                    },
                    ...
                ]
            }
        """
        model = self._get_model(model_size or self._default_model)

        segments, info = model.transcribe(
            audio_path,
            language=language,
            beam_size=5,
            vad_filter=True,  # 启用 VAD 过滤静音
            vad_parameters=dict(
                min_silence_duration_ms=500
            )
        )

        # 收集所有分段
        segment_list = []
        full_text_parts = []

        for segment in segments:
            segment_list.append({
                'start': segment.start,
                'end': segment.end,
                'text': segment.text.strip()
            })
            full_text_parts.append(segment.text.strip())

        return {
            'text': ' '.join(full_text_parts),
            'language': info.language,
            'segments': segment_list
        }

    def is_available(self) -> bool:
        """检查语音识别引擎是否可用"""
        try:
            from faster_whisper import WhisperModel
            return True
        except ImportError:
            return False

    def list_models(self) -> List[str]:
        """列出可用的模型大小"""
        return self.MODEL_SIZES.copy()
