"""
Markdown 格式化器
将树形结构转换为 Markdown 层级列表
"""

from typing import List, Dict, Any
from .base import BaseFormatter


class MarkdownFormatter(BaseFormatter):
    """Markdown 格式化器"""

    @property
    def format_name(self) -> str:
        return "markdown"

    @property
    def file_extension(self) -> str:
        return ".md"

    @property
    def description(self) -> str:
        return "Markdown 层级列表格式"

    def _build_markdown_tree(self, nodes: List[Dict[str, Any]],
                            level: int = 0, use_numbers: bool = False) -> str:
        """
        递归构建 Markdown 树形结构

        参数:
            nodes: 节点列表
            level: 当前层级（用于缩进）
            use_numbers: 是否使用数字编号

        返回:
            Markdown 格式的字符串
        """
        result = []
        indent = "  " * level  # 每级缩进 2 个空格

        for i, node in enumerate(nodes, 1):
            # 根据选项使用数字或符号
            if use_numbers:
                marker = f"{i}."
            else:
                marker = "-"

            # 添加当前节点
            result.append(f"{indent}{marker} {node['text']}")

            # 递归处理子节点
            if node['children']:
                result.append(self._build_markdown_tree(
                    node['children'], level + 1, use_numbers
                ))

        return "\n".join(result)

    def format(self, title: str, tree_nodes: List[Dict[str, Any]],
               use_numbers: bool = False, add_title: bool = True,
               title_level: int = 1, **options) -> str:
        """
        将树形结构格式化为 Markdown

        参数:
            title: 根节点标题
            tree_nodes: 树形结构节点列表
            use_numbers: 是否使用数字编号列表（默认使用 - 符号）
            add_title: 是否添加标题行（默认 True）
            title_level: 标题级别（1-6，默认 1）
            **options: 其他选项

        返回:
            Markdown 格式的字符串
        """
        lines = []

        # 添加标题
        if add_title:
            title_prefix = "#" * min(max(title_level, 1), 6)
            lines.append(f"{title_prefix} {title}")
            lines.append("")  # 空行

        # 构建树形结构
        if tree_nodes:
            tree_content = self._build_markdown_tree(tree_nodes, 0, use_numbers)
            lines.append(tree_content)

        return "\n".join(lines)

    def save(self, content: str, filename: str) -> None:
        """
        保存为 .md 文件

        参数:
            content: format() 方法返回的 Markdown 字符串
            filename: 输出文件路径
        """
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"[OK] Markdown 文件生成成功: {filename}")
