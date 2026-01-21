"""
格式管理器
负责注册、管理和调用各种格式化器
"""

from typing import Dict, List, Optional
from formatters.base import BaseFormatter
from formatters.xmind import XMindFormatter
from formatters.markdown import MarkdownFormatter
from formatters.ppt import PPTFormatter


class FormatManager:
    """格式管理器"""

    def __init__(self):
        self._formatters: Dict[str, BaseFormatter] = {}
        self._register_default_formatters()

    def _register_default_formatters(self):
        """注册默认的格式化器"""
        self.register(XMindFormatter())
        self.register(MarkdownFormatter())
        self.register(PPTFormatter())

    def register(self, formatter: BaseFormatter):
        """
        注册一个格式化器

        参数:
            formatter: 格式化器实例
        """
        self._formatters[formatter.format_name] = formatter

    def unregister(self, format_name: str):
        """
        注销一个格式化器

        参数:
            format_name: 格式名称
        """
        if format_name in self._formatters:
            del self._formatters[format_name]

    def get_formatter(self, format_name: str) -> Optional[BaseFormatter]:
        """
        获取指定的格式化器

        参数:
            format_name: 格式名称

        返回:
            格式化器实例，如果不存在则返回 None
        """
        return self._formatters.get(format_name)

    def list_formats(self) -> List[Dict[str, str]]:
        """
        列出所有可用的格式

        返回:
            格式信息列表，每项包含 name, extension, description
        """
        return [
            {
                "name": formatter.format_name,
                "extension": formatter.file_extension,
                "description": formatter.description
            }
            for formatter in self._formatters.values()
        ]

    def is_format_supported(self, format_name: str) -> bool:
        """
        检查是否支持指定格式

        参数:
            format_name: 格式名称

        返回:
            是否支持
        """
        return format_name in self._formatters

    def export(self, format_name: str, title: str, tree_nodes: List[dict],
               filename: str, **options) -> str:
        """
        导出为指定格式

        参数:
            format_name: 格式名称
            title: 根节点标题
            tree_nodes: 树形结构节点列表
            filename: 输出文件路径
            **options: 格式特定的选项

        返回:
            输出文件路径

        异常:
            ValueError: 如果格式不支持
        """
        formatter = self.get_formatter(format_name)
        if not formatter:
            supported = ", ".join(self._formatters.keys())
            raise ValueError(
                f"不支持的格式: {format_name}。"
                f"支持的格式: {supported}"
            )

        return formatter.export(title, tree_nodes, filename, **options)


# 全局格式管理器实例
_global_manager = FormatManager()


def get_format_manager() -> FormatManager:
    """获取全局格式管理器实例"""
    return _global_manager
