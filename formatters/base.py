"""
格式化器抽象基类
所有输出格式化器都应继承此类
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any


class BaseFormatter(ABC):
    """格式化器抽象基类"""

    @property
    @abstractmethod
    def format_name(self) -> str:
        """格式名称（如 'xmind', 'markdown', 'json'）"""
        pass

    @property
    @abstractmethod
    def file_extension(self) -> str:
        """文件扩展名（如 '.xmind', '.md', '.json'）"""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """格式描述"""
        pass

    @abstractmethod
    def format(self, title: str, tree_nodes: List[Dict[str, Any]], **options) -> Any:
        """
        将树形结构格式化为目标格式

        参数:
            title: 根节点标题
            tree_nodes: 树形结构节点列表
                格式: [{"text": "节点文本", "children": [...]}, ...]
            **options: 格式特定的选项

        返回:
            格式化后的内容（可能是字符串、字节流或其他类型）
        """
        pass

    @abstractmethod
    def save(self, content: Any, filename: str) -> None:
        """
        保存格式化后的内容到文件

        参数:
            content: format() 方法返回的内容
            filename: 输出文件路径
        """
        pass

    def export(self, title: str, tree_nodes: List[Dict[str, Any]],
               filename: str, **options) -> str:
        """
        完整的导出流程：格式化 + 保存

        参数:
            title: 根节点标题
            tree_nodes: 树形结构节点列表
            filename: 输出文件路径
            **options: 格式特定的选项

        返回:
            输出文件路径
        """
        content = self.format(title, tree_nodes, **options)
        self.save(content, filename)
        return filename
