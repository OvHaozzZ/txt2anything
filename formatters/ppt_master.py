"""
PowerPoint 格式化器（基于 ppt-master）
集成 ppt-master 的 SVG 生成和转换工具链
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import List, Dict, Any
from .base import BaseFormatter


class PPTMasterFormatter(BaseFormatter):
    """PowerPoint 格式化器（使用 ppt-master 工具链）"""

    def __init__(self):
        # ppt-master 项目路径
        self.ppt_master_path = Path("c:/Users/22836/Desktop/workspace/ppt-master")

        # 检查 ppt-master 是否存在
        if not self.ppt_master_path.exists():
            raise RuntimeError(
                f"ppt-master 项目未找到: {self.ppt_master_path}\n"
                "请确保已克隆 ppt-master 项目到指定路径"
            )

        # 工具路径
        self.tools_path = self.ppt_master_path / "tools"
        self.svg_to_pptx = self.tools_path / "svg_to_pptx.py"
        self.finalize_svg = self.tools_path / "finalize_svg.py"

    @property
    def format_name(self) -> str:
        return "ppt"

    @property
    def file_extension(self) -> str:
        return ".pptx"

    @property
    def description(self) -> str:
        return "PowerPoint 演示文稿格式（基于 ppt-master）"

    def _generate_svg_from_tree(self, title: str, tree_nodes: List[Dict[str, Any]],
                                output_dir: Path) -> List[Path]:
        """
        从树形结构生成 SVG 文件

        这里我们创建简单的 SVG 幻灯片
        在实际应用中，可以调用 AI 生成更专业的 SVG
        """
        svg_files = []

        # 创建标题页 SVG
        title_svg = self._create_title_slide_svg(title)
        title_file = output_dir / "slide_01_title.svg"
        title_file.write_text(title_svg, encoding='utf-8')
        svg_files.append(title_file)

        # 为每个一级节点创建内容页 SVG
        for idx, node in enumerate(tree_nodes, start=2):
            content_svg = self._create_content_slide_svg(
                node["text"],
                node.get("children", [])
            )
            content_file = output_dir / f"slide_{idx:02d}_{self._sanitize_filename(node['text'])}.svg"
            content_file.write_text(content_svg, encoding='utf-8')
            svg_files.append(content_file)

        return svg_files

    def _sanitize_filename(self, text: str) -> str:
        """清理文件名中的非法字符"""
        import re
        # 移除非法字符
        text = re.sub(r'[<>:"/\\|?*]', '', text)
        # 限制长度
        return text[:30]

    def _create_title_slide_svg(self, title: str) -> str:
        """创建标题幻灯片 SVG"""
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720">
  <defs>
    <linearGradient id="bgGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#003366;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#1565C0;stop-opacity:1" />
    </linearGradient>
  </defs>

  <!-- 背景 -->
  <rect width="1280" height="720" fill="url(#bgGradient)"/>

  <!-- 标题 -->
  <text x="640" y="360" font-family="Microsoft YaHei, Arial, sans-serif"
        font-size="64" font-weight="bold" fill="white"
        text-anchor="middle" dominant-baseline="middle">
    {self._escape_xml(title)}
  </text>
</svg>'''

    def _create_content_slide_svg(self, title: str, children: List[Dict[str, Any]]) -> str:
        """创建内容幻灯片 SVG"""
        # 构建内容项
        content_items = self._flatten_tree(children, level=0)

        # 生成列表项的 SVG
        items_svg = []
        y_pos = 200
        for item in content_items[:8]:  # 最多显示8项
            indent = item['level'] * 40
            items_svg.append(f'''
  <text x="{120 + indent}" y="{y_pos}" font-family="Microsoft YaHei, Arial, sans-serif"
        font-size="24" fill="#333333">
    • {self._escape_xml(item['text'])}
  </text>''')
            y_pos += 50

        return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720">
  <!-- 背景 -->
  <rect width="1280" height="720" fill="#FFFFFF"/>

  <!-- 标题栏 -->
  <rect width="1280" height="100" fill="#003366"/>
  <text x="640" y="55" font-family="Microsoft YaHei, Arial, sans-serif"
        font-size="36" font-weight="bold" fill="white"
        text-anchor="middle" dominant-baseline="middle">
    {self._escape_xml(title)}
  </text>

  <!-- 内容列表 -->
  {''.join(items_svg)}
</svg>'''

    def _flatten_tree(self, nodes: List[Dict[str, Any]], level: int = 0) -> List[Dict[str, Any]]:
        """扁平化树结构为列表"""
        items = []
        for node in nodes:
            items.append({'text': node['text'], 'level': level})
            if node.get('children'):
                items.extend(self._flatten_tree(node['children'], level + 1))
        return items

    def _escape_xml(self, text: str) -> str:
        """转义 XML 特殊字符"""
        return (text.replace('&', '&amp;')
                   .replace('<', '&lt;')
                   .replace('>', '&gt;')
                   .replace('"', '&quot;')
                   .replace("'", '&apos;'))

    def _run_ppt_master_tool(self, script: Path, *args) -> subprocess.CompletedProcess:
        """运行 ppt-master 工具脚本"""
        cmd = [sys.executable, str(script)] + list(args)
        result = subprocess.run(
            cmd,
            cwd=str(self.ppt_master_path),
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        return result

    def format(self, title: str, tree_nodes: List[Dict[str, Any]], **options) -> Path:
        """
        将树形结构格式化为 PowerPoint 演示文稿

        参数:
            title: 演示文稿标题
            tree_nodes: 树形结构节点列表
            **options: 其他选项

        返回:
            临时项目目录路径
        """
        import tempfile
        import shutil

        # 创建临时项目目录
        temp_dir = Path(tempfile.mkdtemp(prefix="txt2ppt_"))
        svg_output_dir = temp_dir / "svg_output"
        svg_final_dir = temp_dir / "svg_final"
        svg_output_dir.mkdir(parents=True)
        svg_final_dir.mkdir(parents=True)

        try:
            # 1. 生成 SVG 文件
            print("[1/3] 生成 SVG 幻灯片...")
            svg_files = self._generate_svg_from_tree(title, tree_nodes, svg_output_dir)
            print(f"      生成了 {len(svg_files)} 张幻灯片")

            # 2. 运行 finalize_svg.py 进行后处理
            print("[2/3] SVG 后处理...")
            result = self._run_ppt_master_tool(
                self.finalize_svg,
                str(svg_output_dir)
            )

            if result.returncode != 0:
                print(f"      警告: SVG 后处理失败，使用原始 SVG")
                print(f"      错误: {result.stderr}")
                # 复制原始 SVG 到 final 目录
                for svg_file in svg_files:
                    shutil.copy(svg_file, svg_final_dir / svg_file.name)
            else:
                print(f"      SVG 后处理完成")
                # 查找处理后的 SVG
                processed_svgs = list(svg_output_dir.glob("*.svg"))
                if processed_svgs:
                    for svg in processed_svgs:
                        shutil.copy(svg, svg_final_dir / svg.name)
                else:
                    # 如果没有处理后的文件，使用原始文件
                    for svg_file in svg_files:
                        shutil.copy(svg_file, svg_final_dir / svg_file.name)

            return temp_dir

        except Exception as e:
            # 清理临时目录
            shutil.rmtree(temp_dir, ignore_errors=True)
            raise RuntimeError(f"PPT 生成失败: {e}")

    def save(self, content: Path, filename: str) -> None:
        """
        保存为 .pptx 文件

        参数:
            content: format() 方法返回的临时项目目录
            filename: 输出文件路径
        """
        import shutil

        temp_dir = content
        svg_final_dir = temp_dir / "svg_final"

        try:
            # 3. 运行 svg_to_pptx.py 转换为 PPTX
            print("[3/3] 转换为 PPTX...")

            # 确保输出目录存在
            output_path = Path(filename)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            result = self._run_ppt_master_tool(
                self.svg_to_pptx,
                str(svg_final_dir),
                "-o", str(output_path)
            )

            if result.returncode != 0:
                raise RuntimeError(f"PPTX 转换失败: {result.stderr}")

            print(f"[OK] PowerPoint 文件生成成功: {filename}")

        finally:
            # 清理临时目录
            shutil.rmtree(temp_dir, ignore_errors=True)
