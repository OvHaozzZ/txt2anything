"""
AI SVG 生成器
使用 AI（Gemini）生成专业的 SVG 幻灯片
"""

import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


def generate_svg_with_ai(
    slide_type: str,
    title: str,
    content: List[Dict[str, Any]],
    api_key: str,
    model: str = "gemini-3-flash-preview",
    style: str = "professional"
) -> str:
    """
    使用 AI 生成 SVG 幻灯片

    参数:
        slide_type: 幻灯片类型 ("title" 或 "content")
        title: 幻灯片标题
        content: 内容列表（对于 content 类型）
        api_key: Gemini API Key
        model: 使用的模型
        style: 风格 ("professional", "creative", "minimal")

    返回:
        生成的 SVG 字符串
    """
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        raise RuntimeError("未安装 Google GenAI 库。请运行 `pip install google-genai`")

    if not api_key:
        raise ValueError("需要 API Key 才能使用 AI 生成 SVG")

    # 构建内容描述
    if slide_type == "title":
        content_desc = f"这是一个标题页，主标题是：{title}"
    else:
        items_text = "\n".join([f"- {item['text']}" for item in content[:10]])
        content_desc = f"这是一个内容页，标题是：{title}\n内容要点：\n{items_text}"

    # 系统提示词
    system_prompt = f"""你是一个专业的 SVG 幻灯片设计师。请根据给定的内容生成一个精美的 SVG 幻灯片。

## 严格要求：
1. SVG 尺寸必须是 1280x720（16:9 比例）
2. 必须以 <?xml version="1.0" encoding="UTF-8"?> 开头
3. 必须包含 xmlns="http://www.w3.org/2000/svg"
4. 只输出 SVG 代码，不要有任何其他文字说明
5. 使用中文字体：Microsoft YaHei, PingFang SC, Arial, sans-serif
6. 确保文字不会超出边界

## 设计风格：{style}
- professional: 商务蓝色调，简洁大气，渐变背景
- creative: 多彩渐变，现代感，几何装饰
- minimal: 极简白底，黑色文字，留白充足

## SVG 结构示例：
```xml
<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720" width="1280" height="720">
  <defs>
    <!-- 渐变、滤镜等定义 -->
  </defs>
  <!-- 背景 -->
  <rect width="1280" height="720" fill="..."/>
  <!-- 装饰元素 -->
  <!-- 文字内容 -->
</svg>
```

## 设计要点：
- 标题页：标题居中，字号 60-72px，可添加副标题和装饰元素
- 内容页：标题在顶部，内容用项目符号列表，字号 24-32px
- 使用渐变背景增加层次感
- 添加适当的阴影和装饰元素
- 确保文字清晰可读，对比度足够
"""

    try:
        # 创建客户端
        client = genai.Client(api_key=api_key)

        # 生成配置
        config = types.GenerateContentConfig(
            temperature=0.8,
            top_p=0.95,
            top_k=64,
            max_output_tokens=8192,
            system_instruction=system_prompt,
        )

        prompt = f"请为以下内容生成一个 SVG 幻灯片：\n\n{content_desc}"

        # 调用 API
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=config
        )

        svg_content = response.text.strip()

        # 清理可能的 markdown 代码块标记
        if svg_content.startswith("```"):
            lines = svg_content.split("\n")
            # 移除第一行（```xml 或 ```svg）
            lines = lines[1:]
            # 移除最后一行（```）
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            svg_content = "\n".join(lines)

        # 验证 SVG 基本结构
        if not svg_content.strip().startswith("<?xml") and not svg_content.strip().startswith("<svg"):
            logger.warning("AI 生成的内容不是有效的 SVG，使用回退方案")
            return None

        return svg_content

    except Exception as e:
        logger.error(f"AI SVG 生成失败: {e}")
        return None


def generate_title_slide_svg(
    title: str,
    api_key: str,
    model: str = "gemini-3-flash-preview",
    style: str = "professional"
) -> Optional[str]:
    """生成标题页 SVG"""
    return generate_svg_with_ai(
        slide_type="title",
        title=title,
        content=[],
        api_key=api_key,
        model=model,
        style=style
    )


def generate_content_slide_svg(
    title: str,
    items: List[Dict[str, Any]],
    api_key: str,
    model: str = "gemini-3-flash-preview",
    style: str = "professional"
) -> Optional[str]:
    """生成内容页 SVG"""
    return generate_svg_with_ai(
        slide_type="content",
        title=title,
        content=items,
        api_key=api_key,
        model=model,
        style=style
    )
