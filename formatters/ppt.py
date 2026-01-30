"""
PowerPoint 格式化器（完整集成 ppt-master）
独立部署版本，包含所有必需的工具和依赖
支持 AI 生成专业 SVG 幻灯片
"""

import os
import sys
import shutil
import tempfile
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from .base import BaseFormatter

logger = logging.getLogger(__name__)


class PPTFormatter(BaseFormatter):
    """PowerPoint 格式化器（完整版，支持 AI 生成 SVG）"""

    def __init__(self):
        # ppt_tools 路径
        self.tools_dir = Path(__file__).parent.parent / "ppt_tools"

        # 检查工具是否存在
        required_tools = ['svg_to_pptx.py', 'finalize_svg.py']
        for tool in required_tools:
            if not (self.tools_dir / tool).exists():
                raise RuntimeError(
                    f"缺少必需的工具: {tool}\n"
                    f"请确保 ppt_tools 目录包含所有必需文件"
                )

        # AI 配置（可通过 options 传入）
        self.api_key: Optional[str] = None
        self.model: str = "gemini-3-flash-preview"
        self.style: str = "professional"
        self.use_ai: bool = False

    @property
    def format_name(self) -> str:
        return "ppt"

    @property
    def file_extension(self) -> str:
        return ".pptx"

    @property
    def description(self) -> str:
        return "PowerPoint 演示文稿格式"

    def _generate_svg_slides(self, title: str, tree_nodes: List[Dict[str, Any]],
                            output_dir: Path) -> List[Path]:
        """
        从树形结构生成 SVG 幻灯片

        参数:
            title: 演示文稿标题
            tree_nodes: 树形结构节点列表
            output_dir: 输出目录

        返回:
            生成的 SVG 文件列表
        """
        svg_files = []

        # 判断是否使用 AI 生成
        if self.use_ai and self.api_key:
            svg_files = self._generate_svg_slides_with_ai(title, tree_nodes, output_dir)
            if svg_files:
                return svg_files
            logger.warning("AI 生成 SVG 失败，回退到模板生成")

        # 回退：使用模板生成
        # 1. 生成标题页
        title_svg = self._create_title_slide(title)
        title_file = output_dir / "01_title.svg"
        title_file.write_text(title_svg, encoding='utf-8')
        svg_files.append(title_file)

        # 2. 为每个一级节点生成内容页
        for idx, node in enumerate(tree_nodes, start=2):
            content_svg = self._create_content_slide(
                node["text"],
                node.get("children", [])
            )
            filename = f"{idx:02d}_{self._sanitize_filename(node['text'])}.svg"
            content_file = output_dir / filename
            content_file.write_text(content_svg, encoding='utf-8')
            svg_files.append(content_file)

        return svg_files

    def _generate_svg_slides_with_ai(self, title: str, tree_nodes: List[Dict[str, Any]],
                                     output_dir: Path) -> List[Path]:
        """
        使用 AI 生成 SVG 幻灯片

        参数:
            title: 演示文稿标题
            tree_nodes: 树形结构节点列表
            output_dir: 输出目录

        返回:
            生成的 SVG 文件列表，失败返回空列表
        """
        try:
            from core.ai_svg_generator import generate_title_slide_svg, generate_content_slide_svg
        except ImportError as e:
            logger.error(f"无法导入 AI SVG 生成器: {e}")
            return []

        svg_files = []

        try:
            # 1. 生成标题页
            logger.info("AI 正在生成标题页...")
            title_svg = generate_title_slide_svg(
                title=title,
                api_key=self.api_key,
                model=self.model,
                style=self.style
            )

            if title_svg:
                title_file = output_dir / "01_title.svg"
                title_file.write_text(title_svg, encoding='utf-8')
                svg_files.append(title_file)
                logger.info("标题页生成成功")
            else:
                logger.warning("AI 生成标题页失败")
                return []

            # 2. 为每个一级节点生成内容页
            for idx, node in enumerate(tree_nodes, start=2):
                logger.info(f"AI 正在生成第 {idx} 页: {node['text'][:20]}...")

                # 扁平化子节点
                items = self._flatten_tree(node.get("children", []), max_items=10)

                content_svg = generate_content_slide_svg(
                    title=node["text"],
                    items=items,
                    api_key=self.api_key,
                    model=self.model,
                    style=self.style
                )

                if content_svg:
                    filename = f"{idx:02d}_{self._sanitize_filename(node['text'])}.svg"
                    content_file = output_dir / filename
                    content_file.write_text(content_svg, encoding='utf-8')
                    svg_files.append(content_file)
                    logger.info(f"第 {idx} 页生成成功")
                else:
                    logger.warning(f"AI 生成第 {idx} 页失败，使用模板回退")
                    # 单页失败时使用模板回退
                    content_svg = self._create_content_slide(
                        node["text"],
                        node.get("children", [])
                    )
                    filename = f"{idx:02d}_{self._sanitize_filename(node['text'])}.svg"
                    content_file = output_dir / filename
                    content_file.write_text(content_svg, encoding='utf-8')
                    svg_files.append(content_file)

            return svg_files

        except Exception as e:
            logger.error(f"AI SVG 生成过程出错: {e}")
            return []

    def _sanitize_filename(self, text: str) -> str:
        """清理文件名"""
        import re
        text = re.sub(r'[<>:"/\\|?*]', '', text)
        text = text.replace(' ', '_')
        return text[:30]

    def _create_title_slide(self, title: str) -> str:
        """创建标题幻灯片 SVG（16:9 格式）"""
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720" width="1280" height="720">
  <defs>
    <linearGradient id="titleGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#003366;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#1565C0;stop-opacity:1" />
    </linearGradient>
    <filter id="shadow">
      <feGaussianBlur in="SourceAlpha" stdDeviation="3"/>
      <feOffset dx="0" dy="2" result="offsetblur"/>
      <feComponentTransfer>
        <feFuncA type="linear" slope="0.3"/>
      </feComponentTransfer>
      <feMerge>
        <feMergeNode/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>

  <!-- 背景渐变 -->
  <rect width="1280" height="720" fill="url(#titleGradient)"/>

  <!-- 装饰元素 -->
  <circle cx="1100" cy="150" r="200" fill="#FFFFFF" opacity="0.05"/>
  <circle cx="200" cy="600" r="150" fill="#FFFFFF" opacity="0.05"/>

  <!-- 标题文本 -->
  <text x="640" y="340"
        font-family="Microsoft YaHei, PingFang SC, Arial, sans-serif"
        font-size="72"
        font-weight="bold"
        fill="#FFFFFF"
        text-anchor="middle"
        filter="url(#shadow)">
    {self._escape_xml(title)}
  </text>

  <!-- 副标题 -->
  <text x="640" y="420"
        font-family="Microsoft YaHei, PingFang SC, Arial, sans-serif"
        font-size="24"
        fill="#FFFFFF"
        opacity="0.8"
        text-anchor="middle">
    由 txt2anything 自动生成
  </text>
