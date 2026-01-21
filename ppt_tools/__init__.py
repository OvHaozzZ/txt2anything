"""
PPT 工具模块
集成自 ppt-master 项目的核心工具
"""

from pathlib import Path

# 工具模块路径
TOOLS_DIR = Path(__file__).parent

__all__ = [
    'svg_to_pptx',
    'finalize_svg',
    'embed_icons',
    'embed_images',
]
