"""
提取器基类模块
定义多模态内容提取器的抽象接口
"""

from abc import ABC, abstractmethod
from typing import Set, Any


class BaseExtractor(ABC):
    """内容提取器抽象基类"""

    @property
    @abstractmethod
    def supported_formats(self) -> Set[str]:
        """
        支持的文件扩展名集合

        返回:
            扩展名集合，如 {'.jpg', '.png', '.jpeg'}
        """
        pass

    @abstractmethod
    def extract(self, file_path: str, **options) -> str:
        """
        从文件中提取内容

        参数:
            file_path: 文件路径
            **options: 提取选项

        返回:
            提取的缩进格式文本，可直接用于 parser.py 解析
        """
        pass

    def supports(self, file_path: str) -> bool:
        """
        检查是否支持指定文件

        参数:
            file_path: 文件路径

        返回:
            是否支持该文件格式
        """
        from pathlib import Path
        ext = Path(file_path).suffix.lower()
        return ext in self.supported_formats
