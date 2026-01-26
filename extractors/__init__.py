"""
多模态内容提取器模块
支持从图片、视频等多媒体文件中提取文本内容
"""

from typing import Dict, List, Optional, Any
from pathlib import Path

from .base import BaseExtractor
from .image_extractor import ImageExtractor
from .video_extractor import VideoExtractor


class ExtractorManager:
    """提取器管理器"""

    def __init__(self):
        """初始化提取器管理器"""
        self._extractors: Dict[str, BaseExtractor] = {}
        self._extension_map: Dict[str, str] = {}
        self._register_default_extractors()

    def _register_default_extractors(self):
        """注册默认提取器"""
        # 注册图片提取器
        self.register('image', ImageExtractor())

        # 注册视频提取器
        self.register('video', VideoExtractor())

    def register(self, name: str, extractor: BaseExtractor):
        """
        注册提取器

        参数:
            name: 提取器名称
            extractor: 提取器实例
        """
        self._extractors[name] = extractor

        # 建立扩展名到提取器的映射
        for ext in extractor.supported_formats:
            self._extension_map[ext] = name

    def get_extractor(self, name: str) -> Optional[BaseExtractor]:
        """
        获取指定名称的提取器

        参数:
            name: 提取器名称

        返回:
            提取器实例，如果不存在则返回 None
        """
        return self._extractors.get(name)

    def get_extractor_for_file(self, file_path: str) -> Optional[BaseExtractor]:
        """
        根据文件类型获取对应的提取器

        参数:
            file_path: 文件路径

        返回:
            提取器实例，如果不支持该文件类型则返回 None
        """
        ext = Path(file_path).suffix.lower()
        extractor_name = self._extension_map.get(ext)
        if extractor_name:
            return self._extractors.get(extractor_name)
        return None

    def extract(self, file_path: str, **options) -> str:
        """
        从文件中提取内容

        参数:
            file_path: 文件路径
            **options: 提取选项

        返回:
            提取的缩进格式文本

        异常:
            ValueError: 如果不支持该文件类型
        """
        extractor = self.get_extractor_for_file(file_path)
        if extractor is None:
            ext = Path(file_path).suffix.lower()
            supported = list(self._extension_map.keys())
            raise ValueError(
                f"不支持的文件类型: {ext}\n"
                f"支持的格式: {', '.join(sorted(supported))}"
            )

        return extractor.extract(file_path, **options)

    def is_supported(self, file_path: str) -> bool:
        """
        检查是否支持指定文件

        参数:
            file_path: 文件路径

        返回:
            是否支持该文件类型
        """
        ext = Path(file_path).suffix.lower()
        return ext in self._extension_map

    def list_supported_formats(self) -> Dict[str, List[str]]:
        """
        列出所有支持的格式

        返回:
            按提取器分组的格式列表
        """
        result = {}
        for name, extractor in self._extractors.items():
            result[name] = sorted(list(extractor.supported_formats))
        return result

    def list_extractors(self) -> List[Dict[str, Any]]:
        """
        列出所有注册的提取器

        返回:
            提取器信息列表
        """
        return [
            {
                'name': name,
                'formats': sorted(list(extractor.supported_formats)),
                'type': type(extractor).__name__
            }
            for name, extractor in self._extractors.items()
        ]


# 全局提取器管理器实例
_extractor_manager: Optional[ExtractorManager] = None


def get_extractor_manager() -> ExtractorManager:
    """
    获取全局提取器管理器实例

    返回:
        ExtractorManager 实例
    """
    global _extractor_manager
    if _extractor_manager is None:
        _extractor_manager = ExtractorManager()
    return _extractor_manager


# 便捷导出
__all__ = [
    'BaseExtractor',
    'ImageExtractor',
    'VideoExtractor',
    'ExtractorManager',
    'get_extractor_manager',
]