</svg>'''

    def _create_content_slide(self, title: str, children: List[Dict[str, Any]]) -> str:
        """创建内容幻灯片 SVG"""
        # 扁平化树结构
        items = self._flatten_tree(children, max_items=10)

        # 生成列表项
        items_svg = []
        y_pos = 220
        line_height = 45

        for item in items:
            indent = item['level'] * 40
            x_pos = 100 + indent

            # 项目符号
            bullet_color = "#1565C0" if item['level'] == 0 else "#FF9800"
            items_svg.append(f'''
  <circle cx="{x_pos - 15}" cy="{y_pos - 8}" r="5" fill="{bullet_color}"/>''')

            # 文本
            font_size = 28 if item['level'] == 0 else 24
            items_svg.append(f'''
  <text x="{x_pos}" y="{y_pos}"
        font-family="Microsoft YaHei, PingFang SC, Arial, sans-serif"
        font-size="{font_size}"
        fill="#333333">
    {self._escape_xml(item['text'])}
  </text>''')

            y_pos += line_height

        return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720" width="1280" height="720">
  <!-- 背景 -->
  <rect width="1280" height="720" fill="#FFFFFF"/>

  <!-- 标题栏 -->
  <rect width="1280" height="120" fill="#003366"/>
  <rect y="120" width="1280" height="4" fill="#FF9800"/>

  <!-- 标题文本 -->
  <text x="640" y="75"
        font-family="Microsoft YaHei, PingFang SC, Arial, sans-serif"
        font-size="42"
        font-weight="bold"
        fill="#FFFFFF"
        text-anchor="middle">
    {self._escape_xml(title)}
  </text>

  <!-- 内容列表 -->
  {''.join(items_svg)}

  <!-- 页脚装饰 -->
  <rect y="700" width="1280" height="20" fill="#F5F5F5"/>
</svg>'''

    def _flatten_tree(self, nodes: List[Dict[str, Any]], level: int = 0,
                     max_items: int = 10) -> List[Dict[str, Any]]:
        """扁平化树结构"""
        items = []
        for node in nodes:
            if len(items) >= max_items:
                break
            items.append({'text': node['text'], 'level': level})
            if node.get('children') and level < 2:  # 最多2级缩进
                items.extend(self._flatten_tree(
                    node['children'], level + 1, max_items - len(items)
                ))
        return items

    def _escape_xml(self, text: str) -> str:
        """转义 XML 特殊字符"""
        return (text.replace('&', '&amp;')
                   .replace('<', '&lt;')
                   .replace('>', '&gt;')
                   .replace('"', '&quot;')
                   .replace("'", '&apos;'))

    def _run_svg_finalize(self, project_dir: Path) -> bool:
        """运行 SVG 后处理"""
        try:
            # 导入 finalize_svg 模块
            sys.path.insert(0, str(self.tools_dir))

            # 强制重新加载模块（避免缓存问题）
            import importlib
            import finalize_svg

            # 使用默认选项（全部启用）
            options = {
                'embed_icons': True,
                'crop_images': True,
                'fix_aspect': True,
                'embed_images': True,
                'flatten_text': True,
                'fix_rounded': True,
            }

            # 运行后处理
            success = finalize_svg.finalize_project(project_dir, options, dry_run=False, quiet=True)
            return success
        except Exception as e:
            import traceback
            print(f"警告: SVG 后处理失败: {e}")
            print(f"错误: {traceback.format_exc()}")
            return False
        finally:
            if str(self.tools_dir) in sys.path:
                sys.path.remove(str(self.tools_dir))

    def _run_svg_to_pptx(self, svg_dir: Path, output_file: Path) -> bool:
        """运行 SVG 转 PPTX"""
        try:
            sys.path.insert(0, str(self.tools_dir))
            import svg_to_pptx

            # 获取所有 SVG 文件
            svg_files = sorted(svg_dir.glob("*.svg"))
            if not svg_files:
                raise RuntimeError("没有找到 SVG 文件")

            # 转换为 PPTX
            svg_to_pptx.create_pptx_with_native_svg(svg_files, output_file)
            return True
        except Exception as e:
            print(f"错误: SVG 转 PPTX 失败: {e}")
            raise
        finally:
            if str(self.tools_dir) in sys.path:
                sys.path.remove(str(self.tools_dir))

    def format(self, title: str, tree_nodes: List[Dict[str, Any]], **options) -> Path:
        """
        格式化为 PowerPoint

        参数:
            title: 演示文稿标题
            tree_nodes: 树形结构节点列表
            **options: 其他选项
                - api_key: Gemini API Key（启用 AI 生成）
                - model: AI 模型名称
                - style: 幻灯片风格 (professional/creative/minimal)

        返回:
            临时目录路径
        """
        # 配置 AI 选项
        self.api_key = options.get('api_key')
        self.model = options.get('model', 'gemini-3-flash-preview')
        self.style = options.get('style', 'professional')
        self.use_ai = bool(self.api_key)

        if self.use_ai:
            logger.info(f"启用 AI SVG 生成，模型: {self.model}，风格: {self.style}")

        # 创建临时目录（使用 finalize_svg.py 期望的目录结构）
        temp_dir = Path(tempfile.mkdtemp(prefix="txt2ppt_"))
        svg_output_dir = temp_dir / "svg_output"  # finalize_svg 期望的输入目录
        svg_output_dir.mkdir()

        try:
            if self.use_ai:
                print("[1/3] AI 正在生成 SVG 幻灯片...")
            else:
                print("[1/3] 生成 SVG 幻灯片...")

            svg_files = self._generate_svg_slides(title, tree_nodes, svg_output_dir)
            print(f"      生成了 {len(svg_files)} 张幻灯片")

            print("[2/3] SVG 后处理...")
            self._run_svg_finalize(temp_dir)  # 传递项目根目录，而不是 svg 目录
            print("      后处理完成")

            return temp_dir

        except Exception as e:
            shutil.rmtree(temp_dir, ignore_errors=True)
            raise RuntimeError(f"PPT 生成失败: {e}")

    def save(self, content: Path, filename: str) -> None:
        """
        保存为 PPTX 文件

        参数:
            content: format() 返回的临时目录
            filename: 输出文件路径
        """
        temp_dir = content
        # 优先使用 svg_final（后处理后的），如果不存在则使用 svg_output
        svg_final_dir = temp_dir / "svg_final"
        svg_output_dir = temp_dir / "svg_output"
        svg_dir = svg_final_dir if svg_final_dir.exists() else svg_output_dir
        output_path = Path(filename)

        try:
            print("[3/3] 转换为 PPTX...")
            output_path.parent.mkdir(parents=True, exist_ok=True)
            self._run_svg_to_pptx(svg_dir, output_path)
            print(f"[OK] PowerPoint 文件生成成功: {filename}")

        finally:
            # 清理临时目录
            shutil.rmtree(temp_dir, ignore_errors=True)
