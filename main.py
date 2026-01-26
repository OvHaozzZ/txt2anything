"""
多格式思维导图生成工具
支持 XMind、Markdown 等多种输出格式
支持从图片、视频等多媒体文件提取内容
"""

import os
import sys
from core.parser import parse_text
from format_manager import get_format_manager
from extractors import get_extractor_manager


def main():
    """主函数"""
    print("=" * 60)
    print("多格式思维导图生成工具")
    print("=" * 60)
    print()

    # 获取管理器
    format_manager = get_format_manager()
    extractor_manager = get_extractor_manager()

    # 默认参数
    layout = "right"
    output_format = "xmind"
    input_file = None
    extract_only = False
    whisper_model = "base"
    frame_interval = 5.0
    max_frames = 50
    extract_ocr = True
    extract_speech = True

    # 解析命令行参数
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        arg = args[i]

        if arg == "--layout":
            if i + 1 < len(args):
                layout = args[i + 1]
                i += 2
            else:
                print("[错误] --layout 参数需要指定值")
                sys.exit(1)

        elif arg == "--format":
            if i + 1 < len(args):
                output_format = args[i + 1]
                i += 2
            else:
                print("[错误] --format 参数需要指定值")
                sys.exit(1)

        elif arg in ["--input", "-i"]:
            if i + 1 < len(args):
                input_file = args[i + 1]
                i += 2
            else:
                print("[错误] --input 参数需要指定值")
                sys.exit(1)

        elif arg == "--extract-only":
            extract_only = True
            i += 1

        elif arg == "--whisper-model":
            if i + 1 < len(args):
                whisper_model = args[i + 1]
                i += 2
            else:
                print("[错误] --whisper-model 参数需要指定值")
                sys.exit(1)

        elif arg == "--frame-interval":
            if i + 1 < len(args):
                try:
                    frame_interval = float(args[i + 1])
                except ValueError:
                    print("[错误] --frame-interval 参数必须是数字")
                    sys.exit(1)
                i += 2
            else:
                print("[错误] --frame-interval 参数需要指定值")
                sys.exit(1)

        elif arg == "--max-frames":
            if i + 1 < len(args):
                try:
                    max_frames = int(args[i + 1])
                except ValueError:
                    print("[错误] --max-frames 参数必须是整数")
                    sys.exit(1)
                i += 2
            else:
                print("[错误] --max-frames 参数需要指定值")
                sys.exit(1)

        elif arg == "--no-ocr":
            extract_ocr = False
            i += 1

        elif arg == "--no-speech":
            extract_speech = False
            i += 1

        elif arg == "--list-formats":
            print("支持的输出格式:")
            print()
            for fmt in format_manager.list_formats():
                print(f"  {fmt['name']:12} {fmt['extension']:8} - {fmt['description']}")
            print()
            sys.exit(0)

        elif arg == "--list-extractors":
            print("支持的内容提取器:")
            print()
            for ext in extractor_manager.list_extractors():
                print(f"  {ext['name']:12} - {', '.join(ext['formats'])}")
            print()
            sys.exit(0)

        elif arg in ["-h", "--help"]:
            show_help(format_manager, extractor_manager)
            sys.exit(0)

        else:
            # 假设是文件路径
            input_file = arg
            i += 1

    # 如果没有指定文件，显示帮助
    if not input_file:
        show_help(format_manager, extractor_manager)
        sys.exit(0)

    # 检查文件是否存在
    if not os.path.exists(input_file):
        print(f"[错误] 文件不存在: {input_file}")
        sys.exit(1)

    # 判断输入文件类型
    is_multimedia = extractor_manager.is_supported(input_file)
    is_text = input_file.endswith('.txt')

    if not is_multimedia and not is_text:
        print(f"[错误] 不支持的文件类型: {input_file}")
        print()
        print("支持的文件类型:")
        print("  - .txt (缩进文本)")
        for name, formats in extractor_manager.list_supported_formats().items():
            print(f"  - {', '.join(formats)} ({name})")
        sys.exit(1)

    try:
        if is_multimedia:
            # 多媒体文件：先提取内容
            print(f"[读取] 正在从文件提取内容: {input_file}")

            extract_options = {
                'frame_interval': frame_interval,
                'max_frames': max_frames,
                'whisper_model': whisper_model,
                'extract_ocr': extract_ocr,
                'extract_speech': extract_speech,
                'title': os.path.splitext(os.path.basename(input_file))[0]
            }

            content = extractor_manager.extract(input_file, **extract_options)
            print("[完成] 内容提取完成")
            print()

            if extract_only:
                # 仅提取模式：输出内容并退出
                print("=" * 60)
                print("提取的内容:")
                print("=" * 60)
                print(content)
                print("=" * 60)
                sys.exit(0)

            # 解析提取的内容
            title, tree_nodes = parse_text(content=content)
        else:
            # 文本文件：直接解析
            print(f"[读取] 正在解析文件: {input_file}")
            title, tree_nodes = parse_text(txt_file=input_file)

        # 检查格式是否支持
        if not format_manager.is_format_supported(output_format):
            print(f"[错误] 不支持的格式: {output_format}")
            print()
            print("支持的格式:")
            for fmt in format_manager.list_formats():
                print(f"  - {fmt['name']}")
            sys.exit(1)

        # 对于 XMind 格式，验证布局参数
        if output_format == "xmind":
            valid_layouts = ["right", "map", "tree", "org"]
            if layout not in valid_layouts:
                print(f"[错误] 无效的布局参数: {layout}")
                print(f"[提示] 可用的布局: {', '.join(valid_layouts)}")
                sys.exit(1)

        print(f"[格式] {output_format}")
        if output_format == "xmind":
            print(f"[布局] {layout}")

        # 生成输出文件名
        base_name = os.path.splitext(input_file)[0]
        formatter = format_manager.get_formatter(output_format)
        output_file = base_name + formatter.file_extension

        # 导出文件
        options = {}
        if output_format == "xmind":
            options["layout"] = layout

        format_manager.export(output_format, title, tree_nodes, output_file, **options)

    except Exception as e:
        print(f"[错误] 处理失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def show_help(format_manager, extractor_manager):
    """显示帮助信息"""
    print("[用法] python main.py <文件路径> [选项]")
    print()
    print("支持的输入文件:")
    print("  - .txt (缩进文本)")
    for name, formats in extractor_manager.list_supported_formats().items():
        print(f"  - {', '.join(formats)} ({name})")
    print()
    print("基本选项:")
    print("  --format <格式>        输出格式（默认: xmind）")
    print("  --layout <布局>        XMind 布局类型（默认: right）")
    print("  --list-formats         列出所有支持的输出格式")
    print("  --list-extractors      列出所有支持的内容提取器")
    print("  -h, --help             显示此帮助信息")
    print()
    print("多媒体提取选项:")
    print("  --extract-only         仅提取内容，不生成思维导图")
    print("  --whisper-model <模型> Whisper 模型大小（默认: base）")
    print("                         可选: tiny, base, small, medium, large-v3")
    print("  --frame-interval <秒>  视频帧提取间隔（默认: 5.0）")
    print("  --max-frames <数量>    最大帧数（默认: 50）")
    print("  --no-ocr               禁用 OCR 提取（仅视频）")
    print("  --no-speech            禁用语音识别（仅视频）")
    print()
    print("支持的输出格式:")
    for fmt in format_manager.list_formats():
        print(f"  {fmt['name']:12} {fmt['extension']:8} - {fmt['description']}")
    print()
    print("XMind 布局类型:")
    print("  right - 向右展开（逻辑图）[默认]")
    print("  map   - 中心辐射（思维导图）")
    print("  tree  - 树状图（向右）")
    print("  org   - 组织结构图（向下）")
    print()
    print("示例:")
    print("  # 从文本生成")
    print("  python main.py example.txt")
    print("  python main.py example.txt --format markdown")
    print()
    print("  # 从图片生成（OCR）")
    print("  python main.py screenshot.png --format xmind")
    print()
    print("  # 从视频生成（OCR + 语音识别）")
    print("  python main.py lecture.mp4 --format markdown")
    print("  python main.py lecture.mp4 --whisper-model small")
    print()
    print("  # 仅提取内容")
    print("  python main.py video.mp4 --extract-only")
    print()
    print("txt 文件格式:")
    print("-" * 60)
    print("思维导图标题")
    print("  一级节点1")
    print("    二级节点1")
    print("    二级节点2")
    print("  一级节点2")
    print("    二级节点3")
    print("-" * 60)


if __name__ == "__main__":
    main()
