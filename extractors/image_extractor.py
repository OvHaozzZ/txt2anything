"""
图片内容提取器
使用 OCR 从图片中提取文字内容
"""

from typing import Set, List, Dict, Optional
from pathlib import Path

from .base import BaseExtractor
from .engines.ocr_engine import OCREngine


class ImageExtractor(BaseExtractor):
    """图片内容提取器"""

    SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.bmp', '.webp', '.tiff', '.tif'}

    def __init__(self, ocr_engine: Optional[OCREngine] = None):
        """
        初始化图片提取器

        参数:
            ocr_engine: OCR 引擎实例，如果不提供则自动创建
        """
        self._ocr = ocr_engine or OCREngine()

    @property
    def supported_formats(self) -> Set[str]:
        return self.SUPPORTED_FORMATS

    def extract(self, file_path: str, **options) -> str:
        """
        从图片中提取文本

        参数:
            file_path: 图片文件路径
            options:
                - preprocess: bool, 是否预处理图片（默认 True）
                - max_size: int, 图片最大尺寸（默认 2048）
                - title: str, 自定义标题（默认使用文件名）

        返回:
            提取的缩进格式文本
        """
        preprocess = options.get('preprocess', True)
        max_size = options.get('max_size', 2048)
        title = options.get('title', None)

        # 加载并预处理图片
        image = self._load_and_preprocess(file_path, preprocess, max_size)

        # OCR 识别
        result = self._ocr.recognize(image)

        # 转换为结构化文本
        return self._format_ocr_result(result, file_path, title)

    def _load_and_preprocess(self, file_path: str, preprocess: bool, max_size: int):
        """加载并预处理图片"""
        try:
            from PIL import Image
        except ImportError:
            raise ImportError("Pillow 未安装。请运行: pip install Pillow")

        image = Image.open(file_path)

        if preprocess:
            # 转换为 RGB（处理 RGBA、灰度等）
            if image.mode != 'RGB':
                image = image.convert('RGB')

            # 自动调整大小（太大的图片会影响速度）
            if max(image.size) > max_size:
                ratio = max_size / max(image.size)
                new_size = (int(image.width * ratio), int(image.height * ratio))
                image = image.resize(new_size, Image.Resampling.LANCZOS)

        return image

    def _format_ocr_result(self, result: List[Dict], file_path: str, custom_title: Optional[str]) -> str:
        """
        将 OCR 结果转换为缩进文本

        基于文本块的位置关系推断层级结构
        """
        if not result:
            title = custom_title or Path(file_path).stem
            return f"{title}\n  （未识别到文字内容）"

        # 按 Y 坐标排序，然后按 X 坐标
        sorted_blocks = sorted(result, key=lambda x: (x['box'][0][1], x['box'][0][0]))

        # 计算基准 X 坐标
        base_x = min(block['box'][0][0] for block in sorted_blocks)

        # 生成标题
        title = custom_title or Path(file_path).stem

        lines = [title]
        prev_y = None
        line_height_threshold = 30  # 行高阈值，用于判断是否换行

        for block in sorted_blocks:
            text = block['text'].strip()
            if not text:
                continue

            x = block['box'][0][0]
            y = block['box'][0][1]

            # 计算缩进级别（基于 X 坐标偏移）
            # 每 50 像素一级缩进
            indent_level = max(0, int((x - base_x) / 50))
            # 至少有一级缩进（因为第一行是标题）
            indent_level = max(1, indent_level)
            indent = "  " * indent_level

            lines.append(f"{indent}{text}")

        return "\n".join(lines)

    def extract_raw(self, file_path: str, **options) -> List[Dict]:
        """
        提取原始 OCR 结果（不格式化）

        参数:
            file_path: 图片文件路径
            options: 同 extract 方法

        返回:
            OCR 识别结果列表
        """
        preprocess = options.get('preprocess', True)
        max_size = options.get('max_size', 2048)

        image = self._load_and_preprocess(file_path, preprocess, max_size)
        return self._ocr.recognize(image)
