"""
XMind 格式化器
将树形结构转换为 XMind 思维导图文件
"""

import json
import zipfile
import os
import random
from datetime import datetime
from typing import List, Dict, Any
from .base import BaseFormatter


class XMindFormatter(BaseFormatter):
    """XMind 格式化器"""

    # 布局样式映射
    LAYOUT_MAP = {
        "right": "org.xmind.ui.logic.right",
        "map": "org.xmind.ui.map.unbalanced",
        "tree": "org.xmind.ui.tree.right",
        "org": "org.xmind.ui.org.down"
    }

    @property
    def format_name(self) -> str:
        return "xmind"

    @property
    def file_extension(self) -> str:
        return ".xmind"

    @property
    def description(self) -> str:
        return "XMind 思维导图格式"

    def _gen_id(self) -> str:
        """生成唯一 ID"""
        return ''.join(random.choices('0123456789abcdef', k=26))

    def _build_node(self, text: str, children: List[Dict] = None,
                    structure_class: str = None) -> Dict:
        """构建单个节点"""
        node = {
            "id": self._gen_id(),
            "title": text
        }

        if structure_class:
            node["structureClass"] = structure_class

        if children:
            node["children"] = {
                "attached": children
            }

        return node

    def _build_tree(self, nodes: List[Dict[str, Any]],
                    structure_class: str) -> List[Dict]:
        """递归构建任意深度的节点树"""
        result = []
        for node in nodes:
            children = None
            if node["children"]:
                children = self._build_tree(node["children"], structure_class)
            result.append(self._build_node(node["text"], children, structure_class))
        return result

    def format(self, title: str, tree_nodes: List[Dict[str, Any]],
               layout: str = "right", **options) -> Dict:
        """
        将树形结构格式化为 XMind 内容

        参数:
            title: 根节点标题
            tree_nodes: 树形结构节点列表
            layout: 布局类型 ('right', 'map', 'tree', 'org')
            **options: 其他选项

        返回:
            XMind 内容字典
        """
        # 获取布局样式
        structure_class = self.LAYOUT_MAP.get(layout, self.LAYOUT_MAP["right"])

        # 构建所有子节点
        attached_nodes = self._build_tree(tree_nodes, structure_class)

        # 构建根节点
        root_topic = self._build_node(title, attached_nodes, structure_class)

        # 完整的 XMind 结构
        content = [{
            "id": self._gen_id(),
            "title": "画布 1",
            "rootTopic": root_topic
        }]

        return {
            "content": content,
            "metadata": {
                "creator": {
                    "name": "txt2xmind",
                    "version": "2.0"
                },
                "created": int(datetime.now().timestamp() * 1000)
            },
            "manifest": {
                "file-entries": {
                    "content.json": {},
                    "metadata.json": {}
                }
            }
        }

    def save(self, content: Dict, filename: str) -> None:
        """
        保存为 .xmind 文件

        参数:
            content: format() 方法返回的内容字典
            filename: 输出文件路径
        """
        # 创建临时目录
        temp_dir = "temp_xmind"
        os.makedirs(temp_dir, exist_ok=True)

        try:
            # 写入 content.json
            with open(f"{temp_dir}/content.json", "w", encoding="utf-8") as f:
                json.dump(content["content"], f, ensure_ascii=False, indent=2)

            # 写入 metadata.json
            with open(f"{temp_dir}/metadata.json", "w", encoding="utf-8") as f:
                json.dump(content["metadata"], f, ensure_ascii=False, indent=2)

            # 写入 manifest.json
            with open(f"{temp_dir}/manifest.json", "w", encoding="utf-8") as f:
                json.dump(content["manifest"], f, ensure_ascii=False, indent=2)

            # 打包成 .xmind 文件（实际上是 ZIP）
            with zipfile.ZipFile(filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(f"{temp_dir}/content.json", "content.json")
                zipf.write(f"{temp_dir}/metadata.json", "metadata.json")
                zipf.write(f"{temp_dir}/manifest.json", "manifest.json")

        finally:
            # 清理临时文件
            for file in ["content.json", "metadata.json", "manifest.json"]:
                filepath = f"{temp_dir}/{file}"
                if os.path.exists(filepath):
                    os.remove(filepath)
            if os.path.exists(temp_dir):
                os.rmdir(temp_dir)

        print(f"[OK] XMind 文件生成成功: {filename}")
