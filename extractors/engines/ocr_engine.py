"""
OCR 引擎模块
封装 RapidOCR 进行文字识别
"""

from typing import List, Dict, Any, Union, Optional, TYPE_CHECKING
from pathlib import Path
import numpy as np

if TYPE_CHECKING:
    from PIL import Image


class OCREngine:
    """RapidOCR 引擎封装"""

    def __init__(self, use_gpu: bool = False):
        """
        初始化 OCR 引擎

        参数:
            use_gpu: 是否使用 GPU（需要安装 rapidocr-onnxruntime-gpu）
        """
        self._engine = None
        self._use_gpu = use_gpu

    def _ensure_engine(self):
        """延迟初始化引擎"""
        if self._engine is None:
            try:
                from rapidocr_onnxruntime import RapidOCR
                self._engine = RapidOCR()
            except ImportError:
                raise ImportError(
                    "RapidOCR 未安装。请运行: pip install rapidocr-onnxruntime"
                )

    def recognize(self, image: Union[str, Path, "Image.Image", np.ndarray]) -> List[Dict[str, Any]]:
        """
        识别图片中的文字

        参数:
            image: 图片路径、PIL Image 或 numpy 数组

        返回:
            识别结果列表，每项包含:
            - box: 文本框坐标 [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
            - text: 识别的文本
            - score: 置信度
        """
        self._ensure_engine()

        # 转换输入格式
        if isinstance(image, (str, Path)):
            img_input = str(image)
        elif hasattr(image, 'mode'):  # PIL Image
            img_input = np.array(image)
        else:
            img_input = image

        # 执行识别
        result, elapse = self._engine(img_input)

        if result is None:
            return []

        # 格式化结果
        formatted = []
        for item in result:
            box, text, score = item
            formatted.append({
                'box': box,
                'text': text,
                'score': score
            })

        return formatted

    def recognize_batch(self, images: List[Union[str, "Image.Image", np.ndarray]]) -> List[List[Dict]]:
        """
        批量识别多张图片

        参数:
            images: 图片列表

        返回:
            每张图片的识别结果列表
        """
        return [self.recognize(img) for img in images]

    def is_available(self) -> bool:
        """检查 OCR 引擎是否可用"""
        try:
            self._ensure_engine()
            return True
        except ImportError:
            return False
