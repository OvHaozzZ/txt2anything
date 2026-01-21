
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
    model: str = "gpt-3.5-turbo"
    layout: str = "right"
    format: str = "xmind"  # 新增：输出格式

def call_openai_to_structure(text: str, api_key: str, base_url: Optional[str], model: str) -> str:
    """
    调用 OpenAI (或兼容的) API 将原始文本结构化为缩进列表。
    """
    try:
        from openai import OpenAI
    except ImportError:
        raise HTTPException(status_code=500, detail="未安装 OpenAI 库。请运行 `pip install openai`。")

    if not api_key:
         raise HTTPException(status_code=400, detail="需要 API Key 才能进行 AI 结构化处理。")

    client_kwargs = {"api_key": api_key}
    if base_url:
        client_kwargs["base_url"] = base_url
    
    # 添加 User-Agent 以避免被拦截
    client_kwargs["default_headers"] = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    client = OpenAI(**client_kwargs)

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

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"OpenAI API Error: {e}")
        raise HTTPException(status_code=502, detail=f"AI 服务错误: {str(e)}")

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
        content = call_openai_to_structure(content, request.api_key, request.base_url, request.model)
        logger.info("AI 结构化完成。")

    # 2. 生成文件
    try:
        # 创建唯一文件名
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        formatter = manager.get_formatter(request.format)
        filename = f"mindmap_{timestamp}{formatter.file_extension}"
        filepath = os.path.join("static", filename)

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
