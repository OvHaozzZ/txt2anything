
import os
import json
import logging
from typing import Optional
from fastapi import FastAPI, HTTPException, Body
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel
import uvicorn
from datetime import datetime

# 导入现有逻辑
from core.parser import parse_text
from format_manager import get_format_manager

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# 确保静态目录存在
os.makedirs("static", exist_ok=True)

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("static/favicon.ico") if os.path.exists("static/favicon.ico") else Response(status_code=204)

class GenerateRequest(BaseModel):
    text: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model: str = "gemini-3-flash-preview"
    layout: str = "right"
    format: str = "xmind"  # 新增：输出格式

def call_gemini_to_structure(text: str, api_key: str, base_url: Optional[str], model: str) -> str:
    """
    调用 Google Gemini API 将原始文本结构化为缩进列表。
    """
    try:
        import google.generativeai as genai
    except ImportError:
        raise HTTPException(status_code=500, detail="未安装 Google Generative AI 库。请运行 `pip install google-generativeai`。")

    if not api_key:
         raise HTTPException(status_code=400, detail="需要 API Key 才能进行 AI 结构化处理。")

    # 配置 Gemini
    genai.configure(api_key=api_key)

    # 如果有 base_url，目前 google-generativeai 库原生支持较弱，通常直接连 Google
    # 但如果用户确实需要自定义端点（例如反代），可能需要更底层的配置或改回 requests 调用
    # 这里我们暂时假设标准用法，忽略 base_url 或仅做日志提示
    if base_url:
        logger.warning("Gemini API 目前主要支持官方端点，Base URL 设置可能无效或需特殊处理。")

    # 使用 Gemini Pro 模型
    # 如果用户传的是 gpt-3.5，我们需要强制转为 gemini 模型
    # 否则直接使用用户传递的模型
    if not model or "gpt" in model:
        target_model = "gemini-3-flash-preview"
    else:
        target_model = model
    
    generation_config = {
        "temperature": 0.7,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }

    system_prompt = """
You are a helpful assistant that summarizes and structures text into a hierarchical indented list.
The output format must be compatible with a specific XMind generator.

Format Rules:
1. The first line must be the Title of the Mind Map.
2. Subsequent lines must use indentation (2 spaces per level) to represent the hierarchy.
3. Do not use bullets like '- ' or '* '. Just pure text with indentation.
4. Keep the text concise and suitable for a mind map node.

Example Input:
"Python is great. It has simple syntax and powerful libraries like pandas and numpy."

Example Output:
Python Overview
  Features
    Simple Syntax
  Libraries
    Data Science
      Pandas
      Numpy
"""

    # 安全设置：尽可能放宽，防止误拦截
    # 注意：使用的 SDK 版本可能需要使用特定的枚举或字符串
    # 这里直接使用字符串键值对，兼容性更好
    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
    ]

    try:
        model_instance = genai.GenerativeModel(
            model_name=target_model,
            system_instruction=system_prompt
        )

        # 使用 generate_content 而不是 chat，适用于单次生成
        response = model_instance.generate_content(
            text,
            generation_config=generation_config,
            safety_settings=safety_settings
        )
        
        # 简单检查 response.text 是否可用
        # 如果被拦截，访问 .text 会抛出 ValueError
        return response.text
        
    except Exception as e:
        logger.error(f"Gemini API Error: {e}")
        # 尝试提供更友好的错误信息
        error_msg = str(e)
        if "403" in error_msg:
             error_msg = "API Key 无效或无权限 (403)"
        raise HTTPException(status_code=502, detail=f"AI 服务错误: {error_msg}")

@app.post("/api/generate")
async def generate_xmind_endpoint(request: GenerateRequest):
    """
    从文本生成思维导图文件（支持多种格式）。
    如果提供了 'api_key'，则先使用 AI 处理文本。
    否则，将文本视为已结构化（已缩进）。
    """
    content = request.text

    # 获取格式管理器
    manager = get_format_manager()

    # 验证格式
    if not manager.is_format_supported(request.format):
        supported = [fmt['name'] for fmt in manager.list_formats()]
        raise HTTPException(
            status_code=400,
            detail=f"不支持的格式: {request.format}。支持的格式: {', '.join(supported)}"
        )

    # 1. AI 处理（可选）
    # 如果用户提供了 API key，我们假设他们想要 AI 结构化。
    # 如果没有，我们假设文本已经是缩进格式的。
    if request.api_key:
        logger.info("正在使用 AI 结构化文本...")
        content = call_gemini_to_structure(content, request.api_key, request.base_url, request.model)
        logger.info("AI 结构化完成。")

    # 2. 生成文件
    try:
        # 创建唯一文件名
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        formatter = manager.get_formatter(request.format)
        filename = f"mindmap_{timestamp}{formatter.file_extension}"
        filepath = os.path.abspath(os.path.join("static", filename))

        # 解析内容
        title, tree_nodes = parse_text(content=content)

        # 导出文件
        options = {}
        if request.format == "xmind":
            options["layout"] = request.layout

        manager.export(request.format, title, tree_nodes, filepath, **options)

        return {
            "download_url": f"/static/{filename}",
            "structured_text": content,
            "format": request.format
        }

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Generation Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/formats")
async def list_formats():
    """列出所有支持的输出格式"""
    manager = get_format_manager()
    return {"formats": manager.list_formats()}

@app.get("/")
async def read_index():
    return FileResponse('static/index.html')

if __name__ == "__main__":
    uvicorn.run("web_app:app", host="0.0.0.0", port=8000, reload=True)
